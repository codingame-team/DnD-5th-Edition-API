import subprocess
import os


def get_git_files():
    try:
        # Get list of tracked files in git
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or git command failed")
        return []


def generate_git_tree():
    print("```")
    git_files = get_git_files()

    # Create dictionary to store directory structure
    tree = {}
    for file_path in git_files:
        parts = file_path.split("/")
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = None

    # Print tree structure
    def print_tree(structure, prefix=""):
        items = sorted(structure.items())
        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1
            print(f"{prefix}{'└── ' if is_last else '├── '}{name}")
            if subtree is not None:  # If it's a directory
                print_tree(subtree, prefix + ("    " if is_last else "│   "))

    print_tree(tree)
    print("```")


# Generate and print the tree
generate_git_tree()
