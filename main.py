# file: main.py
# Processes multiple PcbDoc files, extracts circuits for each, then merges all results

import subprocess
import sys
import re
import time
import os
import shutil

def log_step(message):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_script(cfg, script_name, *args, parallel=False):
    target_script = os.environ.get("TARGET_SCRIPT", "")
    script_basename = os.path.basename(script_name)
    
    if target_script and target_script != script_basename:
        return subprocess.CompletedProcess([], 0)
    
    log_step(f"Running: {script_name}")
    cmd = [cfg.PYTHON_PATH, script_name] + list(args)
    
    if parallel:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    return subprocess.run(cmd)

def process_single_pcb(cfg, pcb_index, field_name, start_step):
    """Process single PcbDoc file and return path to its text_appender file"""
    pcb_path = cfg.PCB_PATHS[pcb_index]
    scheme_name = os.path.basename(pcb_path)
    log_step(f"=== Processing PCB index {pcb_index} as {field_name}: {scheme_name} ===")
    
    scheme_dir = f"{cfg.PCB_TO_SCHEM_DIR}/{pcb_index}"
    graph_dir = f"{cfg.GRAPH_DIR}/{pcb_index}"
    os.makedirs(scheme_dir, exist_ok=True)
    os.makedirs(graph_dir, exist_ok=True)
    
    # Override paths for this iteration
    netlist_path = f"{scheme_dir}/8_resolve_chips.txt"
    netlist_to_graph_path = f"{graph_dir}/1_netlist_to_graph.gml"
    remove_degree2_nets_path = f"{graph_dir}/2_remove_degree2_nets.gml"
    simplify_passive_components_path = f"{graph_dir}/3_simplify_passive_components.gml"
    get_branch_path = f"{graph_dir}/4_get_branch.gml"
    graph_to_text_path = f"{graph_dir}/5_graph_to_text.txt"
    remove_nets_path = f"{graph_dir}/6_remove_nets.txt"
    text_appender_path = f"{graph_dir}/7_text_appender.txt"
    pin_processor_path = f"{graph_dir}/8_1_pin_processor.txt"
    merge_pin_fields_path_1 = f"{graph_dir}/8_merge_pin_fields.txt"
    
# ---------------------------------------------------------------------------------------------
# Шаг 3: Конвертация PcbDoc в нетлист
# ---------------------------------------------------------------------------------------------
    if start_step <= 3:
        run_script(cfg, f"{cfg.PCB_TO_SCHEM_DIR_SRC}/run_pipeline.py", pcb_path, scheme_dir)
    else:
        log_step("Skipping step 3")
    
# ---------------------------------------------------------------------------------------------
# Шаг 4: Конвертация нетлиста в граф
# ---------------------------------------------------------------------------------------------
    if start_step <= 4:
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/1_netlist_to_graph.py", netlist_path, netlist_to_graph_path)
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/2_remove_degree2_nets.py", netlist_to_graph_path, remove_degree2_nets_path)
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/3_simplify_passive_components.py", remove_degree2_nets_path, simplify_passive_components_path)
    else:
        log_step("Skipping step 4")
    
# ---------------------------------------------------------------------------------------------
# Шаг 5: Конвертация графа в электрические цепи для каждого пина в текстовом формате
# ---------------------------------------------------------------------------------------------
    if start_step <= 5:
        pin_list_path = f"{cfg.PINS_DIR}/{cfg.TARGET_COMPONENT}.txt"
        try:
            with open(pin_list_path, "r") as f:
                content = f.read()
        except FileNotFoundError:
            print("Error: pins file not found")
            return None
        
        pins = re.findall(rf'^({cfg.TARGET_COMPONENT}_\w+)$', content, re.MULTILINE)
        
        with open(text_appender_path, "w") as f:
            f.write("")
        
        for i, pin in enumerate(pins, 1):        
            log_step(f"Processing pin {i}/{len(pins)}: {pin}")
            
            result = run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/4_get_branch.py", pin, 
                                simplify_passive_components_path,
                                get_branch_path, cfg.COMMON_NETS_PATH)
            if result.returncode == 0:
                continue
            
            run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/5_graph_to_text.py", cfg.TARGET_COMPONENT,
                       get_branch_path, graph_to_text_path, cfg.COMMON_NETS_PATH)
            run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/6_remove_nets.py", graph_to_text_path, remove_nets_path)
            run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/7_text_appender.py", pin, remove_nets_path, text_appender_path)
    else:
        log_step("Skipping step 5")
    
# ---------------------------------------------------------------------------------------------
# Шаг 6: Слияние с pin_processor для каждого PcbDoc
# ---------------------------------------------------------------------------------------------
    if start_step <= 6:
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/8_merge_pin_fields.py", pin_processor_path, 
                   text_appender_path, merge_pin_fields_path_1, field_name)
    else:
        log_step("Skipping step 6")
    
    return text_appender_path

def merge_all_results(cfg, text_appender_paths, scheme_mapping):
    """Merge all text_appender files using 8_merge_pin_fields.py sequentially"""
    log_step("=== Merging all PCB results ===")
    
    if not text_appender_paths:
        log_step("No files to merge")
        return None
    
    # Start with first file as base
    base_file = text_appender_paths[0]
    
    # Merge sequentially
    current_merged = base_file
    for i in range(1, len(text_appender_paths)):
        temp_merged = f"{cfg.GRAPH_DIR}/temp_merged_{i}.txt"
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/8_merge_pin_fields.py", 
                   current_merged, text_appender_paths[i], temp_merged)
        current_merged = temp_merged
    
    log_step(f"Merged result saved to {current_merged}")
    return current_merged

def main():
    log_step("=== START PROCESSING ===")

    start_step = 1
    target_script = ""
    no_timestamp = False
    
    for i in range(1, len(sys.argv)):
        arg = sys.argv[i]
        if arg.startswith("--step="):
            try:
                start_step = int(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif arg.startswith("--script="):
            target_script = arg.split("=", 1)[1]
        elif arg == "--no-tmp-timestamp":
            no_timestamp = True
    
    from config import Config
    cfg = Config(no_timestamp)
    
    os.makedirs(cfg.PCB_TO_SCHEM_DIR, exist_ok=True)
    os.makedirs(cfg.GRAPH_DIR, exist_ok=True)
    os.makedirs(cfg.HUGE_FILE_TMP_DIR, exist_ok=True)

    os.environ["TARGET_SCRIPT"] = target_script

# ---------------------------------------------------------------------------------------------
# Шаг 1: конвертация pdf в md
# ---------------------------------------------------------------------------------------------
    if start_step <= 1:
        for component in cfg.COMPONENTS:
            pdf_path = f"{cfg.DATASHEETS_DIR}/{component}.pdf"
            md_path = f"{cfg.HUGE_FILE_TMP_DIR}/{component}.md"
            run_script(cfg, f"{cfg.HUGE_FILE_DIR}/0_pdf_to_md.py", pdf_path, md_path)

# ---------------------------------------------------------------------------------------------
# Шаг 2: Парсинг даташитов
# ---------------------------------------------------------------------------------------------
    if start_step <= 2:        
        run_script(cfg, f"{cfg.HUGE_FILE_DIR}/1_clipboard_saver.py", 
                   cfg.CLIPBOARD_SAVER_PATH, parallel=True)
        
        target_script = os.environ.get("TARGET_SCRIPT", "")
        if not target_script or target_script == "2_large_file_slicer.py":
            pin_list_path = f"{cfg.PINS_DIR}/{cfg.TARGET_COMPONENT}.txt"
            try:
                with open(pin_list_path, "r") as f:
                    content = f.read()
            except FileNotFoundError:
                print("Error: pins file not found")
                return 1
        
        for component in cfg.COMPONENTS:
            md_path = f"{cfg.HUGE_FILE_TMP_DIR}/{component}.md"
            pin_list_path = f"{cfg.PINS_DIR}/{component}.txt"
            run_script(cfg, f"{cfg.HUGE_FILE_DIR}/2_large_file_slicer.py", md_path, 
                       cfg.PROMPT_TEMPLATE_PATH_1, cfg.PROMPT_FOLDER, 
                       cfg.FRAGMENT_FOLDER, pin_list_path)
        
        run_script(cfg, f"{cfg.HUGE_FILE_DIR}/3_pin_processor.py", 
                   cfg.CLIPBOARD_SAVER_PATH, cfg.PIN_PROCESSOR_PATH)
    else:
        log_step("Skipping steps 1-2")

# ---------------------------------------------------------------------------------------------
# Шаг 3-6: Обработка каждого PcbDoc файла из SCHEME_MAPPING
# ---------------------------------------------------------------------------------------------
    text_appender_paths = []
    for pcb_index, field_name in cfg.SCHEME_MAPPING.items():
        # Copy pin_processor to each scheme's directory
        dst_pin_processor = f"{cfg.GRAPH_DIR}/{pcb_index}/8_1_pin_processor.txt"
        os.makedirs(os.path.dirname(dst_pin_processor), exist_ok=True)
        if os.path.exists(cfg.PIN_PROCESSOR_PATH):
            shutil.copy2(cfg.PIN_PROCESSOR_PATH, dst_pin_processor)
        
        result_path = process_single_pcb(cfg, pcb_index, field_name, start_step)
        if result_path:
            text_appender_paths.append(result_path)
    
# ---------------------------------------------------------------------------------------------
# Шаг 7: Слияние результатов всех PcbDoc файлов
# ---------------------------------------------------------------------------------------------
    merged_text_appender = None
    if start_step <= 7 and len(text_appender_paths) > 1:
        merged_text_appender = merge_all_results(cfg, text_appender_paths, cfg.SCHEME_MAPPING)
    elif len(text_appender_paths) == 1:
        merged_text_appender = text_appender_paths[0]
        log_step("Only one PCB, skipping merge")
    else:
        log_step("No PCB files processed")
    
# ---------------------------------------------------------------------------------------------
# Шаг 8: Конвертация текстовых электрических цепей в словестное описание
# ---------------------------------------------------------------------------------------------
    if start_step <= 8 and merged_text_appender:
        # Create pin_processor from first scheme for final steps
        first_index = list(cfg.SCHEME_MAPPING.keys())[0]
        pin_processor_path = f"{cfg.GRAPH_DIR}/{first_index}/8_1_pin_processor.txt"
        
        circuit_parser_path = f"{cfg.GRAPH_DIR}/9_circuit_parser.txt"
        filter_components_path = f"{cfg.GRAPH_DIR}/10_filter_components.txt"
        netlist_datasheet_sorter_path = f"{cfg.GRAPH_DIR}/11_netlist_datasheet_sorter.txt"
        merge_pin_fields_path_2 = f"{cfg.GRAPH_DIR}/12_merge_pin_fields.txt"
        
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/8_merge_pin_fields.py", 
                   pin_processor_path, merged_text_appender, merge_pin_fields_path_2)
        
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/9_circuit_parser.py", merge_pin_fields_path_2,
                   circuit_parser_path)
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/10_filter_components.py", circuit_parser_path,
                   filter_components_path)
        run_script(cfg, f"{cfg.GRAPH_DIR_SRC}/11_netlist_datasheet_sorter.py",
                   filter_components_path, pin_processor_path,
                   netlist_datasheet_sorter_path)
        
        # Use netlist_datasheet_sorter_path as input for slicer instead of FULL_DESCRIPTION_PATH
        if os.path.exists(netlist_datasheet_sorter_path):
            run_script(cfg, f"{cfg.HUGE_FILE_DIR}/1_clipboard_saver.py", cfg.CLIPBOARD_SAVER_PATH, parallel=True)
            run_script(cfg, f"{cfg.HUGE_FILE_DIR}/2_large_file_slicer.py", netlist_datasheet_sorter_path,
                       cfg.PROMPT_TEMPLATE_PATH_2, cfg.PROMPT_FOLDER, cfg.FRAGMENT_FOLDER)
        else:
            log_step(f"Warning: {netlist_datasheet_sorter_path} not found, skipping slicer")
    else:
        log_step("Skipping step 8")
    
    log_step("=== PROCESSING COMPLETED ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())