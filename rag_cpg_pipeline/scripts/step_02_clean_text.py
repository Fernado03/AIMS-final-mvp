# scripts/step_02_clean_text_ultra_minimal.py
import os
import json
import re
import sys
import spacy
from typing import List, Dict, Tuple, Optional, Any

# Add the base directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config # type: ignore

# --- CONTROL FLAG ---
ULTRA_MINIMAL_MODE = True # SET THIS TO True FOR THE LEAST AGGRESSIVE CLEANING

# --- Constants and Pre-compiled Regex ---
URL_PLACEHOLDER = " [URL_REMOVED] "
CONTACT_PLACEHOLDER = " [CONTACT_REMOVED] "
ISBN_PLACEHOLDER = " [ISBN_REMOVED] "
TITLE_PAGE_PLACEHOLDER = " [TITLE_PAGE_CONTENT_REMOVED] "
SECTION_REMOVED_PLACEHOLDER_FORMAT = " [SECTION_REMOVED: {section_name}] "
NER_PLACEHOLDER_FORMAT = " [{entity_label}_REMOVED] "

URL_PATTERN = re.compile(r"https?://[^\s/$.?#].[^\s]*|www\.[^\s/$.?#].[^\s]*", re.IGNORECASE)
ISBN_LINE_PATTERN = re.compile(r"^\s*(e[-]?ISBN(?:-1[03])?[:\s\-\dXx]+)\s*$", re.IGNORECASE | re.MULTILINE)
PHONE_PATTERN_GENERAL = re.compile(r"(?:\+?\d{1,3}?[-.\s]?)?\(?\d{2,4}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,5}")
MALAYSIAN_PHONE_PATTERN = re.compile(r"(?:\(\+?60\)|0)[1-9]\d{0,2}[-.\s]?\d{7,8}")
IN_TEXT_CITATION_PATTERN = re.compile(
    r"(?P<author_citation>\([A-Za-z\s.&,]+et al\.,?\s+(?P<year>\d{4}[a-z]?)\))|"
    r"(?P<numeric_citation>\[(?P<numbers>\d{1,3}(?:,\s*\d{1,3})*)\])"
)
TITLES_PATTERN = re.compile(
    r"\b(?:Dr|Dato'|Datin|Datuk|Tan Sri|Puan Sri|Professor|Prof|Associate Professor|Assoc\. Prof|Encik|Puan|Cik|Mr|Ms|Mrs)\.?\s*",
    re.IGNORECASE
)
PAGE_NUM_ALONE_PATTERN = re.compile(r"^\s*([ivxlcdm]+|[0-9]+)\s*$", re.IGNORECASE | re.MULTILINE)
PAGE_NUM_VERBOSE_PATTERN = re.compile(r"^\s*Page\s*[0-9ivxlcdm]+(?:\s*of\s*[0-9ivxlcdm]+)?\s*$", re.IGNORECASE | re.MULTILINE)
YEAR_ALONE_PATTERN = re.compile(r"^\s*\d{4}\s*$")

# --- SpaCy Model ---
NLP_MODEL: Optional[spacy.Language] = None
if not ULTRA_MINIMAL_MODE: # Load NLP model only if not in ultra-minimal (or if some NER rules were kept)
    try:
        NLP_MODEL = spacy.load("en_core_web_sm")
        print("spaCy NER model 'en_core_web_sm' loaded successfully.")
    except OSError:
        print("spaCy model 'en_core_web_sm' not found. NER features will be disabled if any section rule requires them.")
else:
    print("ULTRA_MINIMAL_MODE: spaCy NLP Model loading skipped.")


# --- Document & Section Configurations ---
CPG_SPECIFIC_CONFIGS: Dict[str, Dict[str, Any]] = {
    "prevention of cardiovascular disease in women": {
        "running_header": "", "year_header": "2016",
        "main_title_heuristic": "Prevention of Cardiovascular Disease in Women",
        "special_page_handling": {1: {"replacement_text": TITLE_PAGE_PLACEHOLDER}}
    },
    "dengue infection in adults": {
        "running_header": "CPG Management of Dengue Infection In Adults (Third Edition)",
        "year_header": "2015", "main_title_heuristic": "CPG Management of Dengue Infection In Adults"
    },
    "early management of head injury in adults": {
        "running_header": "Early Management of Head Injury in Adults", "year_header": "",
        "main_title_heuristic": "Early Management of Head Injury in Adults",
        "special_page_handling": {
            1: {"if_extraction_method": "ocr", "replacement_text": TITLE_PAGE_PLACEHOLDER}
        }
    },
    "childhood immunisation": {
        "running_header": "", "year_header": "", # OCR quality is low, rely on very conservative H/F
        "main_title_heuristic": "Childhood Immunisation",
    }
}

# Section processing rules
if ULTRA_MINIMAL_MODE:
    SECTION_PROCESSING_RULES: List[Tuple[str, str, str, Optional[List[str]]]] = []
    print("ULTRA_MINIMAL_MODE: Section processing rules are disabled.")
else:
    SECTION_PROCESSING_RULES = [
        ("REFERENCES_BIBLIOGRAPHY", r"^\s*(?:REFERENCES|BIBLIOGRAPHY)\s*$", "REMOVE", None),
        ("TABLE_OF_CONTENTS", r"^\s*TABLE\s+OF\s+CONTENTS\s*\.?\s*$", "REMOVE", None),
    ]


# --- Helper Functions ---
def get_cpg_document_config(cpg_filename: str, raw_metadata: dict, is_ocr_heavy: bool) -> Dict[str, Any]:
    filename_lower = cpg_filename.lower()
    for pattern_key, cfg in CPG_SPECIFIC_CONFIGS.items():
        if pattern_key in filename_lower:
            print(f"  INFO: Using specific H/F config for '{cpg_filename}'.")
            return cfg

    print(f"  INFO: Using generic H/F config for '{cpg_filename}'.")
    generic_cfg: Dict[str, Any] = {"running_header": "", "year_header": "", "main_title_heuristic": ""}
    
    if ULTRA_MINIMAL_MODE and is_ocr_heavy:
        # For OCR-heavy documents in ultra-minimal mode, don't derive H/F targets from potentially mangled metadata/filename
        print("    ULTRA_MINIMAL_MODE (OCR): Using blank H/F targets for generic config.")
        generic_cfg["main_title_heuristic"] = os.path.splitext(cpg_filename)[0] # Basic title for reference
        return generic_cfg

    metadata_title = raw_metadata.get("title", "").strip()
    if metadata_title:
        generic_cfg["running_header"] = metadata_title
        year_match = re.search(r"(\b\d{4}\b)", metadata_title)
        if year_match: generic_cfg["year_header"] = year_match.group(1)
        title_main_part_match = re.match(
            r"^(.*?)(?:\s*\(.*\)|\[.*\]|\s*-\s*.*|$)",
            metadata_title, re.IGNORECASE)
        main_part = title_main_part_match.group(1).strip() if title_main_part_match and title_main_part_match.group(1) else metadata_title
        generic_cfg["main_title_heuristic"] = main_part if len(main_part.split()) < 10 else ' '.join(main_part.split()[:7])
    else:
        base_name = os.path.splitext(cpg_filename)[0].replace("_", " ").replace("-", " ")
        temp_header = re.sub(r'\s+', ' ', base_name).strip()
        temp_header = re.sub(r'\s*(cpg|guidelines?|preview|final|draft)\s*$', '', temp_header, flags=re.IGNORECASE).strip()
        temp_header = re.sub(r'\s*\(?(?:\d+(?:st|nd|rd|th)?\s*ed(?:ition)?|v\d\.\d|second|third|fourth|fifth)\)?\s*$', '', temp_header, flags=re.IGNORECASE).strip()
        generic_cfg["running_header"] = temp_header
        generic_cfg["main_title_heuristic"] = generic_cfg["running_header"]
        year_match_fn = re.search(r"(\b\d{4}\b)", cpg_filename)
        if year_match_fn: generic_cfg["year_header"] = year_match_fn.group(1)
    
    if not generic_cfg["main_title_heuristic"] and generic_cfg["running_header"]:
        generic_cfg["main_title_heuristic"] = ' '.join(generic_cfg["running_header"].split()[:5])
    elif not generic_cfg["main_title_heuristic"]:
        generic_cfg["main_title_heuristic"] = "Guideline Document"
    return generic_cfg

def clean_page_text_initial(page_data: dict, doc_cfg: dict, cpg_filename: str) -> str:
    page_text = page_data.get("text", "")
    page_num = page_data.get("page_number", 0)
    extraction_method = page_data.get("extraction_method", "direct")

    special_handling = doc_cfg.get("special_page_handling", {}).get(page_num)
    if special_handling: # Apply pre-defined replacements for problematic pages
        if "if_extraction_method" in special_handling:
            if extraction_method == special_handling["if_extraction_method"]:
                print(f"    INFO: Applied special handling (conditional) to page {page_num} of '{cpg_filename}'.")
                return special_handling["replacement_text"]
        elif "replacement_text" in special_handling:
            print(f"    INFO: Applied special handling (direct) to page {page_num} of '{cpg_filename}'.")
            return special_handling["replacement_text"]

    lines = page_text.split('\n')
    if not lines: return ""
    
    body_lines = []
    
    running_header_pattern = None
    if doc_cfg.get("running_header"):
        running_header_pattern = re.compile(r"^\s*" + re.escape(doc_cfg["running_header"]) + r"\s*$", re.IGNORECASE)
    year_pattern = None
    if doc_cfg.get("year_header"):
        year_pattern = re.compile(r"^\s*" + re.escape(doc_cfg["year_header"]) + r"\s*$", re.IGNORECASE)

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if not stripped_line: continue

        is_hf = False
        if ULTRA_MINIMAL_MODE:
            # Only remove exact configured headers/years or page numbers on first/last lines
            if running_header_pattern and running_header_pattern.fullmatch(stripped_line): is_hf = True
            elif year_pattern and year_pattern.fullmatch(stripped_line): is_hf = True
            elif (PAGE_NUM_ALONE_PATTERN.fullmatch(stripped_line) or PAGE_NUM_VERBOSE_PATTERN.fullmatch(stripped_line)):
                if i == 0 or i == (len(lines) - 1): # Only very first or very last line
                    is_hf = True
        else: # Original "minimal" H/F logic (more rules)
            header_depth, footer_depth = 2, 2
            if running_header_pattern and running_header_pattern.fullmatch(stripped_line): is_hf = True
            elif year_pattern and year_pattern.fullmatch(stripped_line): is_hf = True
            elif PAGE_NUM_ALONE_PATTERN.fullmatch(stripped_line) or PAGE_NUM_VERBOSE_PATTERN.fullmatch(stripped_line):
                if i < header_depth or i >= (len(lines) - footer_depth): is_hf = True
            else:
                page_num_prefix_pattern = re.compile(r"^\s*(?:page)?\s*([ivxlcdm]+|[0-9]+)\s*(?:of\s*(?:[ivxlcdm]+|[0-9]+))?\s+(?=\S)", re.IGNORECASE)
                match_prefix = page_num_prefix_pattern.match(stripped_line)
                if match_prefix:
                    remaining = stripped_line[match_prefix.end():].strip()
                    if not remaining: is_hf = True
                    elif running_header_pattern and running_header_pattern.fullmatch(remaining): is_hf = True
                    elif year_pattern and year_pattern.fullmatch(remaining): is_hf = True
                elif (i < 1 or i >= (len(lines) - 1)):
                     if 0 < len(stripped_line) < 5 and not re.search(r'[a-zA-Z]', stripped_line): is_hf = True
        
        if not is_hf:
            body_lines.append(line)
            
    return "\n".join(body_lines)

def assemble_document_text(cleaned_pages: List[str]) -> str:
    full_text = "\n".join(cleaned_pages)
    full_text = "\n".join(line for line in full_text.splitlines() if not re.fullmatch(r"^\s*\[(?:TITLE_PAGE_CONTENT_REMOVED)\]\s*$", line))
    return "\n".join(filter(str.strip, full_text.splitlines()))

def perform_global_text_fixes(text: str) -> str:
    text = re.sub(r"(\w(?:['’]\w)?\w*)-\n(\w(?:['’]\w)?\w*)", r"\1\2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def _apply_ner_cleaning(text_segment: str, nlp: Optional[spacy.Language], labels: Optional[List[str]]) -> str:
    # This function is kept for completeness but won't be called often in ultra-minimal mode
    if not nlp or not text_segment.strip() or not labels or ULTRA_MINIMAL_MODE:
        return text_segment
    
    text_segment = TITLES_PATTERN.sub("", text_segment)
    doc = nlp(text_segment)
    new_parts = []
    current_pos = 0
    for ent in doc.ents:
        if ent.label_ in labels:
            new_parts.append(text_segment[current_pos:ent.start_char])
            new_parts.append(NER_PLACEHOLDER_FORMAT.format(entity_label=ent.label_.upper()))
            current_pos = ent.end_char
    new_parts.append(text_segment[current_pos:])
    return "".join(new_parts)

def segment_and_process_document(full_text: str, nlp: Optional[spacy.Language]) -> str:
    if not SECTION_PROCESSING_RULES: # This will be true in ULTRA_MINIMAL_MODE
        print("  INFO: ULTRA_MINIMAL_MODE - Skipping section segmentation.")
        return full_text # Return text as is, no section processing

    # ... (The existing segmentation logic from the previous "minimal" script would go here)
    # ... (But since SECTION_PROCESSING_RULES is empty, it will effectively do nothing)
    # For safety and clarity in ultra-minimal, we explicitly return above.
    # If SECTION_PROCESSING_RULES were populated (i.e., not ULTRA_MINIMAL_MODE),
    # the previous segmentation logic would run.
    processed_segments = []
    current_offset = 0
    heading_patterns_with_ids = []
    for rule_id, pattern_str, _, _ in SECTION_PROCESSING_RULES:
        safe_rule_id = re.sub(r'\W+', '_', rule_id).upper()
        heading_patterns_with_ids.append(f"(?P<{safe_rule_id}>{pattern_str})")
    
    if not heading_patterns_with_ids: return full_text

    master_heading_regex = re.compile("|".join(heading_patterns_with_ids), re.IGNORECASE | re.MULTILINE)
    last_match_end = 0
    for match in master_heading_regex.finditer(full_text):
        general_text_before_heading = full_text[last_match_end:match.start()]
        if general_text_before_heading.strip():
            processed_segments.append(general_text_before_heading)

        matched_rule_id_key = match.lastgroup
        matched_heading_text = match.group(matched_rule_id_key)
        action, ner_labels_for_section, original_rule_id = "PRESERVE", None, ""
        for r_id, _, r_action, r_ner_labels in SECTION_PROCESSING_RULES:
            if re.sub(r'\W+', '_', r_id).upper() == matched_rule_id_key:
                action, ner_labels_for_section, original_rule_id = r_action, r_ner_labels, r_id
                break
        
        content_start_offset = match.end()
        next_match_for_content_end = master_heading_regex.search(full_text, pos=content_start_offset)
        content_end_offset = next_match_for_content_end.start() if next_match_for_content_end else len(full_text)
        section_content = full_text[content_start_offset:content_end_offset]

        if action == "REMOVE":
            processed_segments.append(SECTION_REMOVED_PLACEHOLDER_FORMAT.format(section_name=original_rule_id.upper()))
        elif action == "NER_CLEAN" and ner_labels_for_section and NLP_MODEL:
            processed_segments.append(matched_heading_text)
            cleaned_content = _apply_ner_cleaning(section_content, nlp, ner_labels_for_section)
            processed_segments.append(cleaned_content)
        else: 
            processed_segments.append(matched_heading_text)
            processed_segments.append(section_content)
        last_match_end = content_end_offset
    
    remaining_general_text = full_text[last_match_end:]
    if remaining_general_text.strip():
        processed_segments.append(remaining_general_text)
    return "".join(processed_segments)


def apply_line_level_final_cleaning(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        if re.fullmatch(r"^\s*\[SECTION_REMOVED: [^\]]+\]\s*$", line.strip()) or \
           re.fullmatch(r"^\s*\[TITLE_PAGE_CONTENT_REMOVED\]\s*$", line.strip()):
            if line.strip(): cleaned_lines.append(line.strip())
            continue

        if not ULTRA_MINIMAL_MODE: # Only apply these removals if not in ultra-minimal
            line = URL_PATTERN.sub(URL_PLACEHOLDER, line)
            if ISBN_LINE_PATTERN.fullmatch(line.strip()):
                line = ISBN_PLACEHOLDER
            else:
                line = PHONE_PATTERN_GENERAL.sub(CONTACT_PLACEHOLDER, line)
                line = MALAYSIAN_PHONE_PATTERN.sub(CONTACT_PLACEHOLDER, line)
        
        # Citation normalization is generally safe and useful
        line = IN_TEXT_CITATION_PATTERN.sub(
            lambda m: (f" (Citation {m.group('year')}) " if m.group('author_citation')
                       else f" [{m.group('numbers')}] " if m.group('numeric_citation')
                       else m.group(0)), line )
        
        if line.strip():
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def final_whitespace_normalization(text: str) -> str:
    # Placeholder pattern adjusted for what might actually exist
    placeholder_regex_str = r"\s*(\[(?:URL_REMOVED|CONTACT_REMOVED|ISBN_REMOVED|SECTION_REMOVED:[^\]]+|TITLE_PAGE_CONTENT_REMOVED"
    if not ULTRA_MINIMAL_MODE and NLP_MODEL: # Add NER placeholders only if they could have been generated
        placeholder_regex_str += r"|PERSON_REMOVED|GPE_REMOVED|LOC_REMOVED|ORG_REMOVED"
    placeholder_regex_str += r")\])\s*"
    
    text = re.sub(placeholder_regex_str, r" \1 ", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def clean_cpg_document(raw_cpg_data: dict, cpg_filename: str) -> str:
    print(f"Processing CPG ({'ULTRA_MINIMAL' if ULTRA_MINIMAL_MODE else 'Minimal'}): {cpg_filename}")

    # Determine if the document is likely OCR-heavy for generic config decisions
    ocr_page_count = sum(1 for page in raw_cpg_data.get("pages", []) if page.get("extraction_method") == "ocr")
    total_pages = raw_cpg_data.get("total_pages", len(raw_cpg_data.get("pages", [])))
    is_ocr_heavy = total_pages > 0 and (ocr_page_count / total_pages) > 0.5 # Example threshold: >50% OCR pages

    doc_cfg = get_cpg_document_config(cpg_filename, raw_cpg_data.get("metadata", {}), is_ocr_heavy)
    print(f"  Effective H/F Targets: RunningHeader='{doc_cfg.get('running_header', '')}', Year='{doc_cfg.get('year_header', '')}'")

    cleaned_pages = [
        clean_page_text_initial(page_data, doc_cfg, cpg_filename)
        for page_data in raw_cpg_data.get("pages", [])
    ]
    print(f"  Step 1: Initial page cleaning completed for {len(cleaned_pages)} pages.")

    assembled_text = assemble_document_text(cleaned_pages)
    globally_fixed_text = perform_global_text_fixes(assembled_text)
    print(f"  Step 2: Document assembled and global fixes. Length: {len(globally_fixed_text)}")
    
    segmented_text = segment_and_process_document(globally_fixed_text, NLP_MODEL)
    print(f"  Step 3: Section segmentation ({'disabled' if ULTRA_MINIMAL_MODE else 'minimal rules'}). Length: {len(segmented_text)}")

    line_cleaned_text = apply_line_level_final_cleaning(segmented_text)
    print(f"  Step 4: Line-level final cleaning. Length: {len(line_cleaned_text)}")

    final_text = final_whitespace_normalization(line_cleaned_text)
    print(f"  Step 5: Final whitespace normalization. Final length: {len(final_text)}")
    
    word_count = len(final_text.split())
    mode_str = "ULTRA_MINIMAL" if ULTRA_MINIMAL_MODE else "Minimal"
    if not final_text or word_count < 10: # Even lower threshold for ultra-minimal
        print(f"  WARNING: Final cleaned text ({mode_str}) for {cpg_filename} is very short ({word_count} words).")
    else:
        print(f"  SUCCESS: Finished {mode_str} cleaning for {cpg_filename} ({word_count} words).")
    return final_text

# --- Main Execution ---
def main():
    mode_name = "ULTRA_MINIMAL" if ULTRA_MINIMAL_MODE else "MINIMAL (but less aggressive than before)"
    print(f"Starting Step 2 (Rewritten - {mode_name}): Text Cleaning for RAG...")
    
    # ... (rest of main function for file I/O is the same as previous script) ...
    try:
        if not os.path.exists(config.RAW_TEXT_DIR):
            print(f"Error: Raw text directory not found at {config.RAW_TEXT_DIR}. Exiting.")
            return
        raw_json_files = [f for f in os.listdir(config.RAW_TEXT_DIR) if f.endswith("_raw.json")]
    except Exception as e:
        print(f"Error accessing raw text directory {config.RAW_TEXT_DIR}: {e}. Exiting.")
        return

    if not raw_json_files:
        print(f"No raw JSON files found in {config.RAW_TEXT_DIR} to clean.")
        return
    print(f"Found {len(raw_json_files)} raw JSON file(s) to process.")

    if not os.path.exists(config.CLEANED_TEXT_DIR):
        try:
            os.makedirs(config.CLEANED_TEXT_DIR)
            print(f"Created cleaned text directory: {config.CLEANED_TEXT_DIR}")
        except Exception as e:
            print(f"Error creating cleaned text directory {config.CLEANED_TEXT_DIR}: {e}. Exiting.")
            return

    for raw_filename in raw_json_files:
        raw_filepath = os.path.join(config.RAW_TEXT_DIR, raw_filename)
        print(f"\n--- Processing file: {raw_filename} ---")
        try:
            with open(raw_filepath, "r", encoding="utf-8") as f:
                raw_cpg_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"  Error parsing JSON from {raw_filepath}: {e}. Skipping.")
            continue
        except Exception as e:
            print(f"  Error reading file {raw_filepath}: {e}. Skipping.")
            continue

        cpg_original_filename = raw_cpg_data.get("filename", raw_filename.replace("_raw.json", ".pdf"))
        
        cleaned_text = clean_cpg_document(raw_cpg_data, cpg_original_filename)
        
        output_filename_base = os.path.splitext(cpg_original_filename)[0]
        output_txt_filename = output_filename_base + f"_cleaned_{'ultra_minimal' if ULTRA_MINIMAL_MODE else 'minimal'}.txt" # Dynamic suffix
        output_path = os.path.join(config.CLEANED_TEXT_DIR, output_txt_filename)
        
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)
            print(f"  Output saved to: {output_path}")
        except Exception as e:
            print(f"  Error saving cleaned text for '{cpg_original_filename}' to {output_path}: {e}")
            
    print(f"\n--- Text Cleaning (Rewritten - {mode_name}) finished for all CPGs. ---")

if __name__ == "__main__":
    main()