from fractions import Fraction

import pygame
import pygame_gui
import os
from typing import List

from dao_classes import Character
from main import save_character, load_xp_levels, load_dungeon_collections, get_roster, load_party, load_encounter_table, load_encounter_gold_table
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

        # Initialize pygame_gui manager
        # self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height), 'theme.json')

        # Create header once during initialization
        self.header = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 50), (self.screen_width, 50)), text="** Castle **", manager=self.manager)

        self.clock = pygame.time.Clock()
        self.running = True

        """Initialize all game data and state"""
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

        # Define menus
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

        self.location = "Castle"
        self.current_menu = self.castle_destinations

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

        # Create menu buttons
        self.buttons = []
        self.create_menu_buttons()

    def create_menu_buttons(self):
        # Clear existing buttons
        for button in self.buttons:
            button.kill()
        self.buttons.clear()

        # Update header text instead of recreating
        self.header.set_text(f"** {self.location} **")

        # Create new buttons based on current_menu
        button_height = 50
        button_width = 300
        start_y = 150

        for i, item in enumerate(self.current_menu):
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(self.screen_width // 2 - button_width // 2,
                                          start_y + i * (button_height + 10),
                                          button_width,
                                          button_height),
                text=item,
                manager=self.manager
            )
            self.buttons.append(button)

    def handle_destination(self, destination: str):
        if self.location == "Castle":
            if destination == "Edge of Town":
                self.location = "Edge of Town"
                self.current_menu = self.edge_of_town_destinations
                self.create_menu_buttons()
            elif destination == "Gilgamesh's Tavern":
                self.gilgamesh_tavern()
            # Add other destination handling here

        elif self.location == "Edge of Town":
            if destination == "Castle":
                self.location = "Castle"
                self.current_menu = self.castle_destinations
                self.create_menu_buttons()
            elif destination == "Leave Game":
                self.quit_game()

    # GILGAMESH TAVERN
    def create_party_table(self):
        """Create an interactive party table"""
        if not hasattr(self, 'party_table'):
            # Define table dimensions and position
            table_width = 600
            table_height = 200
            x_pos = (self.screen_width - table_width) // 2
            y_pos = 100

            # Create table
            self.party_table = pygame_gui.elements.UITable(relative_rect=pygame.Rect((x_pos, y_pos), (table_width, table_height)), manager=self.manager, headers=['Name', 'Level', 'Class', 'Gold', 'Actions'], column_widths=[150, 80, 150, 100, 120])

            # Set table colors and styling
            self.party_table.bg_colour = pygame.Color('#45494e')
            self.party_table.border_colour = pygame.Color('#666666')
            self.party_table.text_colour = pygame.Color('#FFFFFF')
            self.party_table.highlight_colour = pygame.Color('#666666')

        # Clear existing rows
        self.party_table.clear()

        if not self.party:
            self.party_table.add_row(['No party members', '', '', '', ''])
            return

        # Add party members to table
        for i, char in enumerate(self.party):
            # Create action button
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((0, 0), (100, 20)), text='Select', manager=self.manager, container=self.party_table, object_id=f'character_button_{i}')

            self.party_table.add_row([char.name, str(char.level), char.class_type, str(char.gold), button])

    def handle_table_events(self, event):
        """Handle table-related events"""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(event.ui_element, 'object_id'):
                button_id = event.ui_element.object_id
                if button_id.startswith('character_button_'):
                    char_index = int(button_id.split('_')[-1])
                    if char_index < len(self.party):
                        self.show_character_menu(self.party[char_index])

    def show_character_menu(self, character):
        """Show context menu for selected character"""
        options = ['View Status', 'Remove from Party', 'View Equipment', 'Cancel']

        # Calculate position (near the mouse)
        mouse_pos = pygame.mouse.get_pos()
        menu_width = 200
        menu_height = len(options) * 30

        # Create context menu
        context_menu = pygame_gui.windows.UIDropDownMenu(options_list=options, starting_option='Select Action', relative_rect=pygame.Rect(mouse_pos, (menu_width, menu_height)), manager=self.manager)

        # Handle menu selection
        @context_menu.on_drop_down_menu_changed
        def handle_menu_selection(selection):
            if selection == 'View Status':
                self.show_character_status(character)
            elif selection == 'Remove from Party':
                self.remove_character_from_party(character)
            elif selection == 'View Equipment':
                self.show_character_equipment(character)
            context_menu.kill()

    def gilgamesh_tavern(self):
        """Gilgamesh's Tavern interface"""
        # Clear existing UI
        self.manager.clear_and_reset()

        # Create header
        self.header = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 20), (self.screen_width, 50)), text="** GILGAMESH'S TAVERN **", manager=self.manager)

        # Create interactive party table
        self.create_party_table()

        # Create tavern menu buttons
        button_width = 200
        button_height = 40
        button_spacing = 10
        start_y = 320  # Positioned below the table

        tavern_options = ["Add Member", "Remove Member", "Character Status", "Reorder", "Divvy Gold", "Disband Party", "Exit Tavern"]

        tavern_buttons = []
        for i, option in enumerate(tavern_options):
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.screen_width // 2 - button_width // 2, start_y + i * (button_height + button_spacing)), (button_width, button_height)), text=option, manager=self.manager)
            tavern_buttons.append(button)

        # Main tavern loop
        tavern_running = True
        while tavern_running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        tavern_running = False

                # Handle table events
                self.handle_table_events(event)

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    for button in tavern_buttons:
                        if event.ui_element == button:
                            if button.text == "Exit Tavern":
                                tavern_running = False
                            else:
                                self.handle_tavern_option(button.text, party, roster)
                                # Update table after any action
                                self.create_party_table()

                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.screen.fill(self.BLACK)
            self.manager.draw_ui(self.screen)
            pygame.display.update()

        # Cleanup
        if hasattr(self, 'party_table'):
            self.party_table.kill()
        for button in tavern_buttons:
            button.kill()

    def handle_tavern_option(self, option: str):
        """Handle tavern menu options"""
        if option == "Add Member":
            self.show_add_member_dialog()

        elif option == "Remove Member":
            self.show_remove_member_dialog()

        elif option == "Character Status":
            if not self.party:
                self.show_message_dialog("No characters in the party!")
                return
            self.show_character_select_dialog(self.show_character_status)

        elif option == "Reorder":
            if not self.party:
                self.show_message_dialog("No characters in the party!")
                return
            self.show_reorder_dialog()

        elif option == "Divvy Gold":
            if not self.party:
                self.show_message_dialog("No characters in the party!")
                return
            total_gold = sum([c.gold for c in self.party])
            share = total_gold // len(self.party)
            for char in self.party:
                char.gold = share
                save_character(char, _dir=self.characters_dir)
            self.show_message_dialog("All the party's gold has been divided.")

        elif option == "Disband Party":
            if not self.party:
                self.show_message_dialog("No characters in the party!")
                return
            self.show_confirm_dialog("Are you sure you want to disband the party?", lambda: self.disband_party())

    def show_message_dialog(self, message: str):
        """Show a message dialog"""
        dialog = pygame_gui.windows.UIMessageWindow(rect=pygame.Rect((self.screen_width // 2 - 200, self.screen_height // 2 - 100), (400, 200)), html_message=message, manager=self.manager)

    def show_confirm_dialog(self, message: str, callback):
        """Show a confirmation dialog"""
        dialog = pygame_gui.windows.UIConfirmationDialog(rect=pygame.Rect((self.screen_width // 2 - 200, self.screen_height // 2 - 100), (400, 200)), manager=self.manager, action_long_desc=message, window_title="Confirm", action_short_name="Confirm", blocking=True)

        @dialog.confirmation_dialog_events.connect
        def on_confirmation(confirmed: bool):
            if confirmed:
                callback()

    def show_add_member_dialog(self):
        """Show dialog for adding party members"""
        available_chars = [c for c in self.roster if c not in self.party]
        if not available_chars:
            self.show_message_dialog("No available characters to add!")
            return

        options = [f"{c.name} - Level {c.level} {c.class_type}" for c in available_chars]
        dialog = pygame_gui.windows.UISelectionList(relative_rect=pygame.Rect((self.screen_width // 2 - 200, self.screen_height // 2 - 200), (400, 400)), item_list=options, manager=self.manager)

        # Add selection handling...

    def disband_party(self):
        """Disband the party"""
        for char in self.party:
            char.id_party = -1
            save_character(char, _dir=self.characters_dir)
        self.party.clear()

    def quit_game(self):
        self.running = False

    def run(self):
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit_game()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    for button in self.buttons:
                        if event.ui_element == button:
                            self.handle_destination(button.text)

                self.manager.process_events(event)

            # Update the UI
            self.manager.update(time_delta)

            # Draw everything
            self.screen.fill((0, 0, 0))  # Black background
            self.manager.draw_ui(self.screen)

            pygame.display.update()


def main():
    if "TERM" not in os.environ:
        os.environ["TERM"] = "xterm-256color"

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
