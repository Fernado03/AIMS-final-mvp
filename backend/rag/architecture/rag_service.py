import json
import os
import logging
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CACHE_NAME = "minilm_l6_v2_embeddings.npz"


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
        texts: List[str] = []
        sources: List[str] = []
        titles: List[str] = []
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

    def get_document_by_text(self, text: str) -> Optional[Dict]:
        for doc in self.documents:
            if doc.get("text") == text:
                return doc
        return None
