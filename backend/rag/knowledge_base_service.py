# rag/knowledge_base_service.py

import traceback
from typing import Optional

class KnowledgeBaseService:
    def __init__(self, corpus_path: str = "backend/rag/corpus/clinical_practical_guide/"):
        self.corpus_path = corpus_path
        self.rag_service = None
        self._tried = False

    def _ensure(self):
        if self._tried:
            return
        self._tried = True
        try:
            from backend.rag.architecture.rag_service import RAGService
            self.rag_service = RAGService(self.corpus_path)
            print("✅ Knowledge Base service initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize Knowledge Base service: {e}\n{traceback.format_exc()}")
            self.rag_service = None


    def get_clinical_guidelines_context(self, query_text: str, top_k: int = 3):
        self._ensure()
        if not self.rag_service or not query_text:
            return "", []
        try:
            relevant_docs = self.rag_service.retrieve_relevant_documents(query_text, top_k)
            if not relevant_docs:
                return "", []
            context = "\n\nRelevant Clinical Guidelines:\n---\n"
            context += "\n".join([
                f"- {doc['text'][:400]} (Source: {doc.get('title') or doc['source']}, Score: {doc['similarity_score']:.2f})"
                for doc in relevant_docs
            ])
            cites = list(dict.fromkeys(
                (doc.get("title") or doc.get("source") or "CPG").replace(" cleaned ultra minimal", "").strip()
                for doc in relevant_docs
            ))
            return context + "\n\n", cites
        except Exception as e:
            print(f"⚠️ Error retrieving clinical guidelines: {e}\n{traceback.format_exc()}")
            return "", []