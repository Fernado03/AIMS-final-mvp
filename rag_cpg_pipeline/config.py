import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PDFS_DIR = os.path.join(BASE_DIR, "input_pdfs")
OUTPUT_DATA_DIR = os.path.join(BASE_DIR, "output_data")

RAW_TEXT_DIR = os.path.join(OUTPUT_DATA_DIR, "01_raw_text")
CLEANED_TEXT_DIR = os.path.join(OUTPUT_DATA_DIR, "02_cleaned_text")
CHUNKS_DIR = os.path.join(OUTPUT_DATA_DIR, "03_chunks")
EMBEDDED_CHUNKS_DIR = os.path.join(OUTPUT_DATA_DIR, "04_chunks_with_embeddings")

os.makedirs(RAW_TEXT_DIR, exist_ok=True)
os.makedirs(CLEANED_TEXT_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(EMBEDDED_CHUNKS_DIR, exist_ok=True)

# Offline PDF→JSONL default. Runtime retrieve uses MiniLM (all-MiniLM-L6-v2).
EMBEDDING_MODEL_NAME = "basilisk78/nomic-v2-tuned-1"
