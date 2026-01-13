import os
import re
import argparse
from pathlib import Path

# Configuration: Files with these extensions will be processed
TARGET_EXTENSIONS = {'.md', '.qmd', '.rmd', '.markdown'}

# Regex Patterns
CALLOUT_START = re.compile(r"^>\s*\[!([a-zA-Z0-9-]+)\]\s*(.*)$")
LIST_MARKER = re.compile(r"^(\s*)([-*+]|\d+\.)\s+")
HEADER_MARKER = re.compile(r"^#+\s+")
CODE_FENCE = re.compile(r"^\s*```")
MERMAID = re.compile(r"^\s*```mermaid\b")

def convert_callouts(text):
    """
    Transforms GFM blockquote callouts to Quarto div callouts.
    """
    lines = text.splitlines()
    output_lines = []
    
    in_callout = False
    
    for line in lines:
        match = CALLOUT_START.match(line)
        
        # 1. Start of a callout
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
            
        # 2. Inside a callout
        if in_callout:
            # Check if line continues the blockquote (starts with >)
            if line.strip().startswith(">"):
                # Remove the leading '>' and optional space
                content = line.lstrip(">")
                if content.startswith(" "):
                    content = content[1:]
                output_lines.append(content)
            else:
                # End of callout
                output_lines.append(":::")
                in_callout = False
                output_lines.append(line)
        
        # 3. Normal text
        else:
            output_lines.append(line)

    if in_callout:
        output_lines.append(":::")

    return "\n".join(output_lines)

def convert_mermaid_block(text):
    """
    Converts a mermaid block (```mermaid)
    into an executable mermaid block (```{mermaid})
    """
    lines = text.splitlines()
    output_lines = []
    in_code_block = False

    for i, line in enumerate(lines):
        if MERMAID.match(line):
            output_lines.append("```{mermaid}")
        else:
            output_lines.append(line)

    return "\n".join(output_lines)

def ensure_header_spacing(text):
    """
    Ensure empty lines exist before headers (#).
    Ignores headers inside code blocks.
    """
    lines = text.splitlines()
    output_lines = []
    in_code_block = False

    for i, line in enumerate(lines):
        # Toggle code block state
        if CODE_FENCE.match(line):
            in_code_block = not in_code_block

        # Check for header
        if not in_code_block and HEADER_MARKER.match(line):
            # If output is not empty and previous line is not empty, add newline
            if output_lines and output_lines[-1].strip() != "":
                output_lines.append("")
        
        output_lines.append(line)
        
    return "\n".join(output_lines)

def ensure_list_spacing(text):
    """
    Ensure empty lines exist before the START of a list.
    Ignores lists inside code blocks.
    """
    lines = text.splitlines()
    output_lines = []
    in_code_block = False
    in_list_block = False

    for i, line in enumerate(lines):
        # Toggle code block state
        if CODE_FENCE.match(line):
            in_code_block = not in_code_block

        is_list_item = bool(LIST_MARKER.match(line))
        
        if not in_code_block:
            if is_list_item:
                # If we were NOT in a list block previously, this is the first item
                if not in_list_block:
                    # If previous line exists and is not empty, insert newline
                    if output_lines and output_lines[-1].strip() != "":
                        output_lines.append("")
                in_list_block = True
            elif line.strip() == "":
                # Empty line keeps us in "neutral", usually resets list context in markdown
                in_list_block = False
            else:
                # Text line breaks the list context
                in_list_block = False

        output_lines.append(line)

    return "\n".join(output_lines)

def process_file(source_path, dest_path):
    """
    Reads source, applies transformations, writes to dest.
    """
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = convert_callouts(content)
        content = convert_mermaid_block(content)
        content = ensure_header_spacing(content)
        content = ensure_list_spacing(content)
        

        # If destination exists, check if content is identical
        if dest_path.exists():
            with open(dest_path, 'r', encoding='utf-8') as f:
                dest_content = f.read()
            
            if content == dest_content:
                # Content is identical; do not touch the file.
                return

        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Processed: {Path(source_path).name} -> {Path(dest_path).name}")

    except Exception as e:
        print(f"[ERROR] Failed to process {source_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert GFM notes to Quarto notes.")
    parser.add_argument("input_dir", help="Source folder")
    parser.add_argument("output_dir", help="Destination folder")

    args = parser.parse_args()
    
    input_path = Path(args.input_dir)
    output_path = Path(args.output_dir)

    if not input_path.exists():
        print(f"Error: Input directory '{input_path}' does not exist.")
        return

    print(f"Starting conversion: {input_path} -> {output_path}")

    file_count = 0
    
    # Walk through the input directory
    for root, _, files in os.walk(input_path):
        for file in files:
            file_path = Path(root) / file
            
            # Filter extensions
            if file_path.suffix.lower() in TARGET_EXTENSIONS:
                # Calculate relative path to maintain structure
                # e.g. _notes/physics/mech.md -> physics/mech.md
                rel_path = file_path.relative_to(input_path)
                dest_file_path = output_path / rel_path
                
                # Turn all files into qmd
                dest_file_path = dest_file_path.with_suffix('.qmd')
                
                process_file(file_path, dest_file_path)
                file_count += 1

    # Copy attachments folder over
    import shutil
    source_attachments = f"{input_path}/attachments"
    dest_attachments = f"{output_path}/attachments"
    if os.path.exists(source_attachments):
        shutil.copytree(source_attachments, 
                        dest_attachments, 
                        dirs_exist_ok=True)

    print(f"--- Completed. Processed {file_count} files. ---")

if __name__ == "__main__":
    main()
