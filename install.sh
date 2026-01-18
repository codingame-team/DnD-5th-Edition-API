#!/bin/bash

pyinstaller --onefile \
    --add-data "collections:collections" \
    --add-data "data:data" \
    --add-data "sprites:sprites" \
    --add-data "sounds:sounds" \
    --add-data "images:images" \
    --add-data "maze:maze" \
    --add-data "Tables:Tables" \
    --add-data "gameState:gameState" \
    --exclude-module "sprites/rpgcharacterspack/big" \
    dungeon_menu_pygame.py

# shellcheck disable=SC2089
OUTPUT_DIR="$HOME/Home Dropbox/Philippe Mourey"
cp dist/dungeon_menu_pygame "$OUTPUT_DIR"
