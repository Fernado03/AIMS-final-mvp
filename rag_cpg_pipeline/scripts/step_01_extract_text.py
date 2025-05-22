# scripts/step_01_extract_text.py
import fitz  # PyMuPDF
import os
import json
import sys
import io # For handling image bytes
from PIL import Image # For OCR with pytesseract
import pytesseract # Python wrapper for Tesseract OCR

# Add the base directory to the Python path to allow finding the config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore # pylint: disable=import-error,wrong-import-position

# --- OCR Configuration ---
# If Tesseract is not in your PATH, you might need to set this:
# Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
OCR_LANGUAGE = 'eng'  # Change if your documents are primarily in another Tesseract-supported language (e.g., 'msa' for Malay)
MIN_TEXT_LENGTH_FOR_DIRECT_EXTRACTION = 50 # If direct extraction yields less than this, try OCR

def ocr_page_image(page_pixmap):
    """
    Performs OCR on a page image (pixmap from PyMuPDF) using Tesseract.
    """
    try:
        img_bytes = page_pixmap.tobytes("png") # Convert pixmap to PNG bytes
        pil_image = Image.open(io.BytesIO(img_bytes))
        ocr_text = pytesseract.image_to_string(pil_image, lang=OCR_LANGUAGE)
        return ocr_text
    except Exception as e:
        print(f"    OCR Error: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from each page of a PDF.
    Tries direct text extraction first. If text is minimal, falls back to OCR.
    Stores PDF metadata and page-level text.
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return None

    pdf_data = {
        "filename": os.path.basename(pdf_path),
        "metadata": doc.metadata, # PyMuPDF metadata
        "total_pages": doc.page_count,
        "pages": []
    }

    print(f"Extracting text from '{pdf_data['filename']}' ({pdf_data['total_pages']} pages)...")

    for page_num in range(doc.page_count):
        page_text = ""
        extraction_method = "direct"
        try:
            page = doc.load_page(page_num)
            
            # 1. Try direct text extraction
            direct_text = page.get_text("text").strip()

            if len(direct_text) >= MIN_TEXT_LENGTH_FOR_DIRECT_EXTRACTION:
                page_text = direct_text
            else:
                # 2. If direct text is too short, try OCR
                print(f"  Page {page_num + 1}: Direct text minimal ({len(direct_text)} chars). Attempting OCR...")
                # Increase resolution for OCR if needed (default is 72 DPI from get_pixmap)
                # zoom_matrix = fitz.Matrix(2, 2) # Example: 2x zoom (144 DPI)
                # pix = page.get_pixmap(matrix=zoom_matrix)
                pix = page.get_pixmap() # Get image of the page
                ocr_text_result = ocr_page_image(pix)
                if ocr_text_result:
                    page_text = ocr_text_result.strip()
                    extraction_method = "ocr"
                    print(f"    Page {page_num + 1}: OCR successful (found {len(page_text)} chars).")
                else:
                    # If OCR also fails, use the (short) direct text or empty
                    page_text = direct_text 
                    extraction_method = "direct (OCR failed or empty)"
                    if not direct_text:
                         print(f"    Page {page_num + 1}: OCR failed, and direct text was also empty.")

            pdf_data["pages"].append({
                "page_number": page_num + 1,
                "text": page_text,
                "extraction_method": extraction_method
            })

        except Exception as e:
            print(f"  Error processing page {page_num + 1} of {pdf_data['filename']}: {e}")
            pdf_data["pages"].append({
                "page_number": page_num + 1,
                "text": "", # Store empty text on error for this page
                "error": str(e),
                "extraction_method": "error"
            })
    
    doc.close()
    print(f"Finished extracting text from '{pdf_data['filename']}'.")
    return pdf_data

def main():
    print("Starting Step 1: Text Extraction (with OCR fallback)...")
    
    # (Optional: Uncomment and set this if Tesseract is not in your system PATH)
    # try:
    #     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Windows example
    #     # pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract' # Linux example
    #     # pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract' # macOS (Homebrew) example
    #     tesseract_version = pytesseract.get_tesseract_version()
    #     print(f"Tesseract version: {tesseract_version} found at {pytesseract.pytesseract.tesseract_cmd}")
    # except Exception as e:
    #     print(f"Tesseract not found or tesseract_cmd not set correctly. OCR will likely fail. Error: {e}")
    #     print("Please ensure Tesseract OCR is installed and its path is configured if necessary.")
    #     # return # Optionally exit if Tesseract is crucial and not found

    try:
        pdf_filenames = [f for f in os.listdir(config.INPUT_PDFS_DIR) if f.lower().endswith(".pdf")]
    except FileNotFoundError:
        print(f"Error: Input PDF directory not found at {config.INPUT_PDFS_DIR}")
        return
    
    if not pdf_filenames:
        print(f"No PDF files found in {config.INPUT_PDFS_DIR}")
        return

    print(f"Found {len(pdf_filenames)} PDF file(s) to process: {', '.join(pdf_filenames)}")

    for cpg_filename in pdf_filenames:
        pdf_file_path = os.path.join(config.INPUT_PDFS_DIR, cpg_filename)
        
        print(f"\nProcessing CPG: {cpg_filename}")
        extracted_data = extract_text_from_pdf(pdf_file_path)

        if extracted_data:
            output_filename_base = os.path.splitext(cpg_filename)[0]
            output_json_filename = output_filename_base + "_raw.json"
            output_path = os.path.join(config.RAW_TEXT_DIR, output_json_filename)
            
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, indent=4, ensure_ascii=False)
                print(f"Raw extracted text for '{cpg_filename}' saved to: {output_path}")
            except Exception as e:
                print(f"Error saving extracted data for '{cpg_filename}' to JSON: {e}")

    print("\nStep 1: Text Extraction finished for all processed CPGs.\n")

if __name__ == "__main__":
    main()