# netlist_to_graph.py
# Convert netlist to NetworkX graph with nodes

import networkx as nx  # Graph, write_gml
import sys  # argv

input_file = sys.argv[1]
output_file = sys.argv[2]

G = nx.Graph()

with open(input_file) as f:
    for line in f:
        if not line.strip() or ':' not in line:
            continue
        net, nodes = line.strip().split(':', 1)
        G.add_node(net, type='net')
        
        # Каждый компонент соединяется только с NET
        for n in nodes.split(','):
            if '_' in n:
                comp, pin = n.rsplit('_', 1)
                pin_node = f"{comp}_{pin}"
                if not G.has_node(comp):
                    G.add_node(comp, type='component')
                if not G.has_node(pin_node):
                    G.add_node(pin_node, type='pin')
                G.add_edge(comp, pin_node)
                G.add_edge(pin_node, net)
            else:
                if not G.has_node(n):
                    G.add_node(n, type='component')
                G.add_edge(n, net)

nx.write_gml(G, output_file)