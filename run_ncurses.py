#!/usr/bin/env python3
"""
Launcher script for DnD 5th Edition API NCurses version
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from main_ncurses import run_dnd_curses

        # Set terminal type if not set
        if "TERM" not in os.environ:
            os.environ["TERM"] = "xterm-256color"

        # Run the game
        print("Starting D&D 5th Edition NCurses...")
        print("Press Ctrl+C to exit at any time")
        print()

        run_dnd_curses()

    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        import traceback
        traceback.print_exc()
        sys.exit(1)

