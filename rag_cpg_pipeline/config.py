# config.py
import os

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PDFS_DIR = os.path.join(BASE_DIR, "input_pdfs")
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, "output_data")

RAW_TEXT_DIR = os.path.join(OUTPUT_DATA_DIR, "01_raw_text")
CLEANED_TEXT_DIR = os.path.join(OUTPUT_DATA_DIR, "02_cleaned_text")
CHUNKS_DIR = os.path.join(OUTPUT_DATA_DIR, "03_chunks")
EMBEDDED_CHUNKS_DIR = os.path.join(OUTPUT_DATA_DIR, "04_chunks_with_embeddings")

# Ensure output directories exist
os.makedirs(RAW_TEXT_DIR, exist_ok=True)
os.makedirs(CLEANED_TEXT_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(EMBEDDED_CHUNKS_DIR, exist_ok=True)

# --- Embedding Model Configuration ---
# Offline PDF→JSONL pipeline default. Runtime retrieve in
# backend/rag/architecture/rag_service.py uses MiniLM
# (sentence-transformers/all-MiniLM-L6-v2), not this nomic model.
EMBEDDING_MODEL_NAME = 'basilisk78/nomic-v2-tuned-1'

# --- Vector DB Configuration ---
# Unused at runtime (in-process numpy cache, not a hosted index).
VECTOR_DB_INDEX_NAME = "medical_cpgs_index"
VECTOR_DB_INDEX_ENDPOINT_NAME = "medical_cpgs_index_endpoint"
VECTOR_DB_DIMENSIONS = 768

# Note: CPG_FILENAME or CPG_FILENAMES list is no longer needed here
# The scripts will dynamically find PDFs in INPUT_PDFS_DIR