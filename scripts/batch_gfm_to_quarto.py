import os
import re
import shutil
import argparse

# Configuration: Files with these extensions will be processed
TARGET_EXTENSIONS = {'.md', '.qmd', '.rmd', '.markdown'}

def convert_gfm_callouts(text):
    """
    Transforms GFM blockquote callouts to Quarto div callouts.
    Returns the transformed string.
    """
    lines = text.splitlines()
    output_lines = []
    
    # Regex for start of callout: > [!type] Title
    callout_start_pattern = re.compile(r"^>\s*\[!([a-zA-Z0-9-]+)\]\s*(.*)$")
    
    in_callout = False
    
    for line in lines:
        match = callout_start_pattern.match(line)
        
        # CASE 1: Start of a new callout
        if match:
            if in_callout:
                output_lines.append(":::")
            
            callout_type = match.group(1).lower()
            callout_title = match.group(2).strip()
            
            if callout_title:
                header = f"::: {{.callout-{callout_type} title=\"{callout_title}\"}}"
            else:
                header = f"::: {{.callout-{callout_type}}}"
            
            output_lines.append(header)
            in_callout = True
            continue
            
        # CASE 2: Inside a callout
        if in_callout:
            if line.strip().startswith(">"):
                # Strip '>' and optional space
                content = line.lstrip(">")
                if content.startswith(" "):
                    content = content[1:]
                output_lines.append(content)
            else:
                # End of callout
                output_lines.append(":::")
                in_callout = False
                output_lines.append(line)
                
        # CASE 3: Normal text
        else:
            output_lines.append(line)

    if in_callout:
        output_lines.append(":::")

    return "\n".join(output_lines)

def process_file(filepath):
    """
    Backs up and converts a single file.
    """
    try:
        # 1. Create Backup
        # note.md -> note.md.bkp (Quarto ignores .bkp)
        backup_path = filepath + ".bkp"
        shutil.copy2(filepath, backup_path)
        
        # 2. Read Content
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # 3. Convert
        new_content = convert_gfm_callouts(original_content)

        # 4. Write Change (Only if changes were made)
        if new_content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[MODIFIED] {filepath}")
        else:
            # Optional: Delete backup if no changes? 
            # Better to keep it just in case logic is flawed, 
            # but usually, we just leave it.
            print(f"[NO CHANGE] {filepath}")

    except Exception as e:
        print(f"[ERROR] Could not process {filepath}: {e}")

def process_folder(folder_path):
    """
    Recursively walks the folder and processes matching files.
    """
    print(f"Scanning folder: {folder_path}...")
    
    count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Check extension
            _, ext = os.path.splitext(file)
            if ext.lower() in TARGET_EXTENSIONS:
                full_path = os.path.join(root, file)
                process_file(full_path)
                count += 1
                
    print(f"--- Processing Complete. Scanned {count} files. ---")

def main():
    parser = argparse.ArgumentParser(description="Batch convert GFM callouts to Quarto in a folder.")
    parser.add_argument("folder", help="Path to the folder containing notes")

    args = parser.parse_args()
    
    if os.path.isdir(args.folder):
        process_folder(args.folder)
    else:
        print(f"Error: The path '{args.folder}' is not a valid directory.")

if __name__ == "__main__":
    main()
