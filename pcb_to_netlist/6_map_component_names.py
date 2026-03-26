# map_component_names.py      Replace component IDs with designators in nets

import sys

def load_component_map(pcb_file):
    comp_map = {}
    with open(pcb_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('RECORD=Component'):
                continue
            parts = line.split('|')
            comp_id, designator = None, None
            for part in parts:
                if part.startswith('ID='):
                    comp_id = part.split('=')[1]
                elif part.startswith('SOURCEDESIGNATOR='):
                    designator = part.split('=')[1]
            if comp_id and designator:
                comp_map[comp_id] = designator
    return comp_map

def map_nets(nets_file, output_file, comp_map):
    with open(nets_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            line = line.strip()
            if not line or not line.startswith('NET'):
                continue
            net_part, comps_part = line.split(':', 1)
            mapped_comps = []
            for comp in comps_part.split(','):
                comp = comp.strip()
                if '_' not in comp:
                    continue
                comp_id, pin = comp.split('_', 1)
                designator = comp_map.get(comp_id, comp_id)
                mapped_comps.append(f"{designator}_{pin}")
            f_out.write(f"{net_part}:{','.join(mapped_comps)}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python map_component_names.py PCB_FILE NETS_FILE OUTPUT_FILE")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    nets_file = sys.argv[2]
    output_file = sys.argv[3]
    
    comp_map = load_component_map(pcb_file)
    map_nets(nets_file, output_file, comp_map)