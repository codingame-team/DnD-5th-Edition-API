import os
import sys
from copy import copy
from typing import List

import pygame

from dao_classes import Character, Weapon, Armor, HealingPotion, Equipment
from dungeon_pygame import Game, load_character_gamestate, save_character_gamestate
from main import get_roster, save_character, load_character
from populate_functions import request_armor, request_weapon
from populate_rpg_functions import get_available_potions
from tools.common import WHITE, RED, cprint, BLACK, get_save_game_path

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
LINE_HEIGHT = 30
RADIO_BUTTON_POSITIONS = [(x, 350) for x in (50, 200, 350)]
BUY_BUTTON_POS = (800, 300)
SELL_BUTTON_POS = (800, 350)


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
            option_text = f"{item.name} ({cost(item)} gp)"
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
    for index, item in enumerate(hero.inventory):
        y_position = 50 + (index * LINE_HEIGHT) - scroll_offset
        if 0 <= y_position < 500:
            if not item:
                option = font.render("<Free slot>", True, RED)
            else:
                option_text = f"{item.name} ({cost(item) // 2} gp)"
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
        items_in_inventory = [i.name for i in hero.inventory if i]
        if len(items_in_inventory) == 20:
            cprint('Your inventory is full!')
        elif cost(item) <= hero.gold:
            cprint(f'You bought {item.name}!')
            hero.gold -= cost(item)
            if isinstance(item, HealingPotion):
                bought_item = copy(item)
            elif isinstance(item, Armor):
                bought_item = request_armor(item.index)
            else:
                bought_item = request_weapon(item.index)
            empty_slots = [i for i, slot in enumerate(hero.inventory) if not slot]
            hero.inventory[min(empty_slots)] = bought_item
        else:
            cprint(f'Not enough Gold to buy {item.name}!')


def handle_sell(hero, selected_item_index):
    if selected_item_index is not None:
        try:
            item = hero.inventory[selected_item_index]
            cprint(f'You sold {item.name} for {cost(item) // 2} gp!')
            hero.gold += cost(item) // 2
            hero.inventory[hero.inventory.index(item)] = None
        except (AttributeError, IndexError):
            print(f'Error')


def main_game_loop(hero, equipments):
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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_character(hero, get_save_game_path() + '/characters')
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, pos in enumerate(RADIO_BUTTON_POSITIONS):
                    if (pos[0] - 10 < mouse_pos[0] < pos[0] + 10) and (pos[1] + 200 - 10 < mouse_pos[1] < pos[1] + 200 + 10):
                        selected_option = i
                        selected_category = equipments[selected_option]
                        selected_item_buy_index = None
                if draw_button(screen, font, BUY_BUTTON_POS, "Buy").collidepoint(mouse_pos):
                    focused_list = 'buy'
                    handle_buy(hero, selected_item_buy_index, selected_category)
                    selected_item_buy_index = None
                elif draw_button(screen, font, SELL_BUTTON_POS, "Sell").collidepoint(mouse_pos):
                    focused_list = 'sell'
                    handle_sell(hero, selected_item_sell_index)
                    selected_item_sell_index = None
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
                    scroll_offset_sell = max(0, min(len(hero.inventory) * LINE_HEIGHT - 300, scroll_offset_sell + event.y * LINE_HEIGHT))

        screen.fill(BLACK)
        draw_category_items(screen, selected_category, scroll_offset_buy, selected_item_buy_index, font)
        draw_radio_buttons(screen, font, selected_option)
        draw_button(screen, font, BUY_BUTTON_POS, "Buy")
        draw_button(screen, font, SELL_BUTTON_POS, "Sell")
        draw_hero_equipment(screen, hero, scroll_offset_sell, selected_item_sell_index, font)

        hero_name_text = font.render(f"{hero.name}", True, WHITE)
        screen.blit(hero_name_text, hero_name_text.get_rect(topleft=(BUY_BUTTON_POS[0] - 50, BUY_BUTTON_POS[1] - 150)))

        hero_gold_text = font.render(f"Gold: {hero.gold}", True, WHITE)
        screen.blit(hero_gold_text, hero_gold_text.get_rect(topleft=(BUY_BUTTON_POS[0] - 50, BUY_BUTTON_POS[1] - 100)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


def load_game_data(character_name):
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'

    try:
        saved_game = load_character_gamestate(character_name, gamestate_dir)
        hero = saved_game.hero if saved_game else load_character(character_name, characters_dir)
        hero.gold = 10000
        weapons = sorted(hero.allowed_weapons, key=cost)
        armors = sorted(hero.allowed_armors, key=cost)
        potions = get_available_potions()
        return hero, [weapons, armors, potions]
    except Exception as e:
        cprint(f'Error loading {character_name}: {e}')
        sys.exit()


def run(character_name: str = 'Brottor'):
    pygame.init()
    hero, equipments = load_game_data(character_name)
    main_game_loop(hero, equipments)

cost = lambda x: int(x.cost) if isinstance(x, HealingPotion) else int(x.cost['quantity'])

if __name__ == "__main__":
    run()
