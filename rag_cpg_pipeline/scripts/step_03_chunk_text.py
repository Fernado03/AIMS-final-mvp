# scripts/step_03_chunk_text.py
import os
import json
import re
import sys
import uuid # For generating unique chunk IDs
import spacy

# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore

# --- Chunking Configuration ---
# Simple paragraph splitting first. We can make this more complex.
# For paragraph splitting, we assume paragraphs are separated by at least two newlines.
PARAGRAPH_SPLIT_PATTERN = re.compile(r"\n\s*\n+") # Matches 2 or more newlines, with optional whitespace in between

# Token-based chunking configuration
CHUNK_SIZE = 500  # Target number of tokens per chunk
CHUNK_OVERLAP = 100  # Number of overlapping tokens between chunks (20% of CHUNK_SIZE)
MIN_CHAR = 50  # Minimum character length for a chunk

def create_chunks_from_text(cleaned_text, source_filename, source_title_approx, nlp=None):
    """
    Creates chunks from cleaned text using token-based splitting.
    Starts with paragraph splitting, then splits long paragraphs by sentences with token counting.
    """
    def count_tokens(text):
        """Simple token counter that splits on whitespace"""
        return len(text.split())
    
    chunks = []
    
    # Initial split by paragraphs (or what look like paragraphs)
    paragraphs = PARAGRAPH_SPLIT_PATTERN.split(cleaned_text)
    
    chunk_order = 0
    for para_text in paragraphs:
        para_text_stripped = para_text.strip()
        if not para_text_stripped or len(para_text_stripped) < MIN_CHAR: # Skip very short/empty paragraphs
            continue

        # If paragraph is within token limit, treat it as a chunk
        if count_tokens(para_text_stripped) <= CHUNK_SIZE:
            chunk_id = str(uuid.uuid4())
            chunks.append({
                "chunk_id": chunk_id,
                "source_document_filename": source_filename,
                "source_document_title": source_title_approx, # Title derived in Step 2 or from filename
                "text": para_text_stripped,
                "chunk_order": chunk_order, # Relative order within the document
                # Add other metadata if available, e.g., page numbers if you can track them to here
            })
            chunk_order += 1
        else:
            # Paragraph is too long, split it by sentences with token counting
            para_token_count = count_tokens(para_text_stripped)
            print(f"  INFO: Paragraph in '{source_filename}' too long ({para_token_count} tokens). Splitting by sentences.")
            if nlp:
                sentences = [sent.text for sent in nlp(para_text_stripped).sents]
            else:
                sentences = re.split(r'(?<=[.!?])\s+', para_text_stripped) # Fallback to basic sentence split
            
            current_sub_chunk = ""
            current_token_count = 0
            overlap_buffer = []  # Stores sentences for overlap between chunks
            
            for sentence in sentences:
                sentence_stripped = sentence.strip()
                if not sentence_stripped:
                    continue
                
                sentence_tokens = count_tokens(sentence_stripped)
                
                if current_token_count + sentence_tokens <= CHUNK_SIZE:
                    current_sub_chunk += (" " + sentence_stripped if current_sub_chunk else sentence_stripped)
                    current_token_count += sentence_tokens
                    overlap_buffer.append(sentence_stripped)
                    
                    # Keep overlap buffer to CHUNK_OVERLAP tokens
                    while sum(count_tokens(s) for s in overlap_buffer) > CHUNK_OVERLAP:
                        overlap_buffer.pop(0)
                else:
                    # Current sub_chunk is full or next sentence makes it too full
                    if len(current_sub_chunk) > MIN_CHAR: # Only add if substantial
                        chunk_id = str(uuid.uuid4())
                        chunks.append({
                            "chunk_id": chunk_id,
                            "source_document_filename": source_filename,
                            "source_document_title": source_title_approx,
                            "text": current_sub_chunk,
                            "chunk_order": chunk_order,
                        })
                        chunk_order += 1
                    
                    # Start new sub_chunk with overlap content + current sentence
                    current_sub_chunk = " ".join(overlap_buffer + [sentence_stripped])
                    current_token_count = count_tokens(current_sub_chunk)
                    overlap_buffer = [sentence_stripped]
                    
                    # Keep overlap buffer to CHUNK_OVERLAP tokens
                    while sum(count_tokens(s) for s in overlap_buffer) > CHUNK_OVERLAP:
                        overlap_buffer.pop(0)
            
            # Add the last remaining sub_chunk
            if current_sub_chunk and len(current_sub_chunk) > MIN_CHAR:
                chunk_id = str(uuid.uuid4())
                chunks.append({
                    "chunk_id": chunk_id,
                    "source_document_filename": source_filename,
                    "source_document_title": source_title_approx,
                    "text": current_sub_chunk,
                    "chunk_order": chunk_order,
                })
                chunk_order += 1
                
    if not chunks:
        print(f"  WARNING: No chunks generated for {source_filename}. Cleaned text might have been empty or too fragmented.")
    return chunks


def main():
    print("Starting Step 3: Text Chunking...")
    
    # Load spaCy model with fallback to download if not found
    nlp = None
    try:
        try:
            nlp = spacy.load("en_core_web_md")
            print("Loaded spaCy model 'en_core_web_md'")
        except OSError:
            print("spaCy model 'en_core_web_md' not found. Attempting download...")
            try:
                import spacy.cli
                spacy.cli.download("en_core_web_md")
                nlp = spacy.load("en_core_web_md")
                print("Successfully downloaded and loaded spaCy model 'en_core_web_md'")
            except Exception as download_error:
                print(f"Failed to download spaCy model: {download_error}")
                print("  You can manually install it by running:")
                print("  python -m spacy download en_core_web_md")
                print("Falling back to basic sentence splitting")
    except Exception as e:
        print(f"Unexpected error loading spaCy: {e}")
        print("Falling back to basic sentence splitting")

    try:
        cleaned_text_files = [f for f in os.listdir(config.CLEANED_TEXT_DIR) if f.endswith("_cleaned_ultra_minimal.txt")]
    except FileNotFoundError:
        print(f"Error: Cleaned text directory not found at {config.CLEANED_TEXT_DIR}")
        return

    if not cleaned_text_files:
        print(f"No cleaned text files found in {config.CLEANED_TEXT_DIR} to chunk.")
        return

    print(f"Found {len(cleaned_text_files)} cleaned text file(s) to process.")
    
    all_cpg_chunks = [] # To store chunks from all CPGs if saving to one file

    for cleaned_filename in cleaned_text_files:
        cleaned_filepath = os.path.join(config.CLEANED_TEXT_DIR, cleaned_filename)
        cpg_original_pdf_filename = cleaned_filename.replace("_cleaned.txt", ".pdf") # Derive original PDF name
        
        # Derive an approximate title (similar to how it might be done in step_02)
        # This is for metadata; ideally, title comes from PDF metadata if step_01 captured it.
        source_title_approx = os.path.splitext(cpg_original_pdf_filename)[0].replace("_", " ").replace("-", " ")
        source_title_approx = re.sub(r'\s+', ' ', source_title_approx).strip()
        # Remove common suffixes if title is from filename
        source_title_approx = re.sub(r'\s*preview\s*$', '', source_title_approx, flags=re.IGNORECASE)
        source_title_approx = re.sub(r'\s*\(?(?:[1-9](?:st|nd|rd|th)?\s*ed(?:ition)?|v\d\.\d)\)?\s*$', '', source_title_approx, flags=re.IGNORECASE).strip()


        print(f"\nProcessing cleaned file: {cleaned_filename} (for PDF: {cpg_original_pdf_filename})")
        try:
            with open(cleaned_filepath, "r", encoding="utf-8") as f:
                cleaned_cpg_text = f.read()
        except Exception as e:
            print(f"Error reading cleaned text file {cleaned_filepath}: {e}")
            continue

        if not cleaned_cpg_text.strip():
            print(f"  Skipping {cleaned_filename} as it contains no text after cleaning.")
            continue
            
        cpg_chunks = create_chunks_from_text(cleaned_cpg_text, cpg_original_pdf_filename, source_title_approx, nlp)
        
        if cpg_chunks:
            print(f"  Generated {len(cpg_chunks)} chunks for {cpg_original_pdf_filename}.")
            
            # Option 1: Save chunks per CPG
            output_filename_base = os.path.splitext(cpg_original_pdf_filename)[0]
            output_jsonl_filename = output_filename_base + "_chunks.jsonl"
            output_path = os.path.join(config.CHUNKS_DIR, output_jsonl_filename)
            try:
                with open(output_path, "w", encoding="utf-8") as f_out:
                    for chunk_item in cpg_chunks:
                        f_out.write(json.dumps(chunk_item) + "\n")
                print(f"  Chunks for '{cpg_original_pdf_filename}' saved to: {output_path}")
            except Exception as e:
                print(f"  Error saving chunks for '{cpg_original_pdf_filename}': {e}")

            # Option 2: Add to a list for a single combined output file (uncomment if desired)
            # all_cpg_chunks.extend(cpg_chunks)
        else:
            print(f"  No chunks were generated for {cpg_original_pdf_filename}.")

    # If using Option 2 for a single combined file:
    # if all_cpg_chunks:
    #     combined_output_path = os.path.join(config.CHUNKS_DIR, "all_cpgs_chunks.jsonl")
    #     try:
    #         with open(combined_output_path, "w", encoding="utf-8") as f_combined:
    #             for chunk_item in all_cpg_chunks:
    #                 f_combined.write(json.dumps(chunk_item) + "\n")
    #         print(f"\nAll CPG chunks saved to: {combined_output_path}")
    #     except Exception as e:
    #         print(f"Error saving combined chunks file: {e}")

    print("\nStep 3: Text Chunking finished for all processed CPGs.\n")

if __name__ == "__main__":
    main()