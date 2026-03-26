"""
# resolve_components.py      Replace designators with actual component names from COMMENT text by ID
"""

import sys
import re

def trim_name(name):
    """
    Обрезает имя после первого знака '-', ' ', '_' или '('
    """
    for delimiter in ['-', ' ', '_', '(']:
        if delimiter in name:
            return name.split(delimiter)[0]
    return name

def clean_libref(libref):
    """
    Очищает библиотечное имя от маркеров неопределенности (?)
    """
    parts = libref.split(' ')
    clean_parts = [p for p in parts if '?' not in p]
    result = ' '.join(clean_parts).strip()
    return trim_name(result)

def is_passive_component(designator):
    """
    Проверяет, является ли компонент пассивным (только резисторы)
    """
    return re.match(r'^R\d+', designator) is not None

def find_chip_by_id(pcb_file, component_id):
    """
    Ищет имя компонента по ID в текстовых записях компонента
    """
    with open(pcb_file, 'r') as f:
        text_lines = []
        for line in f:
            if not line.startswith('RECORD=Text'):
                continue
            
            if f'|COMPONENT={component_id}' not in line:
                continue
            
            text_lines.append(line)
        
        # Сначала ищем COMMENT=True
        for line in text_lines:
            if '|COMMENT=True' in line:
                parts = line.split('|')
                for part in parts:
                    if part.startswith('TEXT='):
                        result = part.split('=')[1].strip()
                        if '?' in result:
                            break
                        return trim_name(result)
        
        # Если нашли текст с '?' или не нашли COMMENT, ищем DESIGNATOR=True
        for line in text_lines:
            if '|DESIGNATOR=True' in line:
                parts = line.split('|')
                for part in parts:
                    if part.startswith('TEXT='):
                        result = part.split('=')[1].strip()
                        return trim_name(result)
    
    return None

def load_component_map(pcb_file):
    """
    Загружает карту соответствия обозначений компонентов их реальным именам
    """
    print(f"Загрузка карты компонентов из файла: {pcb_file}")
    component_map = {}
    id_to_designator = {}
    designator_libref = {}
    
    with open(pcb_file, 'r') as f:
        for line in f:
            if not line.startswith('RECORD=Component'):
                continue
            
            # Разбираем строку компонента
            parts = line.split('|')
            designator = None
            libref = None
            component_id = None
            
            for part in parts:
                if part.startswith('SOURCEDESIGNATOR='):
                    designator = part.split('=')[1].strip()
                elif part.startswith('SOURCELIBREFERENCE='):
                    libref = part.split('=')[1].strip()
                elif part.startswith('ID='):
                    component_id = part.split('=')[1].strip()
            
            if designator:
                if libref:
                    designator_libref[designator] = libref
                if component_id:
                    id_to_designator[component_id] = designator
    
    # Ищем текстовые имена для всех компонентов
    print(f"\nПоиск текстовых имен для {len(id_to_designator)} компонентов")
    for component_id, designator in id_to_designator.items():
        # Пропускаем пассивные компоненты (резисторы)
        if is_passive_component(designator):
            continue
        
        component_name = find_chip_by_id(pcb_file, component_id)
        if component_name:
            if component_name == "UNKNOWN" and designator in designator_libref:
                component_name = clean_libref(designator_libref[designator])
            component_map[designator] = component_name
    
    print(f"Загружено {len(component_map)} замен для компонентов")
    return component_map

def resolve_nets(nets_file, output_file, component_map):
    """
    Заменяет обозначения компонентов в netlist на реальные имена
    """
    print(f"\nОбработка netlist файла: {nets_file}")
    print(f"Доступно замен: {len(component_map)}")
    
    processed_nets = 0
    total_replacements = 0
    
    with open(nets_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            if ':' not in line:
                continue
            
            net_name, connections = line.strip().split(':', 1)
            processed_nets += 1
            
            resolved = []
            for item in connections.split(','):
                if '_' not in item:
                    resolved.append(item)
                    continue
                
                comp, pin = item.split('_', 1)
                
                if comp in component_map:
                    resolved_comp = component_map[comp]
                    total_replacements += 1
                else:
                    resolved_comp = comp
                
                resolved.append(f"{resolved_comp}_{pin}")
            
            result_line = f"{net_name}:{','.join(resolved)}"
            f_out.write(f"{result_line}\n")
    
    print(f"\nОбработано {processed_nets} сетей")
    print(f"Выполнено {total_replacements} замен компонентов")
    print(f"Результат сохранен в: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python resolve_components.py PCB_FILE NETS_FILE OUTPUT_FILE")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    nets_file = sys.argv[2]
    output_file = sys.argv[3]
    
    print("=" * 60)
    print("Запуск resolve_components.py")
    print(f"PCB файл: {pcb_file}")
    print(f"Netlist файл: {nets_file}")
    print(f"Выходной файл: {output_file}")
    print("=" * 60)
    
    component_map = load_component_map(pcb_file)
    resolve_nets(nets_file, output_file, component_map)
    
    print("=" * 60)
    print("Скрипт завершен успешно")
    print("=" * 60)