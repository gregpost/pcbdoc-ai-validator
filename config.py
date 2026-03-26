# file: config.py
# Configuration with dynamic tmp timestamp support and multiple field names

import os      # getenv
import time    # strftime

class Config:
    def __init__(self, no_timestamp=False):
        # ------------------------------------------------------------------------------------------------
        # ОСНОВНЫЕ НАСТРОЙКИ (менять при каждом запуске)
        # ------------------------------------------------------------------------------------------------
        
        # Варианты путей к PcbDoc файлам
        self.PCB_PATHS = {
            1: "./PcbDocs/RTL8370N-Switch-AR9331-WIFI.PcbDoc",
            2: "./PcbDocs/TL-WR703N.PcbDoc",
            3: "./PcbDocs/8_1000M_Switch_VT1.1.PcbDoc"
        }
        
        # Список обрабатываемых схем: {индекс_в_PCB_PATHS: "имя_поля"}
        self.SCHEME_MAPPING = {
            1: "DEV_SCHEME",
            3: "REF_SCHEME"
        }
        
        # Список компонентов: первый - целевой (TARGET_COMPONENT)
        self.COMPONENTS = [
            "RTL8370N",      # целевой компонент
            "G4801S",
            "BY25Q16BSTIG"
        ]
        
        # Путь к интерпретатору Python
        self.PYTHON_PATH = "D:/venv311/Scripts/python.exe"
        
        # ------------------------------------------------------------------------------------------------
        # ПУТИ К СКРИПТАМ (исходники)
        # ------------------------------------------------------------------------------------------------
        
        self.HUGE_FILE_DIR = "./huge_file"
        self.GRAPH_DIR_SRC = "./graph"
        self.PCB_TO_SCHEM_DIR_SRC = "./pcb_to_schematics"
        
        # ------------------------------------------------------------------------------------------------
        # TMP DIR (с таймкодом)
        # ------------------------------------------------------------------------------------------------
        
        BASE_TMP_DIR = "./tmp"
        
        if no_timestamp:
            self.TMP_DIR = f"{BASE_TMP_DIR}/base"
        else:
            self.TMP_DIR = f"{BASE_TMP_DIR}/tmp_{time.strftime('%Y%m%d_%H%M%S')}"
        
        self.GRAPH_DIR = f"{self.TMP_DIR}/graph"
        self.PCB_TO_SCHEM_DIR = f"{self.TMP_DIR}/pcb_to_netlist"
        self.HUGE_FILE_TMP_DIR = f"{self.TMP_DIR}/huge_file"
        
        # ------------------------------------------------------------------------------------------------
        # ОБЩИЕ ПУТИ К ДАННЫМ (не tmp)
        # ------------------------------------------------------------------------------------------------
        
        self.PINS_DIR = "./pins"
        self.DATASHEETS_DIR = "./datasheets"
        self.PCB_DIR = "./pcbdocs"
        self.PROMPTS_DIR = "./prompts"
        self.NETS_DIR = "./nets"
        
        # ------------------------------------------------------------------------------------------------
        # ВХОДНЫЕ/ВЫХОДНЫЕ ФАЙЛЫ (с использованием tmp)
        # ------------------------------------------------------------------------------------------------
        
        self.TARGET_COMPONENT = self.COMPONENTS[0]
        
        self.COMMON_NETS_PATH = f"{self.NETS_DIR}/common_nets.txt"
        self.COMPRESSED_DATASHEET_PATH = f"{self.DATASHEETS_DIR}/{self.TARGET_COMPONENT}_compressed.txt"
        self.FULL_DESCRIPTION_PATH = f"{self.HUGE_FILE_TMP_DIR}/full_description.txt"
        
        self.CLIPBOARD_SAVER_PATH = f"{self.HUGE_FILE_TMP_DIR}/1_clipboard_saver.txt"
        self.LARGE_FILE_SLICER_PATH = f"{self.HUGE_FILE_TMP_DIR}/2_large_file_slicer.txt"
        self.PIN_PROCESSOR_PATH = f"{self.GRAPH_DIR}/8_1_pin_processor.txt"
        
        self.PROMPT_FOLDER = f"{self.HUGE_FILE_TMP_DIR}/prompt_outputs"
        self.FRAGMENT_FOLDER = f"{self.HUGE_FILE_TMP_DIR}/fragments"
        
        self.PROMPT_TEMPLATE_PATH_1 = f"{self.PROMPTS_DIR}/Составление сжатого даташита.txt"
        self.PROMPT_TEMPLATE_PATH_2 = f"{self.PROMPTS_DIR}/Конвертация схемы в текст.txt"