def remove_duplicate_consecutive_lines(filename):
    """
    Reads a text file, removes the second line if it's an exact duplicate of
    the one before it (ignoring trailing punctuation), and writes the changes
    to a new file.

    Args:
        filename (str): The name of the input text file.
    """
    try:
        # Specify 'utf-8' encoding to handle Chinese characters.
        with open(filename, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return

    new_lines = []
    i = 0
    while i < len(lines):
        current_line = lines[i].strip()
        new_lines.append(lines[i])

        # Check for the next line and if it's a duplicate.
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()

            # Remove trailing punctuation for comparison.
            # The punctuation set can be expanded to include common Chinese punctuation marks.
            # Here we'll just use a small set for demonstration.
            punctuation_to_ignore = '.,!?;:"\'。，！？；：“”‘’'
            current_clean = current_line.rstrip(punctuation_to_ignore)
            next_clean = next_line.rstrip(punctuation_to_ignore)

            if current_clean == next_clean:
                # If they are duplicates, skip the next line.
                i += 2
                continue
        i += 1

    # Write the modified content to a new file, also with 'utf-8' encoding.
    output_filename = filename.replace('.txt', '_modified.txt')
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        outfile.writelines(new_lines)

    print(f"Duplicate consecutive lines have been removed. The modified content is saved to '{output_filename}'.")


# Run the function on the sample file.
remove_duplicate_consecutive_lines('C:\\DATA\\Novels\\Traveling with Sirona from Sinnoh\\Traveling With Sirona From Sinnoh.txt')