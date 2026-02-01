import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def parse_file(file_path):
    """Reads a file and returns a dict of Chinese:Translation."""
    data = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    data[key] = value
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data

def merge_with_report(file_list, output_file, report_file):
    # Dictionary to hold final values
    merged_data = {}
    # Dictionary to hold conflicts: {key: [val_from_file1, val_from_file2, ...]}
    conflicts = {}

    # Stage 1: Parallel Loading
    print("--- Stage 1: Loading Files ---")
    with ThreadPoolExecutor() as executor:
        # We don't reverse here because we want to process 1, then 2, then 3
        # to identify what conflicts with the "primary" (first) file.
        results = list(tqdm(executor.map(parse_file, file_list), 
                           total=len(file_list), 
                           desc="Reading Files"))

    # Stage 2: Merging with Conflict Detection
    print("\n--- Stage 2: Merging & Detecting Conflicts ---")
    for i, file_data in enumerate(results):
        file_name = file_list[i]
        for key, value in file_data.items():
            if key in merged_data:
                # If the key exists but the value is different, log it
                if merged_data[key] != value:
                    if key not in conflicts:
                        conflicts[key] = {file_list[0]: merged_data[key]}
                    conflicts[key][file_name] = value
            else:
                # If key is new, add it
                merged_data[key] = value

    # Stage 3: Sorting
    print("\n--- Stage 3: Sorting ---")
    sorted_items = sorted(merged_data.items(), key=lambda x: len(x[0]), reverse=True)

    # Stage 4: Writing Final File
    with open(output_file, 'w', encoding='utf-8') as f:
        for key, value in tqdm(sorted_items, desc="Writing Merged File"):
            f.write(f"{key}={value}\n")

    # Stage 5: Writing Conflict Report
    if conflicts:
        print(f"\n--- Stage 5: Writing Conflict Report ({len(conflicts)} found) ---")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("CONFLICT REPORT\nFormat: [Key] -> File: Value\n" + "="*30 + "\n")
            for key, versions in conflicts.items():
                f.write(f"\nKey: {key}\n")
                for fname, val in versions.items():
                    f.write(f"  -- {fname}: {val}\n")
    else:
        print("\n--- Stage 5: No conflicts found ---")

    print(f"\nProcess Complete.")
    print(f"Main File: {output_file}")
    if conflicts: print(f"Conflict Report: {report_file}")

if __name__ == "__main__":
    FILE_ROOT = "C:\\DATA\\Novels"
    OUTPUT_FILE = os.path.join(FILE_ROOT, "Combined_Glossary_Word_Replacement_Merged.txt")
    CONFLICT_REPORT_FILE = os.path.join(FILE_ROOT, "Conflict_Report.txt")
    
    # Your input files (First file has highest priority)
    input_files = [
        os.path.join(FILE_ROOT, "Pokemon_Glossary_Word_Replacement.txt"), 
        os.path.join(FILE_ROOT, "Conan_Glossary_Word_Replacement.txt"),
        os.path.join(FILE_ROOT, "GenshinHonkai_Glossary_Word_Replacement.txt"),
        os.path.join(FILE_ROOT, "HarryPotter_Glossary_Word_Replacement.txt"),
        os.path.join(FILE_ROOT, "FairyTail_Glossary_Word_Replacement.txt"),
        os.path.join(FILE_ROOT, "OnePiece_Glossary_Word_Replacement.txt"),
        os.path.join(FILE_ROOT, "General_Glossary_Word_Replacement.txt"),
        ]
    
    merge_with_report(input_files, OUTPUT_FILE, CONFLICT_REPORT_FILE)