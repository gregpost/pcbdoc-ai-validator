# convert_to_utf8.py      Try common encodings and convert input.txt to UTF-8

import sys

def try_encodings(file_path):
    encodings = ['cp1251', 'cp1252', 'latin-1', 'utf-8', 'utf-16', 'ascii']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
                print(f"Success with encoding: {enc}")
                return content, enc
        except UnicodeDecodeError:
            continue
    
    with open(file_path, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')
        print("Fallback: used binary read with ignore")
        return content, 'binary'

def convert_to_utf8(input_file, output_file):
    content, used_enc = try_encodings(input_file)
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(content)
    
    print(f"Converted to UTF-8 using {used_enc}: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_to_utf8.py INPUT_FILE OUTPUT_FILE")
        sys.exit(1)
    
    convert_to_utf8(sys.argv[1], sys.argv[2])