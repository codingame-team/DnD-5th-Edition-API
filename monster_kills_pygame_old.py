import os
import sys
from collections import Counter
import pygame
from dungeon_pygame import Game, load_character_gamestate, WHITE, RED
from tools.common import resource_path, get_save_game_path

# Define colors
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 0, 0)  # Red color for highlighting
HINT_COLOR = (128, 128, 128)  # Gray color for hints

SCROLL_SPEED = 20  # Pixels to scroll per key press or mouse wheel movement

def draw_typing_hint(screen, font, hint_text):
    lines = hint_text.split('\n')
    line_height = font.get_linesize()
    total_height = line_height * len(lines)

    for i, line in enumerate(lines):
        hint_surface = font.render(line.strip(), True, HINT_COLOR)
        hint_rect = hint_surface.get_rect()
        hint_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20 - (len(lines) - 1 - i) * line_height)
        screen.blit(hint_surface, hint_rect)

def draw_monster_kills(screen, font, monster_kills, scroll_offset, selected_image_index, crs):
    text_rects = []
    y = scroll_offset
    total_height = 0

    for i, (monster_name, count) in enumerate(monster_kills.items()):
        text = f"{monster_name} (cr {crs[monster_name]}) : {count}"
        text_surface = font.render(text, True, BLACK)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (20, y)
        total_height = max(total_height, text_rect.bottom)

        # Highlight the selected item
        if i == selected_image_index:
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, text_rect, 2)  # Draw a red rectangle around the selected text

        # Draw only if within screen bounds
        if 0 <= text_rect.top < SCREEN_HEIGHT and 0 <= text_rect.bottom <= SCREEN_HEIGHT:
            screen.blit(text_surface, text_rect)

        text_rects.append((text_rect, monster_name))
        y += text_rect.height + 5  # Add some spacing between lines

    return text_rects, total_height

def handle_scrolling(event, scroll_offset, total_height, num_items, selected_image_index, line_height):
    # Handle mouse wheel scrolling
    if event.type == pygame.MOUSEWHEEL:
        scroll_offset += -event.y * SCROLL_SPEED  # Use -event.y because mouse wheel is inverted
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            selected_image_index = max(selected_image_index - 1, 0)
        elif event.key == pygame.K_DOWN:
            selected_image_index = min(selected_image_index + 1, num_items - 1)

    # Ensure selected index is within bounds
    selected_image_index = max(0, min(selected_image_index, num_items - 1))

    # Ensure selected item stays within bounds of visible area and center it
    center_y = SCREEN_HEIGHT // 2
    selected_item_y = selected_image_index * (line_height + 5)

    # Ensure the scroll_offset doesn't move beyond the last page
    max_scroll_offset = -(total_height - SCREEN_HEIGHT)
    scroll_offset = center_y - selected_item_y - (line_height // 2)

    # Adjust scrolling boundaries so that the content doesn't go off-screen
    scroll_offset = min(0, max(max_scroll_offset, scroll_offset))

    return scroll_offset, selected_image_index

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

    # In your main game loop:
    scroll_offset = 0
    total_height = 0

    while running:
        text_rects = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scroll_offset, selected_image_index = handle_scrolling(
                event, scroll_offset, total_height, num_images, selected_image_index, line_height
            )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
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
        text_rects, total_height = draw_monster_kills(screen, font, monster_kills, scroll_offset, selected_image_index, crs)

        selected_monster_name = list(monster_kills.keys())[selected_image_index]
        monster_image_surface = monster_images.get(selected_monster_name)

        if monster_image_surface is not None:
            screen.blit(monster_image_surface, (SCREEN_WIDTH - monster_image_surface.get_width() - 20, 20))

        draw_typing_hint(screen, font, "Use arrow keys to navigate,\n [Esc] to return to main menu")

        pygame.display.flip()
        clock.tick(60)

def run(character_name: str = 'Brottor'):
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
    run()
