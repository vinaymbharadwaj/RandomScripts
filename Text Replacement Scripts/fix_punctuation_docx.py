import docx
import re
import os
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# --- Mappings ---
PUNCT_REPLACEMENTS = [
    # 1. Curly quotes -> straight
    (r'[\u201C\u201D\u201F\u300C\u300D\u300E\u300F]', '"'), 
    (r'[\u2018\u2019\u201B]', "'"),
    # 2. Ellipsis
    (r'\u2026', '...'),
    # 3. CJK -> ASCII
    (r'，', ','), (r'。', '.'), (r'：', ':'), (r'；', ';'),
    (r'！', '!'), (r'？', '?'), (r'（', '('), (r'）', ')'),
    (r'【', '['), (r'】', ']'), (r'、', ','), 
    # 4. Dashes
    (r'——', '—'), 
    # 5. Cleanup
    (r'\u00A0', ' '), 
]

def clean_text_worker(text):
    """
    Parallel Worker: Cleans text INSIDE a single run.
    """
    if not text: return ""

    # 1. Normalize Unicode Spaces
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[\u00A0\u2000-\u200B\u3000]', ' ', text)

    # 2. Mappings
    for pattern, replacement in PUNCT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text)

    # 3. Numbers/Currency/Contractions
    text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', text)
    text = re.sub(r'(\d)\s*,\s*(\d{3})', r'\1,\2', text)
    text = re.sub(r'(\d)\s+%', r'\1%', text)
    text = re.sub(r'(\$|€|£|¥)\s+(\d)', r'\1\2', text)
    text = re.sub(r'([a-zA-Z])\s+\'', r'\1\'', text)
    text = re.sub(r'\'\s+(s|t|m|re|ll|ve|d)(?!\w)', r"'\1", text, flags=re.IGNORECASE)
    text = re.sub(r'\b(i)\b', 'I', text)

    # 4. Unstick Quotes (NEW RULE)
    # Fix 'word"Word' -> 'word "Word' (Assume opening quote if followed by Capital)
    text = re.sub(r'(?<=[a-zA-Z])"(?=[A-Z])', ' "', text)
    
    # 5. Internal Spacing Fixes
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Fix Space INSIDE Quotes
    # " Hello" -> "Hello"
    text = re.sub(r'"\s+(?=\S)', '"', text)       
    # Hello " -> Hello" (Added ? and ! to lookbehind)
    text = re.sub(r'(?<=[a-zA-Z0-9.,!?])\s+"', '"', text)  
    
    # Fix Parentheses
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)

    # 6. Punctuation Spacing
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    text = re.sub(r'([.,;:!?])(?=[a-zA-Z])', r'\1 ', text)
    text = re.sub(r'([.,;:!?])(?=")', r'\1 ', text)

    # 7. Deduplicate Punctuation
    text = re.sub(r'([,:;])\1+', r'\1', text)
    text = re.sub(r'([!?])\1+', r'\1', text)
    text = re.sub(r'\.{4,}', '...', text)

    # 8. Sentence Capitalization
    if len(text) > 0 and text[0].islower():
        text = text[0].upper() + text[1:]
    text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)

    return text

def fix_split_run_boundaries(doc):
    """
    Advanced Zipper: Fixes spacing errors that span across TWO runs.
    """
    print("Stitching broken run boundaries...")
    
    all_paras = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paras.extend(cell.paragraphs)

    count = 0
    # Define set of closing punctuation chars for cleaner lookups
    CLOSING_PUNCT = {'.', ',', '!', '?', ';', ':'}
    
    for para in tqdm(all_paras, desc="Stitching Boundaries"):
        runs = para.runs
        if len(runs) < 2:
            continue
            
        for i in range(len(runs) - 1):
            curr_run = runs[i]
            next_run = runs[i+1]
            
            if not curr_run.text or not next_run.text:
                continue

            c_txt = curr_run.text
            n_txt = next_run.text
            c_stripped = c_txt.strip()
            n_stripped = n_txt.strip()

            if not c_stripped or not n_stripped:
                continue

            # --- OPENING QUOTE SCENARIOS ---
            # Case 1: Run A ends with [" ] -> Strip Space
            if (c_stripped.endswith('"') or c_stripped.endswith('(')) and c_txt.endswith(' '):
                 curr_run.text = c_txt.rstrip()
                 count += 1

            # Case 2: Run A ends with ["] AND Run B starts with [ ] -> Strip B's space
            elif (c_txt.endswith('"') or c_txt.endswith('(')) and n_txt.startswith(' '):
                 next_run.text = n_txt.lstrip()
                 count += 1

            # --- CLOSING QUOTE SCENARIOS ---
            # Case 3: Run A ends with [ ] AND Run B starts with ["] or [?] -> Strip A's space
            # Ex: A='Wrong? ' B='"'
            elif c_txt.endswith(' ') and (n_txt.startswith('"') or n_txt.startswith(')') or n_txt[0] in CLOSING_PUNCT):
                 curr_run.text = c_txt.rstrip()
                 count += 1
                 
            # Case 4: Run B starts with [ "] or [ ?] -> Strip Space
            # Ex: A='Wrong' B=' "'
            elif n_txt.startswith(' ') and (n_stripped.startswith('"') or n_stripped.startswith(')') or n_stripped[0] in CLOSING_PUNCT):
                 next_run.text = n_txt.lstrip()
                 count += 1

    print(f"Stitched {count} split boundaries.")

def clean_paragraph_ends(doc):
    """
    Removes leading/trailing whitespace from paragraphs.
    """
    print("Cleaning paragraph start/end...")
    all_paras = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paras.extend(cell.paragraphs)
    
    for para in all_paras:
        if not para.runs:
            continue
            
        # Fix Leading Space
        for run in para.runs:
            if run.text:
                if run.text.startswith(' '):
                    run.text = run.text.lstrip()
                break 
        
        # Fix Trailing Space
        for run in reversed(para.runs):
            if run.text:
                if run.text.endswith(' '):
                    run.text = run.text.rstrip()
                break

def collect_runs(doc):
    all_runs = []
    for para in doc.paragraphs:
        for run in para.runs:
            if run.text: all_runs.append(run)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        if run.text: all_runs.append(run)
    return all_runs

def process_docx(input_path, output_path):
    if not os.path.exists(input_path):
        print("File not found.")
        return

    print(f"Loading {input_path}...")
    doc = docx.Document(input_path)

    # 1. Parallel Regex Cleaning
    print("Step 1: Parallel Regex Cleaning...")
    all_runs = collect_runs(doc)
    raw_texts = [run.text for run in all_runs]
    
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        cleaned_texts = list(tqdm(executor.map(clean_text_worker, raw_texts), total=len(raw_texts), unit="run"))

    for i, run in enumerate(all_runs):
        if run.text != cleaned_texts[i]:
            run.text = cleaned_texts[i]

    # 2. Stitch broken boundaries
    print("Step 2: Stitching Boundaries...")
    fix_split_run_boundaries(doc)
    
    # 3. Clean Paragraph Start/Ends
    print("Step 3: Trimming Paragraphs...")
    clean_paragraph_ends(doc)

    print(f"Saving to {output_path}...")
    doc.save(output_path)
    print("Done!")

if __name__ == "__main__":
    # Update these paths as needed
    FILE_ROOT = "C:\\DATA\\Novels\\Genshin Impact, My Villain System is a Bit Abnormal"
    INPUT_FILE = os.path.join(FILE_ROOT, "input.docx")
    OUTPUT_FILE = os.path.join(FILE_ROOT, "output.docx")
    MAX_WORKERS = os.cpu_count()  # Uses all available CPU cores
    process_docx(INPUT_FILE, OUTPUT_FILE)