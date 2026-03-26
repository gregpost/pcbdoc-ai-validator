#!/usr/bin/env python3
"""
large_file_slicer.py: Нарезка файла на фрагменты с коррекцией границ
"""

import keyboard            # keyboard.add_hotkey, keyboard.wait
import pyperclip           # pyperclip.copy, pyperclip.paste
import re                  # re.search
import os                  # os.path.exists, os.makedirs
import sys                 # sys.argv, sys.exit
import time                # time.sleep
import shutil              # shutil.rmtree

HOTKEY = 'ctrl+q'
INPUT_FILE = sys.argv[1]
PROMPT_TEMPLATE_FILE = sys.argv[2]
OUTPUT_SUBFOLDER = sys.argv[3]
FRAGMENTS_SUBFOLDER = sys.argv[4]
ADDITIONAL_FILE = sys.argv[5] if len(sys.argv) > 5 else None
LINES_PER_FRAGMENT = int(sys.argv[6]) if len(sys.argv) > 6 else 300
OVERLAP = int(sys.argv[7]) if len(sys.argv) > 7 else 0
WORD_COUNT = int(sys.argv[8]) if len(sys.argv) > 8 else 0

class FileSlicer:
    def __init__(self):
        self.step_number = 1
        self.completed = False
        self.current_start = 0
        self.last_end = 0
        self.load_file()
        self.has_structural_elements = self.check_structural_elements()
        self.create_folders()
        self.calculate_fragments()
        keyboard.add_hotkey(HOTKEY, self.copy_next_fragment)
        print(f"Скрипт запущен. Нажмите {HOTKEY} для копирования следующего фрагмента")
        print(f"Файл: {INPUT_FILE}, всего строк: {self.total_lines}")
        print(f"Фрагментов: {self.fragment_count}, размер: {LINES_PER_FRAGMENT} строк, нахлест: {OVERLAP}")
        self.copy_next_fragment()

    def calculate_fragments(self):
        self.fragment_count = (self.total_lines + LINES_PER_FRAGMENT - 1) // LINES_PER_FRAGMENT

    def create_folders(self):
        for folder in [OUTPUT_SUBFOLDER, FRAGMENTS_SUBFOLDER]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
            os.makedirs(folder)

    def load_file(self):
        with open(INPUT_FILE, 'r', encoding='utf-8') as file:
            self.lines = file.readlines()
        self.total_lines = len(self.lines)

    def check_structural_elements(self):
        content = ''.join(self.lines)
        has_tags = bool(re.search(r'<<<\w+>>>\s+START', content))
        has_headers = bool(re.search(r'^\s*#{1,6}\s+', content, re.MULTILINE))
        return has_tags or has_headers

    def is_section_boundary(self, line):
        return bool(re.search(r'<<<\w+>>>\s+START', line) or re.match(r'^\s*#{1,6}\s+', line))

    def is_section_end(self, line):
        return bool(re.search(r'<<<\w+>>>\s+END', line))

    def get_next_fragment_range(self):
        start = self.current_start
        end = min(start + LINES_PER_FRAGMENT - 1, self.total_lines - 1)
        return int(start), int(end)

    def copy_next_fragment(self):
        try:
            if self.completed:
                pyperclip.copy('')
                return

            if self.current_start >= self.total_lines:
                self.completed = True
                pyperclip.copy('')
                return

            start, end = self.get_next_fragment_range()
            fragment_lines = self.lines[start:end + 1]
            fragment_text = ''.join(fragment_lines)
            trimmed_lines = len(fragment_lines)

            if self.has_structural_elements:
                fragment_text, trimmed_count = self.trim_incomplete_section(fragment_text)
                trimmed_lines -= trimmed_count

            # Если фрагмент меньше 2 строк, объединяем со следующим
            if trimmed_lines < 2 and start + trimmed_lines < self.total_lines:
                next_start = start + trimmed_lines
                next_end = min(next_start + LINES_PER_FRAGMENT - 1, self.total_lines - 1)
                next_fragment = self.lines[next_start:next_end + 1]
                next_text = ''.join(next_fragment)
                
                if self.has_structural_elements:
                    next_text, next_trimmed = self.trim_incomplete_section(next_text)
                else:
                    next_trimmed = len(next_fragment)
                
                fragment_text = fragment_text + next_text
                trimmed_lines += next_trimmed
                
                self.current_start = next_start + next_trimmed
            else:
                self.current_start += max(trimmed_lines - OVERLAP, 1)

            # Пропускаем пустые фрагменты
            if trimmed_lines == 0 or not fragment_text.strip():
                if self.current_start >= self.total_lines:
                    self.completed = True
                else:
                    self.copy_next_fragment()
                return

            if trimmed_lines < 2:
                self.completed = True
                return

            # Вычисляем реальный нахлест и разрыв
            actual_overlap = 0
            gap = 0
            if self.step_number > 1:
                actual_overlap = max(0, self.last_end - (start + 1) + 1)
                gap = max(0, (start + 1) - self.last_end - 1)

            self.create_prompt_output(fragment_text, start + 1, start + trimmed_lines, actual_overlap, gap)
            self.last_end = start + trimmed_lines

            if self.current_start >= self.total_lines:
                self.completed = True
                return

            self.step_number += 1

        except Exception as e:
            print(f"Ошибка: {e}")

    def create_prompt_output(self, part_text, start_line, end_line, actual_overlap, gap):
        with open(PROMPT_TEMPLATE_FILE, 'r', encoding='utf-8') as f:
            template = f.read()

        additional_text = ""
        if ADDITIONAL_FILE and os.path.exists(ADDITIONAL_FILE):
            with open(ADDITIONAL_FILE, 'r', encoding='utf-8') as f:
                additional_text = f.read().strip()

        result = template.replace('#1', part_text) \
                        .replace('#2', additional_text) \
                        .replace('#3', str(start_line)) \
                        .replace('#4', str(end_line)) \
                        .replace('#5', str(self.total_lines)) \
                        .replace('#6', str(self.step_number)) \
                        .replace('#7', str(WORD_COUNT))

        pyperclip.copy(result)

        fragment_file = os.path.join(FRAGMENTS_SUBFOLDER, f"fragment_{self.step_number}.txt")
        with open(fragment_file, 'w', encoding='utf-8') as f:
            f.write(part_text)

        output_file = os.path.join(OUTPUT_SUBFOLDER, f"prompt_step_{self.step_number}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        lines_count = end_line - start_line + 1
        gap_msg = f", разрыв: {gap}" if gap > 0 else ""
        print(f"Фрагмент {self.step_number}: строки {start_line}-{end_line} из {self.total_lines} (строк: {lines_count}, нахлест: {actual_overlap}{gap_msg})")

    def trim_incomplete_section(self, text):
        lines = text.splitlines(True)
        original_len = len(lines)
        result_lines = []
        in_section = False

        for line in lines:
            if self.is_section_boundary(line):
                in_section = True
                result_lines.append(line)
            elif self.is_section_end(line):
                if in_section:
                    result_lines.append(line)
                in_section = False
            elif in_section:
                result_lines.append(line)
            else:
                result_lines.append(line)

        if in_section:
            while result_lines and not (self.is_section_boundary(result_lines[-1]) or self.is_section_end(result_lines[-1])):
                result_lines.pop()
            if result_lines and not self.is_section_end(result_lines[-1]):
                while result_lines and not self.is_section_boundary(result_lines[-1]):
                    result_lines.pop()
                if result_lines and self.is_section_boundary(result_lines[-1]):
                    result_lines.pop()

        return ''.join(result_lines).rstrip(), original_len - len(result_lines)

if __name__ == "__main__":
    slicer = FileSlicer()
    try:
        while True:
            time.sleep(0.1)
            if slicer.completed:
                current_buffer = pyperclip.paste()
                if not current_buffer:
                    print("Цикл копирования завершен, буфер очищен.")
                    print("Нажмите Enter для выхода из программы...")
                    keyboard.wait('enter')
                    sys.exit(0)
    except KeyboardInterrupt:
        print("\nСкрипт остановлен")
        sys.exit(0)