from docx import Document
from docx.shared import RGBColor
from collections import OrderedDict
from concurrent.futures import ProcessPoolExecutor
import re
import os

# Regex to match “第12章 xxx (1/3)” or “第十二章 xxx （2/4）”
CHAP_RE = re.compile(
    r'^\s*(第[\d一二三四五六七八九十百千]+章)\s+(.+?)\s*(?:[（(]\s*\d+\s*/\s*\d+\s*[）)])?\s*$'
)

def normalize_chapter_title(text: str) -> str | None:
    """Normalize chapter titles by removing (1/3)-style markers."""
    m = CHAP_RE.match(text.strip())
    if not m:
        return None
    return f"{m.group(1)} {m.group(2)}"

def is_heading1(para) -> bool:
    """Detect chapter headings either by style or regex match."""
    style_name = (para.style.name or "").strip().lower().replace(" ", "")
    is_heading = style_name in {"heading1", "标题1", "title1"}
    return is_heading or (normalize_chapter_title(para.text) is not None)

def clone_run(dst_run, src_run):
    """Copy run-level formatting and text."""
    dst_run.text = src_run.text
    f = src_run.font
    if f:
        dst_run.font.bold = f.bold
        dst_run.font.italic = f.italic
        dst_run.font.underline = f.underline
        dst_run.font.size = f.size
        dst_run.font.name = f.name
        if f.color and f.color.rgb:
            dst_run.font.color.rgb = f.color.rgb

def clone_paragraph(dst_doc, src_para):
    """Clone a paragraph (style, alignment, runs) preserving formatting."""
    new_p = dst_doc.add_paragraph()
    if src_para.style:
        new_p.style = src_para.style
    new_p.alignment = src_para.alignment
    new_p.paragraph_format.left_indent = src_para.paragraph_format.left_indent
    new_p.paragraph_format.right_indent = src_para.paragraph_format.right_indent
    new_p.paragraph_format.first_line_indent = src_para.paragraph_format.first_line_indent
    new_p.paragraph_format.space_before = src_para.paragraph_format.space_before
    new_p.paragraph_format.space_after = src_para.paragraph_format.space_after
    new_p.paragraph_format.line_spacing = src_para.paragraph_format.line_spacing

    for r in src_para.runs:
        new_r = new_p.add_run()
        clone_run(new_r, r)

    if not src_para.runs and src_para.text:
        new_p.add_run(src_para.text)
    return new_p

def add_heading_preserving_style(dst_doc, src_para, text):
    """Add heading styled like the source heading."""
    if src_para.style and "heading 1" in src_para.style.name.lower():
        p = dst_doc.add_paragraph()
        p.style = src_para.style
        p.add_run(text)
    else:
        dst_doc.add_heading(text, level=1)

def _normalize_for_index(args):
    """Parallel helper: normalize chapter titles."""
    i, text = args
    normalized = normalize_chapter_title(text) or text.strip()
    is_ch = bool(normalize_chapter_title(text))
    return (i, normalized, is_ch)

def merge_split_chapters_preserve_format(input_path: str, output_path: str):
    """Main function to merge split or duplicate consecutive chapters."""
    doc = Document(input_path)
    para_texts = [(i, p.text) for i, p in enumerate(doc.paragraphs)]

    # Normalize all headings in parallel
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(_normalize_for_index, para_texts))

    norm_by_idx = {i: (norm, is_ch) for i, norm, is_ch in results}

    chapters = OrderedDict()
    current_key = None
    current_header_para = None
    prev_key = None

    for i, para in enumerate(doc.paragraphs):
        norm, is_ch = norm_by_idx[i]

        if is_heading1(para):
            # Normalize title
            norm_title = normalize_chapter_title(para.text) or para.text.strip()

            # NEW LOGIC: Merge consecutive identical chapters
            if norm_title == prev_key:
                # Continue same chapter (don’t create a new key)
                current_key = prev_key
                # update header if not set before
                if chapters[current_key]["header_src"] is None:
                    chapters[current_key]["header_src"] = para
            else:
                current_key = norm_title
                if current_key not in chapters:
                    chapters[current_key] = {"header_src": para, "blocks": []}
            prev_key = norm_title
        else:
            if current_key:
                chapters[current_key]["blocks"].append(para)

    # Rebuild merged document
    new_doc = Document()
    try:
        src_sec = doc.sections[0]
        dst_sec = new_doc.sections[0]
        dst_sec.page_height = src_sec.page_height
        dst_sec.page_width = src_sec.page_width
        dst_sec.left_margin = src_sec.left_margin
        dst_sec.right_margin = src_sec.right_margin
        dst_sec.top_margin = src_sec.top_margin
        dst_sec.bottom_margin = src_sec.bottom_margin
    except Exception:
        pass

    for chap_title, payload in chapters.items():
        add_heading_preserving_style(new_doc, payload["header_src"], chap_title)
        for para in payload["blocks"]:
            clone_paragraph(new_doc, para)
        new_doc.add_paragraph()  # optional blank line between chapters

    new_doc.save(output_path)
    print(f"✅ Merged file saved to: {os.path.abspath(output_path)}")

# Example usage
if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\American horror - Starting from Waterfall Town"
    input_file = os.path.join(file_root, "input.docx")
    output_file = os.path.join(file_root, "output.docx")
    merge_split_chapters_preserve_format(input_file, output_file)