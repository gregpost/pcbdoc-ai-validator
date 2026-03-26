#!/usr/bin/env python3
# rmlines2.py

import sys

BLACKLIST = [
    "RECORD=Arc",
    "RECORD=Track",
    "RECORD=Connection",
    "RECORD=Via",
    "RECORD=Region",
    "RECORD=ComponentBody",
    "RECORD=Board",
]


def line_matches(line: str) -> bool:
    for banned in BLACKLIST:
        if banned in line:
            return False
    return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python filter_pcb.py INPUT_FILE OUTPUT_FILE")
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