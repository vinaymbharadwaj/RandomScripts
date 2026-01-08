#!/usr/bin/env python3
"""
fix_epub_punct_parallel.py

Parallel EPUB punctuation fixer.

Creates: input_fixed.epub

Requirements:
    pip install beautifulsoup4 lxml
"""
from __future__ import annotations
import sys
import zipfile
import io
import re
import argparse
import os
from typing import Tuple, List, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

# --- Normalization rules (same as before) ---
PUNCT_REPLACEMENTS = [
    # curly quotes -> straight
    (r'[\u201C\u201D\u201F]', '"'),   # left/right double curly quotes, double low-9
    (r'[\u2018\u2019\u201B]', "'"),   # left/right single quotes, single low-9
    # ellipsis
    (r'\u2026', '...'),
    # full-width punctuation (common CJK) -> ascii
    ('，', ','),
    ('。', '.'),
    ('：', ':'),
    ('；', ';'),
    ('！', '!'),
    ('？', '?'),
    ('（', '('),
    ('）', ')'),
    ('【', '['),
    ('】', ']'),
    ('「', '"'),
    ('」', '"'),
    ('『', '"'),
    ('』', '"'),
    # non-breaking space -> regular
    (r'\u00A0', ' '),
]

def normalize_text(s: str) -> str:
    import re  # local import safe for process workers

    # apply direct replacements first
    for pat, repl in PUNCT_REPLACEMENTS:
        s = re.sub(pat, repl, s)

    # collapse repeated punctuation like "!!!" -> "!"
    s = re.sub(r'([!?.,;:])\1{1,}', r'\1', s)

    # normalize spaces: multiple -> single
    s = re.sub(r'[ \t\f\v]{2,}', ' ', s)

    # remove spaces before punctuation (e.g. "word , " -> "word,")
    s = re.sub(r'\s+([,.:;?!)\]\}])', r'\1', s)

    # ensure single space after .,!?;: when followed by a letter or quote or opening paren
    # (not end of line or punctuation)
    s = re.sub(r'([,.:;?!])([^\s"\'\)\]\}\.,:;?!])', r'\1 \2', s)

    # NEW: ensure a space after punctuation + closing quote when followed by a non-space
    # Fixes: "Okay!"Yellow -> "Okay!" Yellow
    # This only triggers when the quote is directly after punctuation, so
    # it does NOT affect contractions like don't, I'm, Bulbasaur's, etc.
    s = re.sub(r'(?<=[,.:;?!])(["\'])([^\s])', r'\1 \2', s)

    # fix spacing around quotes and parentheses:
    # no space between opening punctuation and a word: "( word" -> "(word"
    s = re.sub(r'([\(\[\{\u0022\u0027])\s+([^\s])', r'\1\2', s)
    # no space before closing punctuation: "word )" -> "word)"
    s = re.sub(r'([^\s])\s+([\)\]\}\u0022\u0027])', r'\1\2', s)

    # normalize em-dash spacing: put no surrounding spaces (option: change if you prefer spaces)
    s = re.sub(r'\s*—\s*', '—', s)   # keep em dash but unify spacing

    # trim trailing spaces on lines
    s = re.sub(r'[ \t]+(\n|$)', r'\1', s)

    return s

# --- HTML processing (worker) ---
def fix_html_bytes_worker(args: Tuple[str, bytes]) -> Tuple[str, bytes, str]:
    """
    Worker function to process a single HTML/XHTML/XML file contents.
    Returns (filename, new_bytes, error_message_or_empty).
    Runs in separate process.
    """
    filename, data = args
    try:
        # Local imports inside worker (safe for multiprocessing)
        from bs4 import BeautifulSoup, NavigableString, Comment, XMLParsedAsHTMLWarning
        import warnings

        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

        # parse content (try lxml then fallback to html.parser)
        try:
            soup = BeautifulSoup(data, features='lxml')
        except Exception:
            soup = BeautifulSoup(data, features='html.parser')

        def is_visible_text(node):
            if isinstance(node, Comment):
                return False
            parent = node.parent
            if parent is None:
                return True
            name = parent.name
            if name in ('script', 'style', 'noscript'):
                return False
            # skip code-like blocks
            if name in ('code', 'pre', 'samp', 'kbd'):
                return False
            return True

        modified = False
        for node in soup.find_all(string=True):
            if not isinstance(node, NavigableString):
                continue
            if not is_visible_text(node):
                continue
            text = str(node)
            new_text = normalize_text(text)
            if new_text != text:
                node.replace_with(new_text)
                modified = True

        # If modified, return encoded bytes; otherwise return original data to avoid unnecessary changes
        if modified:
            out = soup.encode(formatter='html')
            return (filename, out, "")
        else:
            return (filename, data, "")
    except Exception as e:
        return (filename, data, f"ERROR: {e}")

# --- EPUB processing (main) ---
def process_epub_parallel(input_path: str, output_path: str, workers: int | None = None):
    # Collect entries
    html_exts = ('.xhtml', '.html', '.htm', '.xml')
    entries_to_process: List[Tuple[str, bytes]] = []
    entries_copy: List[zipfile.ZipInfo] = []
    orig_infos: Dict[str, zipfile.ZipInfo] = {}

    with zipfile.ZipFile(input_path, 'r') as zin:
        infolist = zin.infolist()
        for info in infolist:
            orig_infos[info.filename] = info
            lower = info.filename.lower()
            data = zin.read(info.filename)
            if lower.endswith(html_exts):
                entries_to_process.append((info.filename, data))
            else:
                entries_copy.append(info)  # will read data again later from zin

        # We'll process HTML entries in parallel
        processed_map: Dict[str, bytes] = {}
        errors: Dict[str, str] = {}

        if entries_to_process:
            max_workers = workers or os.cpu_count() or 2
            print(f"Processing {len(entries_to_process)} HTML/XML files with {max_workers} worker(s)...")
            # Submit tasks in chunks to avoid overwhelming memory if there are thousands of files
            # But ProcessPoolExecutor handles queueing; we still feed all tasks
            with ProcessPoolExecutor(max_workers=max_workers) as exe:
                future_to_name = {exe.submit(fix_html_bytes_worker, entry): entry[0] for entry in entries_to_process}
                for fut in as_completed(future_to_name):
                    name = future_to_name[fut]
                    try:
                        fname, newdata, err = fut.result()
                        processed_map[fname] = newdata
                        if err:
                            errors[fname] = err
                            print(f"Warning for {fname}: {err}")
                    except Exception as e:
                        # Shouldn't usually happen; record and keep original data
                        errors[name] = str(e)
                        print(f"Worker failed for {name}: {e}")
        else:
            print("No HTML/XML files found to process.")

        # Write output EPUB
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            # We need to iterate original infolist order to preserve spine and mimetype location if present
            for info in infolist:
                fname = info.filename
                if fname in processed_map:
                    # write processed content with original ZipInfo to preserve metadata
                    try:
                        zout.writestr(info, processed_map[fname])
                    except Exception:
                        # fallback: write bytes without ZipInfo
                        zout.writestr(fname, processed_map[fname])
                else:
                    # copy original raw bytes
                    data = zin.read(fname)
                    try:
                        zout.writestr(info, data)
                    except Exception:
                        zout.writestr(fname, data)

    # Summary
    total = len(infolist)
    changed = sum(1 for n, d in processed_map.items() if orig_infos.get(n) and len(d) != orig_infos[n].file_size)
    print(f"Done. Files in EPUB: {total}. HTML/XML processed: {len(processed_map)}. Files with changed size (approx): {changed}.")
    if errors:
        print(f"Warnings/errors for {len(errors)} file(s). Example: {next(iter(errors.items()))}")

# --- CLI ---
def main(argv):
    file_root = "C:\\DATA\\Novels\\Detective Conan - Found Ai Haibara and pursued by Akako"
    input_path = os.path.join(file_root, "input.epub")
    workers = 8

    if not os.path.isfile(input_path):
        print("Input file not found.")
        return 2
    if not input_path.lower().endswith('.epub'):
        print("Input should be an .epub file.")
        return 2

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_fixed.epub"
    
    print(f"Reading: {input_path}\nWriting: {output_path}")
    
    # On Windows: ProcessPoolExecutor requires main guard (we are inside it)
    process_epub_parallel(input_path, output_path, workers)
    print("Finished.")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
