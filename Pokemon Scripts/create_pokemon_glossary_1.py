import requests
import json

# URLs for the data (using fanzeyi's repository which has multilingual support)
urls = {
    "Pokemon": "https://raw.githubusercontent.com/fanzeyi/pokemon.json/master/pokedex.json",
    "Moves": "https://raw.githubusercontent.com/fanzeyi/pokemon.json/master/moves.json",
    "Items": "https://raw.githubusercontent.com/fanzeyi/pokemon.json/master/items.json"
}

def generate_glossary():
    # Open a file to write the results with UTF-8 encoding
    with open("glossary.txt", "w", encoding="utf-8") as f:
        
        # 1. Fetch and Write Pokemon Names
        print("Fetching Pokemon data...")
        try:
            data = requests.get(urls["Pokemon"]).json()
            f.write("[Pokemon Names]\n")
            for entry in data:
                # The structure is usually entry['name']['chinese']
                c_name = entry.get('name', {}).get('chinese')
                e_name = entry.get('name', {}).get('english')
                if c_name and e_name:
                    f.write(f"{c_name}={e_name}\n")
            f.write("\n")
        except Exception as e:
            print(f"Error fetching Pokemon: {e}")

        # 2. Fetch and Write Moves
        print("Fetching Moves data...")
        try:
            data = requests.get(urls["Moves"]).json()
            f.write("[Moves]\n")
            for entry in data:
                c_name = entry.get('cname') # This repo uses 'cname' for Chinese in moves.json
                e_name = entry.get('ename') # and 'ename' for English
                if c_name and e_name:
                    f.write(f"{c_name}={e_name}\n")
            f.write("\n")
        except Exception as e:
            print(f"Error fetching Moves: {e}")

        # 3. Fetch and Write Items
        print("Fetching Items data...")
        try:
            data = requests.get(urls["Items"]).json()
            f.write("[Items]\n")
            for entry in data:
                # Items structure in this repo varies, but usually follows similar name patterns
                # Note: The item file structure might differ slightly, we check for 'name' dict or direct keys
                c_name = entry.get('name', {}).get('chinese')
                e_name = entry.get('name', {}).get('english')
                if c_name and e_name:
                    f.write(f"{c_name}={e_name}\n")
            f.write("\n")
        except Exception as e:
            print(f"Error fetching Items: {e}")

    print("Success! Data saved to 'glossary.txt'.")

if __name__ == "__main__":
    generate_glossary()