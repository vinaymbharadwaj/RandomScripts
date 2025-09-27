import os
from docx import Document

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


def replace_in_text(text, replacements):
    for chinese, english in replacements:
        text = text.replace(chinese, english)
    return text


def replace_text_file(input_file, output_file, replacements):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    text = replace_in_text(text, replacements)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)


def replace_docx_file(input_file, output_file, replacements):
    doc = Document(input_file)

    # Process paragraphs
    for para in doc.paragraphs:
        for run in para.runs:
            run.text = replace_in_text(run.text, replacements)

    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.text = replace_in_text(run.text, replacements)

    doc.save(output_file)


if __name__ == "__main__":
    mapping_file = "C:\\DATA\\Novels\\Pokemon_Glossary_Word_Replacement.txt" # file with Chinese=English lines
    file_root = "C:\\DATA\\Novels\\Pokémon - Starting by Subduing a Shiny Metagross"
    input_file = os.path.join(file_root, "input.docx")  # can be input.txt or input.docx
    output_file = os.path.join(file_root, "output.docx")  # or output.txt

    replacements = load_replacements(mapping_file)

    if input_file.lower().endswith(".txt"):
        replace_text_file(input_file, output_file, replacements)
    elif input_file.lower().endswith(".docx"):
        replace_docx_file(input_file, output_file, replacements)
    else:
        raise ValueError("Unsupported file format. Use .txt or .docx")

    print("Replacement completed.")