#!/usr/bin/env python3
"""
Test de Validation Phase 2 - Migration Frontend
Vérifie que tous les modules s'importent correctement
"""

import sys
import os

# Colors for output
class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"{Color.GREEN}✅ {description:40}{Color.END} PASS")
        return True
    except Exception as e:
        print(f"{Color.RED}❌ {description:40}{Color.END} FAIL: {str(e)[:50]}")
        return False

def main():
    print(f"{Color.BLUE}{'='*70}{Color.END}")
    print(f"{Color.BLUE}  PHASE 2 - Test de Validation de Migration Frontend{Color.END}")
    print(f"{Color.BLUE}{'='*70}{Color.END}")
    print()

    tests = [
        # Core package
        ('dnd_5e_core', 'Package dnd-5e-core'),

        # Main games
        ('main', 'Main.py (console version)'),
        ('main_ncurses', 'Main NCurses'),

        # Pygame games
        ('dungeon_pygame', 'Dungeon Pygame'),
        ('dungeon_menu_pygame', 'Dungeon Menu Pygame'),
        ('boltac_tp_pygame', 'Boltac Trading Post Pygame'),
        ('monster_kills_pygame', 'Monster Kills Pygame'),

        # PyQt modules (will fail without PyQt5, that's ok)
        ('pyQTApp.common', 'PyQt Common Module'),
        ('pyQTApp.qt_common', 'PyQt Table Utils'),
        ('pyQTApp.combat_models', 'PyQt Combat Models'),
    ]

    results = []
    for module, desc in tests:
        result = test_import(module, desc)
        results.append(result)

    # PyQt modules (optional, may fail without PyQt5)
    print()
    print(f"{Color.YELLOW}PyQt Modules (optional):{Color.END}")
    pyqt_tests = [
        ('pyQTApp.Castle.Tavern_module', 'Tavern Module'),
        ('pyQTApp.Castle.Inn_module', 'Inn Module'),
        ('pyQTApp.Castle.Boltac_module', 'Boltac Module'),
        ('pyQTApp.Castle.Cant_module', 'Cant Module'),
    ]

    pyqt_results = []
    for module, desc in pyqt_tests:
        result = test_import(module, desc)
        pyqt_results.append(result)

    # Summary
    print()
    print(f"{Color.BLUE}{'='*70}{Color.END}")
    total_tests = len(results)
    passed = sum(results)
    failed = total_tests - passed

    pyqt_total = len(pyqt_results)
    pyqt_passed = sum(pyqt_results)

    print(f"Core Tests:  {Color.GREEN}{passed}/{total_tests} PASSED{Color.END}", end="")
    if failed > 0:
        print(f", {Color.RED}{failed} FAILED{Color.END}")
    else:
        print()

    print(f"PyQt Tests:  {Color.YELLOW}{pyqt_passed}/{pyqt_total} PASSED{Color.END} (optional)")

    print(f"{Color.BLUE}{'='*70}{Color.END}")

    if passed == total_tests:
        print(f"{Color.GREEN}✅ PHASE 2 MIGRATION: SUCCESS!{Color.END}")
        print(f"{Color.GREEN}All core modules import correctly.{Color.END}")
        return 0
    else:
        print(f"{Color.RED}❌ PHASE 2 MIGRATION: INCOMPLETE{Color.END}")
        print(f"{Color.RED}Some modules failed to import.{Color.END}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

