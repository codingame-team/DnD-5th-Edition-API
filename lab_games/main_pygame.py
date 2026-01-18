import pickle

import pygame
import os
import time
from random import seed
from fractions import Fraction
from typing import List

from main import load_xp_levels, load_dungeon_collections, get_roster, load_party, load_encounter_table, load_encounter_gold_table, save_character
from tools.common import get_save_game_path


class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("D&D 5E RPG")

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GOLD = (255, 215, 0)

        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Game Constants
        self.PAUSE_ON_RAISE_LEVEL = True
        self.POTION_INITIAL_PACK = 15
        self.MAX_ROSTER = 100

        # Initialize game state
        self.initialize_game_state()

        # UI state
        self.running = True
        # self.current_menu = []
        self.selected_index = 0

    def initialize_game_state(self):
        """Initialize all game data and state"""
        seed(time.time())

        # Setup paths
        self.path = os.path.dirname(__file__)
        self.abspath = os.path.abspath(self.path)
        self.game_path = get_save_game_path()
        self.characters_dir = f"{self.game_path}/characters"

        # Load game data
        self.xp_levels = load_xp_levels()
        (
            self.monsters,
            self.armors,
            self.weapons,
            self.equipments,
            self.equipment_categories,
            self.potions,
        ) = load_dungeon_collections()

        # Filter collections
        self.armors = list(filter(lambda a: a, self.armors))
        self.weapons = list(filter(lambda w: w, self.weapons))

        # Setup locations and destinations
        self.locations = ["Edge of Town", "Castle"]
        self.castle_destinations = [
            "Gilgamesh's Tavern",
            "Adventurer's Inn",
            "Temple of Cant",
            "Boltac's Trading Post",
            "Edge of Town",
        ]
        self.edge_of_town_destinations = [
            "Training Grounds",
            "Maze",
            "Leave Game",
            "Castle",
        ]

        # Load roster and party
        self.roster = get_roster(self.characters_dir)
        self.party = load_party(_dir=self.game_path)

        # Load encounter data
        self.encounter_table = load_encounter_table()
        self.encounter_gold_table = load_encounter_gold_table()
        self.available_crs = [Fraction(str(m.challenge_rating)) for m in self.monsters]

        # Set initial location
        self.location = "Castle"
        self.current_menu = self.castle_destinations

    def gilgamesh_tavern(self):
        """Gilgamesh's Tavern interface using Pygame"""
        gt_options = ["Add Member", "Remove Member", "Character Status", "Reorder", "Divvy Gold", "Disband Party", "Exit Tavern"]

        selected_option = 0
        exit_tavern = False

        while not exit_tavern:
            self.screen.fill(self.BLACK)

            # Draw tavern header
            header_text = ["+-----------------------------+", "|  ** GILGAMESH'S TAVERN **  |", "+-----------------------------+"]
            for i, line in enumerate(header_text):
                text = self.font.render(line, True, self.GOLD)
                text_rect = text.get_rect(center=(self.screen_width / 2, 50 + i * 30))
                self.screen.blit(text, text_rect)

            # Display party members
            party_y = 150
            if self.party:
                for i, char in enumerate(self.party):
                    char_text = f"{char.name} - Level {char.level} {char.class_name} - Gold: {char.gold}"
                    text = self.small_font.render(char_text, True, self.WHITE)
                    self.screen.blit(text, (50, party_y + i * 25))
            else:
                text = self.font.render("No party members", True, self.WHITE)
                self.screen.blit(text, (50, party_y))

            # Draw menu options
            menu_y = 300
            for i, option in enumerate(gt_options):
                color = self.GOLD if i == selected_option else self.WHITE
                text = self.font.render(option, True, color)
                text_rect = text.get_rect(center=(self.screen_width / 2, menu_y + i * 40))
                self.screen.blit(text, text_rect)

            pygame.display.flip()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit_tavern = True

                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(gt_options)

                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(gt_options)

                    elif event.key == pygame.K_RETURN:
                        option = gt_options[selected_option]

                        if option == "Exit Tavern":
                            exit_tavern = True

                        elif option == "Add Member":
                            self.add_member_screen()

                        elif option == "Remove Member":
                            self.remove_member_screen()

                        elif option == "Character Status":
                            if not self.party:
                                self.show_message("No characters remains in the party!")
                            else:
                                self.character_status_screen()

                        elif option == "Reorder":
                            if not self.party:
                                self.show_message("No characters remains in the party!")
                            else:
                                self.reorder_party_screen()

                        elif option == "Divvy Gold":
                            if not self.party:
                                self.show_message("No characters remains in the party!")
                            else:
                                total_gold = sum([c.gold for c in self.party])
                                share = total_gold // len(self.party)
                                for char in self.party:
                                    char.gold = share
                                    save_character(char, _dir=self.characters_dir)
                                self.show_message("All the party's gold has been divided.")

                        elif option == "Disband Party":
                            if not self.party:
                                self.show_message("No characters remains in the party!")
                            else:
                                if self.confirm_dialog("Are you sure?"):
                                    for char in self.party:
                                        char.id_party = -1
                                        save_character(char, _dir=self.characters_dir)
                                    self.party.clear()

        def confirm_dialog(self, message):
            """Show a yes/no confirmation dialog"""
            dialog_active = True
            selected = False

            while dialog_active:
                self.screen.fill(self.BLACK)

                # Draw message
                text = self.font.render(message, True, self.WHITE)
                text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 2 - 50))
                self.screen.blit(text, text_rect)

                # Draw options
                yes_color = self.GOLD if selected else self.WHITE
                no_color = self.WHITE if selected else self.GOLD

                yes_text = self.font.render("Yes", True, yes_color)
                no_text = self.font.render("No", True, no_color)

                self.screen.blit(yes_text, (self.screen_width / 2 - 50, self.screen_height / 2 + 50))
                self.screen.blit(no_text, (self.screen_width / 2 + 50, self.screen_height / 2 + 50))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                            selected = not selected
                        elif event.key == pygame.K_RETURN:
                            dialog_active = False
                            return selected
                        elif event.key == pygame.K_ESCAPE:
                            return False

            return False

        def add_member_screen(self):
            """Screen for adding party members"""
            available_chars = [c for c in self.roster if c not in self.party]
            if not available_chars:
                self.show_message("No available characters to add!")
                return

            selected_index = 0
            selecting = True

            while selecting:
                self.screen.fill(self.BLACK)

                # Draw header
                text = self.font.render("Select Character to Add:", True, self.WHITE)
                self.screen.blit(text, (50, 50))

                # Draw character list
                for i, char in enumerate(available_chars):
                    color = self.GOLD if i == selected_index else self.WHITE
                    text = self.font.render(f"{char.name} - Level {char.level} {char.class_name}", True, color)
                    self.screen.blit(text, (50, 100 + i * 30))

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            selecting = False
                        elif event.key == pygame.K_UP:
                            selected_index = (selected_index - 1) % len(available_chars)
                        elif event.key == pygame.K_DOWN:
                            selected_index = (selected_index + 1) % len(available_chars)
                        elif event.key == pygame.K_RETURN:
                            char = available_chars[selected_index]
                            self.party.append(char)
                            char.id_party = len(self.party) - 1
                            save_character(char, _dir=self.characters_dir)
                            selecting = False

        # Add similar methods for remove_member_screen(), character_status_screen(),   # and reorder_party_screen() following the same pattern

    def handle_location_change(self):
        """Handle location-specific logic"""
        if self.location == "Castle":
            self.current_menu = self.castle_destinations
            self.update_party_status()
        else:  # Edge of Town
            self.current_menu = self.edge_of_town_destinations

    def update_party_status(self):
        """Update party members status"""
        for c in self.party[:]:  # Create a copy of the list to modify it
            if c.status != "OK":
                self.party.remove(c)
                if c not in self.roster:
                    self.roster.append(c)

    def handle_destination(self, destination):
        """Handle destination selection"""
        if self.location == "Castle":
            if destination == "Gilgamesh's Tavern":
                self.gilgamesh_tavern()
            elif destination == "Adventurer's Inn":
                if not self.party:
                    self.show_message("No characters remains in the party!")
                else:
                    adventurer_inn(self.party)
            elif destination == "Temple of Cant":
                if not self.party:
                    self.show_message("No characters remains in the party!")
                else:
                    temple_of_cant(self.party, self.roster)
            elif destination == "Boltac's Trading Post":
                boltac_trading_post(self.party)
            elif destination == "Edge of Town":
                self.location = "Edge of Town"
                self.current_menu = self.edge_of_town_destinations

    def show_message(self, message, duration=2000):
        """Display a message on screen"""
        text = self.font.render(message, True, self.WHITE)
        text_rect = text.get_rect(
            center=(self.screen_width / 2, self.screen_height / 2)
        )
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(duration)

    def draw(self):
        """Draw the game screen"""
        self.screen.fill(self.BLACK)

        # Draw location header
        header = f"** {self.location} **"
        text = self.font.render(header, True, self.GOLD)
        text_rect = text.get_rect(center=(self.screen_width / 2, 50))
        self.screen.blit(text, text_rect)

        # Draw menu items
        start_y = 150
        for i, item in enumerate(self.current_menu):
            color = self.GOLD if i == self.selected_index else self.WHITE
            text = self.font.render(item, True, color)
            text_rect = text.get_rect(center=(self.screen_width / 2, start_y + i * 40))
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    def clear_screen(self):
        """Replace efface_ecran() functionality"""
        self.screen.fill(self.BLACK)

    def save_game(self, char_to_party, game_path):
        """Save game state"""
        try:
            # Save character to party
            if char_to_party and game_path:
                characters_dir = os.path.join(game_path, 'characters')
                os.makedirs(characters_dir, exist_ok=True)

                for character in char_to_party:
                    save_path = os.path.join(characters_dir, f"{character.name}.dmp")
                    with open(save_path, 'wb') as f1:
                        pickle.dump(character, f1)

                # Display save confirmation
                text = self.font.render("Game Saved!", True, self.WHITE)
                text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
                self.screen.blit(text, text_rect)
                pygame.display.flip()
                pygame.time.wait(1000)  # Show message for 1 second

        except Exception as e:
            # Display error message
            text = self.font.render(f"Save Error: {str(e)}", True, self.WHITE)
            text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(2000)

    def quit_game(self):
        """Handle game exit"""
        # Display goodbye message
        text = self.font.render("Bye, see you in the next adventure :-)", True, self.WHITE)
        text_rect = text.get_rect(center=(self.screen_width/2, self.screen_height/2))
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)  # Show message for 2 seconds
        pygame.quit()
        exit(0)

    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_game()
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.current_menu)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.current_menu)
                    elif event.key == pygame.K_RETURN:
                        destination = self.current_menu[self.selected_index]
                        self.handle_destination(destination)

            self.draw()
            pygame.time.Clock().tick(60)


if __name__ == "__main__":
    if "TERM" not in os.environ:
        os.environ["TERM"] = "xterm-256color"

    game = Game()
    game.run()
