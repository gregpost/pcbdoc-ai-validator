# remove_nets.py
# Remove all Net-prefixed nodes from serial/parallel chain description

import re
import sys

def remove_net_nodes(text):
    # Remove Net-prefixed nodes with following hyphen
    text = re.sub(r'Net\w+-', '', text)
    # Remove Net-prefixed nodes with preceding hyphen
    text = re.sub(r'-Net\w+', '', text)
    # Remove standalone Net-prefixed nodes
    text = re.sub(r'Net\w+', '', text)
    # Clean up multiple hyphens
    text = re.sub(r'-+', '-', text)
    # Clean up empty parentheses
    text = re.sub(r'\(\s*\)', '', text)
    return text

def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    cleaned = remove_net_nodes(content)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned)

if __name__ == "__main__":
    main()