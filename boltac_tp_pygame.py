from __future__ import annotations

import os
import sys
from copy import copy

import pygame

from dnd_5e_core import Character

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
from dnd_5e_core.equipment import Armor, Equipment, Potion
from dnd_5e_core.ui import cprint

# Note: Data directory is now in dnd-5e-core/data and will be auto-detected

from main import save_character, load_character
from populate_functions import request_armor, request_weapon
from populate_rpg_functions import load_potions_collections
from tools.common import WHITE, RED, BLACK, get_save_game_path

print("✅ [MIGRATION v2] boltac_tp_pygame.py - Using dnd-5e-core package")
print()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
LINE_HEIGHT = 30
RADIO_BUTTON_POSITIONS = [(x, 350) for x in (50, 200, 350)]
BUY_BUTTON_POS = (800, 300)
SELL_BUTTON_POS = (800, 350)
EXIT_BUTTON_POS = (800, 400)  # Position for the EXIT button


def draw_radio_buttons(screen, font, selected_option):
    options = ["Weapons", "Armors", "Potions"]
    for i, pos in enumerate(RADIO_BUTTON_POSITIONS):
        pygame.draw.circle(screen, WHITE, (pos[0], pos[1] + 200), 10, 1)
        if selected_option == i:
            pygame.draw.circle(screen, WHITE, (pos[0], pos[1] + 200), 5)
        text = font.render(options[i], True, WHITE)
        text_rect = text.get_rect(midleft=(pos[0] + 20, pos[1] + 190))
        screen.blit(text, text_rect)


def draw_button(screen, font, pos, text):
    pygame.draw.rect(screen, WHITE, (pos[0] - 50, pos[1] - 20, 100, 40), 1)
    rendered_text = font.render(text, True, WHITE)
    text_rect = rendered_text.get_rect(center=pos)
    screen.blit(rendered_text, text_rect)
    return pygame.Rect(pos[0] - 50, pos[1] - 20, 100, 40)


def draw_category_items(screen, equipments, scroll_offset, selected_item_index, font):
    text_rects = []
    for index, item in enumerate(equipments):
        y_position = 50 + (index * LINE_HEIGHT) - scroll_offset
        if 0 <= y_position < 500:
            #option_text = f"{item.name} ({cost(item)} gp)"
            cost = item.cost if isinstance(item, Equipment) else f'{item.cost} gp'
            option_text = f"{item.name} ({cost})"
            color = (255, 255, 0) if index == selected_item_index else RED
            option = font.render(option_text, True, color)
            rect = option.get_rect(topleft=(20, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)
    return text_rects


def draw_hero_equipment(screen, hero, scroll_offset, selected_item_index, font):
    text_rects = []
    for index, item in enumerate(hero.entity.inventory):
        y_position = 50 + (index * LINE_HEIGHT) - scroll_offset
        if 0 <= y_position < 500:
            if not item:
                option = font.render("<Free slot>", True, RED)
            else:
                # Calculate sell price: half the item's value in cp, then convert to gp
                sell_price_cp = item.cost.value // 2
                sell_price_gp = sell_price_cp // 100

                # Display in appropriate currency
                if sell_price_cp >= 100:
                    option_text = f"{item.name} ({sell_price_gp} gp)"
                else:
                    option_text = f"{item.name} ({sell_price_cp} cp)"

                color = (255, 255, 0) if index == selected_item_index else RED
                option = font.render(option_text, True, color)
            rect = option.get_rect(topleft=(400, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)
    return text_rects


def handle_buy(hero, selected_item_index, selected_category):
    if selected_item_index is not None:
        item = selected_category[selected_item_index]
        items_in_inventory = [i.name for i in hero.entity.inventory if i]
        empty_slots = [i for i, slot in enumerate(hero.entity.inventory) if not slot]

        if len(items_in_inventory) == 20 or not empty_slots:
            cprint('Your inventory is full!')
        elif item.cost.value > hero.entity.gold * 100:
            cprint(f'Not enough Gold to buy {item.name}!')
        elif isinstance(item, Potion) and hero.entity.level < item.min_level:
            cprint(f'You need to be level {item.min_level} to buy {item.name}!')
        else:
            cprint(f'You bought {item.name}!')
            print(f'[DEBUG] Gold BEFORE purchase: {hero.entity.gold}')
            hero.entity.gold -= item.cost.value // 100
            print(f'[DEBUG] Gold AFTER purchase: {hero.entity.gold}')

            if isinstance(item, Potion):
                bought_item = copy(item)
            elif isinstance(item, Armor):
                bought_item = request_armor(item.index)
            else:
                bought_item = request_weapon(item.index)

            slot_index = min(empty_slots)
            print(f'[DEBUG] Adding {item.name} to inventory slot {slot_index}')
            print(f'[DEBUG] Inventory BEFORE: {[i.name if i else None for i in hero.entity.inventory]}')
            hero.entity.inventory[slot_index] = bought_item
            print(f'[DEBUG] Inventory AFTER: {[i.name if i else None for i in hero.entity.inventory]}')
            print(f'[DEBUG] hero object id: {id(hero)}')
            print(f'[DEBUG] hero.entity object id: {id(hero.entity)}')
            print(f'[DEBUG] hero.entity.inventory object id: {id(hero.entity.inventory)}')


def handle_sell(hero, selected_item_index):
    if selected_item_index is not None:
        try:
            item = hero.entity.inventory[selected_item_index]
            if item is None:
                cprint("There's no item in this slot to sell!")
                return

            # Calculate sell price: half the item's value in cp, then convert to gp
            sell_price_cp = item.cost.value // 2
            sell_price_gp = sell_price_cp // 100

            # Display in appropriate currency unit
            if sell_price_cp >= 100:
                cprint(f'You sold {item.name} for {sell_price_gp} gp!')
            else:
                cprint(f'You sold {item.name} for {sell_price_cp} cp!')

            hero.entity.gold += sell_price_gp
            hero.entity.inventory[selected_item_index] = None
        except (AttributeError, IndexError) as e:
            print(f'Error: {e}')

def exit_boltac(hero, original_game=None):
    """Save character when exiting Boltac's shop"""
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'

    # Extract Character entity
    char_entity = hero.entity if hasattr(hero, 'entity') else hero

    print(f'\n[DEBUG EXIT_BOLTAC] Starting exit for {char_entity.name}')
    print(f'[DEBUG] hero object id: {id(hero)}')
    print(f'[DEBUG] hero.entity object id: {id(hero.entity)}')
    print(f'[DEBUG] char_entity.gold: {char_entity.gold}')
    print(f'[DEBUG] char_entity.inventory: {[i.name if i else None for i in char_entity.inventory]}')
    print(f'[DEBUG] original_game provided: {original_game is not None}')
    if original_game:
        print(f'[DEBUG] original_game.hero object id: {id(original_game.hero)}')
        print(f'[DEBUG] original_game.hero is hero: {original_game.hero is hero}')
        print(f'[DEBUG] original_game.hero.entity.gold: {original_game.hero.entity.gold}')
        print(f'[DEBUG] original_game.hero.entity.inventory: {[i.name if i else None for i in original_game.hero.entity.inventory]}')

    # Save to characters directory (for console versions)
    save_character(char=char_entity, _dir=characters_dir)
    print(f'✅ Character {char_entity.name} saved to characters directory')

    # IMPORTANT: Also save gamestate if it exists (for pygame dungeon)
    import dungeon_pygame
    gamestate_file = f'{gamestate_dir}/{char_entity.name}_gamestate.dmp'  # Changed from .pkl to .dmp
    print(f'[DEBUG] Checking for gamestate file: {gamestate_file}')
    print(f'[DEBUG] File exists: {os.path.exists(gamestate_file)}')
    if os.path.exists(gamestate_file):
        print(f'Saving gamestate for {char_entity.name}...')
        try:
            # If we have the original_game, use it directly (modifications already in hero)
            if original_game:
                print(f'✅ Using original game object with modifications')
                print(f'[DEBUG] About to save gamestate with:')
                print(f'[DEBUG]   - Gold: {original_game.hero.entity.gold}')
                print(f'[DEBUG]   - Inventory: {[i.name if i else None for i in original_game.hero.entity.inventory]}')

                # IMPORTANT: Force a copy of the inventory to ensure pickle detects changes
                # Python lists modified in-place might not trigger pickle to save properly
                print(f'[DEBUG] Forcing inventory copy to ensure pickle detects changes...')
                original_inventory = original_game.hero.entity.inventory
                original_game.hero.entity.inventory = original_inventory.copy()
                print(f'[DEBUG] Inventory after copy: {[i.name if i else None for i in original_game.hero.entity.inventory]}')

                # The hero object has been modified, and original_game.hero IS hero
                # So we can save directly
                dungeon_pygame.save_character_gamestate(original_game, gamestate_dir)
                print(f'✅ Gamestate saved with Boltac purchases/sales')
            else:
                # Fallback: load gamestate and update it
                print(f'⚠️  No original game - loading gamestate to update')
                saved_game = dungeon_pygame.load_character_gamestate(char_entity.name, gamestate_dir)
                if saved_game:
                    # Copy inventory and gold to the loaded gamestate
                    print(f'Updating gamestate inventory and gold...')
                    saved_game.hero.entity.inventory = char_entity.inventory.copy()
                    saved_game.hero.entity.gold = char_entity.gold

                    # Save the updated gamestate
                    dungeon_pygame.save_character_gamestate(saved_game, gamestate_dir)
                    print(f'✅ Gamestate updated and saved with Boltac purchases/sales')
        except Exception as e:
            print(f'⚠️  Warning: Could not save gamestate: {e}')
            import traceback
            traceback.print_exc()

def main_game_loop(hero, equipments, original_game=None):
    # Ensure Pygame is initialized
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boltac's Trading Post")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    selected_option = 0
    selected_category = equipments[selected_option]
    selected_item_buy_index = None
    selected_item_sell_index = None
    scroll_offset_buy = scroll_offset_sell = 0
    focused_list = 'buy'

    buy_button_rect = draw_button(screen, font, BUY_BUTTON_POS, "Buy")
    sell_button_rect = draw_button(screen, font, SELL_BUTTON_POS, "Sell")
    exit_button_rect = draw_button(screen, font, EXIT_BUTTON_POS, "Exit")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                exit_boltac(hero, original_game)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, pos in enumerate(RADIO_BUTTON_POSITIONS):
                    if (pos[0] - 10 < mouse_pos[0] < pos[0] + 10) and (pos[1] + 200 - 10 < mouse_pos[1] < pos[1] + 200 + 10):
                        selected_option = i
                        selected_category = equipments[selected_option]
                        # selected_item_buy_index = None
                if buy_button_rect.collidepoint(mouse_pos):
                    focused_list = 'buy'
                    handle_buy(hero, selected_item_buy_index, selected_category)
                    # selected_item_buy_index = None
                elif sell_button_rect.collidepoint(mouse_pos):
                    focused_list = 'sell'
                    handle_sell(hero, selected_item_sell_index)
                    # selected_item_sell_index = None
                    # Check if the EXIT button was clicked
                elif exit_button_rect.collidepoint(event.pos):
                    exit_boltac(hero, original_game)
                    running = False  # Exit the game loop
                else:
                    for index, rect in enumerate(draw_category_items(screen, selected_category, scroll_offset_buy, selected_item_buy_index, font)):
                        if rect and rect.collidepoint(mouse_pos):
                            selected_item_buy_index = index
                            break
                    for index, rect in enumerate(draw_hero_equipment(screen, hero, scroll_offset_sell, selected_item_sell_index, font)):
                        if rect and rect.collidepoint(mouse_pos):
                            selected_item_sell_index = index
                            break
            elif event.type == pygame.MOUSEWHEEL:
                if focused_list == 'buy':
                    scroll_offset_buy = max(0, min(len(selected_category) * LINE_HEIGHT - 300, scroll_offset_buy + event.y * LINE_HEIGHT))
                else:
                    scroll_offset_sell = max(0, min(len(hero.entity.inventory) * LINE_HEIGHT - 300, scroll_offset_sell + event.y * LINE_HEIGHT))

        screen.fill(BLACK)
        draw_category_items(screen, selected_category, scroll_offset_buy, selected_item_buy_index, font)
        draw_radio_buttons(screen, font, selected_option)
        draw_button(screen, font, BUY_BUTTON_POS, "Buy")
        draw_button(screen, font, SELL_BUTTON_POS, "Sell")
        draw_button(screen, font, EXIT_BUTTON_POS, "Exit")
        draw_hero_equipment(screen, hero, scroll_offset_sell, selected_item_sell_index, font)

        hero_name_text = font.render(f"{hero.entity.name}", True, WHITE)
        screen.blit(hero_name_text, hero_name_text.get_rect(topleft=(BUY_BUTTON_POS[0] - 50, BUY_BUTTON_POS[1] - 150)))

        hero_gold_text = font.render(f"Gold: {hero.entity.gold}", True, WHITE)
        screen.blit(hero_gold_text, hero_gold_text.get_rect(topleft=(BUY_BUTTON_POS[0] - 50, BUY_BUTTON_POS[1] - 100)))

        pygame.display.flip()
        clock.tick(60)

    # pygame.quit()
    # sys.exit()


def load_game_data(character_name: str):
    """Load character data for Boltac's shop"""
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'

    try:
        # IMPORTANT: Try to load from gamestate first (if character is in an adventure)
        # This ensures we get the current inventory/gold, not the old saved version
        import dungeon_pygame
        saved_game = dungeon_pygame.load_character_gamestate(character_name, gamestate_dir)

        if saved_game:
            # Character has an active gamestate - use it
            print(f'\n✅ Loading {character_name} from active gamestate (dungeon adventure)')
            char = saved_game.hero.entity
            hero = saved_game.hero  # Already a GameCharacter
            original_game = saved_game  # Keep reference for saving later

            print(f'[DEBUG LOAD] saved_game object id: {id(saved_game)}')
            print(f'[DEBUG LOAD] hero object id: {id(hero)}')
            print(f'[DEBUG LOAD] hero.entity object id: {id(hero.entity)}')
            print(f'[DEBUG LOAD] char.gold: {char.gold}')
            print(f'[DEBUG LOAD] char.inventory: {[i.name if i else None for i in char.inventory[:10]]}...')
        else:
            # No gamestate - load from characters directory (new character)
            print(f'✅ Loading {character_name} from characters directory (new/no adventure)')
            char = load_character(character_name, characters_dir)

            # Wrap in GameCharacter for consistent interface
            from main import get_char_image
            image_name = get_char_image(char.class_type) if hasattr(char, 'class_type') else None
            from game_entity import create_game_character
            hero = create_game_character(char, x=-1, y=-1, image_name=image_name, char_id=1)
            original_game = None  # No gamestate for new characters

        # Get available equipment
        weapons = sorted(char.prof_weapons, key=lambda x: x.cost.value)
        armors = sorted(char.prof_armors, key=lambda x: x.cost.value)
        potions = load_potions_collections()

        return hero, [weapons, armors, potions], original_game
    except Exception as e:
        cprint(f'Error loading {character_name}: {e}')
        import traceback
        traceback.print_exc()
        sys.exit()


def run(character_name: str = 'Laucian'):
    pygame.init()
    hero, equipments, original_game = load_game_data(character_name)
    main_game_loop(hero, equipments, original_game)


if __name__ == "__main__":
    run()
