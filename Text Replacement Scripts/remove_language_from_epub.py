import os
import warnings
from ebooklib import epub
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import langid
import re

# Suppress warnings from ebooklib
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# -------------------------------
# Fragment-level language detection
# -------------------------------

def split_text_fragments(text):
    """
    Split text into small fragments for better language detection.
    Splits on punctuation, parentheses, and quotes.
    """
    pattern = r'([.!?]+|\(.*?\)|\".*?\"|\'.*?\')'
    fragments = []
    last = 0
    for match in re.finditer(pattern, text):
        start, end = match.span()
        if start > last:
            fragments.append(text[last:start].strip())
        fragments.append(text[start:end].strip())
        last = end
    if last < len(text):
        fragments.append(text[last:].strip())
    # Remove empty strings
    return [f for f in fragments if f]

def remove_target_language_from_text(text, lang_to_remove):
    """
    Remove all fragments in lang_to_remove (ISO code) from text.
    """
    fragments = split_text_fragments(text)
    kept = []
    for f in fragments:
        try:
            if f:
                lang, conf = langid.classify(f)
                if lang != lang_to_remove:
                    kept.append(f)
        except:
            kept.append(f)
    return " ".join(kept)

def clean_html_remove_language_bytes(html_bytes, lang_to_remove):
    """
    Remove sentences in the specified language from HTML (bytes in/out).
    """
    html_text = html_bytes.decode('utf-8', errors='replace')
    soup = BeautifulSoup(html_text, 'html.parser')

    for element in soup.find_all(text=True):
        text = element.strip()
        if not text:
            continue
        element.replace_with(remove_target_language_from_text(text, lang_to_remove))

    return str(soup).encode('utf-8')

# -------------------------------
# Parallel EPUB processing
# -------------------------------

def process_item_content_return(file_name, html_bytes, lang_to_remove):
    """Worker function for ThreadPoolExecutor"""
    try:
        cleaned_bytes = clean_html_remove_language_bytes(html_bytes, lang_to_remove)
        return (file_name, cleaned_bytes, None)
    except Exception as e:
        return (file_name, None, str(e))

def remove_language_sentences_from_epub_parallel(input_epub, output_epub, lang_to_remove="es", max_workers=4):
    """
    Remove all sentences/fragments in the specified language from EPUB.
    """
    print(f"📘 Reading: {input_epub}")
    book = epub.read_epub(input_epub)

    # Separate XHTML items and others
    xhtml_items = [i for i in book.get_items() if getattr(i, "media_type", "") == "application/xhtml+xml"]
    other_items = [i for i in book.get_items() if getattr(i, "media_type", "") != "application/xhtml+xml"]

    print(f"🧠 Removing '{lang_to_remove}' fragments from {len(xhtml_items)} chapters using {max_workers} threads...")

    cleaned_map = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item_content_return, item.file_name, item.get_body_content(), lang_to_remove): item for item in xhtml_items}
        for future in as_completed(futures):
            file_name, cleaned_bytes, err = future.result()
            if cleaned_bytes:
                cleaned_map[file_name] = cleaned_bytes
            elif err:
                print(f"⚠️ {file_name}: {err}")

    # Build new EPUB
    new_book = epub.EpubBook()
    for meta_tag in ["identifier", "title", "language"]:
        md = book.get_metadata("DC", meta_tag)
        if md:
            getattr(new_book, f"set_{meta_tag}")(md[0][0])
    for author in book.get_metadata("DC", "creator"):
        new_book.add_author(author[0])

    # Update XHTML items with cleaned content
    for item in xhtml_items:
        if item.file_name in cleaned_map:
            item.set_content(cleaned_map[item.file_name])
        new_book.add_item(item)
    for item in other_items:
        new_book.add_item(item)

    # Preserve structure
    new_book.toc = book.toc
    new_book.spine = book.spine
    new_book.add_item(epub.EpubNcx())
    new_book.add_item(epub.EpubNav())

    epub.write_epub(output_epub, new_book)
    print(f"✅ Cleaned EPUB saved to: {output_epub}")

# -------------------------------
# Example usage
# -------------------------------

if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\Reincarnated into Modern Family"
    input_file = os.path.join(file_root, "input.epub")
    output_file = os.path.join(file_root, "output.epub")
    language_to_remove="es" # <--- change this code ('es', 'fr', 'de', 'it', etc.)
    max_workers = 8
    remove_language_sentences_from_epub_parallel(input_file, output_file, language_to_remove, max_workers)
