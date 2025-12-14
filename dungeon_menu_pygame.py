import pygame
import sys
import multiprocessing as mp
from enum import Enum
from typing import List
import os

from dao_classes import Character
from dungeon_pygame import save_character_gamestate, Game
from main import get_roster, save_character
from tools.cheat_functions import raise_dead_roster
from tools.common import cprint, SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, RED, WHITE, resource_path, GREEN, get_save_game_path
import dungeon_pygame, boltac_tp_pygame, monster_kills_pygame

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 300


class LT(Enum):
    DUNGEON = 0
    BOLTAC = 1
    MONSTER_KILLS = 2


class GameMenu:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(None, 22)
        self.screen_width, self.screen_height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.scroll_offset = 0
        self.line_height = 20
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption('Choose your character')

        path = os.path.dirname(__file__)
        self.abspath = os.path.abspath(path)
        self.game_path = get_save_game_path()
        self.characters_dir = f'{self.game_path}/characters'
        self.gamestate_dir = f'{self.game_path}/pygame'

        if self.game_path and not os.path.exists(self.game_path):
            os.makedirs(self.game_path)
            os.makedirs(self.characters_dir)
            os.makedirs(self.gamestate_dir)
            default_roster: List[Character] = get_roster(characters_dir=resource_path('gameState/characters'))
            for char in default_roster:
                save_character(char=char, _dir=self.characters_dir)
                cprint(f'Personnage {char.name} importé dans {self.characters_dir}', color=GREEN)

    def go_to_location(self, character_name: str, location: LT):
        if location == LT.DUNGEON:
            dungeon_pygame.run(character_name)
        elif location == LT.BOLTAC:
            boltac_tp_pygame.run(character_name)
        elif location == LT.MONSTER_KILLS:
            monster_kills_pygame.run(character_name)
        else:
            cprint('Invalid location', color=RED)

    def reset_ids_all(self, gamestates: List[Game]):
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
            save_character_gamestate(char=character, _dir=self.gamestate_dir, gamestate=game)
            save_character(char=character, _dir=self.characters_dir)

    def draw_character_menu(self, roster, scroll_offset):
        self.screen.fill(WHITE)
        text_rects = []
        for index, character in enumerate(roster):
            y_position = self.line_height * 2 + (index * self.line_height) - scroll_offset
            if 0 <= y_position < self.screen_height:
                if hasattr(character, 'class_type'):
                    option = self.font.render(f"{character.name} (Level {character.level} {character.class_type})", True, RED)
                else:
                    option = self.font.render(f"{character.name} (CR {character.level})", True, RED)
                rect = option.get_rect(topleft=(20, y_position))
                self.screen.blit(option, rect)
                text_rects.append(rect)
            else:
                text_rects.append(None)  # Placeholder for non-visible options

        option2 = self.font.render("Exit", True, BLACK)
        y_position = self.line_height * 2 + (len(roster) * self.line_height) - scroll_offset
        if 0 <= y_position < self.screen_height:
            rect = option2.get_rect(topleft=(20, y_position))
            self.screen.blit(option2, rect)
            text_rects.append(rect)
        else:
            text_rects.append(None)  # Placeholder for non-visible options

        return text_rects

    def draw_radio_buttons(self, selected_option, options, radio_button_positions):
        for i, option in enumerate(options):
            pos = radio_button_positions[i]
            pygame.draw.circle(self.screen, (0, 0, 0), pos, 7, 1)  # Draw the outer circle
            if selected_option == i:
                pygame.draw.circle(self.screen, (0, 0, 0), pos, 4)  # Draw the inner circle if selected
            text = self.font.render(option, True, (0, 0, 0))
            self.screen.blit(text, (pos[0] + 20, pos[1] - 10))

    def main(self, roster: List[Character]):
        clock = pygame.time.Clock()
        running = True
        selected_option = 0  # 0 for Explore Dungeon, 1 for Shop to Boltac, 2 for Monster kills
        options = ["Explore Dungeon", "Shop to Boltac", "Monster kills"]
        radio_button_positions = [(self.screen_width - 330, 60 + 40 * i) for i in range(len(options))]

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    text_rects = self.draw_character_menu(roster, self.scroll_offset)

                    # Check radio button clicks
                    for i, pos in enumerate(radio_button_positions):
                        if (pos[0] - 10 < mouse_pos[0] < pos[0] + 10) and (pos[1] - 10 < mouse_pos[1] < pos[1] + 10):
                            selected_option = i

                    for index, rect in enumerate(text_rects):
                        if rect and rect.collidepoint(mouse_pos):
                            if index < len(roster):
                                selected_character = roster[index]
                                if not selected_character.is_dead:
                                    self.go_to_location(selected_character.name, LT(selected_option))
                                    # Resize screen
                                    self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                                    # running = False  # Close the main loop after starting the game
                                else:
                                    cprint(f'Cannot select character... {selected_character.name} is dead!')
                            else:
                                running = False  # Exit the menu if 'Exit' is clicked
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:  # Scroll up
                    self.scroll_offset = max(self.scroll_offset - self.line_height, 0)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:  # Scroll down
                    max_offset = max(0, (len(roster) + 1) * self.line_height - self.screen_height + self.line_height * 2)
                    self.scroll_offset = min(self.scroll_offset + self.line_height, max_offset)
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_width, self.screen_height = event.size

            self.screen.fill(WHITE)
            self.draw_character_menu(roster, self.scroll_offset)
            self.draw_radio_buttons(selected_option, options, radio_button_positions)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

    def run(self):
        # try:
        roster: List[Character] = get_roster(self.characters_dir)
        # Synchronisation : si un gamestate existe pour un personnage, prendre le hero du gamestate
        # (qui contient le niveau à jour) et persister dans characters_dir pour garder une source unique.
        for i, char in enumerate(roster):
            try:
                saved_game = dungeon_pygame.load_character_gamestate(char.name, self.gamestate_dir)
            except Exception:
                saved_game = None
            if saved_game:
                roster[i] = saved_game.hero
                try:
                    save_character(char=saved_game.hero, _dir=self.characters_dir)
                except Exception:
                    # Ne pas interrompre l'affichage si la persistance échoue, mais afficher un message utile.
                    cprint(f"Warning: unable to persist synced character {saved_game.hero.name} to {self.characters_dir}", color=RED)

        raise_dead_roster(roster, self.characters_dir)
        self.main(roster)
        # except FileNotFoundError:
        #     cprint(f'No characters found in {self.characters_dir}', color=RED)


if __name__ == "__main__":
    game_menu = GameMenu()
    game_menu.run()
