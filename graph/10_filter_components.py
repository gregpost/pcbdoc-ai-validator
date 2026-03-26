#!/usr/bin/env python3
# filter_components.py - Filter strings with exactly one underscore, skip left part before colon, remove right equals left

import sys

def usage():
    print("Usage: filter_components.py <INPUT_PARSED_CIRCUIT_PATH> <OUTPUT_FILTERED_CIRCUIT_PATH>")
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        usage()
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        sys.exit(f"Error: Input file '{input_path}' not found")
    
    output_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Split by colon, keep left part as prefix
        if ':' in line:
            prefix, rest = line.split(':', 1)
            # Process right side only
            substrings = [s.strip() for s in rest.split(',') if s.strip()]
        else:
            prefix = None
            substrings = [s.strip() for s in line.split(',') if s.strip()]
        
        # Filter substrings with exactly one underscore
        filtered = [s for s in substrings if s.count('_') == 1]
        
        # Remove substrings equal to prefix (if prefix exists)
        if prefix is not None:
            filtered = [s for s in filtered if s != prefix]
        
        # Build output line
        if prefix is not None:
            output_lines.append(f"{prefix}:{','.join(filtered)}")
        else:
            output_lines.append(','.join(filtered))
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(output_lines))

if __name__ == "__main__":
    main()