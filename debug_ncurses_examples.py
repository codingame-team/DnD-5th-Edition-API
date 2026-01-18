#!/usr/bin/env python3
"""
Example: How to debug main_ncurses.py with PyCharm

This file demonstrates best practices for debugging ncurses applications
in PyCharm using main_pexpect.py
"""

import logging

# ============================================================================
# SETUP: Configure logging for debugging
# ============================================================================

# Create logger for debugging (works alongside PyCharm debugger)
logging.basicConfig(
    filename='ncurses_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ncurses_debug')

# ============================================================================
# DEBUGGING TECHNIQUES
# ============================================================================

# Technique 1: Breakpoints in Business Logic (✅ GOOD)
# ----------------------------------------------------------------------------
def handle_user_input_good_example(self, key_code: int):
    """
    Example of where to place breakpoints - in business logic

    To debug in PyCharm:
    1. Set breakpoint on line below (click in margin)
    2. Run: main_pexpect.py ncurses (Debug mode)
    3. When breakpoint hits, inspect variables
    """
    # ← BREAKPOINT HERE ✅
    logger.debug(f"Received key: {key_code}")

    if key_code == ord('\n'):  # Enter key
        # ← BREAKPOINT HERE ✅ (inspect self.cursor, self.mode, etc.)
        selected_option = self.get_selected_option()
        logger.debug(f"Selected: {selected_option}")

        # ← BREAKPOINT HERE ✅ (verify selection before processing)
        self.process_selection(selected_option)


# Technique 2: DO NOT put breakpoints in draw functions (❌ BAD)
# ----------------------------------------------------------------------------
def draw_menu_bad_example(self, screen):
    """
    Example of where NOT to place breakpoints - in drawing code

    Why? NCurses display will be corrupted when paused
    Solution: Use logging instead
    """
    # ❌ DON'T PUT BREAKPOINT HERE - screen will freeze/corrupt

    # ✅ DO THIS INSTEAD - use logging
    logger.debug(f"Drawing menu with {len(self.options)} options")

    for idx, option in enumerate(self.options):
        # ❌ DON'T PUT BREAKPOINT HERE
        logger.debug(f"Drawing option {idx}: {option}")
        screen.addstr(idx, 0, option)


# Technique 3: Debug data loading/saving (✅ GOOD)
# ----------------------------------------------------------------------------
def load_game_data_debug_example(self):
    """
    Example: Debug data loading with detailed logging

    Breakpoints work well here since no UI is being drawn
    """
    # ← BREAKPOINT HERE ✅ (before loading)
    logger.info("Starting game data load")

    try:
        # ← BREAKPOINT HERE ✅ (inspect path)
        roster_path = self.get_roster_path()
        logger.debug(f"Loading roster from: {roster_path}")

        # ← BREAKPOINT HERE ✅ (step into to see loading logic)
        self.roster = self.load_roster(roster_path)

        # ← BREAKPOINT HERE ✅ (verify roster loaded)
        logger.info(f"Loaded {len(self.roster)} characters")

        # Log details for each character (visible in log file)
        for char in self.roster:
            logger.debug(f"  - {char.name} (Level {char.level})")

    except Exception as e:
        # ← BREAKPOINT HERE ✅ (catch errors)
        logger.error(f"Failed to load roster: {e}", exc_info=True)
        raise


# Technique 4: Conditional breakpoints (✅ ADVANCED)
# ----------------------------------------------------------------------------
def handle_menu_selection_advanced(self, cursor_position: int):
    """
    Example: Use conditional breakpoints for specific cases

    In PyCharm:
    1. Right-click breakpoint
    2. Add condition: cursor_position == 3
    3. Breakpoint only hits when cursor is at position 3
    """
    # ← CONDITIONAL BREAKPOINT: cursor_position == 3
    logger.debug(f"Menu selection at position {cursor_position}")

    # Your logic here
    if cursor_position == 3:
        # This specific case can be debugged
        logger.debug("Special case: position 3 selected")


# Technique 5: Watch expressions (✅ ADVANCED)
# ----------------------------------------------------------------------------
def game_state_debug_example(self):
    """
    Example: Use watch expressions to monitor state

    In PyCharm Debug panel:
    1. Right-click in Variables panel
    2. Add Watch: len(self.party)
    3. Add Watch: self.mode
    4. See values update as you step through
    """
    # ← BREAKPOINT HERE ✅
    # Add watches:
    # - len(self.party)
    # - len(self.roster)
    # - self.current_location
    # - self.gold

    logger.debug("Game state check:")
    logger.debug(f"  Party size: {len(self.party)}")
    logger.debug(f"  Roster size: {len(self.roster)}")
    logger.debug(f"  Mode: {self.mode}")


# ============================================================================
# REAL-WORLD DEBUGGING SCENARIOS
# ============================================================================

# Scenario 1: "Why isn't my character loading?"
# ----------------------------------------------------------------------------
def debug_character_loading():
    """
    Problem: Characters not appearing in roster

    Debug steps:
    1. Breakpoint in load_game_data()
    2. Inspect self.characters_dir
    3. Step into get_roster()
    4. Verify files are being read
    5. Check Character objects are created correctly
    """
    # In main_ncurses.py, add breakpoints at:
    # Line ~230: self.roster = get_roster(self.characters_dir)
    # Then step through to see what happens
    pass


# Scenario 2: "Menu selection not working"
# ----------------------------------------------------------------------------
def debug_menu_selection():
    """
    Problem: Selecting menu item doesn't do anything

    Debug steps:
    1. Breakpoint in _handle_castle() (or relevant handler)
    2. Press Enter in the game
    3. Breakpoint should hit
    4. Inspect self.castle_cursor
    5. Step through the if/elif chain to see which branch executes
    """
    # In main_ncurses.py, add breakpoints at:
    # Line ~XXX: def _handle_castle(self, c: int):
    # Line ~XXX: if c in (ord('\n'), ord('\r')):
    pass


# Scenario 3: "Game crashes on save"
# ----------------------------------------------------------------------------
def debug_save_crash():
    """
    Problem: Game crashes when saving

    Debug steps:
    1. Breakpoint in save_character() or save_party()
    2. Inspect the character object
    3. Check file path is valid
    4. Step through pickle.dump() to see where it fails
    5. Catch exception and log details
    """
    # In main_ncurses.py, add breakpoints at:
    # Line ~XXX: def save_character(char, _dir):
    # Wrap in try/except with logging
    pass


# ============================================================================
# DEBUGGING CHECKLIST
# ============================================================================

"""
Before starting debug session:
□ Configuration set to main_pexpect.py with parameter 'ncurses'
□ "Emulate terminal in output console" is checked
□ TERM=xterm-256color in environment variables
□ Breakpoints placed in business logic (not drawing code)
□ Logging configured for detailed output

During debug session:
□ Use F8 to step over, F7 to step into
□ Inspect variables in Debug panel
□ Check log file for additional context
□ Use watches for important state variables
□ Test specific scenarios with conditional breakpoints

After finding the bug:
□ Fix the code
□ Test in PyCharm debugger
□ Test in real terminal to verify UI
□ Update tests if needed
"""


# ============================================================================
# COMMON PATTERNS
# ============================================================================

class DebugPatterns:
    """Common debugging patterns for ncurses apps"""

    @staticmethod
    def debug_with_logging(func):
        """Decorator to add automatic logging to functions"""
        def wrapper(*args, **kwargs):
            logger.debug(f"Entering {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__} with result: {result}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise
        return wrapper

    @staticmethod
    def safe_curses_call(func):
        """Decorator to safely call curses functions with error handling"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Curses error in {func.__name__}: {e}")
                # Don't crash the whole app
                return None
        return wrapper


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("This is an example file showing debugging techniques.")
    print()
    print("To debug main_ncurses.py with PyCharm:")
    print()
    print("1. Open PyCharm")
    print("2. Run → Edit Configurations")
    print("3. Create new Python configuration:")
    print("   - Script: main_pexpect.py")
    print("   - Parameters: ncurses")
    print("   - ☑ Emulate terminal in output console")
    print("4. Open main_ncurses.py")
    print("5. Place breakpoints (see examples above)")
    print("6. Click Debug button (🐞)")
    print()
    print("For more info, see: PYCHARM_DEBUG_GUIDE.md")

