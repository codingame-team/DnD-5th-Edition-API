import os
import sys
from copy import copy
from typing import List

import pygame

from dao_classes import Character, Weapon, Armor, HealingPotion, Equipment
from dungeon_pygame import Game, Level, Room, load_character_gamestate, save_character_gamestate
from main import get_roster, save_character, load_character
from populate_functions import request_armor, request_weapon
from populate_rpg_functions import get_available_potions
from tools.common import WHITE, RED, cprint, BLACK


def draw_radio_buttons(screen, font, selected_option):
    options = ["Weapons", "Armors", "Potions"]
    for i, pos in enumerate(radio_button_positions):
        # Draw the outer circle
        pygame.draw.circle(screen, (255, 255, 255), (pos[0], pos[1] + 200), 10, 1)
        # Draw the inner circle if selected
        if selected_option == i:
            pygame.draw.circle(screen, (255, 255, 255), (pos[0], pos[1] + 200), 5)
        # Draw the option text
        text = font.render(options[i], True, (255, 255, 255))
        text_rect = text.get_rect(midleft=(pos[0] + 20, pos[1] + 190))
        screen.blit(text, text_rect)


def draw_buy_button(screen, font):
    pygame.draw.rect(screen, (255, 255, 255), (buy_button_pos[0] - 50, buy_button_pos[1] - 20, 100, 40), 1)
    buy_text = font.render("Buy", True, (255, 255, 255))
    buy_text_rect = buy_text.get_rect(center=buy_button_pos)
    screen.blit(buy_text, buy_text_rect)


def draw_category_items(screen, equipments, scroll_offset, line_height, font, selected_item_index):
    text_rects = []
    for index, item in enumerate(equipments):
        y_position = 50 + (index * line_height) - scroll_offset
        if 0 <= y_position < 500:
            if index == selected_item_index:
                option = font.render(f"{item.name} ({cost(item)} gp)", True, (255, 255, 0))  # Highlight the selected item
            else:
                option = font.render(f"{item.name} ({cost(item)} gp)", True, RED)
            rect = option.get_rect(topleft=(20, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)  # Placeholder for non-visible options
    return text_rects


def draw_sell_button(screen, font):
    pygame.draw.rect(screen, (255, 255, 255), (sell_button_pos[0] - 50, sell_button_pos[1] - 20, 100, 40), 1)
    sell_text = font.render("Sell", True, (255, 255, 255))
    sell_text_rect = sell_text.get_rect(center=sell_button_pos)
    screen.blit(sell_text, sell_text_rect)


def draw_hero_equipment(screen, hero, scroll_offset, line_height, font, selected_item_index):
    text_rects = []
    for index, item in enumerate(hero.inventory):
        y_position = 50 + (index * line_height) - scroll_offset
        if 0 <= y_position < 500:
            if not item:
                option = font.render(f"<Free slot>", True, RED)
            else:
                if index == selected_item_index:
                    option = font.render(f"{item.name} ({cost(item) // 2} gp)", True, (255, 255, 0))  # Highlight the selected item
                else:
                    option = font.render(f"{item.name} ({cost(item)} gp)", True, RED)
            rect = option.get_rect(topleft=(400, y_position))
            screen.blit(option, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)  # Placeholder for non-visible options
    return text_rects


def main():
    global text_rects_buy, text_rects_sell  # Ensure text_rects is accessible in the event loop
    global scroll_offset_buy, scroll_offset_sell

    clock = pygame.time.Clock()
    running = True
    selected_option = 0
    selected_category = equipments[selected_option]
    selected_item_buy_index = None
    selected_item_sell_index = None
    scroll_offset_buy = scroll_offset_sell = 0
    line_height = 30
    focused_list = 'buy'  # Initial focus is on the buy list

    # Set up fonts
    title_font = pygame.font.Font(None, 48)
    item_font = pygame.font.Font(None, 36)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # save_character(hero, characters_dir)
                save_character_gamestate(hero, gamestate_dir, saved_game)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                # Check if a radio button is clicked
                for i, pos in enumerate(radio_button_positions):
                    if (pos[0] - 10 < mouse_pos[0] < pos[0] + 10) and (pos[1] + 200 - 10 < mouse_pos[1] < pos[1] + 200 + 10):
                        selected_option = i
                        selected_category = equipments[selected_option]
                        text_rects_buy = draw_category_items(screen, selected_category, scroll_offset_buy, line_height, font, selected_item_buy_index)
                # Check if the buy button is clicked
                if buy_list_rect.collidepoint(mouse_pos):
                    focused_list = 'buy'
                # Check if the sell button is clicked
                elif sell_list_rect.collidepoint(mouse_pos):
                    focused_list = 'sell'

                # Check if the buy button is clicked
                if buy_button_rect.collidepoint(mouse_pos):
                    focused_list = 'buy'
                    if selected_item_buy_index is not None:
                        item: Equipment = selected_category[selected_item_buy_index]
                        items_in_inventory = [i.name for i in hero.inventory if i]
                        if len(items_in_inventory) == 20:
                            cprint('Your inventory is full!')
                        elif cost(item) <= hero.gold:
                            cprint(f'You bought {item.name}!')
                            hero.gold -= cost(item)
                            if isinstance(item, HealingPotion):
                                bought_item: HealingPotion = copy(item)
                            elif isinstance(item, Armor):
                                bought_item: Armor = request_armor(item.index)
                            else:
                                bought_item: Weapon = request_weapon(item.index)
                            empty_slots = [i for i, slot in enumerate(hero.inventory) if not slot]
                            slot: int = min(empty_slots)
                            hero.inventory[slot] = bought_item
                        else:
                            cprint(f'Not enough Gold to buy {item.name}!')
                    selected_item_buy_index = None  # Deselect the item
                # Check if the sell button is clicked
                elif sell_button_rect.collidepoint(mouse_pos):
                    focused_list = 'sell'
                    if selected_item_sell_index is not None:
                        try:
                            item: Equipment = hero.inventory[selected_item_sell_index]
                            cprint(f'You sold {item.name} for {cost(item) // 2} gp!')
                            hero.gold += cost(item) // 2
                            slot: int = hero.inventory.index(item)  # Find the slot where the item is located
                            hero.inventory[slot] = None  # Remove the item from the inventory
                        except (AttributeError, IndexError):
                            print(f'Error')
                    selected_item_sell_index = None  # Deselect the item
                else:
                    for index, rect in enumerate(text_rects_buy):
                        if rect and rect.collidepoint(mouse_pos):
                            selected_item_buy_index = index
                            break
                    for index, rect in enumerate(text_rects_sell):
                        if rect and rect.collidepoint(mouse_pos):
                            selected_item_sell_index = index
                            break
            # Handle scrolling events
            elif event.type == pygame.MOUSEWHEEL:
                if focused_list == 'buy':
                    scroll_offset_buy = max(0, min(len(selected_category) * line_height - 300, scroll_offset_buy + event.y * line_height))
                else:
                    scroll_offset_sell = max(0, min(len(hero.inventory) * line_height - 300, scroll_offset_sell + event.y * line_height))

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw the list of selected category above the radio button list
        text_rects_buy = draw_category_items(screen, selected_category, scroll_offset_buy, line_height, font, selected_item_buy_index)

        # Draw the radio buttons
        draw_radio_buttons(screen, font, selected_option)

        # Draw the buy button
        draw_buy_button(screen, font)
        buy_button_rect = pygame.Rect(buy_button_pos[0] - 50, buy_button_pos[1] - 20, 100, 40)

        # Draw the sell button
        draw_sell_button(screen, font)
        sell_button_rect = pygame.Rect(sell_button_pos[0] - 50, sell_button_pos[1] - 20, 100, 40)

        # Draw the hero's equipment
        text_rects_sell = draw_hero_equipment(screen, hero, scroll_offset_sell, line_height, font, selected_item_sell_index)

        # Draw the hero's name and gold
        hero_name_text = font.render(f"{hero.name}", True, (255, 255, 255))
        hero_name_rect = hero_name_text.get_rect(topleft=(buy_button_pos[0] - 50, buy_button_pos[1] - 150))
        screen.blit(hero_name_text, hero_name_rect)

        hero_gold_text = font.render(f"Gold: {hero.gold}", True, (255, 255, 255))
        hero_gold_rect = hero_gold_text.get_rect(topleft=(buy_button_pos[0] - 50, buy_button_pos[1] - 100))
        screen.blit(hero_gold_text, hero_gold_rect)

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


cost = lambda x: int(x.cost) if isinstance(x, HealingPotion) else int(x.cost['quantity'])

if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()

    # Set up the display
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Boltac's Trading Post")

    # Set up font
    font = pygame.font.Font(None, 36)

    # Radio button positions and selected option
    radio_button_positions = [(x, 350) for x in (50, 200, 350)]

    # Create a new surface for the category list
    buy_list_surface = pygame.Surface((300, 300))
    buy_list_surface.fill(WHITE)
    buy_list_rect = buy_list_surface.get_rect(topleft=(50, 50))
    buy_list_scroll_y = 0
    buy_list_scroll_speed = 20

    # Create a new surface for the hero's inventory
    sell_list_surface = pygame.Surface((600, 300))
    sell_list_surface.fill(WHITE)
    sell_list_rect = sell_list_surface.get_rect(topleft=(350, 50))
    sell_list_scroll_y = 0
    sell_list_scroll_speed = 20

    # Buy/Sell buttons position
    buy_button_pos = (800, 300)
    sell_button_pos = (800, 350)

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    gamestate_dir = f'{abspath}/gameState/pygame'

    character_name: str = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'

    try:
        # hero: Character = load_character(character_name, characters_dir)
        saved_game: Game = load_character_gamestate(character_name, gamestate_dir)
        hero: Character = saved_game.hero
        hero.gold = 10000
        weapons: List[Weapon] = sorted(hero.allowed_weapons, key=lambda w: cost(w))
        armors: List[Armor] = sorted(hero.allowed_armors, key=lambda a: cost(a))
        potions: List[HealingPotion] = get_available_potions()
        equipments: List[List] = [weapons, armors, potions]

    except IndexError:
        print(f"Character name <{character_name}> not found in roster")

    main()
