from dungeon_pygame import Game, load_character_gamestate, save_character_gamestate
from tools.common import cprint, SCREEN_WIDTH, SCREEN_HEIGHT, draw_character_menu
import os
from typing import List

import pygame
import sys
import subprocess
import multiprocessing as mp

from dao_classes import Character
from main import get_roster, save_character
from tools.cheat_functions import raise_dead_roster


def start_game(character_name):
    mp.set_start_method('spawn')  # Set the start method to 'spawn' to avoid fork issues
    proc = mp.Process(target=run_game, args=(character_name,))
    proc.start()


def run_game(character_name):
    # Run the game here
    subprocess.run(['python', 'dungeon_pygame.py', character_name])


def main(roster):
    global scroll_offset
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                text_rects = draw_character_menu(screen, roster, scroll_offset, line_height, font)
                for index, rect in enumerate(text_rects):
                    if rect and rect.collidepoint(mouse_pos):
                        if index < len(roster):
                            selected_character = roster[index]
                            if selected_character.get_status != 'DEAD':
                                start_game(selected_character.name)
                                running = False  # Ferme la boucle principale après le démarrage du jeu
                            else:
                                cprint(f'Cannot select character... {selected_character.name} is dead!')
                        else:
                            running = False  # Quitte le menu si 'Exit' est cliqué
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # Molette vers le haut
                scroll_offset = max(scroll_offset - line_height, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # Molette vers le bas
                max_offset = max(0, (len(roster) + 1) * line_height - SCREEN_HEIGHT + line_height * 2)
                scroll_offset = min(scroll_offset + line_height, max_offset)

        draw_character_menu(screen, roster, scroll_offset, line_height, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

def reset_ids_all(gamestates):
    for game in gamestates:
        character = game.hero
        print('-----------------------------------')
        print(f'resetting ids for {character.name} - ID = {character.id}')
        print('-----------------------------------')
        if character.sc and character.can_cast:
            for s in character.sc.learned_spells:
                s.id = -1
                print(f'resetting spell id for {character.name}')
        if len(character.inventory) > 20:
            print('-----------------------------------')
            print(f'inventory too long for {character.name}')
            print('-----------------------------------')
            character.inventory = [None] * 20
        else:
            for item in character.inventory:
                    if item:
                        item.id = -1
                        print(f'resetting item id for {character.name}')
        save_character_gamestate(char=character, _dir=gamestate_dir, gamestate=game)
        save_character(char=character, _dir=characters_dir)

if __name__ == "__main__":
    # Initialisation de Pygame
    pygame.init()

    # Police
    font = pygame.font.Font(None, 24)

    # Variables pour le défilement
    scroll_offset = 0
    line_height = 25

    # Définir les dimensions de la fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Choix du personnage')

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    roster: List[Character] = get_roster(characters_dir)
    # Reset all sprites id
    # gamestate_dir = f'{abspath}/gameState/pygame'
    # gamestates: List[Game] = [load_character_gamestate(char.name, gamestate_dir) for char in roster]
    # reset_ids_all(gamestates)
    # exit()
    raise_dead_roster(roster, characters_dir)
    main(roster)
