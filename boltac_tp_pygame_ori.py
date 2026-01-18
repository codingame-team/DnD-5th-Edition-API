import os
import sys
from copy import copy
from typing import List

import pygame

from dao_classes import Character, Weapon, Armor, HealingPotion, Equipment, SpeedPotion, Potion
from dungeon_pygame import Game, load_character_gamestate, save_character_gamestate
from main import get_roster, save_character, load_character
from populate_functions import request_armor, request_weapon
from populate_rpg_functions import load_potions_collections
from tools.common import WHITE, RED, cprint, BLACK, get_save_game_path

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
    for index, item in enumerate(hero.inventory):
        y_position = 50 + (index * LINE_HEIGHT) - scroll_offset
        if 0 <= y_position < 500:
            if not item:
                option = font.render("<Free slot>", True, RED)
            else:
                cost = item.cost.quantity // 2
                unit = item.cost.unit
                option_text = f"{item.name} ({cost} {unit})"
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
        empty_slots = [i for i, slot in enumerate(hero.inventory) if not slot]

        if len(items_in_inventory) == 20 or not empty_slots:
            cprint('Your inventory is full!')
        elif item.cost.value > hero.gold * 100:
            cprint(f'Not enough Gold to buy {item.name}!')
        elif isinstance(item, Potion) and hero.level < item.min_level:
            cprint(f'You need to be level {item.min_level} to buy {item.name}!')
        else:
            cprint(f'You bought {item.name}!')
            hero.gold -= item.cost.value // 100
            if isinstance(item, Potion):
                bought_item = copy(item)
            elif isinstance(item, Armor):
                bought_item = request_armor(item.index)
            else:
                bought_item = request_weapon(item.index)
            hero.inventory[min(empty_slots)] = bought_item


def handle_sell(hero, selected_item_index):
    if selected_item_index is not None:
        try:
            item = hero.inventory[selected_item_index]
            if item is None:
                cprint("There's no item in this slot to sell!")
                return

            sell_price = item.cost.quantity // 2
            cprint(f'You sold {item.name} for {sell_price} {item.cost.unit}!')
            hero.gold += sell_price // 100
            hero.inventory[selected_item_index] = None
        except (AttributeError, IndexError) as e:
            print(f'Error: {e}')

def exit_boltac(saved_game, hero):
    game_path = get_save_game_path()
    if saved_game:
        save_character_gamestate(char=hero, _dir=game_path + '/pygame', gamestate=saved_game)
    else:
        save_character(char=hero, _dir=game_path + '/characters')

def main_game_loop(saved_game, hero, equipments, characters_dir):
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
                exit_boltac(saved_game, hero)
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
                    exit_boltac(saved_game, hero)
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
                    scroll_offset_sell = max(0, min(len(hero.inventory) * LINE_HEIGHT - 300, scroll_offset_sell + event.y * LINE_HEIGHT))

        screen.fill(BLACK)
        draw_category_items(screen, selected_category, scroll_offset_buy, selected_item_buy_index, font)
        draw_radio_buttons(screen, font, selected_option)
        draw_button(screen, font, BUY_BUTTON_POS, "Buy")
        draw_button(screen, font, SELL_BUTTON_POS, "Sell")
        draw_button(screen, font, EXIT_BUTTON_POS, "Exit")
        draw_hero_equipment(screen, hero, scroll_offset_sell, selected_item_sell_index, font)

        hero_name_text = font.render(f"{hero.name}", True, WHITE)
        screen.blit(hero_name_text, hero_name_text.get_rect(topleft=(BUY_BUTTON_POS[0] - 50, BUY_BUTTON_POS[1] - 150)))

        hero_gold_text = font.render(f"Gold: {hero.gold}", True, WHITE)
        screen.blit(hero_gold_text, hero_gold_text.get_rect(topleft=(BUY_BUTTON_POS[0] - 50, BUY_BUTTON_POS[1] - 100)))

        pygame.display.flip()
        clock.tick(60)

    # pygame.quit()
    # sys.exit()


def load_game_data(character_name):
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'

    try:
        saved_game = load_character_gamestate(character_name, gamestate_dir)
        hero = saved_game.hero if saved_game else load_character(character_name, characters_dir)
        weapons = sorted(hero.prof_weapons, key=lambda x: x.cost.value)
        armors = sorted(hero.prof_armors, key=lambda x: x.cost.value)
        potions = load_potions_collections()
        return saved_game, hero, [weapons, armors, potions]
    except Exception as e:
        cprint(f'Error loading {character_name}: {e}')
        sys.exit()


def run(character_name: str = 'Brottor'):
    # pygame.init()
    saved_game, hero, equipments = load_game_data(character_name)
    main_game_loop(saved_game, hero, equipments, f'{get_save_game_path()}/characters')


if __name__ == "__main__":
    run()
