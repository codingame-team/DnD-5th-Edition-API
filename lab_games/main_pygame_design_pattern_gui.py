import os

import pygame_gui
import pygame

from main import get_roster, load_party, save_character
from tools.common import get_save_game_path


class BaseGUI:
    """Base class for GUI components"""

    def __init__(
        self, manager: pygame_gui.UIManager, screen_width: int, screen_height: int
    ):
        self.manager = manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.elements = []  # Track UI elements for cleanup

    def cleanup(self):
        """Remove all UI elements"""
        for element in self.elements:
            element.kill()
        self.elements.clear()


class CharacterMenuGUI(BaseGUI):
    """Handles character context menu"""

    def __init__(self, manager: pygame_gui.UIManager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)
        self.is_visible = False
        self.context_menu = None
        self.callback_handlers = {}
        self.current_character = None

    def hide(self):
        """Hide the character menu"""
        self.is_visible = False  # Add any other cleanup or hiding logic needed

    def show_menu(self, character, position, callbacks):
        """Show context menu for selected character"""
        self.current_character = character
        self.callback_handlers = callbacks

        options = ["View Status", "Remove from Party", "View Equipment", "Cancel"]
        menu_width = 200
        menu_height = 30  # Height for dropdown

        # Create context menu
        self.context_menu = pygame_gui.elements.UIDropDownMenu(
            options_list=options,
            starting_option="View Status",
            relative_rect=pygame.Rect(position, (menu_width, menu_height)),
            manager=self.manager,
        )
        self.elements.append(self.context_menu)

    def process_event(self, event):
        """Process UI events"""
        if (
            event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
            and event.ui_element == self.context_menu
        ):
            self.handle_selection(event.text)

    def handle_selection(self, option: str):
        """Handle menu selection"""
        if option in self.callback_handlers and self.current_character:
            self.callback_handlers[option](self.current_character)
        self.cleanup()

    def cleanup(self):
        """Remove all UI elements"""
        super().cleanup()
        self.context_menu = None
        self.callback_handlers = {}
        self.current_character = None


class CharacterStatusGUI(BaseGUI):
    """Handles character status display"""

    def show_status(self, character):
        # Create status window
        window_width = 400
        window_height = 500
        x_pos = (self.screen_width - window_width) // 2
        y_pos = (self.screen_height - window_height) // 2

        status_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((x_pos, y_pos), (window_width, window_height)),
            manager=self.manager,
            window_display_title=f"{character.name}'s Status",
        )
        self.elements.append(status_window)

        # Add character info
        status_text = (
            f"Name: {character.name}\n"
            f"Level: {character.level}\n"
            f"Class: {character.class_type}\n"
            f"Gold: {character.gold}\n"
            # Add more character stats here
        )

        text_box = pygame_gui.elements.UITextBox(
            html_text=status_text,
            relative_rect=pygame.Rect(
                (10, 10), (window_width - 20, window_height - 60)
            ),
            manager=self.manager,
            container=status_window,
        )
        self.elements.append(text_box)


class CharacterEquipmentGUI(BaseGUI):
    """Handles character equipment display"""

    def show_equipment(self, character):
        window_width = 400
        window_height = 500
        x_pos = (self.screen_width - window_width) // 2
        y_pos = (self.screen_height - window_height) // 2

        equip_window = pygame_gui.elements.UIWindow(
            rect=pygame.Rect((x_pos, y_pos), (window_width, window_height)),
            manager=self.manager,
            window_display_title=f"{character.name}'s Equipment",
        )
        self.elements.append(equip_window)

        # Add equipment list
        equipment_text = "<br>".join([str(item) for item in character.inventory])
        if not equipment_text:
            equipment_text = "No equipment"

        text_box = pygame_gui.elements.UITextBox(
            html_text=equipment_text,
            relative_rect=pygame.Rect(
                (10, 10), (window_width - 20, window_height - 60)
            ),
            manager=self.manager,
            container=equip_window,
        )
        self.elements.append(text_box)


class PartyDisplayGUI(BaseGUI):
    """Handles party member display and selection"""

    def __init__(self, manager: pygame_gui.UIManager, screen_width: int, screen_height: int):
        super().__init__(manager, screen_width, screen_height)
        self.party_list = None
        self.item_height = 30  # Height of each party member entry
        self.display_rect = None

    def create_party_display(self, party):
        """Create scrollable party display"""
        display_width = 600
        display_height = 200
        x_pos = (self.screen_width - display_width) // 2
        y_pos = 100

        self.display_rect = pygame.Rect((x_pos, y_pos), (display_width, display_height))

        # Create party list items
        if not party:
            party_items = ["No party members"]
        else:
            party_items = [
                f"{char.name} - Level {char.level} {char.class_type} - Gold: {char.gold}"
                for char in party
            ]

        # Create selection list
        self.party_list = pygame_gui.elements.UISelectionList(
            relative_rect=self.display_rect,
            item_list=party_items,
            manager=self.manager,
            allow_double_clicks=True,
        )
        self.elements.append(self.party_list)

    def get_character_at_position(self, mouse_pos, party) -> int:
        """Get the index of character at mouse position"""
        if not self.display_rect or not self.party_list:
            return -1

        # Check if click is within the party display area
        if not self.display_rect.collidepoint(mouse_pos):
            return -1

        # Calculate relative position within the list
        relative_y = mouse_pos[1] - self.display_rect.top

        # Add scroll offset if scroll bar exists
        if hasattr(self.party_list, "scroll_bar") and self.party_list.scroll_bar:
            relative_y += self.party_list.scroll_bar.scroll_position

        # Calculate index based on item height and list view position
        visible_index = relative_y // self.item_height

        # Validate index
        if 0 <= visible_index < len(party):
            return visible_index
        return -1

    def get_selected_character_index(self) -> int:
        """Get the currently selected character index"""
        if not self.party_list:
            return -1

        selected_text = self.party_list.get_single_selection()
        if not selected_text:
            return -1

        # Find all indices where the text matches
        matching_indices = [i for i, item in enumerate(self.party_list.item_list) if item.get('text') == selected_text]

        # Return the first matching index if any found, otherwise return -1
        return min(matching_indices) if matching_indices else -1

    def cleanup(self):
        """Remove all UI elements"""
        super().cleanup()
        self.party_list = None
        self.display_rect = None


class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.window_surface = pygame.display.set_mode(
            (self.screen_width, self.screen_height)
        )
        self.manager = pygame_gui.UIManager((self.screen_width, self.screen_height))

        # Initialize GUI components
        self.party_display = PartyDisplayGUI(
            self.manager, self.screen_width, self.screen_height
        )
        self.character_menu = CharacterMenuGUI(
            self.manager, self.screen_width, self.screen_height
        )
        self.character_status = CharacterStatusGUI(
            self.manager, self.screen_width, self.screen_height
        )
        self.character_equipment = CharacterEquipmentGUI(
            self.manager, self.screen_width, self.screen_height
        )

        self.clock = pygame.time.Clock()
        self.running = True

        """Initialize all game data and state"""
        # Setup paths
        self.path = os.path.dirname(__file__)
        self.abspath = os.path.abspath(self.path)
        self.game_path = get_save_game_path()
        self.characters_dir = f"{self.game_path}/characters"

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

        # Create initial party display
        self.party_display.create_party_display(self.party)

    def gilgamesh_tavern(self):
        """Gilgamesh's Tavern interface"""
        # Store current state
        previous_menu = self.current_menu
        previous_location = self.location

        # Clear existing UI
        self.manager.clear_and_reset()

        # Create header
        self.header = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 20), (self.screen_width, 50)),
            text="** GILGAMESH'S TAVERN **",
            manager=self.manager,
        )

        # Create party display
        self.party_display.create_party_display(self.party)

        # Create tavern menu buttons  # ... rest of tavern code ...

    def show_character_menu(self, character):
        """Show context menu for selected character"""
        # Hide any existing menus first
        self.hide_all_character_menus()

        callbacks = {"View Status": self.show_character_status, "Remove from Party": self.remove_character_from_party, "View Equipment": self.show_character_equipment, }
        mouse_pos = pygame.mouse.get_pos()
        self.character_menu.show_menu(character, mouse_pos, callbacks)

    def hide_all_character_menus(self):
        """Hide all open character menus"""
        if hasattr(self, 'character_menu'):
            self.character_menu.hide()

    def show_character_status(self, character):
        """Show character status window"""
        self.character_status.show_status(character)

    def show_character_equipment(self, character):
        """Show character equipment window"""
        self.character_equipment.show_equipment(character)

    def update_party_display(self):
        """Update the party display after changes"""
        self.party_display.cleanup()
        self.party_display.create_party_display(self.party)

    def remove_character_from_party(self, character):
        """Remove character from party"""
        if character in self.party:
            self.party.remove(character)
            character.id_party = -1
            save_character(character, _dir=self.characters_dir)
            self.update_party_display()

    def handle_events(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                # First check if we clicked on a UI element
                if (
                    not self.manager.get_focus_set()
                ):  # Only process if we didn't click on a UI element
                    char_index = self.party_display.get_character_at_position(
                        mouse_pos, self.party
                    )
                    if char_index >= 0:
                        self.show_character_menu(self.party[char_index])

        # Handle selection list double clicks
        if event.type == pygame_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == self.party_display.party_list:
                selected_index = self.party_display.get_selected_character_index()
                if selected_index >= 0 and selected_index < len(self.party):
                    self.show_character_menu(self.party[selected_index])

        # Process character menu events
        self.character_menu.process_event(event)

        self.manager.process_events(event)

    def run(self):
        """Main game loop"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.handle_events(event)

            self.manager.update(time_delta)
            self.window_surface.fill((0, 0, 0))
            self.manager.draw_ui(self.window_surface)
            pygame.display.update()


def main():
    if "TERM" not in os.environ:
        os.environ["TERM"] = "xterm-256color"

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
