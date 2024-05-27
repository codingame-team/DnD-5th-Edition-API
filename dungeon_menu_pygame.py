import os
from typing import List

import pygame
import sys
import subprocess
import multiprocessing as mp

from dao_classes import Character
from main import get_roster

# Initialisation de Pygame
pygame.init()

# Définir les dimensions de la fenêtre
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Choix du personnage')

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Police
font = pygame.font.Font(None, 36)

# # Classe de personnage
# class Character:
#     def __init__(self, name, color, health, strength):
#         self.name = name
#         self.color = color
#         self.health = health
#         self.strength = strength
#
#     def display_stats(self, screen, x, y):
#         text = font.render(f"Name: {self.name}, Health: {self.health}, Strength: {self.strength}", True, self.color)
#         screen.blit(text, (x, y))
#
# # Création des personnages
# characters = [
#     Character("Warrior", RED, 100, 20),
#     Character("Mage", BLUE, 80, 25),
#     Character("Archer", GREEN, 90, 15)
# ]

# Fonctions pour dessiner les menus
def draw_main_menu():
    screen.fill(WHITE)
    title = font.render("=== Main Menu ===", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    option1 = font.render("1. Choose Character", True, BLACK)
    screen.blit(option1, (SCREEN_WIDTH // 2 - option1.get_width() // 2, 150))

    option2 = font.render("2. Exit", True, BLACK)
    screen.blit(option2, (SCREEN_WIDTH // 2 - option2.get_width() // 2, 200))

def draw_character_menu(roster):
    screen.fill(WHITE)
    title = font.render("=== Choose Your Character ===", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    for index, character in enumerate(roster):
        option = font.render(f"{index + 1}. {character.name} (Level {character.level} {character.class_type})", True, RED)
        screen.blit(option, (SCREEN_WIDTH // 2 - option.get_width() // 2, 150 + index * 50))

    option2 = font.render(f"{len(roster) + 1}. Exit", True, BLACK)
    screen.blit(option2, (SCREEN_WIDTH // 2 - option2.get_width() // 2,  150 + len(roster) * 50))
    # back_option = font.render("4. Go back to Main Menu", True, BLACK)
    # screen.blit(back_option, (SCREEN_WIDTH // 2 - back_option.get_width() // 2, 150 + len(roster) * 50))

def start_game_old(character_name):
    # Lancer un autre script Python avec le nom du personnage comme argument
    subprocess.run(['python', 'dungeon_pygame.py', character_name])

def start_game(character_name):
    mp.set_start_method('spawn')  # Set the start method to 'spawn' to avoid fork issues
    proc = mp.Process(target=run_game, args=(character_name,))
    proc.start()

def run_game(character_name):
    # Run the game here
    subprocess.run(['python', 'dungeon_pygame.py', character_name])

def main(roster):
    clock = pygame.time.Clock()
    running = True
    in_main_menu = True
    in_character_menu = False
    selected_character = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # if in_main_menu:
                #     if event.key == pygame.K_1:
                #         in_main_menu = False
                #         in_character_menu = True
                #     elif event.key == pygame.K_2:
                #         running = False
                # elif in_character_menu:
                if event.key == pygame.K_0:
                    in_character_menu = False
                    in_main_menu = True
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    print(f'event key = {event.key}')
                    index = event.key - pygame.K_1
                    if index < len(roster):
                        selected_character = roster[index]
                        start_game(selected_character.name)
                        running = False  # Ferme la boucle principale après le démarrage du jeu

        # if in_main_menu:
        #     draw_main_menu()
        # if in_character_menu:
        draw_character_menu(roster)
        # else:
        if selected_character:
            start_game(selected_character.name)
            running = False  # Ferme la boucle principale après le démarrage du jeu
            # selected_character = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    roster: List[Character] = get_roster(characters_dir)
    main(roster)

