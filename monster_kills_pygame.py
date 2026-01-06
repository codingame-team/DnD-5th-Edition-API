from collections import Counter
import pygame
import os
import sys

# ============================================
# MIGRATION: Add dnd-5e-core to path (development mode)
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
from dnd_5e_core.entities import Character, Monster

# Note: Data directory is now in dnd-5e-core/data and will be auto-detected

from dungeon_pygame import load_character_gamestate
from tools.common import resource_path, get_save_game_path

print("✅ [MIGRATION v2] monster_kills_pygame.py - Using dnd-5e-core package")
print()


def load_monsters_images(monsters: dict) -> dict:
    monster_images_dir = resource_path('images/monsters/tokens')
    monster_images = {}
    for filename in os.listdir(monster_images_dir):
        monster_name, _ = os.path.splitext(filename)
        if monster_name not in monsters:
            continue
        image_path = os.path.join(monster_images_dir, filename)
        original_image = pygame.image.load(image_path)
        # Resize the image to 280x280 pixels
        monster_images[monster_name] = pygame.transform.scale(original_image, (280, 280))
    return monster_images


def draw_screen(monsters, scroll_offset):
    screen.fill(white)

    # Draw items with scrolling
    for i, (monster_name, (cr, count)) in enumerate(monsters.items()):
        color = black if i == selected_index else (100, 100, 100)
        item: str = f"{monster_name} (cr {cr}) : {count}"
        text = font.render(item, True, color)

        # Calculate the vertical position of the text with reduced line spacing
        item_y = 50 + i * 30 - scroll_offset  # Decreased from 40 to 30
        if 0 <= item_y <= screen_height - 100:
            screen.blit(text, (50, item_y))

    # Draw selected monster image
    selected_monster_name = list(monsters.keys())[selected_index]
    monster_image = monster_images.get(selected_monster_name)
    if monster_image is not None:
        monster_rect = (screen_width - monster_image.get_width() - 20, 20)
        screen.blit(monster_image, monster_rect)

    pygame.display.flip()


def handle_scrolling(monsters, scroll_offset):
    # Calculate the desired position of the selected item to keep it centered
    center_y = screen_height // 2 - 50  # Center position, accounting for top margin
    selected_y = selected_index * 30  # Decreased from 40 to 30 for line height

    # Adjust scroll_offset to center the selected item
    if selected_y < scroll_offset + center_y:
        scroll_offset = selected_y - center_y
    elif selected_y > scroll_offset + center_y + 30:  # Adjusted from 40 to 30 for item height
        scroll_offset = selected_y - center_y - 30

    # Bound the scroll offset to not exceed the top or bottom of the list
    max_scroll_offset = max(0, len(monsters) * 30 - (screen_height - 100))  # Updated to 30
    scroll_offset = max(0, min(scroll_offset, max_scroll_offset))

    return scroll_offset


def main(monsters):
    global selected_index
    running = True
    clock = pygame.time.Clock()
    scroll_offset = 0

    key_delay = 125  # Delay in milliseconds between key repeats
    last_key_time = 0

    while running:
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()  # Detect if keys are held

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        # Handle key repetition for UP and DOWN arrows
        if keys[pygame.K_DOWN] and current_time - last_key_time > key_delay:
            if selected_index < len(monsters) - 1:  # Stop at the last item
                selected_index += 1
            last_key_time = current_time
        elif keys[pygame.K_UP] and current_time - last_key_time > key_delay:
            if selected_index > 0:  # Stop at the first item
                selected_index -= 1
            last_key_time = current_time

        # Handle scrolling
        scroll_offset = handle_scrolling(monsters, scroll_offset)

        # Draw the updated screen with scrolling
        draw_screen(monsters, scroll_offset)

        clock.tick(30)


def run(character_name: str = 'Brottor'):
    global selected_index, monster_images
    global screen, font, white, black
    global screen_width, screen_height

    # Ensure Pygame is initialized (but don't reinitialize if already running)
    if not pygame.get_init():
        pygame.init()

    # Screen dimensions
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Monster List Navigation with Scrolling")

    # Colors
    white = (255, 255, 255)
    black = (0, 0, 0)

    # Font - Decreased font size from 24 to 18
    font = pygame.font.Font(None, 24)

    game_path = get_save_game_path()
    gamestate_dir = f'{game_path}/pygame'

    try:
        game = load_character_gamestate(character_name, gamestate_dir)
        if not hasattr(game, 'kills'):
            game.kills = []
        monsters_count = Counter([m.name for m in game.kills])
        pygame.display.set_caption(f"{len(monsters_count)} different types of monsters killed by {character_name} for a total of {len(game.kills)} kills")
        monsters = {m.name: (m.challenge_rating, monsters_count[m.name]) for m in game.hero.kills}
        monsters = dict(sorted(monsters.items(), key=lambda x: x[1], reverse=True))

        monster_images = load_monsters_images(monsters)
        selected_index = 0

        if not game:
            print(f"No saved game found for {character_name}")
        else:
            main(monsters)
    except IndexError:
        print(f"Character name <{character_name}> not found in roster")
    except AttributeError:
        print(f"Character name <{character_name}> has no saved game")


if __name__ == "__main__":
    run()
