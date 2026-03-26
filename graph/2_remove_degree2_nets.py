# remove_degree2_nets.py
# Удаление NET-узлов со степенью 2 и соединение их соседей напрямую

import networkx as nx
import sys

# ------------------ Загрузка графа ------------------
input_file = sys.argv[1]
output_file = sys.argv[2]

G = nx.read_gml(input_file)
H = G.copy()

# ------------------ Поиск и удаление NET-узлов со степенью 2 ------------------
removed_count = 0
processed = set()

while True:
    found = False
    for node in list(H.nodes()):
        if node in processed:
            continue
            
        # Проверяем что это NET узел и имеет ровно 2 связи
        if H.nodes[node].get('type') == 'net' and H.degree(node) == 2:
            neighbors = list(H.neighbors(node))
            
            # Получаем соседей
            n1, n2 = neighbors[0], neighbors[1]
            
            # Добавляем прямое соединение между соседями
            if not H.has_edge(n1, n2):
                H.add_edge(n1, n2)
            
            # Удаляем NET узел
            H.remove_node(node)
            processed.add(node)
            removed_count += 1
            found = True
            break
        else:
            processed.add(node)
    
    if not found:
        break

print(f"\nУдалено NET-узлов со степенью 2: {removed_count}")
print(f"Итоговое количество узлов: {H.number_of_nodes()}")
print(f"Итоговое количество ребер: {H.number_of_edges()}")

# ------------------ Сохранение результата ------------------
nx.write_gml(H, output_file)
print(f"Граф сохранен в {output_file}")