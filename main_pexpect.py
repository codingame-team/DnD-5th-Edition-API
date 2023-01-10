import pty

"""
    Script to emulate pseudo Terminal (to make usage of IntelliJ Debugger...)
"""

pty.spawn(['python3.11', 'main.py'])