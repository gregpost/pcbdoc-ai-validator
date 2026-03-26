#!/usr/bin/env python3
# file: text_appender.py
# Appends content from input file to output file with tags

import sys

INPUT_FILE = sys.argv[2]
OUTPUT_FILE = sys.argv[3]

def main():
    if len(sys.argv) < 2:
        print("Usage: python text_appender.py <PIN_NAME> [INPUT_FILE] [OUTPUT_FILE]")
        return
    
    pin_name = sys.argv[1]
    
    try:
        with open(INPUT_FILE, "r") as in_file:
            content = in_file.read()
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found")
        return
    
    with open(OUTPUT_FILE, "a") as out_file:
        out_file.write(f"\n<<<{pin_name}>>> START\n")
        out_file.write(content)
        if not content.endswith('\n'):
            out_file.write('\n')
        out_file.write(f"<<<{pin_name}>>> END\n")

if __name__ == "__main__":
    main()