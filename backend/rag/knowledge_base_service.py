# rag/knowledge_base_service.py

import traceback
from typing import List, Dict, Optional
from backend.rag.architecture.rag_service import RAGService

class KnowledgeBaseService:
    def __init__(self, corpus_path: str = "backend/rag/corpus/clinical_practical_guide/"):
        self.rag_service: Optional[RAGService] = None
        try:
            self.rag_service = RAGService(corpus_path)
            self.rag_service.load_documents()
            print("✅ Knowledge Base service initialized successfully")
        except Exception as e:
            print(f"⚠️ Failed to initialize Knowledge Base service: {e}\n{traceback.format_exc()}")
            self.rag_service = None

    def get_clinical_guidelines_context(self, query_text: str, top_k: int = 3) -> str:
        """
        Retrieves relevant clinical guidelines context for the given query
        
        Args:
            query_text: The query to search against the knowledge base
            top_k: Number of most relevant documents to return
            
        Returns:
            Formatted context string with relevant guidelines, or empty string if none found
        """
        if not self.rag_service or not query_text:
            return ""

        try:
            relevant_docs = self.rag_service.retrieve_relevant_documents(query_text, top_k)
            
            if not relevant_docs:
                return ""
                
            context = "\n\nRelevant Clinical Guidelines:\n---\n"
            context += "\n".join([
                f"- {doc['text']} (Source: {doc['source']}, Score: {doc['similarity_score']:.2f})"
                for doc in relevant_docs
            ])
            context += "\n\n"
            return context
        except Exception as e:
            print(f"⚠️ Error retrieving clinical guidelines: {e}\n{traceback.format_exc()}")
            return ""