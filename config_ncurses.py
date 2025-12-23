"""
Configuration file for DnD 5E NCurses interface
Customize the game appearance and behavior here
"""

# Terminal settings
MIN_COLS = 80  # Minimum terminal width
MIN_LINES = 24  # Minimum terminal height

# Display settings
SHOW_DEBUG_INFO = False  # Show debug information
SHOW_FPS = False  # Show frames per second
ANIMATION_SPEED = 0.15  # Seconds between animation frames

# Color scheme (if terminal supports colors)
COLOR_SCHEME = {
    'header': 1,      # Green
    'error': 2,       # Red
    'warning': 3,     # Yellow
    'info': 4,        # Cyan
    'success': 1,     # Green
    'normal': 0,      # Default
}

# UI settings
MESSAGE_TIMEOUT = 2.0  # Seconds to show panel messages
MESSAGE_HISTORY_SIZE = 100  # Maximum messages in log
CURSOR_CHAR = '►'  # Character for menu cursor
EQUIPPED_MARKER = '(E)'  # Marker for equipped items

# Keyboard bindings
KEY_BINDINGS = {
    'up': ['KEY_UP', 'k'],
    'down': ['KEY_DOWN', 'j'],
    'left': ['KEY_LEFT', 'h'],
    'right': ['KEY_RIGHT', 'l'],
    'select': ['\n', '\r'],
    'back': ['KEY_ESC', 27],
    'quit': ['q', 'Q'],
    'inventory': ['i', 'I'],
    'menu': ['m', 'M'],
    'help': ['?', 'h'],
}

# Game settings
AUTO_SAVE = True  # Auto-save on important actions
SAVE_FILE = 'save_game.json'
CHARACTERS_DIR = 'characters'
PAUSE_ON_LEVEL_UP = True  # Pause when character levels up

# Party settings
MAX_PARTY_SIZE = 6  # Maximum characters in party
MAX_ROSTER_SIZE = 100  # Maximum characters in roster

# Combat settings
SHOW_COMBAT_ANIMATION = True
COMBAT_DELAY = 0.5  # Seconds between combat actions
SHOW_DAMAGE_NUMBERS = True
SHOW_DICE_ROLLS = True

# Dungeon settings
ENCOUNTER_RATE = 0.4  # Probability of encounter when wandering
TREASURE_RATE = 0.3  # Probability of finding treasure
SHOW_MINI_MAP = False  # Show minimap (if implemented)

# Debug settings (for development)
DEBUG_MODE = False
VERBOSE_LOGGING = False
SKIP_INTRO = False
FAST_MODE = False  # Skip animations and delays

# File paths
GAME_DATA_PATH = './data'
SAVE_GAME_PATH = './gameState'
MAZE_PATH = './maze_tk'

# Feature flags (for gradual rollout)
FEATURES = {
    'character_creation': False,  # Character creation screen
    'combat_system': False,       # Full combat implementation
    'inventory_system': False,    # Advanced inventory management
    'trading_post': False,        # Buy/sell equipment
    'temple_services': False,     # Resurrection, healing
    'dungeon_exploration': False, # Maze exploration
    'save_load': True,            # Save/load game
    'party_management': True,     # Recruit/dismiss characters
}

# UI Layout
LAYOUT = {
    'header_height': 2,
    'footer_height': 3,
    'sidebar_width': 20,
    'message_area_height': 5,
}

# Text formatting
TEXT = {
    'title': '=== {} ===',
    'separator': '─' * 80,
    'bullet': '• ',
    'cursor': '► ',
    'empty_slot': '(empty)',
}

# Messages
MESSAGES = {
    'welcome': 'Welcome to Dungeons & Dragons 5th Edition!',
    'loading': 'Loading game data...',
    'saving': 'Saving game...',
    'saved': 'Game saved successfully!',
    'error_load': 'Error loading game data',
    'error_save': 'Error saving game',
    'terminal_too_small': 'Terminal too small. Minimum: {}x{}',
    'no_party': 'No characters in party',
    'no_roster': 'No characters available',
    'party_full': 'Party is full (max {})',
    'character_added': 'Added {} to party',
    'character_removed': 'Removed {} from party',
}

# Color pairs initialization
def init_colors():
    """Initialize color pairs if terminal supports colors"""
    import curses

    if curses.has_colors():
        curses.start_color()

        # Basic colors
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # Bright variants (if supported)
        try:
            curses.init_pair(11, curses.COLOR_GREEN | curses.A_BOLD, curses.COLOR_BLACK)
            curses.init_pair(12, curses.COLOR_RED | curses.A_BOLD, curses.COLOR_BLACK)
            curses.init_pair(13, curses.COLOR_YELLOW | curses.A_BOLD, curses.COLOR_BLACK)
            curses.init_pair(14, curses.COLOR_CYAN | curses.A_BOLD, curses.COLOR_BLACK)
        except:
            pass  # Terminal doesn't support bold colors

# Import this config in main_ncurses.py:
# from config_ncurses import *

