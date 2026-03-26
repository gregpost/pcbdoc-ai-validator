#!/usr/bin/env python3
# run_pipeline.py      Run eight Python utilities sequentially to generate schematic.txt from PCB path

import subprocess
import sys
import os

def main():
    if len(sys.argv) != 3:
        print("Usage: python run_pipeline.py <PcbPath> <PcbToSchematicsPath>")
        sys.exit(1)
    
    pcb_path = sys.argv[1]
    pcb_to_schematics_path = sys.argv[2]
    
    # Fixed paths
    convert_to_utf8_path = f"{pcb_to_schematics_path}/1_convert_to_utf8.txt"
    pcb_doc_filter_path = f"{pcb_to_schematics_path}/2_pcb_doc_filter.txt"
    rm_lines_path = f"{pcb_to_schematics_path}/3_rmlines.txt"
    rm_lines2_path = f"{pcb_to_schematics_path}/4_rmlines2.txt"
    parse_nets_path = f"{pcb_to_schematics_path}/5_parse_nets.txt"
    map_component_names_path = f"{pcb_to_schematics_path}/6_map_component_names.txt"
    map_net_names_path = f"{pcb_to_schematics_path}/7_map_net_names.txt"
    resolve_chips_path = f"{pcb_to_schematics_path}/8_resolve_chips.txt"
    
    # Check if Python is available
    try:
        subprocess.run(["python", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Python not found in PATH")
        sys.exit(1)
    
    # Verify input file exists
    if not os.path.exists(pcb_path):
        print(f"Error: Input file '{pcb_path}' not found")
        sys.exit(1)
    
    steps = [
        ("Step 1: ConvertToUTF8", ["python", "../pcb_to_schematics/1_convert_to_utf8.py", pcb_path, convert_to_utf8_path]),
        ("Step 2: PcbDocFilter", ["python", "../pcb_to_schematics/2_pcbdoc_filter.py", convert_to_utf8_path, pcb_doc_filter_path]),
        ("Step 3: RmLines", ["python", "../pcb_to_schematics/3_rmlines.py", pcb_doc_filter_path, rm_lines_path]),
        ("Step 4: RmLines2", ["python", "../pcb_to_schematics/4_rmlines2.py", rm_lines_path, rm_lines2_path]),
        ("Step 5: ParseNets", ["python", "../pcb_to_schematics/5_parse_nets.py", rm_lines2_path, parse_nets_path]),
        ("Step 5: MapComponentNames", ["python", "../pcb_to_schematics/6_map_component_names.py", rm_lines2_path, parse_nets_path, map_component_names_path]),
        ("Step 6: MapNetNames", ["python", "../pcb_to_schematics/7_map_net_names.py", rm_lines2_path, map_component_names_path, map_net_names_path]),
        ("Step 7: ResolveChips", ["python", "../pcb_to_schematics/8_resolve_chips.py", rm_lines2_path, map_net_names_path, resolve_chips_path])
    ]
    
    for step_name, cmd in steps:
        print(step_name)
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(result.returncode)
    
    print(f"Pipeline finished. Output: '{resolve_chips_path}'")

if __name__ == "__main__":
    main()
