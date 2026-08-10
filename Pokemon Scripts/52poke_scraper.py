import requests
from bs4 import BeautifulSoup
import time

# ================= CONFIGURATION =================
# We will scrape these specific list pages from 52poke
TARGETS = [
    {
        "name": "Pokemon",
        "url": "https://wiki.52poke.com/wiki/宝可梦列表（按全国图鉴编号）",
        "headers": ["中文", "英文"], # Columns to look for
        "type": "table"
    },
    {
        "name": "Moves",
        "url": "https://wiki.52poke.com/wiki/招式列表",
        "headers": ["中文", "英文"],
        "type": "table"
    },
    {
        "name": "Abilities",
        "url": "https://wiki.52poke.com/wiki/特性列表",
        "headers": ["中文", "英文"],
        "type": "table"
    },
    {
        "name": "Items",
        "url": "https://wiki.52poke.com/wiki/道具列表",
        "headers": ["中文", "英文"],
        "type": "table"
    },
     {
        "name": "Locations",
        "url": "https://wiki.52poke.com/wiki/地点列表",
        "headers": ["中文", "英文"],
        "type": "table"
    }
]

OUTPUT_FILE = "glossary_52poke.txt"
# =================================================

def fetch_and_parse(target):
    print(f"Scraping {target['name']} from {target['url']}...")
    pairs = {}
    
    try:
        # User-agent is important so the wiki doesn't block the script
        response = requests.get(target['url'], headers={'User-Agent': 'Mozilla/5.0'})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tables on the page
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this table has the headers we want
            # We look for 'th' (header) elements
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            
            # Find the index of Chinese and English columns
            try:
                # Sometimes headers are complex, so we check if our keyword is *in* the header
                cn_idx = -1
                en_idx = -1
                
                for i, h in enumerate(headers):
                    if "中文" in h or "名字" in h: cn_idx = i
                    if "英文" in h: en_idx = i
                
                # Special case for Pokemon List which often has "中文" in a different structure
                # The big pokemon table usually has: # | icon | Chinese | Japanese | English ...
                # So we might need to manual override for some lists if detection fails.
                if target['name'] == "Pokemon" and cn_idx == -1:
                    cn_idx = 2 # Common index for Chinese name
                    en_idx = 4 # Common index for English name
                
                if cn_idx == -1 or en_idx == -1:
                    continue # Skip this table, it's not a data table
                
                # Now parse rows
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    # Skip header rows or incomplete rows
                    if len(cols) <= max(cn_idx, en_idx):
                        continue
                        
                    cn_text = cols[cn_idx].get_text(strip=True)
                    en_text = cols[en_idx].get_text(strip=True)
                    
                    # Clean up data (remove asterisks, footnotes, etc.)
                    # Example: "Bulbasaur*" -> "Bulbasaur"
                    if cn_text and en_text and cn_text != "中文" and en_text != "英文":
                        pairs[cn_text] = en_text
                        
            except Exception:
                continue

    except Exception as e:
        print(f"  [!] Error: {e}")
        
    print(f"  -> Found {len(pairs)} entries.")
    return pairs

def main():
    all_data = {}
    
    for target in TARGETS:
        data = fetch_and_parse(target)
        # Merge into main dictionary
        all_data.update(data)
        time.sleep(1) # Be polite to the server
        
    # Sort by length (Longest Chinese first) to prevent partial replacement errors
    sorted_keys = sorted(all_data.keys(), key=len, reverse=True)
    
    print(f"\nWriting {len(all_data)} total entries to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 52poke Wiki Glossary\n")
        for cn in sorted_keys:
            en = all_data[cn]
            f.write(f"{cn}={en}\n")
            
    print("Done!")

if __name__ == "__main__":
    main()