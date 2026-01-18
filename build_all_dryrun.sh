#!/bin/bash

# Dry-run wrapper for build_all.sh
# Prints what would be executed without running pip/pyinstaller

set -e

echo "DRY RUN: showing build steps without executing pip or pyinstaller"

echo "Would run: pip install -e ../dnd-5e-core (if local) or pip install dnd-5e-core"
echo "Would check pyinstaller and install if missing"
echo "Would remove build/ dist/"
echo "Would run: pyinstaller main.spec --clean --noconfirm (if main.spec exists)"
echo "Would run: pyinstaller dungeon_menu_pygame.spec --clean --noconfirm (if dungeon_menu_pygame.spec exists)"
echo "Would list dist/ contents"

echo "Dry run complete. To perform actual build: ./build_all.sh"

