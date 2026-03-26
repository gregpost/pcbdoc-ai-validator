#!/usr/bin/env python3
# circuit_parser.py - Replace newlines, parentheses, and dashes with commas; extract tagged sections
# Usage: python circuit_parser.py <CIRCUIT_FILE> <PARSED_FILE>

import sys
import re

def main():
    if len(sys.argv) != 3:
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Find all tagged sections
    pattern = r'<<<(\w+)>>> START\n(.*?)<<<\1>>> END'
    matches = re.findall(pattern, content, re.DOTALL)
    
    results = []
    for tag, block in matches:
        # Remove all whitespace
        block = re.sub(r'\s+', '', block)
        # Replace target characters with comma
        for char in '\n()-':
            block = block.replace(char, ',')
        # Remove multiple commas
        block = re.sub(r',+', ',', block)
        # Strip leading/trailing commas
        block = block.strip(',')
        results.append(f"{tag}:{block}")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(results))

if __name__ == "__main__":
    main()