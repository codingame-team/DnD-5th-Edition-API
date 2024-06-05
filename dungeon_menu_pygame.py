from tools.common import cprint
import os
from typing import List

import pygame
import sys
import subprocess
import multiprocessing as mp

from dao_classes import Character
from main import get_roster
from tools.cheat_functions import raise_dead

# Initialisation de Pygame
pygame.init()

# Définir les dimensions de la fenêtre
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Choix du personnage')

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Police
font = pygame.font.Font(None, 24)

# Variables pour le défilement
scroll_offset = 0
line_height = 25

# Fonctions pour dessiner les menus et gérer les rectangles de texte
def draw_character_menu(roster, scroll_offset):
    screen.fill(WHITE)
    # title = font.render("=== Choose Your Character ===", True, BLACK)
    # screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, line_height))

    text_rects = []
    for index, character in enumerate(roster):
        y_position = line_height * 2 + (index * line_height) - scroll_offset
        if 0 <= y_position < SCREEN_HEIGHT:
            # option = font.render(f"{index + 1}. {character.name} (Level {character.level} {character.class_type})", True, RED)
            option = font.render(f"{character.name} (Level {character.level} {character.class_type})", True, RED)
            rect = option.get_rect(center=(SCREEN_WIDTH // 2, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)  # Placeholder for non-visible options

    # option2 = font.render(f"{len(roster) + 1}. Exit", True, BLACK)
    option2 = font.render(f"Exit", True, BLACK)
    y_position = line_height * 2 + (len(roster) * line_height) - scroll_offset
    if 0 <= y_position < SCREEN_HEIGHT:
        rect = option2.get_rect(center=(SCREEN_WIDTH // 2, y_position))
        screen.blit(option2, rect)
        text_rects.append(rect)
    else:
        text_rects.append(None)  # Placeholder for non-visible options

    return text_rects

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
    selected_character = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                text_rects = draw_character_menu(roster, scroll_offset)
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

        draw_character_menu(roster, scroll_offset)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    roster: List[Character] = get_roster(characters_dir)
    raise_dead(roster, characters_dir)
    main(roster)
