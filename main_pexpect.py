import pty
import sys


def version_tuple(v):
    return tuple(map(int, (v.split()[0].split("."))))


"""
    Script to emulate pseudo Terminal (to make usage of IntelliJ Debugger...)
"""

required_version: str = version_tuple('3.10.0')
actual_version = version_tuple(sys.version)

# print(sys.version)
# print(version_tuple(sys.version))
# print(version_tuple(required_version))


if actual_version < required_version:
    print(f'requires Python version at least 3.10 to run!')
    exit(1)
else:
    print(f'Python version {sys.version.split()[0]} is compatible!')
    python_version = '.'.join(map(str, actual_version[:2]))
    pty.spawn([f"python{python_version}", 'main.py'])

