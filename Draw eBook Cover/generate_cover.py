from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def generate_cover(title, author=None, output_path='cover.jpg'):
    # Image size (standard 6x9 inches at 300 DPI)
    width, height = 1800, 2700
    background_color = (0, 0, 0)      # Black
    title_color = (255, 255, 255)     # White
    author_color = (173, 216, 230)    # Light Blue

    # Create the image
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        title_font = ImageFont.truetype("trebuc.ttf", 100)
        author_font = ImageFont.truetype("trebuc.ttf", 50)
    except IOError:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Wrap title text
    wrapped_title = textwrap.fill(title.upper(), width=15)

    # Calculate text bounding box for title
    title_bbox = draw.textbbox((0, 0), wrapped_title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]

    title_x = (width - title_width) / 2
    title_y = height * 0.3
    draw.text((title_x, title_y), wrapped_title, font=title_font, fill=title_color)

    # Draw author name
    if author:
        author_text = f"by {author}"
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        author_height = author_bbox[3] - author_bbox[1]

        author_x = (width - author_width) / 2
        author_y = title_y + title_height + 100
        draw.text((author_x, author_y), author_text, font=author_font, fill=author_color)

    # Save the image
    img.save(output_path)
    print(f"Cover saved to {output_path}")

# Example usage:
generate_cover("The Forgotten Realm", author="Jane Doe")
