# rmlines.py

import sys

SUBSTRINGS = [
    "NET=",
    "COMPONENT=",
    "SOURCEDESIGNATOR=",
    "ID=",
    "NAME=",
    "SOURCELIBREFERENCE=",
    "COMMENT="
]


def line_matches(line: str) -> bool:
    return any(substring in line for substring in SUBSTRINGS)


def main():
    if len(sys.argv) != 3:
        print("Usage: python pcbdoc_filter.py INPUT_FILE OUTPUT_FILE")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, "r", encoding="utf-8", errors="ignore") as infile:
        with open(output_file, "w", encoding="utf-8") as outfile:
            for line in infile:
                if line_matches(line):
                    outfile.write(line)


if __name__ == "__main__":
    main()