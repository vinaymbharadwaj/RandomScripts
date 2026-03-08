import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import sys

def get_flat_toc(book):
    """
    Helper to flatten the Table of Contents into a simple list of Link objects.
    EbookLib stores TOC as a nested tree (tuples and lists), so we need to flatten it
    to match them up linearly.
    """
    flat_toc = []
    
    def recursive_extract(toc_item):
        if isinstance(toc_item, (list, tuple)):
            for item in toc_item:
                recursive_extract(item)
        elif isinstance(toc_item, epub.Link):
            flat_toc.append(toc_item)
        elif isinstance(toc_item, epub.Section):
            # If there are sections, we might want to capture them or dive deeper
            # For this specific request, we usually just want the links inside
            recursive_extract(toc_item.href) # Recursion logic depends on structure
            # Simplify: assume standard Link objects for chapters
            pass

    # Basic flattening for standard TOC structures
    for item in book.toc:
        if isinstance(item, epub.Link):
            flat_toc.append(item)
        elif isinstance(item, (list, tuple)):
            # This handles nested chapters or sections
            for sub_item in item:
                if isinstance(sub_item, epub.Link):
                    flat_toc.append(sub_item)
    
    return flat_toc

def update_chapter_content(content_bytes, new_title):
    """
    Parses HTML, finds the first <h1>, and replaces its text.
    """
    soup = BeautifulSoup(content_bytes, 'html.parser')
    
    # Find the first H1 tag
    h1 = soup.find('h1')
    
    if h1:
        # Replace the text of the h1 tag
        h1.string = new_title
    else:
        # If no h1 exists, you might want to prepend one or log a warning
        # For now, we assume the user's description is accurate (headers exist)
        print(f"Warning: No <h1> tag found for chapter '{new_title}'. Skipping header update.")

    return str(soup).encode('utf-8')

def main(target_file, source_file, output_file):
    print(f"Loading Source (Titles): {source_file}")
    book_source = epub.read_epub(source_file)
    
    print(f"Loading Target (To be updated): {target_file}")
    book_target = epub.read_epub(target_file)

    # 1. Extract titles from Source Book
    source_toc = get_flat_toc(book_source)
    source_titles = [link.title for link in source_toc]
    
    print(f"Found {len(source_titles)} chapters in Source.")

    # 2. Get Target Book TOC
    target_toc = get_flat_toc(book_target)
    
    if len(source_titles) != len(target_toc):
        print("WARNING: Chapter counts do not match!")
        print(f"Source: {len(source_titles)} vs Target: {len(target_toc)}")
        print("Proceeding with the minimum length of the two...")

    # 3. Iterate and Update
    # We zip them to pair the first chapter of A with the first of B, etc.
    count = 0
    for target_link, new_title in zip(target_toc, source_titles):
        # Update the Title in the Table of Contents object
        target_link.title = new_title
        
        # Find the actual item (HTML file) in the book using the href
        # target_link.href often looks like 'chapter1.html#fragment', we need just 'chapter1.html'
        href_clean = target_link.href.split('#')[0]
        item = book_target.get_item_with_href(href_clean)
        
        if item:
            # Update the <h1> inside the file
            original_content = item.get_content()
            updated_content = update_chapter_content(original_content, new_title)
            item.set_content(updated_content)
            count += 1
        else:
            print(f"Could not find file for {target_link.title}")

    # 4. Refresh the NCX and NAV files (The system files for Table of Contents)
    # EbookLib requires us to explicitly add these back to update the structure
    book_target.add_item(epub.EpubNcx())
    book_target.add_item(epub.EpubNav())

    # 5. Save the new file
    print(f"Updated {count} chapters.")
    print(f"Saving to {output_file}...")
    epub.write_epub(output_file, book_target, {})
    print("Done!")

if __name__ == "__main__":
    # CONFIGURATION
    # Replace these filenames with your actual files
    FILE_ROOT = "C:\\DATA\\Novels\\Genshin Impact - Starting from Liyue to Build Infrastructure"
    BOOK_WITH_BAD_NAMES =  os.path.join(FILE_ROOT, "Genshin Impact - Starting from Liyue to Build Infrastructure (Webnovel).epub")
    BOOK_WITH_GOOD_NAMES = os.path.join(FILE_ROOT, "Genshin Impact - Starting from Liyue to Build Infrastructure (TRXS).epub")
    OUTPUT_FILENAME = os.path.join(FILE_ROOT, "book_updated.epub")

    main(BOOK_WITH_BAD_NAMES, BOOK_WITH_GOOD_NAMES, OUTPUT_FILENAME)