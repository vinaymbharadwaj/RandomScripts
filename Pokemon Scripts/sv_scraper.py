import requests
import sys

# ================= CONFIGURATION =================
# Define the URL and column index for each file.
# Indices start at 0 (1st column = 0, 2nd column = 1, etc.)

FILES_CONFIG = {
    "Pokemon": {
        "url": "https://raw.githubusercontent.com/Ruimusume/PMSV/main/Pok%C3%A9mon%20Names.txt",
        # Format: 987(0) [TAB] Flutter Mane(1) [TAB] 振翼发(2) [TAB] Japanese(3)
        "cn_idx": 2, # Chinese is in column 2
        "en_idx": 1  # English is in column 1
    },
    "Items": {
        "url": "https://raw.githubusercontent.com/Ruimusume/PMSV/main/Item%20Names.txt",
        # Format: 3(0) [TAB] 0003(1) [TAB] 超级球(2) [TAB] Japanese(3) [TAB] Great Ball(4) [TAB] TRUE(5)
        # Note: Chinese comes BEFORE English in this specific file!
        "cn_idx": 2,
        "en_idx": 4
    },
    "Moves": {
        "url": "https://raw.githubusercontent.com/Ruimusume/PMSV/main/Move%20Names.txt",
        # Format: 4(0) [TAB] 0004(1) [TAB] Comet Punch(2) [TAB] 连续拳(3) [TAB] Japanese(4)
        "cn_idx": 3,
        "en_idx": 2
    },
    "Abilities": {
        "url": "https://raw.githubusercontent.com/Ruimusume/PMSV/main/Ability%20Names.txt",
        # Format: 24(0) [TAB] Rough Skin(1) [TAB] 粗糙皮肤(2) [TAB] Japanese(3)
        "cn_idx": 2,
        "en_idx": 1
    }
}

OUTPUT_FILE = "glossary_pmsv_final.txt"
# ===========================================

def get_text_content(url):
    """Downloads the raw text file."""
    try:
        print(f"Downloading: {url} ...", end=" ")
        resp = requests.get(url)
        if resp.status_code == 200:
            print("[SUCCESS]")
            return resp.text
        else:
            print(f"[FAILED] HTTP {resp.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def main():
    # Force UTF-8 output to prevent Windows console errors
    sys.stdout.reconfigure(encoding='utf-8')
    
    all_pairs = {}
    total_count = 0

    print(f"--- Parsing Ruimusume/PMSV Repository ---\n")

    for name, config in FILES_CONFIG.items():
        content = get_text_content(config["url"])
        if not content:
            continue
            
        lines = content.splitlines()
        count = 0
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Split by TAB character '\t'
            parts = line.split('\t')
            
            cn_index = config["cn_idx"]
            en_index = config["en_idx"]
            
            # Ensure the line has enough columns
            min_len = max(cn_index, en_index) + 1
            
            if len(parts) >= min_len:
                cn_text = parts[cn_index].strip()
                en_text = parts[en_index].strip()
                
                # Basic validation: ensure we aren't saving empty strings
                if cn_text and en_text and cn_text != en_text:
                    all_pairs[cn_text] = en_text
                    count += 1
            else:
                # Debugging: Print first error to see if format changed
                if count == 0 and len(parts) > 1:
                    print(f"  [WARNING] Format mismatch for {name}. Line parts: {parts}")

        print(f"  -> {name}: Extracted {count} entries")
        total_count += count

    # ================= SORTING & SAVING =================
    # CRITICAL STEP: Sort by Chinese length (Descending)
    # This prevents partial replacement errors. 
    # Example: If we replace "Ball" (球) before "Great Ball" (超级球), 
    # "超级球" might become "超级Ball" and break the next replacement.
    sorted_keys = sorted(all_pairs.keys(), key=len, reverse=True)
    
    print(f"\nWriting {len(all_pairs)} entries to '{OUTPUT_FILE}' ...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Ruimusume/PMSV Glossary (Auto-Generated)\n")
        f.write("# Format: Chinese=English\n\n")
        
        for cn in sorted_keys:
            en = all_pairs[cn]
            f.write(f"{cn}={en}\n")

    print("Done! Please check the output file.")

if __name__ == "__main__":
    main()