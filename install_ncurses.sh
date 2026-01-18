#!/bin/bash

pyinstaller --onefile rpg_ncurses.py --target-arch universal2 --name dungeon_tk
#    --add-data "collections:collections" \
#    --add-data "data:data" \
#    --add-data "maze_tk:maze_tk" \


## shellcheck disable=SC2089
#OUTPUT_DIR="$HOME/Home Dropbox/Philippe Mourey"
#cp dist/dungeon_tk "$OUTPUT_DIR"
