import os
import sys

import pygame

from dao_classes import Character
from dungeon_pygame import Game, load_character_gamestate, WHITE, RED


def draw_monster_kills(screen, font, monster_kills):
    index: int = 0
    text_rects = []
    for monster_name, count in monster_kills.items():
        y_position = line_height * 2 + (index * line_height) - scroll_offset
        if 0 <= y_position < SCREEN_HEIGHT:
            option = font.render(f"{monster_name} : {count}", True, RED)
            rect = option.get_rect(topleft=(20, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)  # Placeholder for non-visible options
        index += 1
    return text_rects

def main(game: Game):
    global scroll_offset
    clock = pygame.time.Clock()
    running = True

    monster_kills: dict = {}
    for m in game.kills:
        if m.name in monster_kills:
            monster_kills[m.name] += 1
        else:
            monster_kills[m.name] = 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # Scroll up
                scroll_offset = max(scroll_offset - line_height, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # Scroll down
                max_offset = max(0, (len(monster_kills) + 1) * line_height - SCREEN_HEIGHT + line_height * 2)
                scroll_offset = min(scroll_offset + line_height, max_offset)
        screen.fill(WHITE)
        draw_monster_kills(screen, font, monster_kills)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()

    # Set up font
    font = pygame.font.Font(None, 24)

    # Dimensions de la fenêtre du menu principal
    SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
    scroll_offset = 0
    line_height = 20
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    gamestate_dir = f'{abspath}/gameState/pygame'

    character_name: str = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'

    try:
        pygame.display.set_caption(f"Monster kills by {character_name}")
        # hero: Character = load_character(character_name, characters_dir)
        saved_game: Game = load_character_gamestate(character_name, gamestate_dir)
        main(saved_game)
    except IndexError:
        print(f"Character name <{character_name}> not found in roster")

