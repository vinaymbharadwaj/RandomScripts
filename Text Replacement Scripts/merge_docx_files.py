import os
import re
import math
from docx import Document
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def extract_number(filename):
    """Extracts the last number found in the filename for sorting."""
    nums = re.findall(r'\d+', filename)
    return int(nums[-1]) if nums else filename

def get_sorted_files(folder_path):
    """Gathers and sorts files based on trailing numbers or alphabetically."""
    files = [f for f in os.listdir(folder_path) if f.endswith('.docx') and not f.startswith('~')]
    
    # Check if files contain numbers to determine sorting strategy
    if any(re.search(r'\d+', f) for f in files):
        files.sort(key=extract_number)
    else:
        files.sort()
    return files

def merge_docx(input_folder, output_filename):
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' not found.")
        return

    files = get_sorted_files(input_folder)
    if not files:
        print("No .docx files found in the directory.")
        return

    print(f"Found {len(files)} files. Preparing for merge...")

    # Initialize the base document with the first file
    first_file_path = os.path.join(input_folder, files[0])
    combined_doc = Document(first_file_path)
    
    # We use a progress bar to keep the user informed
    with tqdm(total=len(files)-1, desc="Merging Documents") as pbar:
        # Note: While we can read files in parallel, the python-docx 
        # objects must be appended sequentially to maintain order.
        for i in range(1, len(files)):
            file_path = os.path.join(input_folder, files[i])
            
            # Add a page break between files if desired
            combined_doc.add_page_break()
            
            sub_doc = Document(file_path)
            
            # Append elements from sub_doc to combined_doc
            for element in sub_doc.element.body:
                combined_doc.element.body.append(element)
            
            pbar.update(1)

    print(f"Saving merged file as '{output_filename}'... (This may take a moment for huge files)")
    combined_doc.save(output_filename)
    print("Success! Merge complete.")

if __name__ == "__main__":
    # CONFIGURATION
    target_folder = "C:\\DATA\\Novels\\Daily life of a spy in the world of Conan\\output_parts"
    output_name = os.path.join(target_folder, "output.docx")
    
    merge_docx(target_folder, output_name)