# pipeline.py: Запускает скрипты обработки данных последовательно

import subprocess
import sys
import os


def run_script(script_name, args=None):
    """Запускает Python-скрипт с аргументами."""
    if args is None:
        args = []
    cmd = [sys.executable, script_name] + args
    print(f"Запуск: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Ошибка в {script_name}:")
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
    return result


def main():
    # 0_pdf_to_md.py <input.pdf> <output.md>
    run_script("0_pdf_to_md.py", ["input.pdf", "output.md"])

    # 1_clipboard_saver.py [logfile]
    run_script("1_clipboard_saver.py", ["../tmp/huge_file/clipboard_log.txt"])

    # 2_large_file_slicer <input> <template> <output_dir> <fragments_dir> [answer_file]
    run_script("2_large_file_slicer.py", [
        "../tmp/graph/branches_tmp.txt",
        "../prompts/Конвертация схемы в текст.txt",
        "../tmp/huge_file/prompt_outputs",
        "../tmp/huge_file/fragments",
        "../tmp/huge_file/answer.txt"
    ])

    # 3_pin_processor.py <input_file> [output_file]
    run_script("3_pin_processor.py", [
        "../tmp/huge_file/prompt_outputs/merged.txt",
        "../tmp/huge_file/pin_processed.txt"
    ])


if __name__ == "__main__":
    main()