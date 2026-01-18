import os

def generate_markdown_tree(startpath):
    output = []
    output.append("```")
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = '    ' * level
        output.append(f"{indent}{os.path.basename(root)}/")
        subindent = '    ' * (level + 1)
        for f in files:
            output.append(f"{subindent}{f}")
    output.append("```")
    return '\n'.join(output)


def generate_detailed_tree(startpath):
    print("# Project Structure")
    print("```")
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * level
        print(f"{indent}├── {os.path.basename(root)}/")
        subindent = '│   ' * (level + 1)
        for f in files:
            if f.endswith('.py'):  # Add more conditions as needed
                print(f"{subindent}├── {f:<20} # Python module")
            elif f.endswith('.md'):
                print(f"{subindent}├── {f:<20} # Documentation")
            else:
                print(f"{subindent}├── {f}")
    print("```")

# Usage
# generate_detailed_tree('.')

# Usage
print(generate_markdown_tree('.'))