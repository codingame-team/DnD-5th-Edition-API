#!/usr/bin/env python3
"""
Test script for main_ncurses.py
Verifies basic functionality without requiring full game data
"""

import curses
import time


def test_ui(stdscr):
    """Test basic ncurses functionality"""
    curses.curs_set(0)
    stdscr.clear()

    # Test 1: Basic display
    stdscr.addstr(0, 0, "=== NCurses Test Suite ===", curses.A_BOLD)
    stdscr.addstr(2, 0, "Test 1: Basic display")
    stdscr.addstr(3, 2, "✓ Text rendering works")
    stdscr.refresh()
    time.sleep(1)

    # Test 2: Colors
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.addstr(5, 0, "Test 2: Color support")
        stdscr.addstr(6, 2, "✓ Colors available", curses.color_pair(1))
    else:
        stdscr.addstr(5, 0, "Test 2: Color support")
        stdscr.addstr(6, 2, "⚠ Colors not available")
    stdscr.refresh()
    time.sleep(1)

    # Test 3: Terminal size
    lines, cols = stdscr.getmaxyx()
    stdscr.addstr(8, 0, "Test 3: Terminal size")
    stdscr.addstr(9, 2, f"Size: {cols}x{lines}")

    if cols >= 80 and lines >= 24:
        stdscr.addstr(10, 2, "✓ Size OK for game", curses.color_pair(1) if curses.has_colors() else 0)
    else:
        stdscr.addstr(10, 2, f"⚠ Size too small (need 80x24)", curses.color_pair(2) if curses.has_colors() else 0)
    stdscr.refresh()
    time.sleep(1)

    # Test 4: Keyboard input
    stdscr.addstr(12, 0, "Test 4: Keyboard input")
    stdscr.addstr(13, 2, "Press any key to continue...")
    stdscr.refresh()

    key = stdscr.getch()
    key_name = curses.keyname(key).decode('utf-8') if isinstance(key, int) else str(key)
    stdscr.addstr(14, 2, f"✓ Key pressed: {key_name}")
    stdscr.refresh()
    time.sleep(1)

    # Test 5: Menu simulation
    stdscr.clear()
    stdscr.addstr(0, 0, "=== Menu Test ===", curses.A_BOLD | curses.A_REVERSE)

    menu_items = ["Start Game", "Load Game", "Options", "Quit"]
    cursor = 0

    while True:
        stdscr.addstr(2, 0, "Use ↑/↓ or j/k to navigate, Enter to select, q to quit")

        for idx, item in enumerate(menu_items):
            marker = "►" if idx == cursor else " "
            attr = curses.A_REVERSE if idx == cursor else 0
            stdscr.addstr(4 + idx, 2, f"{marker} {item}", attr)

        stdscr.addstr(10, 0, f"Current selection: {menu_items[cursor]}")
        stdscr.refresh()

        c = stdscr.getch()

        if c in (curses.KEY_DOWN, ord('j')):
            cursor = min(cursor + 1, len(menu_items) - 1)
        elif c in (curses.KEY_UP, ord('k')):
            cursor = max(0, cursor - 1)
        elif c in (ord('\n'), ord('\r')):
            stdscr.clear()
            stdscr.addstr(0, 0, f"You selected: {menu_items[cursor]}", curses.A_BOLD)
            stdscr.addstr(2, 0, "Press any key to return to menu...")
            stdscr.refresh()
            stdscr.getch()
            stdscr.clear()
        elif c == ord('q'):
            break

    # Final message
    stdscr.clear()
    stdscr.addstr(0, 0, "=== All Tests Complete ===", curses.A_BOLD)
    stdscr.addstr(2, 0, "✓ NCurses is working correctly")
    stdscr.addstr(3, 0, "✓ Ready to run main_ncurses.py")
    stdscr.addstr(5, 0, "Press any key to exit...")
    stdscr.refresh()
    stdscr.getch()


def main():
    """Run the test suite"""
    try:
        curses.wrapper(test_ui)
        print("\n✓ All tests passed!")
        print("You can now run: python main_ncurses.py")
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

