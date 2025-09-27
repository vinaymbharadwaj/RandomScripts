from deep_translator import GoogleTranslator

def translate_file(input_file, output_file):
    # Read the input Chinese text
    with open(input_file, 'r', encoding='utf-8') as f:
        chinese_text = f.read()

    # Translate text to English
    translated_text = GoogleTranslator(source='zh-CN', target='en').translate(chinese_text)

    # Save the translated text to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    print(f"Translation saved to {output_file}")

# Example usage
input_file = "C:\\DATA\\Novels\\Pokémon development strategy\\Test\\Pokémon development strategy.txt"
output_file = "C:\\DATA\\Novels\\Pokémon development strategy\\Test\\Pokémon development strategy (translated).txt"
translate_file(input_file, output_file)
