import requests
import time

# ================= SETTINGS =================
OUTPUT_FILE = "glossary_full.txt"

# 1. Gen 9 Source (Scarlet/Violet)
SV_REPO_BASE = "https://raw.githubusercontent.com/Pokemon-Project-com/sv-text/master/common"
# We will try these folder names for Chinese until one works
CN_FOLDERS_TO_TRY = ["sc", "schinese", "chs", "zh-hans", "zh-Hans", "zho", "dat_chs"]
EN_FOLDER = "english" # Usually standard, but if this fails, try "en" or "dat_en"

# 2. Gen 1-7 Source (Fanzeyi - Very Stable)
# This database is excellent for older gens if the SV repo fails or is incomplete
FANZEYI_BASE = "https://raw.githubusercontent.com/fanzeyi/pokemon.json/master"

# ============================================

def fetch_text_lines(url):
    """Fetches a raw text file and returns lines."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Decode utf-8 and split
            return response.content.decode('utf-8').splitlines()
    except Exception:
        pass
    return None

def fetch_json(url):
    """Fetches a JSON file."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def main():
    all_pairs = {} # Use a dict to avoid duplicates (Key=Chinese, Value=English)

    print(f"--- STARTING GLOSSARY GENERATION ---\n")

    # ================= PART 1: GEN 9 (SV-TEXT) =================
    print(f"Attempting to fetch Gen 9 (Scarlet/Violet) data...")
    
    # 1. Find the working Chinese folder
    valid_cn_folder = None
    for folder in CN_FOLDERS_TO_TRY:
        test_url = f"{SV_REPO_BASE}/{folder}/monsname.txt"
        print(f"  Checking folder: '{folder}'...", end="\r")
        if fetch_text_lines(test_url):
            valid_cn_folder = folder
            print(f"  [SUCCESS] Found valid Chinese folder: '{folder}'        ")
            break
    
    if valid_cn_folder:
        files = ["monsname", "wazaname", "itemname", "tokusei", "seikaku", "typename"]
        for filename in files:
            url_cn = f"{SV_REPO_BASE}/{valid_cn_folder}/{filename}.txt"
            url_en = f"{SV_REPO_BASE}/{EN_FOLDER}/{filename}.txt"
            
            lines_cn = fetch_text_lines(url_cn)
            lines_en = fetch_text_lines(url_en)
            
            if lines_cn and lines_en:
                count = 0
                for cn, en in zip(lines_cn, lines_en):
                    cn, en = cn.strip(), en.strip()
                    if cn and en and cn != "－－－－" and "reserve" not in en.lower():
                        all_pairs[cn] = en
                        count += 1
                print(f"    + Extracted {count} entries from {filename}")
            else:
                print(f"    ! Failed to download {filename}")
    else:
        print("  [FAILED] Could not find Gen 9 data folders. Skipping to Gen 1-7 backup.")

    # ================= PART 2: GEN 1-7 (FANZEYI BACKUP) =================
    print(f"\nFetching Gen 1-7 Backup data (Fanzeyi)...")
    
    # Pokemon
    data = fetch_json(f"{FANZEYI_BASE}/pokedex.json")
    if data:
        count = 0
        for entry in data:
            c = entry.get('name', {}).get('chinese')
            e = entry.get('name', {}).get('english')
            if c and e and c not in all_pairs: # Only add if we don't have it yet
                all_pairs[c] = e
                count += 1
        print(f"    + Added {count} older Pokemon names.")

    # Moves
    data = fetch_json(f"{FANZEYI_BASE}/moves.json")
    if data:
        count = 0
        for entry in data:
            c = entry.get('cname')
            e = entry.get('ename')
            if c and e and c not in all_pairs:
                all_pairs[c] = e
                count += 1
        print(f"    + Added {count} older Moves.")

    # Items
    data = fetch_json(f"{FANZEYI_BASE}/items.json")
    if data:
        count = 0
        for entry in data:
            c = entry.get('cname') # This repo uses cname/ename for items too usually
            e = entry.get('ename')
            # Fallback for different structure
            if not c: c = entry.get('name', {}).get('chinese')
            if not e: e = entry.get('name', {}).get('english')
            
            if c and e and c not in all_pairs:
                all_pairs[c] = e
                count += 1
        print(f"    + Added {count} older Items.")

    # ================= WRITING FILE =================
    print(f"\nWriting results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Pokemon Glossary (Generated)\n")
        # Sort by length of Chinese string (descending) 
        # This prevents partial replacements (e.g., replacing 'Potion' inside 'Super Potion')
        sorted_keys = sorted(all_pairs.keys(), key=len, reverse=True)
        
        for cn in sorted_keys:
            f.write(f"{cn}={all_pairs[cn]}\n")

    print(f"Done! Total terms collected: {len(all_pairs)}")

if __name__ == "__main__":
    main()