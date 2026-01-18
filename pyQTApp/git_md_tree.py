import subprocess
import os


def get_git_files():
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
        return sorted(result.stdout.splitlines())
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git command failed")
        return []


def print_markdown_tree():
    files = get_git_files()
    if not files:
        return

    print("```markdown")
    last_path = []

    for file_path in files:
        current_path = file_path.split("/")

        # Compare with last path to determine where to start printing
        level = 0
        while level < len(current_path) - 1:
            if level >= len(last_path) or current_path[level] != last_path[level]:
                break
            level += 1

        # Print the path components
        for i in range(level, len(current_path)):
            prefix = "│   " * i
            if i == len(current_path) - 1:
                print(f"{prefix}├── {current_path[i]}")
            else:
                print(f"{prefix}├── {current_path[i]}/")

        last_path = current_path
    print("```")


# Generate and print the tree
print_markdown_tree()
