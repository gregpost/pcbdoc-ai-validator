# graph_to_text.py
# Convert GML graph to compact serial/parallel textual chain with tree view

import re
import sys

class Graph:
    def __init__(self):
        self.nodes = {}
        self.adj = {}

    def add_node(self, node_id, label):
        self.nodes[node_id] = label
        self.adj.setdefault(node_id, [])

    def add_edge(self, a, b):
        self.adj[a].append(b)
        self.adj[b].append(a)

    def find_id(self, label):
        for i, l in self.nodes.items():
            if l == label:
                return i
        return None


def parse_gml(path):
    g = Graph()
    text = open(path, "r", encoding="utf-8").read()
    
    if text.strip() == "NOT_CONNECTED":
        return None

    for block in re.findall(r'node\s*\[(.*?)\]', text, re.S):
        nid = int(re.search(r'id\s+(\d+)', block).group(1))
        label = re.search(r'label\s+"([^"]+)"', block).group(1)
        g.add_node(nid, label)

    for block in re.findall(r'edge\s*\[(.*?)\]', text, re.S):
        s = int(re.search(r'source\s+(\d+)', block).group(1))
        t = int(re.search(r'target\s+(\d+)', block).group(1))
        g.add_edge(s, t)

    return g


def build_chain(g, node, visited, described, common_nets, indent=""):
    label = g.nodes[node]

    if label in common_nets:
        return label

    visited.add(node)
    described.add(node)

    branches = []

    for n in g.adj[node]:
        if n in visited:
            continue
        if g.nodes[n] not in common_nets and n in described:
            continue
        branches.append(build_chain(g, n, visited.copy(), described, common_nets, indent))

    if not branches:
        return label

    if len(branches) == 1:
        return f"{label}-{branches[0]}"

    inner = ",\n".join(branches)
    inner = re.sub(r"^", indent + "  ", inner, flags=re.M)
    return f"{label}(\n{inner}\n{indent})"


def main():
    if len(sys.argv) < 5:
        print("Usage: python graph_to_text.py START_NODE INPUT_FILE OUTPUT_FILE COMMON_NETS_FILE")
        sys.exit(1)
    
    start_node = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    common_nets_file = sys.argv[4]
    
    with open(common_nets_file, 'r') as f:
        common_nets = set(line.strip() for line in f if line.strip())
    
    g = parse_gml(input_file)
    
    if g is None:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("NOT_CONNECTED")
        return
    
    start = g.find_id(start_node)
    described = set()
    result = build_chain(g, start, set(), described, common_nets)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)


if __name__ == "__main__":
    main()