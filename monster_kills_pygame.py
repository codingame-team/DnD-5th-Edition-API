import os
import sys
from collections import Counter

import pygame

from dungeon_pygame import Game, Level, Room, load_character_gamestate, WHITE, RED

from tools.common import resource_path, get_save_game_path

# Define colors
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 0, 0)  # Red color for highlighting
HINT_COLOR = (128, 128, 128)  # Gray color for hints

def draw_typing_hint(screen, font, hint_text):
    hint_surface = font.render(hint_text, True, HINT_COLOR)
    hint_rect = hint_surface.get_rect()
    hint_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
    screen.blit(hint_surface, hint_rect)


def draw_monster_kills(screen, font, monster_kills, scroll_offset, selected_image_index, crs):
    text_rects = []
    y = scroll_offset
    for i, (monster_name, count) in enumerate(monster_kills.items()):
        text = f"{monster_name} (cr {crs[monster_name]}) : {count}"
        text_surface = font.render(text, True, BLACK)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (20, y)
        if i == selected_image_index:
            # Highlight the selected monster's text
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, text_rect, 2)  # Draw a red rectangle around the text
            text_surface = font.render(text, True, HIGHLIGHT_COLOR)  # Render the text in red
        screen.blit(text_surface, text_rect.topleft)
        text_rects.append((text_rect, monster_name))
        y += line_height
    return text_rects


def main(game: Game):
    global scroll_offset

    clock = pygame.time.Clock()
    running = True
    show_monster_image = False
    monster_image_surface = None

    if not hasattr(game, 'kills'):
        game.kills = []
    crs = {m.name: m.challenge_rating for m in game.kills}

    monster_kills = Counter(m.name for m in game.kills)
    monster_kills = dict(sorted(monster_kills.items(), key=lambda x: crs.get(x[0]), reverse=True))

    selected_image_index = 0
    num_images = len(monster_kills)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:  # Scroll up
                    selected_image_index = max(selected_image_index - 1, 0)
                elif event.key == pygame.K_DOWN:  # Scroll down
                    selected_image_index = min(selected_image_index + 1, num_images - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # Scroll up
                scroll_offset = max(scroll_offset - line_height, 0)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # Scroll down
                max_offset = max(0, (len(monster_kills) + 1) * line_height - SCREEN_HEIGHT + line_height * 2)
                scroll_offset = min(scroll_offset + line_height, max_offset)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for rect, monster_name in text_rects:
                    if rect and rect.collidepoint(mouse_pos):
                        show_monster_image = True
                        monster_image_surface = monster_images.get(monster_name)
                        break
                else:
                    show_monster_image = False
                    monster_image_surface = None

        screen.fill(WHITE)
        text_rects = draw_monster_kills(screen, font, monster_kills, scroll_offset, selected_image_index, crs)

        # if show_monster_image and monster_image_surface:
        #     screen.blit(monster_image_surface, (SCREEN_WIDTH - monster_image_surface.get_width() - 20, 20))

        selected_monster_name = list(monster_kills.keys())[selected_image_index]
        monster_image_surface = monster_images.get(selected_monster_name)

        if monster_image_surface is not None:
            screen.blit(monster_image_surface, (SCREEN_WIDTH - monster_image_surface.get_width() - 20, 20))

        # Draw typing hint
        draw_typing_hint(screen, font, "Use arrow keys to navigate, [Esc] to return to main menu")

        pygame.display.flip()
        clock.tick(60)

    # pygame.quit()
    # sys.exit()

def run(character_name: str ='Brottor'):
    global scroll_offset, line_height, monster_images
    global SCREEN_WIDTH, SCREEN_HEIGHT
    global game_path, characters_dir, gamestate_dir
    global monster_kills, crs
    global selected_image_index, num_images, text_rects
    global screen, font

    pygame.init()

    # Set up font
    font = pygame.font.Font(None, 24)

    # Screen dimensions
    SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800
    scroll_offset = 0
    line_height = 20
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'


    # Load monster images
    monster_images = {}
    monster_images_dir = resource_path('images/monsters/tokens')
    for filename in os.listdir(monster_images_dir):
        monster_name, _ = os.path.splitext(filename)
        image_path = os.path.join(monster_images_dir, filename)
        original_image = pygame.image.load(image_path)
        # Resize the image to 280x280 pixels
        monster_images[monster_name] = pygame.transform.scale(original_image, (280, 280))

    try:
        pygame.display.set_caption(f"Monster kills by {character_name}")
        saved_game = load_character_gamestate(character_name, gamestate_dir)
        if not saved_game:
            print(f"No saved game found for {character_name}")
        else:
            main(saved_game)
    except IndexError:
        print(f"Character name <{character_name}> not found in roster")

if __name__ == "__main__":
    # character_name = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'
    run()
