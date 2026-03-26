# get_branch.py
# Визуализация ветви графа NetworkX от указанного узла с остановкой на микросхемах и общих проводах

import networkx as nx
import matplotlib.pyplot as plt
import re
import sys

# ------------------ Параметры пользователя ------------------
if len(sys.argv) < 5:
    print("Usage: python get_branch.py START_NODE INPUT_GML OUTPUT_GML COMMON_NETS_FILE [MAX_NODES] [SHOW_PLOT]")
    print("  MAX_NODES: max nodes to traverse (default: 15, 0 = unlimited)")
    print("  SHOW_PLOT: 1 to show visualization, 0 to disable (default: 0)")
    sys.exit(1)

START_NODE = sys.argv[1]
INPUT_GML = sys.argv[2]
OUTPUT_GML = sys.argv[3]
COMMON_NETS_FILE = sys.argv[4]
MAX_NODES = int(sys.argv[5]) if len(sys.argv) > 5 else 25
SHOW_PLOT = bool(int(sys.argv[6])) if len(sys.argv) > 6 else False
SHOW_NET_NAMES = False

# ------------------ Загрузка общих цепей ------------------
with open(COMMON_NETS_FILE, 'r') as f:
    COMMON_NETS = set(line.strip() for line in f if line.strip())

# ------------------ Загрузка графа ------------------
try:
    G = nx.read_gml(INPUT_GML)
except FileNotFoundError:
    print(f"Error: {INPUT_GML} not found")
    sys.exit(0)

# ------------------ Проверка существования узла ------------------
if START_NODE not in G:
    with open(OUTPUT_GML, "w") as f:
        f.write("NOT_CONNECTED")
    sys.exit(1)

# ------------------ Фильтрация ветви ------------------
def is_chip(node):
    if G.nodes[node].get('type') != 'component':
        return False
    latin_count = sum(1 for c in node if c.isalpha() and c.isascii())
    return latin_count > 1

def traverse(node, visited=None):
    if visited is None:
        visited = set()
    
    if MAX_NODES > 0 and len(visited) >= MAX_NODES:
        return []
        
    visited.add(node)
    branch_edges = []
    for nbr in G.neighbors(node):
        if nbr not in visited:
            if MAX_NODES > 0 and len(visited) >= MAX_NODES:
                break
            if nbr in COMMON_NETS or is_chip(nbr):
                branch_edges.append((node, nbr))
            else:
                branch_edges.append((node, nbr))
                branch_edges.extend(traverse(nbr, visited))
    return branch_edges

edges_to_draw = traverse(START_NODE)
H = nx.Graph()
H.add_edges_from(edges_to_draw)

# ------------------ Сохранение ветви в GML файл ------------------
for node in H.nodes():
    if node in G.nodes:
        H.nodes[node].update(G.nodes[node])

nx.write_gml(H, OUTPUT_GML)

# ------------------ Визуализация (опционально) ------------------
if SHOW_PLOT:
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(H, seed=42)

    net_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'net' and n not in COMMON_NETS]
    common_net_nodes = [n for n in H.nodes() if n in COMMON_NETS]
    resistor_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'component' and re.match(r'^R\d+', n)]
    capacitor_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'component' and re.match(r'^C\d+', n)]
    inductor_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'component' and re.match(r'^L\d+', n)]
    pin_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'pin']
    chip_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'component' and is_chip(n) and not re.match(r'^[RCL]\d+', n)]
    other_nodes = [n for n in H.nodes() if G.nodes[n].get('type') == 'component' and not is_chip(n) and not re.match(r'^[RCL]\d+', n)]

    labels = {}
    for n in other_nodes + resistor_nodes + capacitor_nodes + inductor_nodes + chip_nodes + common_net_nodes:
        labels[n] = n
    for n in pin_nodes:
        labels[n] = n.split('_')[-1]
    if SHOW_NET_NAMES:
        for n in net_nodes:
            labels[n] = n

    nx.draw_networkx_edges(H, pos, edge_color="gray")

    if SHOW_NET_NAMES:
        nx.draw_networkx_nodes(H, pos, nodelist=net_nodes, node_color="brown", node_size=500)
    else:
        nx.draw_networkx_nodes(H, pos, nodelist=net_nodes, node_color="black", node_size=20)

    nx.draw_networkx_nodes(H, pos, nodelist=common_net_nodes, node_color="white", edgecolors="black", linewidths=2, node_size=500)
    nx.draw_networkx_nodes(H, pos, nodelist=resistor_nodes, node_color="red", node_size=500)
    nx.draw_networkx_nodes(H, pos, nodelist=capacitor_nodes, node_color="cyan", node_size=500)
    nx.draw_networkx_nodes(H, pos, nodelist=inductor_nodes, node_color="yellow", node_size=500)
    nx.draw_networkx_nodes(H, pos, nodelist=pin_nodes, node_color="lightgray", node_size=300)
    nx.draw_networkx_nodes(H, pos, nodelist=chip_nodes, node_color="magenta", node_size=700)
    nx.draw_networkx_nodes(H, pos, nodelist=other_nodes, node_color="lightgreen", node_size=500)

    nx.draw_networkx_labels(H, pos, labels=labels, font_size=8, font_weight="bold")

    plt.title(f"Branch from {START_NODE} (nodes: {H.number_of_nodes()})")
    plt.axis('off')
    plt.show()
    
sys.exit(1)