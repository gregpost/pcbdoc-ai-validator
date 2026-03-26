# map_net_names.py      Replace NET IDs with names and sort

import sys

def load_net_map(pcb_file):
    net_map = {}
    with open(pcb_file, 'r') as f:
        for line in f:
            if not line.startswith('RECORD=Net'):
                continue
            parts = line.split('|')
            net_id, name = None, None
            for part in parts:
                if part.startswith('ID='):
                    net_id = part.split('=')[1]
                elif part.startswith('NAME='):
                    name = part.split('=')[1].strip()
            if net_id and name:
                net_map[net_id] = name
    return net_map

def map_nets(nets_file, output_file, net_map):
    nets = []
    with open(nets_file, 'r') as f_in:
        for line in f_in:
            if not line.startswith('NET'):
                continue
            net_part, connections = line.strip().split(':', 1)
            net_id = net_part[3:]
            net_name = net_map.get(net_id, net_id)
            nets.append(f"{net_name}:{connections}")
    
    nets.sort(key=lambda x: x.split(':')[0])
    
    with open(output_file, 'w') as f_out:
        f_out.write('\n'.join(nets))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python map_net_names.py PCB_FILE NETS_FILE OUTPUT_FILE")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    nets_file = sys.argv[2]
    output_file = sys.argv[3]
    
    net_map = load_net_map(pcb_file)
    map_nets(nets_file, output_file, net_map)