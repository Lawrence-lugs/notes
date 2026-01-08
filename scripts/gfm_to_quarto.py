import re
import sys
import argparse

supported_callout_types = [
    'note',
    'tip',
    'important',
    'warning',
    'caution'
]

callout_conversion_table = {
    'quote':'note',
    'question':'tip',
    'example':'note'
}

def convert_gfm_callouts(text):
    lines = text.splitlines()
    output_lines = []
    
    # Regex to identify the start of a GFM callout
    # Captures: 1=Type (e.g., note, warning), 2=Title (optional)
    callout_start_pattern = re.compile(r"^>\s*\[!([a-zA-Z0-9-]+)\]\s*(.*)$")
    
    in_callout = False
    
    for line in lines:
        match = callout_start_pattern.match(line)
        
        if match:
            # If we were already in a callout, close the previous one first
            if in_callout:
                output_lines.append(":::")
            
            callout_type = match.group(1).lower()
            callout_title = match.group(2).strip()
            
            if callout_type.casefold() not in supported_callout_types:
                callout_type = 'note'
                if callout_type.casefold() in callout_conversion_table.keys():
                    callout_type = callout_conversion_table[callout_type]
                    if not callout_title:
                        callout_title = callout_conversion_table[callout_type]

            # Construct Quarto header
            if callout_title:
                header = f"::: {{.callout-{callout_type} title=\"{callout_title}\"}}"
            else:
                header = f"::: {{.callout-{callout_type}}}"
            
            output_lines.append(header)
            in_callout = True
            continue
            
        if in_callout:
            # Check if line continues the blockquote (starts with >)
            if line.strip().startswith(">"):
                # Remove the leading '>' and the first space if it exists
                content = line.lstrip(">")
                if content.startswith(" "):
                    content = content[1:]
                output_lines.append(content)
            else:
                # The blockquote has ended (line doesn't start with >)
                # Close the div
                output_lines.append(":::")
                in_callout = False
                # Append the current line as normal text
                output_lines.append(line)
                
        else:
            output_lines.append(line)

    if in_callout:
        output_lines.append(":::")

    return "\n".join(output_lines)

def main():
    parser = argparse.ArgumentParser(description="Convert GFM callouts to Quarto divs.")
    parser.add_argument("input_file", nargs='?', help="Input Markdown file path")
    parser.add_argument("-o", "--output", help="Output file path")

    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        print("Error: No input provided. Pipe text or provide a filename.")
        return

    converted_content = convert_gfm_callouts(content)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(converted_content)
    else:
        print(converted_content)

if __name__ == "__main__":
    main()
