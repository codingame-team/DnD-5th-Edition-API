#!/usr/bin/env python3
"""
Script to emulate pseudo Terminal (to make usage of IntelliJ Debugger or non-TTY environments)
✅ MIGRATED VERSION - Launches v2 scripts using dnd-5e-core package

Supports both main_v2.py and main_ncurses_v2_FULL.py

Usage:
    python main_pexpect.py              # Launch main_ncurses_v2_FULL.py with pseudo-TTY
    python main_pexpect.py ncurses      # Launch main_ncurses_v2_FULL.py with pseudo-TTY
    python main_pexpect.py main         # Launch main_v2.py with pseudo-TTY (explicit)
"""

import pty
import sys
import os


def version_tuple(v):
    return tuple(map(int, (v.split()[0].split("."))))


def is_tty():
    """Check if running in a TTY terminal"""
    return sys.stdin.isatty() and sys.stdout.isatty()


def get_script_to_run():
    """Determine which script to run based on arguments"""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['--help', '-h', 'help']:
            print(__doc__)
            print("\n✅ MIGRATED VERSION - Uses dnd-5e-core package")
            print("\nAvailable options:")
            print("  ncurses, nc, n  - Launch main_ncurses.py (NCurses interface)")
            print("  main, text, t, m - Launch main.py (text interface v2)")
            print("  --help, -h      - Show this help message")
            print("\nExamples:")
            print("  python main_pexpect.py           # Default: main_ncurses.py")
            print("  python main_pexpect.py ncurses   # NCurses version v2")
            print("  python main_pexpect.py main      # Text version v2")
            sys.exit(0)
        elif arg in ['ncurses', 'nc', 'n']:
            return 'main_ncurses.py'
        elif arg in ['main', 'text', 't', 'm']:
            return 'main.py'
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python main_pexpect.py [ncurses|main|--help]")
            sys.exit(1)
    # Default to ncurses
    return 'main_ncurses.py'


def run_with_pty(script_name):
    """Run script with pseudo-TTY"""
    python_version = '.'.join(map(str, actual_version[:2]))
    python_cmd = f"python{python_version}"

    print(f"Running {script_name} with pseudo-TTY...")
    print(f"Command: {python_cmd} {script_name}")
    print("-" * 60)

    try:
        pty.spawn([python_cmd, script_name])
    except Exception as e:
        print(f"\nError running script: {e}")
        sys.exit(1)


def run_directly(script_name):
    """Run script directly (already in TTY)"""
    python_version = '.'.join(map(str, actual_version[:2]))
    python_cmd = f"python{python_version}"

    print(f"Running {script_name} directly (TTY detected)...")
    print(f"Command: {python_cmd} {script_name}")
    print("-" * 60)

    os.execvp(python_cmd, [python_cmd, script_name])


# Check Python version
required_version = version_tuple('3.10.0')
actual_version = version_tuple(sys.version)

if actual_version < required_version:
    print(f'ERROR: Requires Python version at least 3.10 to run!')
    print(f'Current version: {sys.version.split()[0]}')
    sys.exit(1)

print(f'✓ Python version {sys.version.split()[0]} is compatible!')

# Determine which script to run
script_to_run = get_script_to_run()

# Check if script exists
if not os.path.exists(script_to_run):
    print(f"ERROR: Script '{script_to_run}' not found!")
    sys.exit(1)

# Check TTY and run accordingly
if is_tty():
    print(f"✓ TTY detected - running directly")
    run_directly(script_to_run)
else:
    print(f"⚠ No TTY detected - using pseudo-TTY")
    run_with_pty(script_to_run)

