#!/usr/bin/env python3
"""
pin_processor.py: Process all component PIN blocks from input file, merge and clean descriptions.
"""

import sys
import re
import os


def process_pin_file(input_filepath, output_filepath=None, remove_duplicates=True):
    """Reads input file, processes all PIN blocks, and writes result."""
    
    if output_filepath and os.path.exists(output_filepath):
        os.remove(output_filepath)
    
    with open(input_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all pin blocks - pin name can contain any characters except '>>>'
    block_pattern = r'<<<([^_]+)_([^>]+?)>>> START\s+<<<NAME>>> = (.*?)\s+<<<\1_\2_DATASHEET>>> START\s+(.*?)\s+<<<\1_\2_DATASHEET>>> END\s+<<<\1_\2>>> END'
    matches = re.findall(block_pattern, content, re.DOTALL)
    
    pin_data = {}
    
    for component_name, pin_id, name, description in matches:
        if not description.strip() or description.strip() == "NO_DATA":
            continue
        
        key = (component_name, pin_id)
        
        if key not in pin_data:
            pin_data[key] = {'name': name.strip(), 'descriptions': []}
        
        pin_data[key]['descriptions'].append(description.strip())
    
    all_output_blocks = []
    
    for (component_name, pin_id), data in pin_data.items():
        merged_description = '\n\n'.join(data['descriptions'])
        
        if remove_duplicates:
            lines = merged_description.split('\n')
            unique_lines = []
            seen = set()
            
            for line in lines:
                if line not in seen:
                    unique_lines.append(line)
                    seen.add(line)
            
            merged_description = '\n'.join(unique_lines)
        
        # Remove blank lines
        lines = merged_description.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        merged_description = '\n'.join(non_empty_lines)
        
        block = f"<<<{component_name}_{pin_id}>>> START\n[NAME] = {data['name']}\n[DATASHEET] START\n{merged_description}\n[DATASHEET] END\n<<<{component_name}_{pin_id}>>> END"
        all_output_blocks.append(block)
    
    output_content = '\n\n'.join(all_output_blocks)
    
    if output_filepath:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(output_content)
    else:
        print(output_content)
    
    # Minimal output
    print(f"[3_pin_processor.py] Processed pins: {len(all_output_blocks)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pin_processor.py <input_file> [output_file] [remove_duplicates]")
        print("remove_duplicates: 0 or 1 (default: 1)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    remove_duplicates = True
    
    if len(sys.argv) > 3:
        remove_duplicates = sys.argv[3] == '1'
    
    process_pin_file(input_file, output_file, remove_duplicates)