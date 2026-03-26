# simplify_passive_components.py
# Упрощение графа: замена пинов пассивных компонентов на один узел компонента

import networkx as nx
import re
import sys

# ------------------ Загрузка графа ------------------
input_file = sys.argv[1]
output_file = sys.argv[2]

G = nx.read_gml(input_file)
H = G.copy()

# ------------------ Определение пассивных компонентов ------------------
def is_passive_component(node):
    # Резисторы (R), конденсаторы (C), катушки (L)
    return re.match(r'^[RCL]\d+', node) is not None

# ------------------ Поиск и замена ------------------
components_to_simplify = {}

# Сначала находим все компоненты для упрощения
for node in G.nodes():
    if is_passive_component(node):
        # Находим все пины этого компонента (Rxx_1, Rxx_2 и т.д.)
        pins = []
        for nbr in G.neighbors(node):
            if nbr.startswith(f"{node}_"):  # Пины имеют вид Rxx_1, Rxx_2
                pins.append(nbr)
        
        if len(pins) == 2:  # Ожидаем 2 пина для пассивного компонента
            components_to_simplify[node] = pins

# Выполняем замену для каждого найденного компонента
for comp, pins in components_to_simplify.items():
    # Находим соседей каждого пина (кроме самого компонента)
    neighbors_1 = [n for n in G.neighbors(pins[0]) if n != comp]
    neighbors_2 = [n for n in G.neighbors(pins[1]) if n != comp]
    
    # Проверяем, что у пинов есть соседи
    if neighbors_1 and neighbors_2:
        # Удаляем старые ребра от пинов к соседям
        for n1 in neighbors_1:
            if H.has_edge(pins[0], n1):
                H.remove_edge(pins[0], n1)
        for n2 in neighbors_2:
            if H.has_edge(pins[1], n2):
                H.remove_edge(pins[1], n2)
        
        # Добавляем новые ребра от компонента к соседям
        for n1 in neighbors_1:
            H.add_edge(comp, n1)
        for n2 in neighbors_2:
            H.add_edge(comp, n2)
        
        # Удаляем пины
        H.remove_node(pins[0])
        H.remove_node(pins[1])

# ------------------ Сохранение результата ------------------
nx.write_gml(H, output_file)
print(f"\nГотово. Упрощенный граф сохранен в {output_file}")
print(f"Упрощено компонентов: {len(components_to_simplify)}")