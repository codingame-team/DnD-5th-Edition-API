import pygame
import sys
import subprocess
import multiprocessing as mp
from enum import Enum
from typing import List
import os

from dao_classes import Character
from dungeon_pygame import save_character_gamestate, Game
from main import get_roster, save_character
from tools.cheat_functions import raise_dead_roster
from tools.common import cprint, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, RED, WHITE


class LT(Enum):
    DUNGEON = 1
    BOLTAC = 2


def go_to_location(character_name: str, location: LT):
    mp.set_start_method('spawn')  # Set the start method to 'spawn' to avoid fork issues
    target = explore_dungeon if location == LT.DUNGEON else shop_to_boltac
    proc = mp.Process(target=target, args=(character_name,))
    proc.start()


def shop_to_boltac(character_name):
    subprocess.run(['python', 'boltac_tp_pygame.py', character_name])


def explore_dungeon(character_name):
    subprocess.run(['python', 'dungeon_pygame.py', character_name])


def reset_ids_all(gamestates: List[Game]):
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


# Fonctions pour dessiner les menus et gérer les rectangles de texte
def draw_character_menu(screen, roster, scroll_offset, line_height, font):
    screen.fill(WHITE)

    text_rects = []
    for index, character in enumerate(roster):
        y_position = line_height * 2 + (index * line_height) - scroll_offset
        if 0 <= y_position < SCREEN_HEIGHT:
            if hasattr(character, 'class_type'):
                option = font.render(f"{character.name} (Level {character.level} {character.class_type})", True, RED)
            else:
                option = font.render(f"{character.name} (CR {character.level})", True, RED)
            rect = option.get_rect(topleft=(20, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)  # Placeholder for non-visible options

    option2 = font.render("Exit", True, BLACK)
    y_position = line_height * 2 + (len(roster) * line_height) - scroll_offset
    if 0 <= y_position < SCREEN_HEIGHT:
        rect = option2.get_rect(topleft=(20, y_position))
        screen.blit(option2, rect)
        text_rects.append(rect)
    else:
        text_rects.append(None)  # Placeholder for non-visible options

    return text_rects


def draw_radio_buttons(screen, font, selected_option):
    options = ["Explore Dungeon", "Shop to Boltac"]
    radio_button_positions = [(SCREEN_WIDTH - 330, 60), (SCREEN_WIDTH - 330, 100)]

    for i, option in enumerate(options):
        pos = radio_button_positions[i]
        pygame.draw.circle(screen, (0, 0, 0), pos, 7, 1)  # Draw the outer circle
        if selected_option == i:
            pygame.draw.circle(screen, (0, 0, 0), pos, 4)  # Draw the inner circle if selected
        text = font.render(option, True, (0, 0, 0))
        screen.blit(text, (pos[0] + 20, pos[1] - 10))


def main(roster):
    global scroll_offset
    clock = pygame.time.Clock()
    running = True
    selected_option = 0  # 0 for Explore Dungeon, 1 for Shop to Boltac

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                text_rects = draw_character_menu(screen, roster, scroll_offset, line_height, font)

                # Check radio button clicks
                for i, pos in enumerate([(SCREEN_WIDTH - 330, 60), (SCREEN_WIDTH - 330, 100)]):
                    if (pos[0] - 10 < mouse_pos[0] < pos[0] + 10) and (pos[1] - 10 < mouse_pos[1] < pos[1] + 10):
                        selected_option = i

                for index, rect in enumerate(text_rects):
                    if rect and rect.collidepoint(mouse_pos):
                        if index < len(roster):
                            selected_character = roster[index]
                            if not selected_character.is_dead:
                                go_to_location(selected_character.name, LT.DUNGEON if selected_option == 0 else LT.BOLTAC)
                                running = False  # Close the main loop after starting the game
                            else:
                                cprint(f'Cannot select character... {selected_character.name} is dead!')
                        else:
                            running = False  # Exit the menu if 'Exit' is clicked
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # Scroll up
                scroll_offset = max(scroll_offset - line_height, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # Scroll down
                max_offset = max(0, (len(roster) + 1) * line_height - SCREEN_HEIGHT + line_height * 2)
                scroll_offset = min(scroll_offset + line_height, max_offset)

        screen.fill(WHITE)
        draw_character_menu(screen, roster, scroll_offset, line_height, font)
        draw_radio_buttons(screen, font, selected_option)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    pygame.init()

    font = pygame.font.Font(None, 22)

    # Dimensions de la fenêtre du menu principal
    SCREEN_WIDTH, SCREEN_HEIGHT = 600, 300

    scroll_offset = 0
    line_height = 20

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Choose your character')

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    roster: List[Character] = get_roster(characters_dir)
    gamestate_dir = f'{abspath}/gameState/pygame'
    raise_dead_roster(roster, characters_dir)

    main(roster)
