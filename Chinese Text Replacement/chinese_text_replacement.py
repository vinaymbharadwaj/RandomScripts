def load_replacements(mapping_file):
    replacements = {}
    seen = set()
    with open(mapping_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            chinese, english = line.split("=", 1)
            if chinese not in seen:  # keep only first occurrence
                replacements[chinese] = english
                seen.add(chinese)
    # Sort by length of Chinese key (longest first)
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)
    return sorted_replacements


def replace_text(input_file, output_file, replacements):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    for chinese, english in replacements:
        text = text.replace(chinese, english)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    mapping_file = "C:\\DATA\\Novels\\Pokemon_Glossary_Word_Replacement.txt" # file with Chinese=English lines
    file_root = "C:\\DATA\\Novels\\Pokémon - Starting with a Volcarona"
    input_file = file_root+"\\"+"input.txt" # file with Chinese text
    output_file = file_root+"\\"+"output.txt" # where to save result

    replacements = load_replacements(mapping_file)
    replace_text(input_file, output_file, replacements)

    print("Replacement completed.")
