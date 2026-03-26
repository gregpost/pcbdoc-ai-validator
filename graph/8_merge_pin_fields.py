#!/usr/bin/env python3
# merge_pin_fields.py - Merge additional pin data into main pin data file with optional tagging

"""
Usage:
    merge_pin_fields.py <INPUT_PIN_DATA_FILE> <INPUT_ADDITIONAL_PIN_DATA_FILE> \
        <OUTPUT_COMBINED_PIN_DATA_FILE> [TAG_NAME]
    
Example:
    merge_pin_fields.py pins.txt extra.txt combined.txt
    merge_pin_fields.py pins.txt extra.txt combined.txt SOME_TAG_NAME
"""

import sys
import re

def parse_pin_file(filename):
    """Parse file into dict: pin_name -> content_lines"""
    with open(filename, 'r') as f:
        content = f.read()
    
    pattern = r'<<<(.+?)>>> START\n(.*?)\n<<<.+?>>> END'
    matches = re.findall(pattern, content, re.DOTALL)
    return {pin: lines.strip() for pin, lines in matches}

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    additional_file = sys.argv[2]
    output_file = sys.argv[3]
    tag_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    main_data = parse_pin_file(input_file)
    additional_data = parse_pin_file(additional_file)
    
    with open(input_file, 'r') as f:
        original_content = f.read()
    
    result_content = original_content
    
    for pin_name, main_text in main_data.items():
        if pin_name in additional_data:
            additional_text = additional_data[pin_name]
            
            if tag_name:
                insert_text = f"[{tag_name}] START\n{additional_text}\n[{tag_name}] END"
            else:
                insert_text = additional_text
            
            # Find the END tag position and insert before it
            end_pattern = f'<<<{pin_name}>>> END'
            result_content = result_content.replace(
                end_pattern,
                f"{insert_text}\n{end_pattern}"
            )
        else:
            # Remove pin block if not in additional file
            block_pattern = rf'<<<{pin_name}>>> START\n.*?\n<<<{pin_name}>>> END'
            result_content = re.sub(block_pattern, '', result_content, flags=re.DOTALL)
    
    # Clean up extra newlines
    result_content = re.sub(r'\n\s*\n+', '\n\n', result_content).strip()
    
    with open(output_file, 'w') as f:
        f.write(result_content)

if __name__ == '__main__':
    main()