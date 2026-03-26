# pdf_to_md.py
# Convert single PDF to Markdown via pdf2markdown4llm, filter lines by minimum length

import sys  # argv
from pdf2markdown4llm import PDF2Markdown4LLM  # PDF2Markdown4LLM

# Минимальная длина строки в даташите (нужно, чтобы удалить мусорные строки)
DEFAULT_MIN_LENGTH = 10

def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    min_length = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_MIN_LENGTH

    print(f"Processing: {input_path} -> {output_path}")

    converter = PDF2Markdown4LLM(
        remove_headers=False,
        skip_empty_tables=True,
        table_header="### Table"
    )

    md = converter.convert(input_path)

    lines = md.splitlines(keepends=True)
    filtered_lines = [line for line in lines if len(line.rstrip('\n')) >= min_length]

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(filtered_lines)


if __name__ == "__main__":
    main()