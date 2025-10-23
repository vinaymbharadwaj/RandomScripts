import os
import re

# digit and unit maps
CH_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
             "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
LOW_UNITS = {"十": 10, "百": 100, "千": 1000}
BIG_UNITS = {"万": 10**4, "亿": 10**8}

# match only numbers appearing between "CHAPTER" and ":"
TARGET_PATTERN = re.compile(r"(CHAPTER\s*)([0-9零〇一二两三四五六七八九十百千万亿点负-]+)(:)")

def mixed_chinese_arabic_to_number(s: str):
    """Convert a mixed string of Arabic digits + Chinese numerals to a numeric value."""
    if not s:
        return None
    s = s.strip()
    neg = False
    if s.startswith('负') or s.startswith('-'):
        neg = True
        s = s[1:]

    # split integer and fractional parts
    if '点' in s:
        int_part, frac_part = s.split('点', 1)
    else:
        int_part, frac_part = s, ''

    def parse_integer_part(p: str):
        if p == '':
            return 0
        total = 0
        section = 0
        number = 0
        i = 0
        n = len(p)
        while i < n:
            ch = p[i]
            # Arabic multi-digit sequence
            if ch.isdigit():
                j = i
                while j < n and p[j].isdigit():
                    j += 1
                number = int(p[i:j])
                i = j
                continue
            # Chinese digit
            if ch in CH_DIGITS:
                number = CH_DIGITS[ch]
                i += 1
                continue
            # low unit
            if ch in LOW_UNITS:
                unit_value = LOW_UNITS[ch]
                if number == 0:
                    number = 1
                section += number * unit_value
                number = 0
                i += 1
                continue
            # big unit
            if ch in BIG_UNITS:
                unit_value = BIG_UNITS[ch]
                section += number
                if section == 0:
                    section = 1
                total += section * unit_value
                section = 0
                number = 0
                i += 1
                continue
            # zero
            if ch == '零':
                number = 0
                i += 1
                continue
            i += 1
        section += number
        total += section
        return total

    int_val = parse_integer_part(int_part)
    if int_val is None:
        return None

    if frac_part:
        frac_digits = []
        for ch in frac_part:
            if ch.isdigit():
                frac_digits.append(ch)
            elif ch in CH_DIGITS:
                frac_digits.append(str(CH_DIGITS[ch]))
            else:
                break
        if frac_digits:
            value = float(f"{int_val}.{''.join(frac_digits)}")
        else:
            value = float(int_val)
    else:
        value = int_val

    if neg:
        value = -value
    return value


def replace_chapter_numbers(text: str) -> str:
    """Replace only the numbers following 'CHAPTER' and before ':'."""

    def repl(m):
        prefix, num_token, suffix = m.groups()
        val = mixed_chinese_arabic_to_number(num_token)
        if val is None:
            return m.group(0)
        if isinstance(val, float) and val.is_integer():
            val = int(val)
        return f"{prefix}{val}{suffix}"

    return TARGET_PATTERN.sub(repl, text)


def process_file(in_path: str, out_path: str, encoding="utf-8"):
    with open(in_path, "r", encoding=encoding) as f:
        content = f.read()
    new_content = replace_chapter_numbers(content)
    with open(out_path, "w", encoding=encoding) as f:
        f.write(new_content)
    print(f"Saved: {out_path}")


# Example usage
if __name__ == "__main__":
    file_root = "C:\\DATA\\Novels\\Conan's Sin Value System"
    input_file = os.path.join(file_root, "input.txt")
    output_file = os.path.join(file_root, "output.txt")
    process_file(input_file, output_file)