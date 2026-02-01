import os
import sys
import uuid
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

import docx
from docx.document import Document as _Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.table import Table

from ebooklib import epub

# --- Configuration & Helpers ---

def get_image_from_run(run, parent_part):
    """Safely extracts image binary from a docx run."""
    if not hasattr(run, 'element') or not run.element.xpath('.//a:blip'):
        return None

    try:
        blip = run.element.xpath('.//a:blip')[0]
        embed_id = blip.get(qn('r:embed'))
        if not embed_id:
            return None

        image_part = parent_part.related_parts[embed_id]
        image_bytes = image_part.blob
        content_type = image_part.content_type
        ext = content_type.split('/')[-1].replace('jpeg', 'jpg')
        filename = f"img_{uuid.uuid4().hex[:8]}.{ext}"
        
        return filename, image_bytes, content_type
    except Exception as e:
        logging.warning(f"Could not extract image: {e}")
        return None

def html_escape(text):
    if not text: return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def convert_run_to_html(run, parent_part, images_buffer):
    """Converts a run (text/image) to HTML string."""
    text = html_escape(run.text)
    
    img_data = get_image_from_run(run, parent_part)
    if img_data:
        fname, bytes_data, mime = img_data
        images_buffer.append((fname, bytes_data, mime))
        return f'<img src="images/{fname}" alt="image" style="max-width:100%; height:auto;" />'

    if not text: return ""

    if run.bold: text = f"<b>{text}</b>"
    if run.italic: text = f"<i>{text}</i>"
    if run.underline: text = f"<u>{text}</u>"
    return text

def get_paragraph_content(paragraph, parent_part, images_buffer):
    """Safely extracts content from paragraph, handling XML for links."""
    if not hasattr(paragraph, 'element'):
        # Fallback for weird objects that python-docx occasionally yields
        return html_escape(getattr(paragraph, 'text', ""))

    content_parts = []
    try:
        for child in paragraph.element.iterchildren():
            # Standard Text Run
            if child.tag == qn('w:r'):
                run = Run(child, paragraph)
                content_parts.append(convert_run_to_html(run, parent_part, images_buffer))
            
            # Hyperlink
            elif child.tag == qn('w:hyperlink'):
                rid = child.get(qn('r:id'))
                url = "#"
                if rid and rid in parent_part.rels:
                    try:
                        url = parent_part.rels[rid].target_ref
                    except: pass
                
                link_text = ""
                for sub_child in child.iterchildren():
                    if sub_child.tag == qn('w:r'):
                        sub_run = Run(sub_child, paragraph)
                        link_text += convert_run_to_html(sub_run, parent_part, images_buffer)
                
                if link_text:
                    content_parts.append(f'<a href="{url}">{link_text}</a>')
                    
    except Exception as e:
        logging.error(f"Error in paragraph XML parsing: {e}")
        return html_escape(paragraph.text)

    return "".join(content_parts)

def process_block_to_html(block, parent_part, images_buffer):
    """Routes docx blocks to HTML converters."""
    if block is None: return ""

    if isinstance(block, Paragraph):
        content = get_paragraph_content(block, parent_part, images_buffer)
        try:
            style = block.style.name.lower()
        except: style = "normal"
        
        if not content.strip() and not images_buffer: return ""

        if 'heading 1' in style: return f"<h1>{content}</h1>"
        elif 'heading 2' in style: return f"<h2>{content}</h2>"
        elif 'list' in style: return f"<li>{content}</li>"
        else: return f"<p>{content}</p>"

    elif isinstance(block, Table):
        html = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">'
        try:
            for row in block.rows:
                html += "<tr>"
                for cell in row.cells:
                    cell_html = "".join([get_paragraph_content(p, parent_part, images_buffer) for p in cell.paragraphs])
                    html += f"<td style='padding:5px; border:1px solid #ccc;'>{cell_html}</td>"
                html += "</tr>"
            html += "</table>"
            return html
        except Exception as e:
            logging.error(f"Table conversion error: {e}")
            return "<p><i>[Table omitted due to error]</i></p>"
    return ""

def iter_block_items(parent):
    """Yields each paragraph and table in document order."""
    parent_elm = parent.element.body if isinstance(parent, _Document) else parent
    for child in parent_elm.iterchildren():
        if child.tag == qn('w:p'): yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'): yield Table(child, parent)

# --- Core Processing ---

def chapter_worker(chapter_data):
    """Worker function for threading."""
    try:
        html_parts = []
        images = []
        for block in chapter_data['blocks']:
            html_parts.append(process_block_to_html(block, chapter_data['part'], images))
        
        return {
            "title": chapter_data['title'],
            "html": "\n".join(html_parts),
            "images": images
        }
    except Exception as e:
        logging.error(f"Worker failed on chapter {chapter_data['title']}: {e}")
        return None

def convert(docx_path, epub_path, cover_path=None):
    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} not found."); return

    doc = docx.Document(docx_path)
    title = doc.core_properties.title or "Untitled Book"
    author = doc.core_properties.author or "Unknown Author"

    # Split into chapters
    chapters_raw = []
    current_blocks = []
    current_title = "Front Matter"
    
    print("Indexing document...")
    all_blocks = list(iter_block_items(doc))
    for block in tqdm(all_blocks, desc="Splitting Chapters"):
        if isinstance(block, Paragraph) and "heading 1" in block.style.name.lower():
            if current_blocks:
                chapters_raw.append({'title': current_title, 'blocks': current_blocks, 'part': doc.part})
            current_title = block.text.strip()
            current_blocks = []
        else:
            current_blocks.append(block)
    if current_blocks:
        chapters_raw.append({'title': current_title, 'blocks': current_blocks, 'part': doc.part})

    # Parallel Processing
    results = []
    print(f"Converting {len(chapters_raw)} chapters...")
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(chapter_worker, c): i for i, c in enumerate(chapters_raw)}
        for f in tqdm(as_completed(futures), total=len(chapters_raw), desc="HTML Generation"):
            res = f.result()
            if res: results.append((futures[f], res))
    
    results.sort(key=lambda x: x[0]) # Maintain order

    # Build EPUB
    book = epub.EpubBook()
    book.set_title(title)
    book.add_author(author)
    book.set_language('en')
    book.set_identifier(str(uuid.uuid4()))

    if cover_path and os.path.exists(cover_path):
        with open(cover_path, 'rb') as f:
            book.set_cover(os.path.basename(cover_path), f.read())

    style = 'body { font-family: serif; } h1 { text-align: center; } a { color: #0000EE; }'
    css = epub.EpubItem(uid="style", file_name="style/main.css", media_type="text/css", content=style)
    book.add_item(css)

    epub_chaps = []
    seen_imgs = set()
    for i, (_, data) in enumerate(results):
        for img_name, img_bytes, img_mime in data['images']:
            if img_name not in seen_imgs:
                item = epub.EpubItem(uid=img_name, file_name=f"images/{img_name}", media_type=img_mime, content=img_bytes)
                book.add_item(item)
                seen_imgs.add(img_name)

        chapter = epub.EpubHtml(title=data['title'], file_name=f"chap_{i}.xhtml")
        chapter.content = f"<h1>{data['title']}</h1>" + data['html']
        chapter.add_item(css)
        book.add_item(chapter)
        epub_chaps.append(chapter)

    book.toc = tuple(epub_chaps)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + epub_chaps

    print("Writing EPUB...")
    epub.write_epub(epub_path, book, {})
    print(f"Finished! Errors (if any) logged to conversion_errors.log")


if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\Genshin Impact - Starting from Liyue to Build Infrastructure"
    input_file = os.path.join(file_root, "Genshin Impact - Starting from Liyue to Build Infrastructure (TRXS).docx")
    output_file = os.path.join(file_root, "Genshin Impact - Starting from Liyue to Build Infrastructure (TRXS).epub")
    cover_file = os.path.join(file_root, "Cover 2.jpeg")

    # --- Logging Setup ---
    logging.basicConfig(
        filename=os.path.join(file_root, "conversion_errors.log"),
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if os.path.exists(input_file):
        convert(input_file, output_file, cover_file if os.path.exists(cover_file) else None)
    else:
        print(f"No input file found at {input_file}.")