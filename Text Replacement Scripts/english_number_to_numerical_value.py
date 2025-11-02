import os
import re
from tqdm import tqdm
from word2number import w2n
from docx import Document


# --- core regex replacement ---
def replace_chapter_numbers_in_text(text):
    """
    Convert spelled-out numbers after 'Chapter' to digits.
    Handles complex numbers like 'Twenty-Seven', 'One Hundred and Twenty-One', etc.
    """

    # Match 'Chapter' followed by any valid spelled number phrase
    # Includes words like 'One', 'Hundred', 'Thousand', hyphens, and 'and'
    pattern = re.compile(
        r'\b(Chapter)\s+((?:[A-Za-z]+[\s\-and]*)+)(?=[\:\-\—\.\!\?\,\;\s]|$)',
        re.IGNORECASE,
    )

    def repl(m):
        chapter = m.group(1)
        words = m.group(2).strip()
        # Normalize hyphens (w2n expects spaces)
        words_normalized = re.sub(r'[\-]+', ' ', words)
        try:
            num = w2n.word_to_num(words_normalized)
            return f"{chapter} {num}"
        except Exception:
            return m.group(0)

    return pattern.sub(repl, text)


# --- DOCX handling ---
def process_docx_file(input_path, output_path):
    doc = Document(input_path)

    for i, para in enumerate(tqdm(doc.paragraphs, desc="Processing DOCX paragraphs")):
        txt = para.text.strip()
        if not txt:
            continue

        new_txt = replace_chapter_numbers_in_text(txt)

        if new_txt != txt:
            style = para.style
            # Insert a new paragraph below, with same style but new text
            new_para = para.insert_paragraph_before(new_txt)
            new_para.style = style
            # Delete the old paragraph entirely
            p = para._element
            p.getparent().remove(p)
            p._p = p._element = None

    doc.save(output_path)
    print(f"✅ DOCX processing complete → {output_path}")


# --- TXT handling ---
def process_txt_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    new_text = replace_chapter_numbers_in_text(text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(f"✅ TXT processing complete → {output_path}")


# --- main wrapper ---
def replace_chapter_numbers(input_path, output_path=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    if output_path is None:
        stem, ext = os.path.splitext(input_path)
        output_path = f"{stem}_processed{ext}"

    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".docx":
        process_docx_file(input_path, output_path)
    elif ext == ".txt":
        process_txt_file(input_path, output_path)
    else:
        raise ValueError("Only .docx or .txt supported")

    return output_path


if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\The Elementary School Detective King"
    input_file = os.path.join(file_root, "input.docx")  # can be input.txt or input.docx
    replace_chapter_numbers(input_file)