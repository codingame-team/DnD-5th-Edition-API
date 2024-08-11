#!/bin/bash

pyinstaller --onefile \
    --add-data "collections:collections" \
    --add-data "data:data" \
    --add-data "sprites:sprites" \
    --add-data "images:images" \
    --add-data "maze:maze" \
    --add-data "Tables:Tables" \
    --add-data "gameState:gameState" \
    --exclude-module "sprites/rpgcharacterspack/big" \
    dungeon_menu_pygame.py
