import os
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from docx import Document
from ebooklib import epub
from PIL import Image
from copy import deepcopy
import uuid
from tqdm import tqdm


def process_chunk_serializable(args):
    """Worker function — executed in parallel for each chapter chunk."""
    chunk_index, title, blocks, images_base_path = args

    def runs_to_html(runs):
        parts = []
        for r in runs:
            text = (r.get("text") or "").replace("<", "&lt;").replace(">", "&gt;")
            if not text:
                continue
            prefix = ""
            suffix = ""
            color = r.get("color")
            if color:
                prefix += f'<span style="color:{color}">'
                suffix = "</span>" + suffix
            if r.get("bold"):
                prefix += "<strong>"
                suffix = "</strong>" + suffix
            if r.get("italic"):
                prefix += "<em>"
                suffix = "</em>" + suffix
            if r.get("underline"):
                prefix += "<u>"
                suffix = "</u>" + suffix
            hyperlink = r.get("hyperlink")
            inner = f"{prefix}{text}{suffix}"
            if hyperlink:
                inner = f'<a href="{hyperlink}">{inner}</a>'
            parts.append(inner)
        return "".join(parts)

    html = ""
    i = 0
    while i < len(blocks):
        blk = blocks[i]
        if blk["type"] == "paragraph":
            style = blk.get("style", "")
            if "Bullet" in style or "Number" in style:
                list_tag = "ul" if "Bullet" in style else "ol"
                html += f"<{list_tag}>"
                while i < len(blocks) and blocks[i]["type"] == "paragraph" and (
                    "Bullet" in blocks[i].get("style", "")
                    or "Number" in blocks[i].get("style", "")
                ):
                    pblk = blocks[i]
                    text_html = runs_to_html(pblk.get("runs", []))
                    if pblk.get("hyperlink"):
                        text_html += f' <a href="{pblk["hyperlink"]}">{pblk["hyperlink_text"]}</a>'
                    html += f"<li>{text_html}</li>"
                    i += 1
                html += f"</{list_tag}>"
                continue
            else:
                if style.startswith("Heading 2"):
                    text_html = runs_to_html(blk.get("runs", []))
                    html += f"<h2>{text_html}</h2>"
                else:
                    text_html = runs_to_html(blk.get("runs", []))
                    if blk.get("hyperlink"):
                        text_html += f' <a href="{blk["hyperlink"]}">{blk.get("hyperlink_text","")}</a>'
                    if text_html:
                        html += f"<p>{text_html}</p>"
            i += 1

        elif blk["type"] == "image":
            fname = blk["file"]
            html += f'<div style="text-align:center;"><img src="images/{fname}" alt="Image"/></div>'
            i += 1

        elif blk["type"] == "table":
            html += blk.get("html", "")
            i += 1
        else:
            i += 1

    return (chunk_index, title, html)


def docx_to_epub_parallel(docx_path, epub_path, max_workers=None, temp_dir=None):
    """Convert DOCX -> EPUB using parallel chapter processing with progress reporting."""
    doc = Document(docx_path)
    props = doc.core_properties
    title = props.title or os.path.splitext(os.path.basename(docx_path))[0]
    author = props.author or "Unknown Author"

    if not temp_dir:
        parent = os.path.dirname(os.path.abspath(epub_path)) or "."
        temp_dir = os.path.join(parent, f"temp_epub_images_{uuid.uuid4().hex[:8]}")
    os.makedirs(temp_dir, exist_ok=True)

    def save_image_bytes(img_bytes, ext="png"):
        fname = f"image_{uuid.uuid4().hex[:8]}.{ext}"
        fpath = os.path.join(temp_dir, fname)
        with open(fpath, "wb") as f:
            f.write(img_bytes)
        try:
            im = Image.open(fpath)
            if im.width > 1600 or im.height > 1600:
                im.thumbnail((1600, 1600))
                im.save(fpath)
        except Exception:
            pass
        return fname

    # Extract all blocks
    blocks = []
    paragraphs = list(doc.paragraphs)
    paragraph_index = 0

    for child in doc.element.body:
        tag = child.tag
        if tag.endswith("}p"):
            para = paragraphs[paragraph_index]
            paragraph_index += 1
            run_list = []
            para_hyperlink = None
            para_hyperlink_text = None

            # Detect hyperlinks
            for rel in para._element.xpath(".//w:hyperlink"):
                rId = rel.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
                try:
                    if rId and rId in para.part.rels:
                        url = para.part.rels[rId].target_ref
                        para_hyperlink = url
                        runs = rel.xpath(".//w:r")
                        para_hyperlink_text = "".join([r.xpath("string(.)") for r in runs])
                        break
                except Exception:
                    continue

            for run in para.runs:
                # ✅ Fully compatible image extraction (iter approach)
                for blip in run._element.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
                    rId = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
                    if rId:
                        try:
                            rel = para.part.rels[rId]
                            img_bytes = rel.target_part.blob
                            ext = getattr(rel.target_part, "content_type", "").split("/")[-1] or "png"
                            fname = save_image_bytes(img_bytes, ext)
                            blocks.append({"type": "image", "file": fname})
                        except Exception:
                            continue

                font = run.font
                color = None
                try:
                    if font and font.color and getattr(font.color, "rgb", None):
                        color = f"#{str(font.color.rgb)}"
                except Exception:
                    color = None
                run_list.append({
                    "text": run.text,
                    "bold": bool(run.bold),
                    "italic": bool(run.italic),
                    "underline": bool(run.underline),
                    "color": color,
                    "hyperlink": None,
                })

            blocks.append({
                "type": "paragraph",
                "style": para.style.name if para.style else "",
                "runs": run_list,
                "hyperlink": para_hyperlink,
                "hyperlink_text": para_hyperlink_text,
            })

        elif tag.endswith("}tbl"):
            table_obj = None
            for t in doc.tables:
                if t._element == child:
                    table_obj = t
                    break
            if table_obj is not None:
                html = "<table border='1' style='border-collapse:collapse;width:100%;'>"
                for row in table_obj.rows:
                    html += "<tr>"
                    for cell in row.cells:
                        cell_text = " ".join(r.text for p in cell.paragraphs for r in p.runs).strip()
                        html += f"<td style='padding:6px;vertical-align:top'>{cell_text}</td>"
                    html += "</tr>"
                html += "</table>"
                blocks.append({"type": "table", "html": html})

    # Split into chapters by Heading 1
    chapter_chunks = []
    current_title = "Introduction"
    current_chunk_blocks = []
    for b in blocks:
        if b["type"] == "paragraph" and b.get("style", "").startswith("Heading 1"):
            chapter_chunks.append((len(chapter_chunks), current_title, current_chunk_blocks))
            current_title = "".join([r.get("text", "") for r in b.get("runs", [])]) or "Chapter"
            current_chunk_blocks = []
        else:
            current_chunk_blocks.append(b)
    chapter_chunks.append((len(chapter_chunks), current_title, current_chunk_blocks))

    # Parallel conversion with progress
    worker_args = [(ci, title, deepcopy(blocks_list), temp_dir) for (ci, title, blocks_list) in chapter_chunks]
    results = []
    print(f"⚙️ Processing {len(worker_args)} chapters using {max_workers or os.cpu_count()} workers...\n")
    with ProcessPoolExecutor(max_workers=max_workers) as exe, tqdm(total=len(worker_args), desc="Converting chapters", unit="chapter") as pbar:
        future_to_idx = {exe.submit(process_chunk_serializable, arg): arg[0] for arg in worker_args}
        for fut in as_completed(future_to_idx):
            results.append(fut.result())
            pbar.update(1)

    results.sort(key=lambda x: x[0])

    # Build EPUB
    print("\n📘 Building EPUB...")
    book = epub.EpubBook()
    book.set_identifier(uuid.uuid4().hex)
    book.set_title(title)
    book.set_language("en")
    book.add_author(author)

    # Embed images
    for fname in tqdm(sorted(os.listdir(temp_dir)), desc="Embedding images", unit="img"):
        fpath = os.path.join(temp_dir, fname)
        if not os.path.isfile(fpath):
            continue
        with open(fpath, "rb") as f:
            data = f.read()
        ext = fname.split(".")[-1].lower()
        media_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
        img_item = epub.EpubImage()
        img_item.file_name = f"images/{fname}"
        img_item.media_type = media_type
        img_item.content = data
        book.add_item(img_item)

    # Add chapters
    epub_chapters = []
    for idx, title_txt, html in tqdm(results, desc="Adding chapters", unit="chapter"):
        file_name = f"chap_{idx+1}.xhtml"
        ch = epub.EpubHtml(title=title_txt, file_name=file_name, lang="en")
        ch.content = f"<h1>{title_txt}</h1>{html}"
        book.add_item(ch)
        epub_chapters.append(ch)

    book.toc = tuple(epub_chapters)
    book.spine = ["nav"] + epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(epub_path, book)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\n✅ EPUB created: {epub_path}\n📖 Title: {title}\n✍️ Author: {author}")


if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\I Repair Cultural Relics for the Country"
    input_file = os.path.join(file_root, "input.docx")
    output_file = os.path.join(file_root, "output.epub")
    max_workers = 8
    docx_to_epub_parallel(input_file, output_file, max_workers)