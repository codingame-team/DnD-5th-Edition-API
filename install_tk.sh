#!/bin/bash

pyinstaller --onefile \
    --add-data "collections:collections" \
    --add-data "data:data" \
    --add-data "maze_tk:maze_tk" \
    --add-data "sprites:sprites" \
    --exclude-module "sprites/rpgcharacterspack/big" \
    dungeon_tk.py

## shellcheck disable=SC2089
#OUTPUT_DIR="$HOME/Home Dropbox/Philippe Mourey"
#cp dist/dungeon_tk "$OUTPUT_DIR"
