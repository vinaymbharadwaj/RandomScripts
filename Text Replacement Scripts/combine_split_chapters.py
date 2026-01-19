import re
import os
from docx import Document
from tqdm import tqdm

def clean_chapter_title(title):
    """
    Removes suffixes like (1/3), [2/2], （1/2） from the end of the title.
    Also strips trailing whitespace.
    """
    # Pattern matches (1/3), [1/3], （1/3） at the end of a string
    pattern = r'[\(\[（]\s*\d+\s*/\s*\d+\s*[\)\]）]\s*$'
    return re.sub(pattern, '', title).strip()

def merge_chapters(input_path, output_path, report_path):
    doc = Document(input_path)
    
    # We will track paragraphs to delete and log merges
    paragraphs = doc.paragraphs
    to_delete = []
    merge_log = []
    
    current_header_text = None
    current_header_para = None
    
    print("Analyzing document structure...")
    # Progress bar for scanning
    for i in tqdm(range(len(paragraphs)), desc="Scanning"):
        p = paragraphs[i]
        
        # We only care about Heading 1
        if p.style.name == 'Heading 1':
            original_text = p.text.strip()
            cleaned_text = clean_chapter_title(original_text)
            
            # Logic: If cleaned text matches the previous header, merge it
            if current_header_text is not None and cleaned_text == current_header_text:
                to_delete.append(p)
                merge_log.append(f"Merged: '{original_text}' -> into -> '{current_header_text}'")
            else:
                # This is a new unique chapter, update the "master" header
                p.text = cleaned_text
                current_header_text = cleaned_text
                current_header_para = p
        else:
            # If it's normal text and we have a "master" header, 
            # we keep it as is (it stays under the current header).
            pass

    print(f"Applying changes and removing {len(to_delete)} redundant headers...")
    # Progress bar for deletion
    for p in tqdm(to_delete, desc="Processing"):
        # Access the underlying XML element and remove it from the parent
        p._element.getparent().remove(p._element)

    # Save the document
    doc.save(output_path)
    
    # Write the report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Merge Report\n{'='*20}\n")
        f.write(f"Total redundant headers removed: {len(to_delete)}\n\n")
        for entry in merge_log:
            f.write(entry + "\n")

    print(f"\nDone! Saved to: {output_path}")
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    # Update these paths as needed
    FILE_ROOT = "C:\\DATA\\Novels\\Pirate - Nami! Give me back my Berry!"
    INPUT_FILE = os.path.join(FILE_ROOT, "input.docx")
    OUTPUT_FILE = os.path.join(FILE_ROOT, "novel_merged.docx")
    REPORT_FILE = os.path.join(FILE_ROOT, "report.txt")

    if os.path.exists(INPUT_FILE):
        merge_chapters(INPUT_FILE, OUTPUT_FILE, REPORT_FILE)
    else:
        print(f"Error: {INPUT_FILE} not found.")