import json
import os
import logging
import traceback
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_NAME = "minilm_l6_v2_embeddings.npz"
CORPUS_PATH = "backend/rag/corpus/clinical_practical_guide/"

_rag = None
_tried = False


class RAGService:
    def __init__(self, corpus_path: str):
        self.corpus_dir = corpus_path
        self.documents: List[Dict] = []
        self.embeddings = None
        self.reranker = None
        print(f"🧠 Loading {EMBED_MODEL}...")
        self.embedding_model = SentenceTransformer(EMBED_MODEL)
        try:
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            print("✅ CrossEncoder loaded")
        except Exception as e:
            # ponytail: skip rerank if MiniLM CrossEncoder OOMs; cosine still works
            print(f"⚠️ CrossEncoder skipped: {e}")
        self.load_documents()

    def _cache_path(self) -> str:
        return os.path.join(self.corpus_dir, CACHE_NAME)

    def load_documents(self) -> None:
        texts, sources, titles = [], [], []
        if not os.path.exists(self.corpus_dir):
            logging.warning(f"Corpus directory not found: {self.corpus_dir}")
            return
        for filename in sorted(os.listdir(self.corpus_dir)):
            if not filename.endswith(".jsonl"):
                continue
            with open(os.path.join(self.corpus_dir, filename), "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    doc = json.loads(line)
                    texts.append(doc.get("text", ""))
                    sources.append(filename)
                    titles.append(doc.get("source_document_title") or filename)
        self.documents = [{"text": t, "source": s, "title": ti} for t, s, ti in zip(texts, sources, titles)]
        cache = self._cache_path()
        if os.path.exists(cache):
            data = np.load(cache)
            if len(data["embeddings"]) == len(texts):
                self.embeddings = data["embeddings"]
                print(f"✅ MiniLM cache loaded: {len(texts)} chunks")
                return
        print(f"🧠 Embedding {len(texts)} CPG chunks with MiniLM (first run)...")
        self.embeddings = self.embedding_model.encode(
            texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True
        )
        np.savez_compressed(cache, embeddings=self.embeddings)
        print(f"✅ MiniLM cache saved ({len(texts)} chunks)")

    def retrieve_relevant_documents(self, query_text: str, top_k: int = 5) -> List[Dict]:
        if self.embeddings is None or not self.documents:
            return []
        q = self.embedding_model.encode([query_text], normalize_embeddings=True)[0]
        sims = self.embeddings @ q
        pool = min(max(top_k * 4, top_k), len(self.documents), 20)
        idx = np.argpartition(sims, -pool)[-pool:]
        idx = idx[np.argsort(sims[idx])[::-1]]
        results = [{**self.documents[int(i)], "similarity_score": float(sims[int(i)])} for i in idx]
        if self.reranker and results:
            pairs = [(query_text, r["text"][:512]) for r in results]
            scores = self.reranker.predict(pairs)
            for r, s in zip(results, scores):
                r["rerank_score"] = float(s)
            results.sort(key=lambda x: x["rerank_score"], reverse=True)
        return results[:top_k]

    def get_clinical_guidelines_context(self, query_text: str, top_k: int = 3):
        if not query_text:
            return "", []
        try:
            docs = self.retrieve_relevant_documents(query_text, top_k)
            if not docs:
                return "", []
            context = "\n\nRelevant Clinical Guidelines:\n---\n" + "\n".join(
                f"- {doc['text'][:400]} (Source: {doc.get('title') or doc['source']}, Score: {doc['similarity_score']:.2f})"
                for doc in docs
            )
            cites = list(dict.fromkeys(
                (doc.get("title") or doc.get("source") or "CPG").replace(" cleaned ultra minimal", "").strip()
                for doc in docs
            ))
            return context + "\n\n", cites
        except Exception as e:
            print(f"⚠️ Error retrieving clinical guidelines: {e}\n{traceback.format_exc()}")
            return "", []


def get_clinical_guidelines_context(query_text: str, top_k: int = 3):
    global _rag, _tried
    if not _tried:
        _tried = True
        try:
            _rag = RAGService(CORPUS_PATH)
            print("✅ Knowledge Base service initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize Knowledge Base service: {e}\n{traceback.format_exc()}")
            _rag = None
    if not _rag:
        return "", []
    return _rag.get_clinical_guidelines_context(query_text, top_k)
