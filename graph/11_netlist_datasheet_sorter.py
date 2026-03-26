#!/usr/bin/env python3
"""
netlist_datasheet_sorter.py - Parse netlist and extract matching datasheet sections.

Usage: python netlist_datasheet_sorter.py <INPUT_NETLIST_PATH> <INPUT_DATASHEETS_PATH> \
       <OUTPUT_SORTED_DATASHEETS_PATH>

Example:
  python netlist_datasheet_sorter.py netlist.txt datasheets.txt output.txt
"""

import sys
import re
from pathlib import Path
from typing import Dict, List


def parse_netlist(netlist_path: str) -> List[List[str]]:
    """Read netlist file, return list of component pin groups."""
    with open(netlist_path, 'r') as f:
        groups = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                target, sources = line.split(':', 1)
                sources_list = [s.strip() for s in sources.split(',')]
                groups.append([target.strip()] + sources_list)
            else:
                groups.append([line])
    return groups


def parse_datasheets(datasheets_path: str) -> Dict[str, str]:
    """Extract all datasheet blocks into {tag: content} dictionary."""
    with open(datasheets_path, 'r') as f:
        content = f.read()
    
    pattern = r'<<<(.+?)>>> START\n(.*?)<<<\1>>> END'
    matches = re.findall(pattern, content, re.DOTALL)
    
    datasheets = {}
    for tag, block_content in matches:
        # Replace square brackets with curly brackets in the content
        converted_content = block_content.replace('[', '{').replace(']', '}')
        datasheets[tag] = converted_content.strip()
    return datasheets


def write_sorted_output(output_path: str, groups: List[List[str]], 
                        datasheets: Dict[str, str]) -> None:
    """Write sorted datasheets grouped by component pins."""
    with open(output_path, 'w') as f:
        for group in groups:
            target_pin = group[0]
            f.write(f'<<<{target_pin}>>> START\n')
            
            for component in group[1:]:
                if component in datasheets:
                    f.write(f'[{component}] START\n')
                    f.write(datasheets[component])
                    f.write(f'\n[{component}] END\n')
            
            f.write(f'<<<{target_pin}>>> END\n\n')


def main(input_netlist_path: str, input_datasheets_path: str, 
         output_sorted_path: str) -> None:
    """Main orchestration function."""
    groups = parse_netlist(input_netlist_path)
    datasheets = parse_datasheets(input_datasheets_path)
    write_sorted_output(output_sorted_path, groups, datasheets)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <INPUT_NETLIST_PATH> <INPUT_DATASHEETS_PATH> \
              <OUTPUT_SORTED_DATASHEETS_PATH>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])