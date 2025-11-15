import sys
import re
import os # Added os for path handling
from ebooklib import epub, ITEM_DOCUMENT
from collections import namedtuple

# Define a named tuple to easily store chapter data
# Updated: 'title' replaced with 'filename'
ChapterData = namedtuple('ChapterData', ['number', 'filename', 'char_count'])

def strip_html(content):
    """
    Strips HTML tags from a string and replaces newlines/extra spaces.
    
    Args:
        content (bytes): The raw content bytes, often XHTML.
        
    Returns:
        str: Clean text content.
    """
    try:
        text = content.decode('utf-8')
    except AttributeError:
        # If content is already a string
        text = content

    # 1. Remove script and style tags
    text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style\b[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. Normalize whitespace (remove newlines, tabs, and reduce multiple spaces to one)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def analyze_epub(filepath):
    """
    Analyzes an EPUB file to extract XHTML file names and character counts,
    and writes the results to epub_data.txt in the same directory.
    
    Args:
        filepath (str): The path to the EPUB file.
    """
    try:
        # Load the book
        book = epub.read_epub(filepath)
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return
    except Exception as e:
        print(f"Error reading EPUB file: {e}")
        print("Please ensure the file is a valid EPUB and dependencies are installed.")
        return

    chapter_data = []
    chapter_number = 0
    output_lines = [] # List to store all lines for the output file

    # Iterate through all items in the book's spine (which defines reading order).
    for spine_item_tuple in book.spine:
        item_id = spine_item_tuple[0]
        
        # Use get_item_with_id() to retrieve the item object
        chapter = book.get_item_with_id(item_id)
        
        # We are typically interested in document (HTML/XHTML) content
        if chapter and chapter.get_type() == ITEM_DOCUMENT:
            # Increment chapter count only for document items
            chapter_number += 1
            
            # Get clean text and count characters
            content = chapter.content
            clean_text = strip_html(content)
            char_count = len(clean_text)
            
            # Retrieve the XHTML file name (href)
            file_name = chapter.file_name 

            chapter_data.append(ChapterData(chapter_number, file_name, char_count))

    # --- Output Table Generation ---
    if not chapter_data:
        output_lines.append("No readable chapters found in the EPUB file.")
    else:
        # Define the column widths for formatting
        COL_NUM_WIDTH = 10
        # Title width is now File Name width
        COL_FILENAME_WIDTH = 60 
        COL_COUNT_WIDTH = 20

        # Header
        header = (
            f"{'Chapter #':<{COL_NUM_WIDTH}} | "
            f"{'XHTML File Name':<{COL_FILENAME_WIDTH}} | " # <-- Updated column name
            f"{'Character Count':>{COL_COUNT_WIDTH}}"
        )
        separator = "-" * (COL_NUM_WIDTH + COL_FILENAME_WIDTH + COL_COUNT_WIDTH + 6)

        output_lines.append("--- EPUB Analysis Report ---")
        output_lines.append(header)
        output_lines.append(separator)

        # Data Rows
        for data in chapter_data:
            # Ensure file name is truncated if too long, and padded
            display_filename = data.filename[:COL_FILENAME_WIDTH].ljust(COL_FILENAME_WIDTH)
            
            row = (
                f"{data.number:<{COL_NUM_WIDTH}} | "
                f"{display_filename} | "
                f"{data.char_count:>{COL_COUNT_WIDTH},}" # Use comma for thousands separator
            )
            output_lines.append(row)
            
        output_lines.append(separator)
        output_lines.append(f"Total Chapters Analyzed: {len(chapter_data)}")
        
        total_chars = sum(d.char_count for d in chapter_data)
        output_lines.append(f"Total Characters in Book: {total_chars:,}")

    # --- Write to File ---
    output_filename = "epub_data.txt"
    # Get the directory of the input EPUB file
    output_dir = os.path.dirname(os.path.abspath(filepath))
    output_path = os.path.join(output_dir, output_filename)
    
    # Fallback to current directory if os.path.dirname returns empty (e.g., if filepath is just "book.epub")
    if not output_dir and os.path.isabs(filepath) == False:
        output_path = output_filename 

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"\nSuccessfully wrote analysis report to:\n{output_path}")
    except Exception as e:
        print(f"\nError writing output file to '{output_path}': {e}")


if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\Daily Drama"
    input_file = os.path.join(file_root, "Daily American Drama.epub")
    analyze_epub(input_file)