"""
clipboard_saver.py: Saves clipboard content to file on Alt+N hotkey with GUI status window.
"""

import pyperclip
import keyboard
import os
import stat
import sys
import tkinter as tk
from tkinter import Label, Frame

TARGET_FILENAME = sys.argv[1]

def ensure_file_writable():
    """Снимает атрибут 'только чтение' если файл существует."""
    if os.path.exists(TARGET_FILENAME):
        os.chmod(TARGET_FILENAME, stat.S_IWRITE)

def get_file_size():
    """Возвращает размер файла в байтах или 0 если файл не существует."""
    if os.path.exists(TARGET_FILENAME):
        return os.path.getsize(TARGET_FILENAME)
    return 0

class StatusWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Clipboard Saver")
        self.window.geometry("161x120+0+0")
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        self.window.configure(bg='green')
        
        # Header frame for dragging and buttons
        self.header = Frame(self.window, bg='darkgreen', height=25)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)
        
        # Close button
        self.close_btn = Label(self.header, text="X", bg='darkgreen', fg='white', cursor='hand2')
        self.close_btn.pack(side='right', padx=5)
        
        # Title
        self.title_label = Label(self.header, text="Clipboard Saver", bg='darkgreen', fg='white')
        self.title_label.pack(side='left', padx=5)
        
        # Status label
        self.status_label = Label(self.window, text="Status: Ready\nSize: 0 bytes", 
                                  font=("Arial", 10), bg='green', fg='white')
        self.status_label.pack(expand=True, fill='both')
        
        # Bind dragging
        self.header.bind('<Button-1>', self.start_move)
        self.header.bind('<B1-Motion>', self.on_move)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.on_move)
        
        # Button command
        self.close_btn.bind('<Button-1>', lambda e: self.window.destroy())
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    
    def update_status(self, message):
        size = get_file_size()
        self.status_label.config(text=f"{message}\nSize: {size} bytes")
        self.window.update()
    
    def show_copy_success(self):
        self.update_status("Copied!")
        self.window.after(1000, lambda: self.update_status("Ready"))
    
    def run(self):
        self.window.mainloop()

def save_clipboard(gui):
    try:
        text = pyperclip.paste().rstrip()
        if text:
            with open(TARGET_FILENAME, 'a', encoding='utf-8') as f:
                f.write(text + '\n')
            gui.show_copy_success()
    except Exception as e:
        gui.update_status(f"Error: {str(e)[:20]}")

def main():
    os.makedirs(os.path.dirname(TARGET_FILENAME), exist_ok=True)
    
    ensure_file_writable()
    open(TARGET_FILENAME, 'w', encoding='utf-8').close()
    
    gui = StatusWindow()
    
    def on_hotkey():
        save_clipboard(gui)
    
    keyboard.add_hotkey('alt+n', on_hotkey)
    print("Скрипт запущен. Нажмите Alt+N для сохранения буфера обмена.")
    
    gui.run()

if __name__ == "__main__":
    main()