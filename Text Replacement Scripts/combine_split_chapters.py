from docx import Document
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import re
import os

# ---------------- REGEX ----------------

# Matches suffix like (1/2), （2/3）
PART_SUFFIX_RE = re.compile(
    r'^(?P<title>.+?)\s*[（(]\s*\d+\s*/\s*\d+\s*[）)]\s*$'
)

# Loose chapter hint (language-agnostic)
CHAPTER_HINT_RE = re.compile(
    r'^(第.+?章|chapter\s+\d+|chap\.?\s*\d+|ch\.?\s*\d+)',
    re.IGNORECASE
)

# ---------------- HELPERS ----------------

def normalize_title(text: str) -> str:
    text = text.strip()
    m = PART_SUFFIX_RE.match(text)
    return m.group("title").strip() if m else text

def looks_like_chapter(text: str) -> bool:
    return bool(CHAPTER_HINT_RE.match(text.strip()))

def is_heading(para) -> bool:
    style = (para.style.name or "").lower().replace(" ", "")
    return style in {"heading1", "title1", "标题1"} or looks_like_chapter(para.text)

def clone_run(dst, src):
    dst.text = src.text
    f = src.font
    if f:
        dst.bold = f.bold
        dst.italic = f.italic
        dst.underline = f.underline
        dst.font.size = f.size
        dst.font.name = f.name
        if f.color and f.color.rgb:
            dst.font.color.rgb = f.color.rgb

def clone_paragraph(dst_doc, src):
    p = dst_doc.add_paragraph()
    p.style = src.style
    p.alignment = src.alignment
    pf, sf = p.paragraph_format, src.paragraph_format
    pf.left_indent = sf.left_indent
    pf.right_indent = sf.right_indent
    pf.first_line_indent = sf.first_line_indent
    pf.space_before = sf.space_before
    pf.space_after = sf.space_after
    pf.line_spacing = sf.line_spacing

    for r in src.runs:
        nr = p.add_run()
        clone_run(nr, r)

def add_heading(dst_doc, src_para, title):
    if src_para.style and "heading" in src_para.style.name.lower():
        p = dst_doc.add_paragraph(title)
        p.style = src_para.style
    else:
        dst_doc.add_heading(title, level=1)

# ---------------- PARALLEL NORMALIZATION ----------------

def normalize_worker(args):
    idx, text = args
    return idx, normalize_title(text), looks_like_chapter(text)

# ---------------- MAIN LOGIC ----------------

def merge_chapters_consecutive_only(input_path, output_path):
    doc = Document(input_path)

    para_texts = [(i, p.text) for i, p in enumerate(doc.paragraphs)]

    # Parallel preprocessing
    with ProcessPoolExecutor() as ex:
        results = list(tqdm(
            ex.map(normalize_worker, para_texts),
            total=len(para_texts),
            desc="Analyzing chapter titles"
        ))

    norm_map = {i: (norm, is_ch) for i, norm, is_ch in results}

    new_doc = Document()

    current_title = None
    current_header = None
    buffer = []

    for i, para in enumerate(doc.paragraphs):
        norm_title, is_chapter = norm_map[i]

        if is_heading(para):
            # If same normalized title as current → MERGE
            if current_title == norm_title:
                continue

            # Flush previous chapter
            if current_title:
                add_heading(new_doc, current_header, current_title)
                for p in buffer:
                    clone_paragraph(new_doc, p)
                new_doc.add_paragraph()

            # Start new chapter
            current_title = norm_title
            current_header = para
            buffer = []
        else:
            if current_title:
                buffer.append(para)

    # Flush last chapter
    if current_title:
        add_heading(new_doc, current_header, current_title)
        for p in buffer:
            clone_paragraph(new_doc, p)

    new_doc.save(output_path)
    print(f"\n✅ Done: {os.path.abspath(output_path)}")

# ---------------- USAGE ----------------
if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\NBA - Starting with a fusion of Durant and Draymond"
    input_file = os.path.join(file_root, "input.docx")
    output_file = os.path.join(file_root, "output.docx")
    merge_chapters_consecutive_only(input_file, output_file)