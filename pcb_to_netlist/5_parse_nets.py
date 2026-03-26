# parse_nets.py      Extract net connections from PcbDoc to nets_raw.txt

import sys

def parse_nets(input_file, output_file):
    nets = {}
    with open(input_file, 'r') as f:
        for line in f:
            if not line.startswith('RECORD=Pad'):
                continue
            parts = line.split('|')
            net_id, comp_id, pin_name = None, None, None
            for part in parts:
                if part.startswith('NET='):
                    net_id = part.split('=')[1]
                elif part.startswith('COMPONENT='):
                    comp_id = part.split('=')[1]
                elif part.startswith('NAME='):
                    pin_name = part.split('=')[1]
            if net_id and comp_id and pin_name:
                nets.setdefault(net_id, []).append(f"{comp_id}_{pin_name}")
    
    with open(output_file, 'w') as f:
        for net_id, connections in nets.items():
            f.write(f"NET{net_id}:{','.join(connections)}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_nets.py INPUT_FILE OUTPUT_FILE")
        sys.exit(1)
    
    parse_nets(sys.argv[1], sys.argv[2])