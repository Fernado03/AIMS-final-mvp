import json
import os
import logging
from typing import List, Dict, Optional
import numpy as np
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer, CrossEncoder
import google.generativeai as genai
from backend.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME

# Matryoshka embedding truncation dimension for nomic-ai/nomic-embed-text-v2-moe
TRUNCATE_DIMENSION = 256

# Logging configuration should be done at application level

class RAGService:
    def __init__(self, corpus_path: str):
        """Initialize RAG service with directory containing embedded documents and separate models for embedding and generation."""
        self.corpus_dir = corpus_path
        self.documents: List[Dict] = []
        self.embeddings: List[np.ndarray] = []
        self.embedding_model = None
        self.generative_model = None
        self.reranker = None
        
        # Initialize Google Generative AI
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.generative_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            logging.info(f"Successfully initialized generative model: {GEMINI_MODEL_NAME}")
        except Exception as e:
            logging.error(f"Failed to initialize generative model: {e}")
            raise RuntimeError(f"Failed to initialize generative model: {e}")

        try:
            self.embedding_model = SentenceTransformer('basilisk78/nomic-v2-tuned-1', trust_remote_code=True)
            logging.info("Successfully initialized tuned Nomic embedding model: basilisk78/nomic-v2-tuned-1")
        except Exception as e:
            logging.error(f"Failed to initialize Nomic AI embedding model: {e}")
            raise RuntimeError(f"Failed to initialize embedding model: {e}")
            
        try:
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
            logging.info("Successfully initialized CrossEncoder re-ranker: cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            logging.error(f"Failed to initialize CrossEncoder re-ranker: {e}")
            raise RuntimeError(f"Failed to initialize re-ranker: {e}")
            
        self.load_documents()
        
    def load_documents(self) -> None:
        """Load all embedded documents from the corpus directory."""
        self.documents = []
        self.embeddings = []
        
        if not os.path.exists(self.corpus_dir):
            logging.warning(f"Corpus directory not found: {self.corpus_dir}. Starting with empty knowledge base.")
            return

        try:
            for filename in os.listdir(self.corpus_dir):
                if filename.endswith('.jsonl'):
                    with open(os.path.join(self.corpus_dir, filename), 'r', encoding='utf-8') as f:
                        for line in f:
                            doc = json.loads(line)
                            self.documents.append({
                                'text': doc.get('text', ''),
                                'metadata': doc.get('metadata', {}),
                                'source': filename
                            })
                            self.embeddings.append(np.array(doc.get('embedding', [])))
            logging.info(f"Successfully loaded {len(self.documents)} documents from {self.corpus_dir}")
        except Exception as e:
            logging.error(f"Failed to load documents from {self.corpus_dir}: {e}")
            # Don't raise, just log error and continue with what we have or empty
            # raise RuntimeError(f"Failed to load documents: {str(e)}")

    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        return np.dot(a, b) / (norm(a) * norm(b))

    def retrieve_relevant_documents(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve most relevant documents for a given query text by first embedding the query.
        
        Args:
            query_text: The text of the query
            top_k: Number of documents to return
            
        Returns:
            List of relevant documents with their similarity scores
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized.")

        try:
            query_embedding = self.embedding_model.encode([query_text], prompt_name="query")[0]  # Returns list of embeddings, take first
            query_embedding = np.array(query_embedding).flatten()  # Convert to numpy array and flatten
            query_embedding = query_embedding[:TRUNCATE_DIMENSION]  # Truncate to Matryoshka dimension
            logging.info(f"DEBUG: Query embedding shape: {query_embedding.shape}, dimension: {len(query_embedding)} (truncated to {TRUNCATE_DIMENSION}D)")
        except Exception as e:
            logging.error(f"Failed to generate embedding for query '{query_text}': {e}")
            raise RuntimeError(f"Failed to generate query embedding: {e}")

        if not self.documents or not self.embeddings:
            logging.warning("No documents loaded in knowledge base.")
            return []
            
        if len(self.embeddings) > 0 and len(self.embeddings[0]) > TRUNCATE_DIMENSION:
            # Truncate document embeddings if they're larger than our target dimension
            # Ideally this should be done at load time, but doing here for safety
            # Note: This is inefficient if done every query, but load_documents should handle it if adapted
            # For now, let's assume they might be raw.
            pass # We'll just slice in the loop or assume they match. 
            # Actually, let's slice them on the fly if needed
            
        # Check potential dimension mismatch on first item
        if len(self.embeddings) > 0 and len(self.embeddings[0]) != TRUNCATE_DIMENSION and len(self.embeddings[0]) != query_embedding.shape[0]:
             # If doc embedding is bigger, we can slice it.
             if len(self.embeddings[0]) > TRUNCATE_DIMENSION:
                 # Slice all embeddings once (optimization: should be done in load, but okay here for now)
                 self.embeddings = [emb[:TRUNCATE_DIMENSION] for emb in self.embeddings]
        
        if len(self.embeddings) > 0 and query_embedding.shape[0] != len(self.embeddings[0]):
            logging.error(f"Query embedding dimension ({query_embedding.shape[0]}) does not match document embeddings dimension ({len(self.embeddings[0])})")
            raise ValueError("Query embedding dimension doesn't match document embeddings")
            
        similarities = [
            self.cosine_similarity(query_embedding, doc_embedding)
            for doc_embedding in self.embeddings
        ]
        
        # Get indices of initial_top_k most similar documents (larger pool for re-ranking)
        initial_top_k = min(top_k * 2, len(self.documents))
        if initial_top_k == 0: return []
        
        top_indices = np.argsort(similarities)[-initial_top_k:][::-1]
        
        results = []
        for idx in top_indices:
            try:
                # Convert index to integer and validate
                doc_idx = int(idx.item() if hasattr(idx, 'item') else idx)
                if not (0 <= doc_idx < len(self.documents)) or doc_idx >= len(self.embeddings):
                    logging.warning(f"Invalid document index: {doc_idx}")
                    continue
                    
                results.append({
                    **self.documents[doc_idx],
                    'similarity_score': float(similarities[doc_idx])
                })
            except (ValueError, TypeError, AttributeError) as e:
                logging.error(f"Error processing index {idx}: {e}")
                continue
                
        # Apply re-ranking if reranker is available
        if self.reranker and len(results) > 0:
            try:
                # Create (query, document) pairs for re-ranking
                pairs = [(query_text, res['text']) for res in results]
                
                # Get re-ranking scores
                rerank_scores = self.reranker.predict(pairs)
                
                # Combine with original scores (weighted average)
                # Need to match the indices correctly. results[i] corresponds to rerank_scores[i]
                for i in range(len(results)):
                   results[i]['combined_score'] = 0.7 * rerank_scores[i] + 0.3 * results[i]['similarity_score']

                # Sort by combined score
                results.sort(key=lambda x: x['combined_score'], reverse=True)
                
                # Trim to top_k
                results = results[:top_k]
                
            except Exception as e:
                logging.error(f"Re-ranking failed, falling back to original results: {e}")
                results = results[:top_k]
        else:
             results = results[:top_k]
                
        return results

    def get_document_by_text(self, text: str) -> Optional[Dict]:
        """
        Get a document by its exact text content.
        
        Args:
            text: Exact text content to search for
            
        Returns:
            The matching document or None if not found
        """
        for doc in self.documents:
            if doc['text'] == text:
                return doc
        return None