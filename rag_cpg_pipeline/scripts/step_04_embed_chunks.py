import os
import json
import sys
import time
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer

# Add parent directory to Python path (optional, adjust as needed)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration imports
try:
    from config import (
        CHUNKS_DIR,
        EMBEDDED_CHUNKS_DIR,
        EMBEDDING_MODEL_NAME
    )
except ImportError as e:
    raise ImportError("Failed to import configuration. Ensure config.py defines all required variables.") from e

# Global embedding model
local_embedding_model: SentenceTransformer = None


def initialize_local_embedding_model() -> None:
    """Initialize the SentenceTransformer embedding model if not already loaded."""
    global local_embedding_model
    if local_embedding_model is None:
        print(f"Initializing SentenceTransformer model: {EMBEDDING_MODEL_NAME}")
        try:
            local_embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, trust_remote_code=True)
        except Exception as err:
            print(f"Error initializing SentenceTransformer model '{EMBEDDING_MODEL_NAME}': {err}")
            raise
        print(f"SentenceTransformer model '{EMBEDDING_MODEL_NAME}' initialized successfully.")


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Return a list of embeddings for the given texts."""
    if local_embedding_model is None:
        initialize_local_embedding_model()
    
    BATCH_SIZE = 5
    embeddings = []
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        try:
            batch_embeddings = local_embedding_model.encode(batch_texts, prompt_name="passage", show_progress_bar=False)
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Error generating embeddings for batch {i}-{i+BATCH_SIZE}: {e}")
            raise
    
    return embeddings


def process_file(input_path: str, output_path: str, batch_size: int = 50) -> None:
    """Read chunks from input JSONL, compute embeddings, and write to output JSONL."""
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:

        buffer_texts: List[str] = []
        buffer_chunks: List[Dict] = []

        for lineno, line in enumerate(infile, start=1):
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError as decode_err:
                print(f"[Line {lineno}] Skipping malformed JSON: {decode_err}")
                continue

            text = chunk.get('text')
            if not isinstance(text, str):
                print(f"[Line {lineno}] Missing or invalid 'text' field, skipping.")
                continue

            buffer_texts.append(text)
            buffer_chunks.append(chunk)

            if len(buffer_texts) >= batch_size:
                _write_batch(buffer_texts, buffer_chunks, outfile)
                buffer_texts.clear()
                buffer_chunks.clear()

        # process any remaining items
        if buffer_texts:
            _write_batch(buffer_texts, buffer_chunks, outfile)


def _write_batch(texts: List[str], chunks: List[Dict], outfile) -> None:
    """Compute embeddings for a batch and write enriched chunks to outfile."""
    try:
        embeddings = get_embeddings(texts)
        for chunk, emb in zip(chunks, embeddings):
            chunk['embedding'] = emb.tolist() if isinstance(emb, np.ndarray) else emb
            json_line = json.dumps(chunk, ensure_ascii=False, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else None)
            outfile.write(json_line + '\n')
    except Exception as e:
        print(f"Error processing batch: {e}")


def main() -> None:
    initialize_local_embedding_model()

    if not os.path.isdir(CHUNKS_DIR):
        print(f"Chunks directory not found: {CHUNKS_DIR}")
        sys.exit(1)

    os.makedirs(EMBEDDED_CHUNKS_DIR, exist_ok=True)

    processed = 0
    for fname in os.listdir(CHUNKS_DIR):
        if fname.endswith('_chunks.jsonl'):
            src = os.path.join(CHUNKS_DIR, fname)
            base = fname.rsplit('_chunks.jsonl', 1)[0]
            dest = os.path.join(EMBEDDED_CHUNKS_DIR, f"{base}_embedded.jsonl")
            print(f"Processing {src} -> {dest}")
            process_file(src, dest)
            processed += 1

    print(f"Completed embedding for {processed} file(s).")


if __name__ == '__main__':
    main()
