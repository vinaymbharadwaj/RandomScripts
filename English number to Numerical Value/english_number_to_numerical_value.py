import re
from word2number import w2n

def replace_words_with_numbers(text):
    # Regex matches sequences of number words (but NOT spaces)
    pattern = re.compile(r'\b(?:(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|'
                         r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|'
                         r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|'
                         r'eighty|ninety|hundred|thousand|million|billion|and)(?:[- ]))*'
                         r'(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|'
                         r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|'
                         r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|'
                         r'eighty|ninety|hundred|thousand|million|billion)\b',
                         re.IGNORECASE)

    def convert(match):
        phrase = match.group(0)
        try:
            return str(w2n.word_to_num(phrase))
        except ValueError:
            return phrase  # leave unchanged if not a valid number phrase

    return pattern.sub(convert, text)


def process_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    replaced_text = replace_words_with_numbers(text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(replaced_text)


# Example usage
input_file = "input.txt"
output_file = "output.txt"
process_file(input_file, output_file)
print("Replacement complete! Check", output_file)
