#!/usr/bin/env python3
"""
DnD 5th Edition API - NCurses Interface v2
✅ MIGRATED VERSION - Using dnd-5e-core package instead of dao_classes
"""

import curses
import time
import os
import sys
import pickle
from typing import List
from random import seed, randint

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

from dnd_5e_core.entities import Character, Monster
from dnd_5e_core.equipment import Weapon, Armor, Cost, Equipment, EquipmentCategory, HealingPotion
from dnd_5e_core.ui import cprint, Color

# Note: Data directory is now in dnd-5e-core/data and will be auto-detected
# No need to call set_data_directory() anymore

from tools.common import get_save_game_path
from populate_functions import (populate, request_monster, request_armor, request_weapon, request_equipment, request_equipment_category)

print("✅ [MIGRATION v2] Successfully loaded with dnd-5e-core package")
print("   Game logic: dnd-5e-core")
print("   Data loading: populate_functions.py")
print()


# Define functions that are in main.py but we need without PyQt5
def load_potions_collections():
	"""Load healing potions - stub for now"""
	return []


def get_roster(characters_dir: str):
	"""Load roster from character files"""
	import os
	import pickle
	roster = []
	if not os.path.exists(characters_dir):
		return roster
	try:
		char_file_list = os.scandir(characters_dir)
		for entry in char_file_list:
			if entry.is_file() and entry.name.endswith(".dmp"):
				try:
					with open(entry, "rb") as f1:
						roster.append(pickle.load(f1))
				except Exception:
					pass
	except Exception:
		pass
	return roster


def load_party(_dir: str):
	"""Load party from file"""
	import os
	import pickle
	party = []
	party_file = os.path.join(_dir, "party.dmp")
	if os.path.exists(party_file):
		try:
			with open(party_file, "rb") as f1:
				party = pickle.load(f1)
		except Exception:
			pass
	return party if party else []


def save_party(party, _dir: str):
	"""Save party to file"""
	import os
	import pickle
	os.makedirs(_dir, exist_ok=True)
	party_file = os.path.join(_dir, "party.dmp")
	with open(party_file, "wb") as f1:
		pickle.dump(party, f1)


def save_character(char, _dir: str):
	"""Save character to file"""
	import os
	import pickle
	os.makedirs(_dir, exist_ok=True)
	char_file = os.path.join(_dir, f"{char.name}.dmp")
	with open(char_file, "wb") as f1:
		pickle.dump(char, f1)


def load_character_collections():
	"""Load character creation collections - stub for now"""
	return [], [], [], [], [], [], {}, {}, []


def load_dungeon_collections():
	"""Load dungeon collections without PyQt5 dependency"""
	monster_names = populate(collection_name="monsters", key_name="results")
	monsters = [request_monster(name) for name in monster_names]
	armor_names = populate(collection_name="armors", key_name="equipment")
	armors = [request_armor(name) for name in armor_names]
	weapon_names = populate(collection_name="weapons", key_name="equipment")
	weapons = [request_weapon(name) for name in weapon_names]
	equipment_names = populate(collection_name="equipment", key_name="results")
	equipments = [request_equipment(name) for name in equipment_names]
	equipment_category_names = populate(collection_name="equipment-categories", key_name="results")
	equipment_categories = [request_equipment_category(name) for name in equipment_category_names]
	healing_potions = load_potions_collections()
	return monsters, armors, weapons, equipments, equipment_categories, healing_potions


 # Import D&D 5e rules from package
from dnd_5e_core.mechanics import (
    XP_LEVELS,
    generate_encounter_distribution,
    ENCOUNTER_TABLE,
    ENCOUNTER_GOLD_TABLE,
    get_encounter_gold,
)
from dnd_5e_core.mechanics.encounter_builder import select_monsters_by_encounter_table

# Import UI helpers
from ui_helpers import (
    display_character_sheet,
    menu_read_options,
    delete_character_prompt_ok,
    rename_character_prompt_ok,
)

# Import project-specific functions from main
from main import (
    create_new_character,
    explore_dungeon,
)

# Compatibility aliases
load_xp_levels_func = XP_LEVELS
generate_encounter_levels = generate_encounter_distribution
load_encounter_table = lambda: ENCOUNTER_TABLE
load_encounter_gold_table = lambda: ENCOUNTER_GOLD_TABLE
generate_encounter = select_monsters_by_encounter_table


MIN_COLS = 80
MIN_LINES = 24
SAVE_FILE = 'save_game.json'
MAX_ROSTER = 100  # Maximum number of characters allowed
POTION_INITIAL_PACK = 15


class Location:
	"""Represents a game location"""
	CASTLE = 'castle'
	EDGE_OF_TOWN = 'edge_of_town'
	TAVERN = 'tavern'
	INN = 'inn'
	TEMPLE = 'temple'
	TRADING_POST = 'trading_post'
	TRAINING_GROUNDS = 'training_grounds'
	DUNGEON = 'dungeon'


class DnDCursesUI:
	def __init__(self, stdscr):
		self.stdscr = stdscr

		# Initialize game data
		self.game_path = get_save_game_path()
		self.characters_dir = f"{self.game_path}/characters"

		# Load game resources
		self.xp_levels: List[int] = []
		self.monsters = []
		self.armors = []
		self.weapons = []
		self.equipments = []
		self.equipment_categories = []
		self.potions = []

		# Game state
		self.roster: List[Character] = []
		self.party: List[Character] = []
		self.location = Location.CASTLE

		# UI state
		self.mode = 'main_menu'
		self.menu_cursor = 0
		self.location_cursor = 0
		self.castle_cursor = 0
		self.edge_cursor = 0
		self.party_cursor = 0
		self.tavern_cursor = 0
		self.inn_cursor = 0
		self.temple_cursor = 0
		self.training_cursor = 0
		self.roster_cursor = 0
		self.char_status_cursor = 0
		self.trading_cursor = 0
		self.trading_action_cursor = 0
		self.buy_cursor = 0
		self.sell_cursor = 0
		self.reorder_cursor = 0
		self.char_select_cursor = 0
		self.inventory_item_cursor = 0  # For character inventory management
		self.spell_cursor = 0  # For spell viewing
		self.cheat_cursor = 0  # For cheat menu

		# Submenu cursors
		self.character_to_rest = None
		self.character_selected = None
		self.character_trading = None
		self.character_viewing = None
		self.reorder_selected = None

		# Dungeon exploration
		self.dungeon_message = ""
		self.dungeon_step = 0
		self.dungeon_log = []

		# Game data collections
		self.races = []
		self.subraces = []
		self.classes = []
		self.alignments = []
		self.proficiencies = []
		self.names = {}
		self.human_names = {}
		self.spells = []
		self.encounter_table = {}
		self.encounter_gold_table = []
		self.available_crs = []

		# Message system
		self.messages: List[str] = []
		self.panel_message: str = ""
		self.panel_message_time: float = 0

		# Previous mode tracking
		self.previous_mode = None
		self.previous_location = None

	def push_message(self, msg: str) -> None:
		"""Add message to scrolling log"""
		self.messages.append(msg)
		if len(self.messages) > 100:
			self.messages.pop(0)

	def push_panel(self, msg: str) -> None:
		"""Set panel message (shown for 2 seconds)"""
		self.panel_message = msg
		self.panel_message_time = time.time()

	def get_panel_message(self) -> str:
		"""Get current panel message if still valid"""
		if self.panel_message and time.time() - self.panel_message_time < 2:
			return self.panel_message
		return ""

	def check_bounds(self):
		"""Ensure terminal is large enough"""
		lines, cols = self.stdscr.getmaxyx()
		while cols < MIN_COLS or lines < MIN_LINES:
			try:
				self.stdscr.erase()
				self.stdscr.addstr(0, 0, f"Terminal too small. Minimum: {MIN_COLS}x{MIN_LINES}")
				self.stdscr.addstr(1, 0, f"Current: {cols}x{lines}")
				self.stdscr.addstr(2, 0, "Resize to continue...")
				self.stdscr.refresh()
			except curses.error:
				pass
			time.sleep(0.5)
			lines, cols = self.stdscr.getmaxyx()

	def load_game_data(self):
		"""Load all game data"""
		self.push_message("Loading game data...")

		# Load XP levels
		self.xp_levels = self.load_xp_levels()

		# Load databases
		self.monsters, self.armors, self.weapons, self.equipments, self.equipment_categories, self.potions = load_dungeon_collections()

		# Filter out None values
		self.armors = list(filter(lambda a: a, self.armors))
		self.weapons = list(filter(lambda w: w, self.weapons))

		# Debug: Log data loaded
		if self.monsters:
			self.push_message(f"Loaded {len(self.monsters)} monsters")
		else:
			self.push_message("WARNING: No monsters loaded!")

		if self.weapons:
			self.push_message(f"Loaded {len(self.weapons)} weapons")
		else:
			self.push_message("WARNING: No weapons loaded!")

		if self.armors:
			self.push_message(f"Loaded {len(self.armors)} armors")
		else:
			self.push_message("WARNING: No armors loaded!")

		# Create directories if they don't exist
		os.makedirs(self.characters_dir, exist_ok=True)
		os.makedirs(self.game_path, exist_ok=True)

		# Load roster
		self.roster = get_roster(self.characters_dir)
		self.push_message(f"Loaded {len(self.roster)} characters from roster")

		# Load party
		self.party = load_party(_dir=self.game_path)
		self.push_message(f"Loaded {len(self.party)} characters in party")

		# Load encounter tables if available
		self.encounter_table = load_encounter_table()
		self.encounter_gold_table = load_encounter_gold_table()

		if self.encounter_table:
			self.push_message(f"Loaded encounter table")
		else:
			self.push_message("WARNING: No encounter table loaded!")

		# Load character collections (races, classes, spells, etc.)
		try:
			self.races, self.subraces, self.classes, self.alignments, _, _, self.names, self.human_names, self.spells = load_character_collections()

			# Debug: Check what was loaded
			if self.races and self.classes:
				self.push_message(f"✓ Loaded {len(self.races)} races, {len(self.classes)} classes, {len(self.spells)} spells")
			else:
				self.push_message(f"⚠ WARNING: races={len(self.races or [])}, classes={len(self.classes or [])}")
		except Exception as e:
			self.push_message(f"✗ ERROR loading character collections: {str(e)[:50]}")
			# Initialize empty to avoid errors
			self.races = []
			self.subraces = []
			self.classes = []
			self.alignments = []
			self.names = {}
			self.human_names = {}
			self.spells = []
			self.names = {}
			self.human_names = {}
			self.spells = []

		if self.monsters:
			from fractions import Fraction
			self.available_crs = [Fraction(str(m.challenge_rating)) for m in self.monsters]
			self.push_message(f"Available CRs: {len(self.available_crs)}")
		else:
			self.available_crs = []
			self.push_message("WARNING: No CRs available (no monsters)!")

	def load_xp_levels(self) -> List[int]:
		"""Load XP levels from file"""
		try:
			# Placeholder - adapt to your actual implementation
			return [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
		except Exception:
			return []

	def draw_header(self, title: str, lines: int, cols: int):
		"""Draw common header"""
		try:
			# Title bar
			title_bar = f" {title} ".center(cols, "=")
			self.stdscr.addstr(0, 0, title_bar[:cols - 1], curses.A_REVERSE | curses.A_BOLD)

			# Party info if exists
			if self.party:
				party_info = f"Party: {len(self.party)} | Location: {self.location}"
				self.stdscr.addstr(1, 0, party_info[:cols - 1])
		except curses.error:
			pass

	def draw_footer(self, instructions: str, lines: int, cols: int):
		"""Draw footer with instructions"""
		try:
			separator = "─" * min(cols - 1, 100)
			self.stdscr.addstr(lines - 3, 0, separator[:cols - 1])

			# Panel message
			panel_msg = self.get_panel_message()
			if panel_msg:
				self.stdscr.addstr(lines - 2, 0, f">>> {panel_msg}"[:cols - 1], curses.A_BOLD)

			# Instructions
			self.stdscr.addstr(lines - 1, 0, instructions[:cols - 1], curses.A_REVERSE)
		except curses.error:
			pass

	def draw_main_menu(self, lines: int, cols: int):
		"""Draw main menu"""
		self.check_bounds()
		try:
			self.draw_header("D&D 5E - Main Menu", lines, cols)

			options = ['Start New Game', 'Load Game', 'Cheat Menu', 'Options', 'Quit']

			start_y = 4
			for idx, opt in enumerate(options):
				marker = '►' if idx == self.menu_cursor else ' '
				self.stdscr.addstr(start_y + idx, 2, f"{marker} {opt}")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [q] Quit", lines, cols)
		except curses.error:
			pass

	def draw_location_menu(self, lines: int, cols: int):
		"""Draw location selection menu"""
		self.check_bounds()
		try:
			if self.location == Location.CASTLE:
				self.draw_castle_menu(lines, cols)
			elif self.location == Location.EDGE_OF_TOWN:
				self.draw_edge_menu(lines, cols)
		except curses.error:
			pass

	def draw_castle_menu(self, lines: int, cols: int):
		"""Draw castle menu"""
		try:
			self.draw_header("CASTLE", lines, cols)

			options = ["Gilgamesh's Tavern", "Adventurer's Inn", "Temple of Cant", "Boltac's Trading Post", "Edge of Town", "Save & Exit"]

			start_y = 4
			self.stdscr.addstr(start_y, 2, "What would you like to do?", curses.A_BOLD)

			for idx, opt in enumerate(options):
				marker = '►' if idx == self.castle_cursor else ' '
				self.stdscr.addstr(start_y + 2 + idx, 4, f"{marker} {opt}")

			# Display party info
			if self.party:
				party_y = start_y + 2 + len(options) + 2
				self.stdscr.addstr(party_y, 2, "Current Party:", curses.A_UNDERLINE)
				for idx, char in enumerate(self.party[:5]):  # Show max 5
					char_info = f"  {char.name} - Lvl {char.level} - HP: {char.hit_points}/{char.max_hit_points}"
					self.stdscr.addstr(party_y + 1 + idx, 2, char_info[:cols - 3])

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_edge_menu(self, lines: int, cols: int):
		"""Draw edge of town menu"""
		try:
			self.draw_header("EDGE OF TOWN", lines, cols)

			options = ["Training Grounds", "Enter Maze", "Castle", "Leave Game"]

			start_y = 4
			self.stdscr.addstr(start_y, 2, "Where would you like to go?", curses.A_BOLD)

			for idx, opt in enumerate(options):
				marker = '►' if idx == self.edge_cursor else ' '
				self.stdscr.addstr(start_y + 2 + idx, 4, f"{marker} {opt}")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_reorder_party(self, lines: int, cols: int):
		"""Draw party reorder interface in ncurses"""
		try:
			self.draw_header("REORDER PARTY", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, "Select character to move:", curses.A_BOLD)

			for idx, char in enumerate(self.party):
				marker = '►' if idx == self.reorder_cursor else ' '
				char_info = f"{marker} {idx + 1}. {char.name} - Lvl {char.level} {char.class_type.name}"
				self.stdscr.addstr(start_y + 2 + idx, 4, char_info[:cols - 5])

			if hasattr(self, 'reorder_selected') and self.reorder_selected is not None:
				y = start_y + 2 + len(self.party) + 2
				self.stdscr.addstr(y, 2, f"Moving: {self.party[self.reorder_selected].name}", curses.A_REVERSE)
				self.stdscr.addstr(y + 1, 2, "Select new position (↑/↓ then Enter)")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select/Confirm  [Esc] Cancel", lines, cols)
		except curses.error:
			pass

	def draw_char_select_menu(self, lines: int, cols: int, char_list, title):
		"""Draw character selection menu"""
		try:
			self.draw_header(title, lines, cols)

			start_y = 4
			if char_list:
				display_start = max(0, self.char_select_cursor - 10)
				for idx, char in enumerate(char_list[display_start:display_start + 15]):
					actual_idx = display_start + idx
					marker = '►' if actual_idx == self.char_select_cursor else ' '
					status = f" ({char.status})" if char.status != "OK" else ""
					char_info = f"{marker} {char.name} - Lvl {char.level} {char.class_type.name}{status}"
					self.stdscr.addstr(start_y + idx, 2, char_info[:cols - 3])
			else:
				self.stdscr.addstr(start_y, 2, "(No characters available)")

			self.draw_footer("[↑/↓] Navigate  [Enter] View Status  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_dungeon_explore(self, lines: int, cols: int):
		"""Draw dungeon exploration interface"""
		try:
			self.draw_header("DUNGEON EXPLORATION", lines, cols)

			start_y = 3

			# Calculate column widths - split screen in half
			party_col_start = 2
			party_col_width = (cols - 4) // 2
			monster_col_start = party_col_start + party_col_width + 2
			monster_col_width = cols - monster_col_start - 2

			# Party status (left side)
			self.stdscr.addstr(start_y, party_col_start, "PARTY STATUS:", curses.A_BOLD | curses.A_UNDERLINE)
			y = start_y + 1
			for idx, char in enumerate(self.party[:6]):
				hp_ratio = char.hit_points / max(char.max_hit_points, 1)
				hp_bar_length = int(hp_ratio * 10)
				hp_bar = f"[{'█' * hp_bar_length}{'·' * (10 - hp_bar_length)}]"

				# Color based on HP
				if hp_ratio > 0.66:
					color = curses.color_pair(1)  # Green
				elif hp_ratio > 0.33:
					color = curses.color_pair(3)  # Yellow
				else:
					color = curses.color_pair(2)  # Red

				status_str = f" [{char.status}]" if char.status != "OK" else ""
				char_info = f"{idx + 1}. {char.name}: {hp_bar} {char.hit_points}/{char.max_hit_points} HP{status_str}"
				self.stdscr.addstr(y, party_col_start + 2, char_info[:party_col_width - 2], color)
				y += 1

			party_height = y - start_y  # Track party section height

			# Monster status (right side) - only show if in combat
			if hasattr(self, 'dungeon_state') and self.dungeon_state.get('monsters'):
				monsters = self.dungeon_state.get('alive_monsters', self.dungeon_state.get('monsters', []))

				if monsters:
					self.stdscr.addstr(start_y, monster_col_start, "MONSTER STATUS:", curses.A_BOLD | curses.A_UNDERLINE)

					# Calculate how many monsters fit in the same height as party
					max_monster_rows = party_height - 1  # -1 for header
					monsters_per_col = max(6, max_monster_rows)  # At least 6 per column

					# Split monsters into columns if needed
					num_cols = (len(monsters) + monsters_per_col - 1) // monsters_per_col
					num_cols = min(num_cols, 2)  # Max 2 columns to avoid overflow

					col_width = monster_col_width // num_cols if num_cols > 1 else monster_col_width

					for col_idx in range(num_cols):
						start_idx = col_idx * monsters_per_col
						end_idx = min(start_idx + monsters_per_col, len(monsters))
						col_monsters = monsters[start_idx:end_idx]

						col_x = monster_col_start + (col_idx * col_width)
						mon_y = start_y + 1

						for idx, monster in enumerate(col_monsters):
							if mon_y >= start_y + party_height:
								break  # Don't exceed party height

							# Calculate monster HP bar
							hp_ratio = monster.hit_points / max(monster.max_hit_points, 1)
							hp_bar_length = int(hp_ratio * 8)  # Shorter bar for monsters
							hp_bar = f"[{'█' * hp_bar_length}{'·' * (8 - hp_bar_length)}]"

							# Color based on HP
							if hp_ratio > 0.66:
								color = curses.color_pair(1)  # Green
							elif hp_ratio > 0.33:
								color = curses.color_pair(3)  # Yellow
							else:
								color = curses.color_pair(2)  # Red

							# Display monster info
							monster_name = monster.name if hasattr(monster, 'name') else str(monster)
							monster_info = f"{monster_name[:15]}: {hp_bar} {monster.hit_points}/{monster.max_hit_points}"

							self.stdscr.addstr(mon_y, col_x, monster_info[:col_width - 1], color)
							mon_y += 1

			# Dungeon log (last 12 messages) - start after party/monster section
			log_y = start_y + party_height + 1
			if log_y < lines - 3:
				self.stdscr.addstr(log_y, 2, "COMBAT LOG:", curses.A_BOLD | curses.A_UNDERLINE)
				log_y += 1

				display_log = self.dungeon_log[-12:] if len(self.dungeon_log) > 12 else self.dungeon_log
				for msg in display_log:
					if log_y >= lines - 3:
						break
					# Colorize specific keywords
					if "KILLED" in msg or "DEAD" in msg or "DEFEAT" in msg:
						self.stdscr.addstr(log_y, 4, msg[:cols - 5], curses.color_pair(2))
					elif "VICTORY" in msg or "earned" in msg:
						self.stdscr.addstr(log_y, 4, msg[:cols - 5], curses.color_pair(1))
					elif "attacks" in msg or "launches" in msg:
						self.stdscr.addstr(log_y, 4, msg[:cols - 5], curses.color_pair(3))
					else:
						self.stdscr.addstr(log_y, 4, msg[:cols - 5])
					log_y += 1

			# Current message
			if self.dungeon_message:
				self.stdscr.addstr(lines - 3, 2, self.dungeon_message[:cols - 3], curses.A_BOLD)

			# Footer depends on whether all party is dead
			all_party_dead = all(c.hit_points <= 0 for c in self.party)
			if all_party_dead:
				self.draw_footer("[Enter] Return to Castle", lines, cols)
			else:
				self.draw_footer("[Enter] Continue  [Esc] Flee Combat", lines, cols)
		except curses.error:
			pass

	def draw_party_roster(self, lines: int, cols: int):
		"""Draw party and roster management"""
		try:
			self.draw_header("Party & Roster Management", lines, cols)

			start_y = 3

			# Party section
			self.stdscr.addstr(start_y, 2, "CURRENT PARTY", curses.A_UNDERLINE | curses.A_BOLD)
			if self.party:
				for idx, char in enumerate(self.party):
					marker = '►' if idx == self.party_cursor and self.party_cursor < len(self.party) else ' '
					char_info = f"{marker} {char.name} - Lvl {char.level} {char.class_type.name} - HP: {char.hit_points}/{char.max_hit_points}"
					self.stdscr.addstr(start_y + 1 + idx, 4, char_info[:cols - 5])
			else:
				self.stdscr.addstr(start_y + 1, 4, "(No characters in party)")

			# Roster section
			roster_y = start_y + len(self.party) + 3
			self.stdscr.addstr(roster_y, 2, "AVAILABLE ROSTER", curses.A_UNDERLINE | curses.A_BOLD)
			available_roster = [c for c in self.roster if c not in self.party and c.status == "OK"]

			if available_roster:
				display_start = max(0, self.party_cursor - len(self.party) - 5)
				for idx, char in enumerate(available_roster[display_start:display_start + 10]):
					actual_idx = idx + len(self.party)
					marker = '►' if actual_idx == self.party_cursor else ' '
					char_info = f"{marker} {char.name} - Lvl {char.level} {char.class_type.name}"
					self.stdscr.addstr(roster_y + 1 + idx, 4, char_info[:cols - 5])
			else:
				self.stdscr.addstr(roster_y + 1, 4, "(No available characters)")

			self.draw_footer("[↑/↓] Navigate  [Enter] Add/Remove  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_tavern_menu(self, lines: int, cols: int):
		"""Draw Gilgamesh's Tavern menu"""
		try:
			self.draw_header("GILGAMESH'S TAVERN", lines, cols)

			options = ["Add Member", "Remove Member", "Character Status", "Reorder", "Divvy Gold", "Disband Party", "Exit Tavern"]

			start_y = 4
			self.stdscr.addstr(start_y, 2, "What would you like to do?", curses.A_BOLD)

			for idx, opt in enumerate(options):
				marker = '►' if idx == self.tavern_cursor else ' '
				self.stdscr.addstr(start_y + 2 + idx, 4, f"{marker} {opt}")

			# Show party
			if self.party:
				party_y = start_y + 2 + len(options) + 2
				self.stdscr.addstr(party_y, 2, "Current Party:", curses.A_UNDERLINE)
				for idx, char in enumerate(self.party[:6]):  # Show all 6 members
					char_info = f"  {idx + 1}. {char.name} - Lvl {char.level} - HP: {char.hit_points}/{char.max_hit_points} - Gold: {char.gold}"
					self.stdscr.addstr(party_y + 1 + idx, 2, char_info[:cols - 3])

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_inn_menu(self, lines: int, cols: int):
		"""Draw Adventurer's Inn menu"""
		try:
			self.draw_header("ADVENTURER'S INN", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, "Welcome to Adventurer's Inn!", curses.A_BOLD)
			self.stdscr.addstr(start_y + 1, 2, "Who will Enter?")

			if self.party:
				for idx, char in enumerate(self.party):
					marker = '►' if idx == self.inn_cursor else ' '
					char_info = f"{marker} {char.name} - HP: {char.hit_points}/{char.max_hit_points} - Gold: {char.gold}GP"
					self.stdscr.addstr(start_y + 3 + idx, 4, char_info[:cols - 5])
			else:
				self.stdscr.addstr(start_y + 3, 4, "(No characters in party)")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select Room  [Esc] Exit Inn", lines, cols)
		except curses.error:
			pass

	def draw_inn_rooms(self, lines: int, cols: int, character):
		"""Draw room selection for Inn"""
		try:
			self.draw_header(f"ADVENTURER'S INN - {character.name}", lines, cols)

			rooms = [("The Stables (Free!)", 0, 0), ("A Cot (10 GP / Week)", 10, 1), ("Economy Room (100 GP / Week)", 100, 3), ("Merchant Suites (200 GP / Week)", 200, 7), ("The Royal Suites (500 GP / Week)", 500, 10)]

			start_y = 4
			self.stdscr.addstr(start_y, 2, f"Welcome {character.name}!", curses.A_BOLD)
			self.stdscr.addstr(start_y + 1, 2, f"HP: {character.hit_points}/{character.max_hit_points}  Gold: {character.gold}GP")

			for idx, (room_name, fee, weeks) in enumerate(rooms):
				marker = '►' if idx == self.inn_cursor else ' '
				affordable = "" if fee <= character.gold else " (Can't afford)"
				self.stdscr.addstr(start_y + 3 + idx, 4, f"{marker} {room_name}{affordable}"[:cols - 5])

			self.draw_footer("[↑/↓] Navigate  [Enter] Rest  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_temple_menu(self, lines: int, cols: int):
		"""Draw Temple of Cant menu"""
		try:
			self.draw_header("TEMPLE OF CANT", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, "Temple of Cant -- Praise God!!!", curses.A_BOLD)

			# Show characters that need healing/resurrection
			cures_costs = {"PARALYZED": 100, "STONED": 200, "DEAD": 250, "ASHES": 500}
			candidates = [(c, cures_costs.get(c.status, 0) * c.level) for c in self.roster if c.status in cures_costs]

			if candidates:
				self.stdscr.addstr(start_y + 2, 2, "Who do You Want to Save?")
				for idx, (char, cost) in enumerate(candidates):
					marker = '►' if idx == self.temple_cursor else ' '
					char_info = f"{marker} {char.name} - Status: {char.status} - Cost: {cost}GP"
					self.stdscr.addstr(start_y + 4 + idx, 4, char_info[:cols - 5])
			else:
				self.stdscr.addstr(start_y + 2, 2, "No more character to save HERE!")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Exit Temple", lines, cols)
		except curses.error:
			pass

	def draw_trading_post_menu(self, lines: int, cols: int):
		"""Draw Boltac's Trading Post character selection"""
		try:
			self.draw_header("BOLTAC'S TRADING POST", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, "Welcome to Boltac's!", curses.A_BOLD)
			self.stdscr.addstr(start_y + 1, 2, "Everyday, Everything Low Price!!")
			self.stdscr.addstr(start_y + 3, 2, "Who will Enter?")

			if self.party:
				for idx, char in enumerate(self.party):
					marker = '►' if idx == self.trading_cursor else ' '
					char_info = f"{marker} {char.name} - Gold: {char.gold}GP"
					self.stdscr.addstr(start_y + 5 + idx, 4, char_info[:cols - 5])
			else:
				self.stdscr.addstr(start_y + 5, 4, "(No characters in party)")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Exit", lines, cols)
		except curses.error:
			pass

	def draw_trading_actions(self, lines: int, cols: int, character):
		"""Draw trading actions for selected character"""
		try:
			self.draw_header(f"BOLTAC'S TRADING POST - {character.name}", lines, cols)

			options = ["Buy", "Sell", "Pool Gold", "Exit"]

			start_y = 4
			self.stdscr.addstr(start_y, 2, f"Hello, {character.name}!", curses.A_BOLD)
			self.stdscr.addstr(start_y + 1, 2, f"Gold: {character.gold}GP")

			for idx, opt in enumerate(options):
				marker = '►' if idx == self.trading_action_cursor else ' '
				self.stdscr.addstr(start_y + 3 + idx, 4, f"{marker} {opt}")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_buy_items(self, lines: int, cols: int, character):
		"""Draw buy items menu - matches main.py logic"""
		try:
			self.draw_header(f"BUY ITEMS - {character.name}", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, f"Gold: {character.gold}GP", curses.A_BOLD)

			# Get available items: weapons + prof_armors (like main.py line 1281)
			items = []
			debug_msgs = []

			# Check weapons availability
			if not self.weapons:
				debug_msgs.append("No weapons in database")

			# Check character attributes
			if not hasattr(character, 'prof_armors'):
				debug_msgs.append("Character has no prof_armors attribute")
			if not hasattr(character, 'prof_weapons'):
				debug_msgs.append("Character has no prof_weapons attribute")

			# Build items list
			if self.weapons and hasattr(character, 'prof_armors') and hasattr(character, 'prof_weapons'):
				# Sort weapons by cost, then prof_armors by cost (like main.py line 1281)
				try:
					weapons_sorted = sorted(self.weapons, key=lambda i: i.cost.value if hasattr(i.cost, 'value') else 0)
					items.extend(weapons_sorted)
					debug_msgs.append(f"Added {len(weapons_sorted)} weapons")
				except Exception as e:
					debug_msgs.append(f"Error sorting weapons: {str(e)[:30]}")

				try:
					if character.prof_armors:
						armors_sorted = sorted(character.prof_armors, key=lambda i: i.cost.value if hasattr(i.cost, 'value') else 0)
						items.extend(armors_sorted)
						debug_msgs.append(f"Added {len(armors_sorted)} armors")
					else:
						debug_msgs.append("Character has 0 prof_armors")
				except Exception as e:
					debug_msgs.append(f"Error sorting armors: {str(e)[:30]}")

			if items:
				display_start = max(0, self.buy_cursor - 10)
				for idx, item in enumerate(items[display_start:display_start + 15]):
					actual_idx = display_start + idx
					marker = '►' if actual_idx == self.buy_cursor else ' '

					# Check proficiency (like main.py line 1283-1284)
					# Already imported at top: from dnd_5e_core.equipment import Weapon
					prof_label = " [NOT PROF]" if isinstance(item, Weapon) and item not in character.prof_weapons else ""

					cost = item.cost if hasattr(item, 'cost') else "??GP"
					affordable = "" if character.gold * 100 >= (item.cost.value if hasattr(item.cost, 'value') else 99999) else " (No gold)"

					item_line = f"{marker} {item.name} ({cost}){prof_label}{affordable}"

					# Color code if not proficient or can't afford
					if prof_label or affordable:
						self.stdscr.addstr(start_y + 2 + idx, 2, item_line[:cols - 3], curses.color_pair(2))  # Red
					else:
						self.stdscr.addstr(start_y + 2 + idx, 2, item_line[:cols - 3])
			else:
				self.stdscr.addstr(start_y + 2, 2, "No items available")
				# Display debug messages
				y_offset = 4
				for msg in debug_msgs[:5]:  # Show max 5 debug messages
					self.stdscr.addstr(start_y + y_offset, 4, f"[DEBUG] {msg}"[:cols - 5])
					y_offset += 1

			self.draw_footer("[↑/↓] Navigate  [Enter] Buy  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_sell_items(self, lines: int, cols: int, character):
		"""Draw sell items menu - matches main.py logic"""
		try:
			self.draw_header(f"SELL ITEMS - {character.name}", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, f"Gold: {character.gold}GP", curses.A_BOLD)

			# Get character inventory
			inventory_items = [item for item in character.inventory if item]

			if inventory_items:
				display_start = max(0, self.sell_cursor - 10)
				for idx, item in enumerate(inventory_items[display_start:display_start + 15]):
					actual_idx = display_start + idx
					marker = '►' if actual_idx == self.sell_cursor else ' '

					# Check proficiency (like main.py line 1310)
					# Already imported at top: from dnd_5e_core.equipment import Weapon, Armor
					prof_label = " [NOT PROF]" if isinstance(item, Weapon) and hasattr(character, 'prof_weapons') and item not in character.prof_weapons else ""

					# Check equipped (like main.py line 1311)
					equipped_label = " (Equipped)" if (isinstance(item, Weapon) or isinstance(item, Armor)) and hasattr(item, 'equipped') and item.equipped else ""

					# Handle different cost types (like main.py line 1312-1313)
					# Already imported at top: from dnd_5e_core.equipment import Cost
					if hasattr(item, 'cost'):
						if isinstance(item.cost, Cost):
							cost = str(item.cost)
						elif isinstance(item.cost, dict):
							cost = f"{item.cost.get('quantity', '?')} {item.cost.get('unit', 'gp')}"
						else:
							cost = f"{item.cost} gp"
					else:
						cost = "?? gp"

					item_line = f"{marker} {item.name} ({cost}){equipped_label}{prof_label}"

					# Color code if equipped or not proficient
					if equipped_label:
						self.stdscr.addstr(start_y + 2 + idx, 2, item_line[:cols - 3], curses.color_pair(3))  # Yellow
					elif prof_label:
						self.stdscr.addstr(start_y + 2 + idx, 2, item_line[:cols - 3], curses.color_pair(2))  # Red
					else:
						self.stdscr.addstr(start_y + 2 + idx, 2, item_line[:cols - 3])
			else:
				self.stdscr.addstr(start_y + 2, 2, "No items in inventory")

			self.draw_footer("[↑/↓] Navigate  [Enter] Sell  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_cheat_menu(self, lines: int, cols: int):
		"""Draw cheat menu for debugging/testing"""
		try:
			self.draw_header("CHEAT MENU", lines, cols)

			start_y = 4
			self.stdscr.addstr(start_y, 2, "⚠️  Developer Tools - Use with Caution  ⚠️", curses.A_BOLD | curses.color_pair(3))

			options = ["Revive All Dead Characters", "Full Heal All Characters", "Add 1000 Gold to All Characters", "Level Up All Characters", "Return to Main Menu"]

			start_y += 3
			for idx, opt in enumerate(options):
				marker = '►' if idx == self.cheat_cursor else ' '
				self.stdscr.addstr(start_y + idx, 4, f"{marker} {opt}")

			# Show current party/roster status
			status_y = start_y + len(options) + 2
			if self.party:
				self.stdscr.addstr(status_y, 2, "PARTY STATUS:", curses.A_UNDERLINE)
				status_y += 1
				for idx, char in enumerate(self.party[:6]):
					status = f"  {char.name} - Lvl {char.level} - HP: {char.hit_points}/{char.max_hit_points} - {char.status} - Gold: {char.gold}"
					color = curses.color_pair(2) if char.status != "OK" else 0
					self.stdscr.addstr(status_y + idx, 2, status[:cols - 3], color)

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Return", lines, cols)
		except curses.error:
			pass

	def draw_training_grounds(self, lines: int, cols: int):
		"""Draw Training Grounds menu"""
		try:
			self.draw_header("TRAINING GROUNDS", lines, cols)

			options = ["Create a New Character", "Create a Random Character", "Character Status", "Delete a Character", "Rename a Character", "Return to Castle"]

			start_y = 4
			for idx, opt in enumerate(options):
				marker = '►' if idx == self.training_cursor else ' '
				self.stdscr.addstr(start_y + idx, 2, f"{marker} {opt}")

			# Show roster count
			roster_y = start_y + len(options) + 2
			self.stdscr.addstr(roster_y, 2, f"Roster: {len(self.roster)}/{MAX_ROSTER} characters")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Return", lines, cols)
		except curses.error:
			pass

	def draw_character_list(self, lines: int, cols: int, title: str):
		"""Draw a list of characters for selection"""
		try:
			self.draw_header(title, lines, cols)

			start_y = 4
			available_chars = [c for c in self.roster if c not in self.party]

			if available_chars:
				display_start = max(0, self.roster_cursor - 10)
				for idx, char in enumerate(available_chars[display_start:display_start + 15]):
					actual_idx = display_start + idx
					marker = '►' if actual_idx == self.roster_cursor else ' '
					char_info = f"{marker} {char.name} - Lvl {char.level} {char.class_type.name} - Status: {char.status}"
					self.stdscr.addstr(start_y + idx, 2, char_info[:cols - 3])
			else:
				self.stdscr.addstr(start_y, 2, "(No characters available)")

			self.draw_footer("[↑/↓] Navigate  [Enter] Select  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_character_status(self, lines: int, cols: int, character):
		"""Draw detailed character status in ncurses"""
		try:
			self.draw_header(f"CHARACTER STATUS - {character.name}", lines, cols)

			y = 3
			# Basic info
			self.stdscr.addstr(y, 2, f"Name: {character.name}", curses.A_BOLD)
			y += 1
			self.stdscr.addstr(y, 2, f"Race: {character.race.name if hasattr(character, 'race') else 'Unknown'}")
			y += 1
			self.stdscr.addstr(y, 2, f"Class: {character.class_type.name} (Level {character.level})")
			y += 1
			self.stdscr.addstr(y, 2, f"Status: {character.status}")
			y += 2

			# Stats
			self.stdscr.addstr(y, 2, "STATS:", curses.A_UNDERLINE)
			y += 1
			self.stdscr.addstr(y, 2, f"HP: {character.hit_points}/{character.max_hit_points}")
			y += 1

			# XP: current/needed for next level
			xp_needed = "MAX"
			if hasattr(self, 'xp_levels') and character.level < len(self.xp_levels):
				xp_needed = str(self.xp_levels[character.level])
			self.stdscr.addstr(y, 2, f"XP: {character.xp}/{xp_needed}")
			y += 1

			self.stdscr.addstr(y, 2, f"Gold: {character.gold} GP")
			y += 1

			# Age in years (convert from weeks)
			age_years = character.age // 52 if hasattr(character, 'age') else 0
			age_display = f"{age_years} years" if age_years != 1 else "1 year"
			self.stdscr.addstr(y, 2, f"Age: {age_display}")
			y += 2

			# Spell slots (if spell caster)
			if hasattr(character, 'is_spell_caster') and character.is_spell_caster:
				if hasattr(character, 'sc') and hasattr(character.sc, 'spell_slots'):
					self.stdscr.addstr(y, 2, "SPELL SLOTS:", curses.A_UNDERLINE)
					y += 1
					slots_display = " ".join([f"L{i+1}:{s}" for i, s in enumerate(character.sc.spell_slots) if i < 9])
					self.stdscr.addstr(y, 2, slots_display)
					y += 2

			# Abilities
			if hasattr(character, 'abilities'):
				self.stdscr.addstr(y, 2, "ABILITIES:", curses.A_UNDERLINE)
				y += 1
				try:
					self.stdscr.addstr(y, 2, f"STR: {character.abilities.str}  DEX: {character.abilities.dex}  CON: {character.abilities.con}")
					y += 1
					self.stdscr.addstr(y, 2, f"INT: {character.abilities.int}  WIS: {character.abilities.wis}  CHA: {character.abilities.cha}")
					y += 2
				except:
					pass

			# Inventory preview
			if hasattr(character, 'inventory'):
				self.stdscr.addstr(y, 2, "INVENTORY:", curses.A_UNDERLINE)
				y += 1
				items = [item for item in character.inventory if item][:5]
				if items:
					for item in items:
						equipped = " [E]" if hasattr(item, 'equipped') and item.equipped else ""
						self.stdscr.addstr(y, 4, f"- {item.name}{equipped}"[:cols - 5])
						y += 1
					if len([i for i in character.inventory if i]) > 5:
						self.stdscr.addstr(y, 4, f"... and {len([i for i in character.inventory if i]) - 5} more")
				else:
					self.stdscr.addstr(y, 4, "(Empty)")

			# Footer with spell menu if spell caster
			if hasattr(character, 'is_spell_caster') and character.is_spell_caster:
				self.draw_footer("[i] Manage Inventory  [s] View Spells  [Esc] Back", lines, cols)
			else:
				self.draw_footer("[i] Manage Inventory  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_character_spells(self, lines: int, cols: int, character):
		"""Draw character's spell list"""
		try:
			self.draw_header(f"SPELLS - {character.name}", lines, cols)

			y = 3

			# Spell slots
			if hasattr(character, 'sc') and hasattr(character.sc, 'spell_slots'):
				self.stdscr.addstr(y, 2, "SPELL SLOTS:", curses.A_BOLD)
				y += 1
				slots_display = " | ".join([f"Lvl {i+1}: {s}" for i, s in enumerate(character.sc.spell_slots) if i < 9])
				self.stdscr.addstr(y, 2, slots_display)
				y += 2

			# Learned spells
			if hasattr(character, 'sc') and hasattr(character.sc, 'learned_spells'):
				spells = character.sc.learned_spells

				if not spells:
					self.stdscr.addstr(y, 2, "No spells learned")
				else:
					# Group by level
					cantrips = [s for s in spells if not s.level or s.level == 0]
					leveled_spells = {}
					for spell in spells:
						if spell.level and spell.level > 0:
							if spell.level not in leveled_spells:
								leveled_spells[spell.level] = []
							leveled_spells[spell.level].append(spell)

					# Display cantrips
					if cantrips:
						self.stdscr.addstr(y, 2, "CANTRIPS:", curses.A_UNDERLINE)
						y += 1
						for spell in cantrips:
							spell_info = f"  {spell.name}"
							if hasattr(spell, 'school'):
								# school can be a string or an object with .name
								school_name = spell.school.name if hasattr(spell.school, 'name') else str(spell.school)
								spell_info += f" ({school_name})"
							self.stdscr.addstr(y, 2, spell_info[:cols - 3])
							y += 1
						y += 1

					# Display leveled spells
					for level in sorted(leveled_spells.keys()):
						if y >= lines - 3:
							break
						self.stdscr.addstr(y, 2, f"LEVEL {level}:", curses.A_UNDERLINE)
						y += 1
						for spell in leveled_spells[level]:
							if y >= lines - 3:
								break
							spell_info = f"  {spell.name}"
							if hasattr(spell, 'school'):
								# school can be a string or an object with .name
								school_name = spell.school.name if hasattr(spell.school, 'name') else str(spell.school)
								spell_info += f" ({school_name})"
							self.stdscr.addstr(y, 2, spell_info[:cols - 3])
							y += 1
						y += 1
			else:
				self.stdscr.addstr(y, 2, "Not a spell caster")

			self.draw_footer("[Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw_character_inventory(self, lines: int, cols: int, character):
		"""Draw interactive character inventory for equipping/using items (like ui_curses.py)"""
		try:
			self.draw_header(f"INVENTORY - {character.name}", lines, cols)

			y = 3
			# Gold and HP display
			self.stdscr.addstr(y, 2, f"Gold: {character.gold} GP", curses.A_BOLD)
			y += 1
			self.stdscr.addstr(y, 2, f"HP: {character.hit_points}/{character.max_hit_points}")
			y += 2

			# Count items
			# Already imported at top: from dnd_5e_core.equipment import Weapon, Armor, HealingPotion

			# Healing potions
			potions = [item for item in character.inventory if item and isinstance(item, HealingPotion)]
			weapons = [item for item in character.inventory if item and isinstance(item, Weapon)]
			armors = [item for item in character.inventory if item and isinstance(item, Armor)]

			cursor_idx = 0

			# Potions section
			self.stdscr.addstr(y, 2, "POTIONS:", curses.A_UNDERLINE)
			y += 1
			if potions:
				for idx, potion in enumerate(potions):
					marker = '►' if self.inventory_item_cursor == cursor_idx else ' '
					try:
						heal_val = potion.heal_at_slot_level.get(0, 0) if hasattr(potion, 'heal_at_slot_level') else 0
						self.stdscr.addstr(y, 4, f"{marker} {potion.name} (+{heal_val} HP)"[:cols - 5])
					except:
						self.stdscr.addstr(y, 4, f"{marker} {potion.name}"[:cols - 5])
					y += 1
					cursor_idx += 1
			else:
				self.stdscr.addstr(y, 4, "(None)")
				y += 1
			y += 1

			# Weapons section
			self.stdscr.addstr(y, 2, "WEAPONS:", curses.A_UNDERLINE)
			y += 1
			if weapons:
				for idx, weapon in enumerate(weapons):
					marker = '►' if self.inventory_item_cursor == cursor_idx else ' '
					equipped = "(E)" if hasattr(weapon, 'equipped') and weapon.equipped else "   "
					try:
						dmg = weapon.damage_dice.score() if hasattr(weapon, 'damage_dice') else "?"
						self.stdscr.addstr(y, 4, f"{marker} {weapon.name} {equipped} (DMG: {dmg})"[:cols - 5])
					except:
						self.stdscr.addstr(y, 4, f"{marker} {weapon.name} {equipped}"[:cols - 5])
					y += 1
					cursor_idx += 1
			else:
				self.stdscr.addstr(y, 4, "(None)")
				y += 1
			y += 1

			# Armors section
			self.stdscr.addstr(y, 2, "ARMORS:", curses.A_UNDERLINE)
			y += 1
			if armors:
				for idx, armor in enumerate(armors):
					marker = '►' if self.inventory_item_cursor == cursor_idx else ' '
					equipped = "(E)" if hasattr(armor, 'equipped') and armor.equipped else "   "
					try:
						ac = armor.armor_class.get('base', '?') if hasattr(armor, 'armor_class') else "?"
						self.stdscr.addstr(y, 4, f"{marker} {armor.name} {equipped} (AC: {ac})"[:cols - 5])
					except:
						self.stdscr.addstr(y, 4, f"{marker} {armor.name} {equipped}"[:cols - 5])
					y += 1
					cursor_idx += 1
			else:
				self.stdscr.addstr(y, 4, "(None)")
				y += 1

			# Panel message (special line for feedback)
			if y < lines - 3:
				panel_msg = self.get_panel_message()
				if panel_msg:
					self.stdscr.addstr(lines - 3, 2, f">>> {panel_msg}"[:cols - 4], curses.A_BOLD)

			self.draw_footer("[↑/↓] Navigate  [u] Use Item  [e] Equip/Unequip  [Esc] Back", lines, cols)
		except curses.error:
			pass

	def draw(self):
		"""Main draw function"""
		self.stdscr.erase()
		lines, cols = self.stdscr.getmaxyx()
		self.check_bounds()

		if self.mode == 'main_menu':
			self.draw_main_menu(lines, cols)
		elif self.mode == 'cheat_menu':
			self.draw_cheat_menu(lines, cols)
		elif self.mode == 'location':
			self.draw_location_menu(lines, cols)
		elif self.mode == 'party_roster':
			self.draw_party_roster(lines, cols)
		elif self.mode == 'tavern':
			self.draw_tavern_menu(lines, cols)
		elif self.mode == 'inn':
			self.draw_inn_menu(lines, cols)
		elif self.mode == 'inn_rooms':
			if self.character_to_rest:
				self.draw_inn_rooms(lines, cols, self.character_to_rest)
		elif self.mode == 'temple':
			self.draw_temple_menu(lines, cols)
		elif self.mode == 'trading':
			self.draw_trading_post_menu(lines, cols)
		elif self.mode == 'trading_actions':
			if self.character_trading:
				self.draw_trading_actions(lines, cols, self.character_trading)
		elif self.mode == 'buy_items':
			if self.character_trading:
				self.draw_buy_items(lines, cols, self.character_trading)
		elif self.mode == 'sell_items':
			if self.character_trading:
				self.draw_sell_items(lines, cols, self.character_trading)
		elif self.mode == 'training':
			self.draw_training_grounds(lines, cols)
		elif self.mode == 'character_list':
			self.draw_character_list(lines, cols, "Select Character")
		elif self.mode == 'character_status':
			if self.character_viewing:
				self.draw_character_status(lines, cols, self.character_viewing)
		elif self.mode == 'character_inventory':
			if self.character_viewing:
				self.draw_character_inventory(lines, cols, self.character_viewing)
		elif self.mode == 'character_spells':
			if self.character_viewing:
				self.draw_character_spells(lines, cols, self.character_viewing)
		elif self.mode == 'char_select_party':
			self.draw_char_select_menu(lines, cols, self.party, "Select Character from Party")
		elif self.mode == 'char_select_roster':
			self.draw_char_select_menu(lines, cols, [c for c in self.roster if c not in self.party], "Select Character from Roster")
		elif self.mode == 'reorder_party':
			self.draw_reorder_party(lines, cols)
		elif self.mode == 'dungeon_explore':
			self.draw_dungeon_explore(lines, cols)
		elif self.mode == 'messages':
			self.draw_messages(lines, cols)

		self.stdscr.refresh()

	def draw_messages(self, lines: int, cols: int):
		"""Draw message log"""
		try:
			self.draw_header("Messages", lines, cols)

			start = max(0, len(self.messages) - (lines - 6))
			for idx, msg in enumerate(self.messages[start:]):
				if idx < lines - 6:
					self.stdscr.addstr(3 + idx, 0, msg[:cols - 1])

			self.draw_footer("[Esc] Back", lines, cols)
		except curses.error:
			pass

	def mainloop(self):
		"""Main game loop"""
		self.stdscr.nodelay(False)
		curses.curs_set(0)

		# Initialize colors if available
		if curses.has_colors():
			curses.start_color()
			curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
			curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
			curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
			curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

		self.push_message("Welcome to Dungeons & Dragons 5th Edition!")
		self.push_message("Loading game data...")

		# Load game data
		self.load_game_data()

		while True:
			self.check_bounds()
			self.draw()
			c = self.stdscr.getch()

			# Dispatch to appropriate handler
			if self.mode == 'main_menu':
				if not self._handle_main_menu(c):
					break  # User quit
			elif self.mode == 'location':
				self._handle_location(c)
			elif self.mode == 'party_roster':
				self._handle_party_roster(c)
			elif self.mode == 'tavern':
				self._handle_tavern(c)
			elif self.mode == 'inn':
				self._handle_inn(c)
			elif self.mode == 'inn_rooms':
				self._handle_inn_rooms(c)
			elif self.mode == 'temple':
				self._handle_temple(c)
			elif self.mode == 'trading':
				self._handle_trading(c)
			elif self.mode == 'trading_actions':
				self._handle_trading_actions(c)
			elif self.mode == 'buy_items':
				self._handle_buy_items(c)
			elif self.mode == 'sell_items':
				self._handle_sell_items(c)
			elif self.mode == 'training':
				self._handle_training(c)
			elif self.mode == 'character_list':
				self._handle_character_list(c)
			elif self.mode == 'char_select_party':
				self._handle_char_select(c, self.party)
			elif self.mode == 'char_select_roster':
				# Show all roster if coming from training, otherwise show only available
				if self.previous_mode == 'training':
					self._handle_char_select(c, self.roster)
				else:
					self._handle_char_select(c, [c for c in self.roster if c not in self.party])
			elif self.mode == 'character_status':
				self._handle_character_status(c)
			elif self.mode == 'character_inventory':
				self._handle_character_inventory(c)
			elif self.mode == 'character_spells':
				self._handle_character_spells(c)
			elif self.mode == 'reorder_party':
				self._handle_reorder_party(c)
			elif self.mode == 'cheat_menu':
				self._handle_cheat_menu(c)
			elif self.mode == 'dungeon_explore':
				self._handle_dungeon_explore(c)
			elif self.mode == 'messages':
				self._handle_messages(c)

	def _handle_main_menu(self, c: int) -> bool:
		"""Handle main menu input"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.menu_cursor = min(self.menu_cursor + 1, 4)  # Updated to 4 for 5 options
		elif c in (curses.KEY_UP, ord('k')):
			self.menu_cursor = max(0, self.menu_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.menu_cursor == 0:  # Start New Game
				# Reset party for a fresh start, but keep roster
				self.party = []
				# Keep roster loaded - don't reset it!
				# self.roster remains unchanged so characters can be created/viewed
				self.push_panel("Starting new game...")
				# Save empty party to disk
				try:
					save_party(self.party, _dir=self.game_path)
					self.push_panel("New game initialized!")
				except Exception as e:
					self.push_panel(f"Error initializing new game: {e}")
				self.mode = 'location'
				self.location = Location.CASTLE
			elif self.menu_cursor == 1:  # Load Game
				# Reload saved roster and party from disk
				self.push_panel("Loading saved game...")
				self.roster = get_roster(self.characters_dir)
				self.party = load_party(_dir=self.game_path)
				self.push_panel(f"Loaded {len(self.roster)} characters, {len(self.party)} in party")
				self.mode = 'location'
				self.location = Location.CASTLE
			elif self.menu_cursor == 2:  # Cheat Menu
				self.mode = 'cheat_menu'
				self.cheat_cursor = 0
			elif self.menu_cursor == 3:  # Options
				self.push_panel("Options not yet implemented")
			else:  # Quit
				return False
		elif c == ord('q'):
			return False
		return True

	def _handle_location(self, c: int) -> None:
		"""Handle location menu input"""
		if self.location == Location.CASTLE:
			self._handle_castle(c)
		elif self.location == Location.EDGE_OF_TOWN:
			self._handle_edge(c)

	def _handle_castle(self, c: int) -> None:
		"""Handle castle menu"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.castle_cursor = min(self.castle_cursor + 1, 5)
		elif c in (curses.KEY_UP, ord('k')):
			self.castle_cursor = max(0, self.castle_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.castle_cursor == 0:  # Tavern
				self.mode = 'tavern'
				self.tavern_cursor = 0
				self.previous_mode = 'location'
			elif self.castle_cursor == 1:  # Inn
				if not self.party:
					self.push_panel("No characters in party!")
				else:
					self.mode = 'inn'
					self.inn_cursor = 0
					self.previous_mode = 'location'
			elif self.castle_cursor == 2:  # Temple
				self.mode = 'temple'
				self.temple_cursor = 0
				self.previous_mode = 'location'
			elif self.castle_cursor == 3:  # Trading Post
				if not self.party:
					self.push_panel("No characters in party!")
				else:
					self.mode = 'trading'
					self.trading_cursor = 0
					self.previous_mode = 'location'
			elif self.castle_cursor == 4:  # Edge of Town
				self.location = Location.EDGE_OF_TOWN
				self.edge_cursor = 0
			else:  # Save & Exit
				# Save party and characters
				try:
					save_party(self.party, _dir=self.game_path)
					for char in self.party:
						save_character(char, _dir=self.characters_dir)
					self.push_panel("Game saved!")
				except Exception as e:
					self.push_panel(f"Save error: {str(e)}")
				self.mode = 'main_menu'
		elif c == 27:  # Esc
			self.mode = 'main_menu'

	def _handle_edge(self, c: int) -> None:
		"""Handle edge of town menu"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.edge_cursor = min(self.edge_cursor + 1, 3)
		elif c in (curses.KEY_UP, ord('k')):
			self.edge_cursor = max(0, self.edge_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.edge_cursor == 0:  # Training Grounds
				self.mode = 'training'
				self.training_cursor = 0
				self.previous_mode = 'location'
			elif self.edge_cursor == 1:  # Maze/Dungeon
				if not self.party:
					self.push_panel("No party! Recruit adventurers first.")
				else:
					# Switch to dungeon exploration mode (ncurses)
					self.mode = 'dungeon_explore'
					self.dungeon_message = "Entering the dungeon..."
					self.dungeon_step = 0
			elif self.edge_cursor == 2:  # Castle
				self.location = Location.CASTLE
				self.castle_cursor = 0
			else:  # Leave Game
				# Save and exit
				try:
					save_party(self.party, _dir=self.game_path)
					for char in self.party:
						save_character(char, _dir=self.characters_dir)
				except Exception:
					pass
				self.mode = 'main_menu'  # Go back to main menu
		elif c == 27:  # Esc
			self.location = Location.CASTLE

	def _handle_party_roster(self, c: int) -> None:
		"""Handle party roster management"""
		total_chars = len(self.party) + len([c for c in self.roster if c not in self.party and c.status == "OK"])

		if c in (curses.KEY_DOWN, ord('j')):
			self.party_cursor = min(self.party_cursor + 1, total_chars - 1) if total_chars > 0 else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.party_cursor = max(0, self.party_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			# Add/Remove character from party
			if self.party_cursor < len(self.party):
				# Remove from party
				char = self.party.pop(self.party_cursor)
				self.push_panel(f"Removed {char.name} from party")
			else:
				# Add to party
				available = [c for c in self.roster if c not in self.party and c.status == "OK"]
				idx = self.party_cursor - len(self.party)
				if idx < len(available):
					char = available[idx]
					self.party.append(char)
					self.push_panel(f"Added {char.name} to party")
		elif c == 27:  # Esc
			self.mode = 'location'

	def _handle_tavern(self, c: int) -> None:
		"""Handle tavern menu"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.tavern_cursor = min(self.tavern_cursor + 1, 6)
		elif c in (curses.KEY_UP, ord('k')):
			self.tavern_cursor = max(0, self.tavern_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.tavern_cursor == 0:  # Add Member
				available = [c for c in self.roster if c not in self.party and c.status == "OK"]
				if not available:
					self.push_panel("No characters available to add")
				elif len(self.party) >= 6:
					self.push_panel("Party is full (max 6)")
				else:
					self.mode = 'character_list'
					self.roster_cursor = 0
					self.previous_mode = 'tavern'
			elif self.tavern_cursor == 1:  # Remove Member
				if not self.party:
					self.push_panel("No characters in party")
				else:
					if len(self.party) > 0:
						char = self.party.pop(0)
						char.id_party = -1
						try:
							save_character(char, _dir=self.characters_dir)
						except Exception:
							pass
						self.push_panel(f"Removed {char.name} from party")
			elif self.tavern_cursor == 2:  # Character Status
				if not self.party:
					self.push_panel("No characters in party")
				else:
					# Switch to ncurses character selection
					self.mode = 'char_select_party'
					self.char_select_cursor = 0
					self.previous_mode = 'tavern'
			elif self.tavern_cursor == 3:  # Reorder
				if len(self.party) < 2:
					self.push_panel("Need at least 2 characters to reorder")
				else:
					# Switch to ncurses reorder interface
					self.mode = 'reorder_party'
					self.reorder_cursor = 0
					self.reorder_selected = None
					self.previous_mode = 'tavern'
			elif self.tavern_cursor == 4:  # Divvy Gold
				if not self.party:
					self.push_panel("No characters in party")
				else:
					total_gold = sum([c.gold for c in self.party])
					share = total_gold // len(self.party)
					for char in self.party:
						char.gold = share
						try:
							save_character(char, _dir=self.characters_dir)
						except Exception:
							pass
					self.push_panel(f"Gold divided: {share}GP each")
			elif self.tavern_cursor == 5:  # Disband Party
				if not self.party:
					self.push_panel("No party to disband")
				else:
					for char in self.party:
						char.id_party = -1
						try:
							save_character(char, _dir=self.characters_dir)
						except Exception:
							pass
					self.party.clear()
					self.push_panel("Party disbanded")
			else:  # Exit Tavern (cursor == 6)
				self.mode = 'location'
				self.tavern_cursor = 0  # Reset cursor for next visit
				self.push_panel("Exited tavern")
		elif c == 27:  # Esc
			self.mode = 'location'
			self.tavern_cursor = 0  # Reset cursor for next visit

	def _handle_inn(self, c: int) -> None:
		"""Handle inn character selection"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.inn_cursor = min(self.inn_cursor + 1, len(self.party) - 1) if self.party else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.inn_cursor = max(0, self.inn_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.party and self.inn_cursor < len(self.party):
				self.character_to_rest = self.party[self.inn_cursor]
				self.mode = 'inn_rooms'
				self.inn_cursor = 0  # Reset for room selection
		elif c == 27:  # Esc
			self.mode = self.previous_mode or 'location'

	def _handle_inn_rooms(self, c: int) -> None:
		"""Handle inn room selection and resting"""
		rooms = [(0, 0), (10, 1), (100, 3), (200, 7), (500, 10)]  # (fee, weeks)

		if c in (curses.KEY_DOWN, ord('j')):
			self.inn_cursor = min(self.inn_cursor + 1, 4)
		elif c in (curses.KEY_UP, ord('k')):
			self.inn_cursor = max(0, self.inn_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			fee, weeks = rooms[self.inn_cursor]
			char = self.character_to_rest

			if fee > char.gold:
				self.push_panel("Not enough gold!")
			else:
				# Rest the character - ensure HP never exceeds max HP
				hp_needed = char.max_hit_points - char.hit_points
				if hp_needed > 0:
					while fee and char.hit_points < char.max_hit_points and char.gold >= fee:
						hp_recovery = min(fee // 10, hp_needed)
						char.hit_points = min(char.max_hit_points, char.hit_points + hp_recovery)
						char.gold -= fee
						char.age += weeks
						hp_needed = char.max_hit_points - char.hit_points
						if hp_needed <= 0:
							break

				# Check for level up FIRST (before restoring spell slots)
				leveled_up = False
				if hasattr(self, 'xp_levels') and char.level < len(self.xp_levels) and char.xp >= self.xp_levels[char.level]:
					from populate_functions import populate, request_spell
					try:
						old_level = char.level
						if hasattr(char.class_type, 'can_cast') and char.class_type.can_cast:
							# Load spells for spell casters
							spell_names = populate(collection_name="spells", key_name="results")
							all_spells = [request_spell(name) for name in spell_names]
							class_tome_spells = [s for s in all_spells if s is not None and hasattr(s, 'allowed_classes') and char.class_type.index in s.allowed_classes]
							display_message, new_spells = char.gain_level(tome_spells=class_tome_spells, verbose=False)
						else:
							display_message, new_spells = char.gain_level(verbose=False)

						leveled_up = True
						# Show level up message with details
						self.push_panel(f"{char.name} gained a level! (Lvl {old_level} → {char.level})")
					except Exception as e:
						# Show error for debugging
						self.push_panel(f"Level up error: {str(e)[:40]}")

				# Restore spell slots AFTER level up (uses new level)
				if hasattr(char.class_type, 'can_cast') and char.class_type.can_cast:
					if hasattr(char, 'sc') and hasattr(char.sc, 'spell_slots'):
						char.sc.spell_slots = char.class_type.spell_slots[char.level]

				# Ensure HP doesn't exceed max
				char.hit_points = min(char.hit_points, char.max_hit_points)

				try:
					save_character(char, _dir=self.characters_dir)
				except Exception:
					pass

				status = "fully healed" if char.hit_points == char.max_hit_points else "partially healed"
				self.push_panel(f"{char.name} {status} (aged {weeks} weeks)")
				self.mode = 'inn'
				self.character_to_rest = None
		elif c == 27:  # Esc
			self.mode = 'inn'
			self.character_to_rest = None

	def _handle_temple(self, c: int) -> None:
		"""Handle temple resurrection services"""
		cures_costs = {"PARALYZED": 100, "STONED": 200, "DEAD": 250, "ASHES": 500}
		candidates = [(c, cures_costs.get(c.status, 0) * c.level) for c in self.roster if c.status in cures_costs]

		if c in (curses.KEY_DOWN, ord('j')):
			self.temple_cursor = min(self.temple_cursor + 1, len(candidates) - 1) if candidates else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.temple_cursor = max(0, self.temple_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if candidates and self.temple_cursor < len(candidates):
				char_to_save, cost = candidates[self.temple_cursor]

				# Find a contributor from party
				if not self.party:
					self.push_panel("No party members to contribute!")
				else:
					contributor = self.party[0]  # Use first party member

					if contributor.gold < cost:
						self.push_panel("Not enough gold!")
					else:
						contributor.gold -= cost

						# Attempt resurrection based on status
						from random import randint
						if char_to_save.status == "DEAD":
							success = randint(1, 100) < (50 + 3 * char_to_save.constitution)
							if success:
								char_to_save.status = "OK"
								char_to_save.hit_points = 1
								char_to_save.age += randint(1, 52)
								self.push_panel(f"{char_to_save.name} LIVES!")
							else:
								char_to_save.status = "ASHES"
								self.push_panel(f"{char_to_save.name} turned to ASHES!")
						elif char_to_save.status == "ASHES":
							success = randint(1, 100) < (40 + 3 * char_to_save.constitution)
							if success:
								char_to_save.status = "OK"
								char_to_save.hit_points = char_to_save.max_hit_points
								char_to_save.age += randint(1, 52)
								self.push_panel(f"{char_to_save.name} LIVES!")
							else:
								char_to_save.status = "LOST"
								self.push_panel(f"{char_to_save.name} is LOST!")
						else:
							char_to_save.status = "OK"
							self.push_panel(f"{char_to_save.name} is cured!")

						try:
							save_character(char_to_save, _dir=self.characters_dir)
							save_character(contributor, _dir=self.characters_dir)
						except Exception:
							pass
		elif c == 27:  # Esc
			self.mode = self.previous_mode or 'location'

	def _handle_trading(self, c: int) -> None:
		"""Handle trading post character selection"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.trading_cursor = min(self.trading_cursor + 1, len(self.party) - 1) if self.party else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.trading_cursor = max(0, self.trading_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.party and self.trading_cursor < len(self.party):
				self.character_trading = self.party[self.trading_cursor]
				self.mode = 'trading_actions'
				self.trading_action_cursor = 0
		elif c == 27:  # Esc
			self.mode = self.previous_mode or 'location'

	def _handle_trading_actions(self, c: int) -> None:
		"""Handle trading action selection (Buy/Sell/Pool Gold)"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.trading_action_cursor = min(self.trading_action_cursor + 1, 3)
		elif c in (curses.KEY_UP, ord('k')):
			self.trading_action_cursor = max(0, self.trading_action_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.trading_action_cursor == 0:  # Buy
				self.mode = 'buy_items'
				self.buy_cursor = 0
			elif self.trading_action_cursor == 1:  # Sell
				self.mode = 'sell_items'
				self.sell_cursor = 0
			elif self.trading_action_cursor == 2:  # Pool Gold
				if self.character_trading and self.party:
					total_gold = sum([c.gold for c in self.party])
					for ch in self.party:
						ch.gold = total_gold if ch == self.character_trading else 0
					self.push_panel("All gold pooled")
					try:
						for ch in self.party:
							save_character(ch, _dir=self.characters_dir)
					except Exception:
						pass
			else:  # Exit
				self.mode = 'trading'
				self.character_trading = None
		elif c == 27:  # Esc
			self.mode = 'trading'
			self.character_trading = None

	def _handle_buy_items(self, c: int) -> None:
		"""Handle buying items - matches main.py logic"""
		if not self.character_trading:
			self.mode = 'trading_actions'
			return

		# Get items list: weapons + prof_armors (like main.py line 1281)
		items = []
		if self.weapons and hasattr(self.character_trading, 'prof_armors'):
			weapons_sorted = sorted(self.weapons, key=lambda i: i.cost.value if hasattr(i.cost, 'value') else 0)
			armors_sorted = sorted(self.character_trading.prof_armors, key=lambda i: i.cost.value if hasattr(i.cost, 'value') else 0)
			items = weapons_sorted + armors_sorted

		if not items:
			self.push_panel("No items available")
			self.mode = 'trading_actions'
			return

		if c in (curses.KEY_DOWN, ord('j')):
			self.buy_cursor = min(self.buy_cursor + 1, len(items) - 1) if items else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.buy_cursor = max(0, self.buy_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if items and self.buy_cursor < len(items):
				item = items[self.buy_cursor]
				cost_value = item.cost.value if hasattr(item.cost, 'value') else 0

				# Check if can afford (like main.py line 1291)
				if self.character_trading.gold * 100 < cost_value:
					self.push_panel("Not enough gold!")
				else:
					# Deduct gold (like main.py line 1295)
					self.character_trading.gold -= cost_value // 100

					# Add to inventory (like main.py line 1296-1302)
					from copy import copy
					free_slots = [i for i, inv_item in enumerate(self.character_trading.inventory) if not inv_item]
					if free_slots:
						self.character_trading.inventory[free_slots[0]] = copy(item)
						self.push_panel(f"Bought {item.name} for {item.cost}")
						try:
							save_character(self.character_trading, _dir=self.characters_dir)
						except Exception:
							pass
					else:
						# Refund if inventory full
						self.character_trading.gold += cost_value // 100
						self.push_panel("Inventory full!")
		elif c == 27:  # Esc
			self.mode = 'trading_actions'

	def _handle_sell_items(self, c: int) -> None:
		"""Handle selling items - matches main.py logic"""
		if not self.character_trading:
			self.mode = 'trading_actions'
			return

		inventory_items = [item for item in self.character_trading.inventory if item]

		if c in (curses.KEY_DOWN, ord('j')):
			self.sell_cursor = min(self.sell_cursor + 1, len(inventory_items) - 1) if inventory_items else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.sell_cursor = max(0, self.sell_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if inventory_items and self.sell_cursor < len(inventory_items):
				item = inventory_items[self.sell_cursor]

				# Check if equipped (like main.py line 1311)
				# Already imported at top: from dnd_5e_core.equipment import Weapon, Armor
				equipped_label = " (Equipped)" if (isinstance(item, Weapon) or isinstance(item, Armor)) and hasattr(item, 'equipped') and item.equipped else ""

				if equipped_label:
					self.push_panel(f"Unequip {item.name} first!")
				else:
					# Calculate sell price: cost_value // 200 (like main.py line 1322-1324)
					# Already imported at top: from dnd_5e_core.equipment import Cost
					if hasattr(item, 'cost'):
						if isinstance(item.cost, Cost):
							cost_value = item.cost.value
						elif isinstance(item.cost, dict):
							cost_value = int(item.cost.get('quantity', 0))
						elif isinstance(item.cost, int):
							cost_value = item.cost
						else:
							# Try to get value attribute or convert to int
							cost_value = getattr(item.cost, 'value', 0)
					else:
						cost_value = 0

					# Sell for half price (like main.py line 1323)
					self.character_trading.gold += cost_value // 200

					# Remove from inventory (like main.py line 1325)
					idx = self.character_trading.inventory.index(item)
					self.character_trading.inventory[idx] = None
					self.push_panel(f"Sold {item.name}")

					try:
						save_character(self.character_trading, _dir=self.characters_dir)
					except Exception:
						pass

					# Reset cursor if needed
					if self.sell_cursor >= len([i for i in self.character_trading.inventory if i]):
						self.sell_cursor = max(0, self.sell_cursor - 1)
		elif c == 27:  # Esc
			self.mode = 'trading_actions'

	def _handle_training(self, c: int) -> None:
		"""Handle training grounds menu"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.training_cursor = min(self.training_cursor + 1, 5)
		elif c in (curses.KEY_UP, ord('k')):
			self.training_cursor = max(0, self.training_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.training_cursor == 0:  # Create New Character
				if len(self.roster) >= MAX_ROSTER:
					self.push_panel(f"Max roster ({MAX_ROSTER}) reached!")
				else:
					# Call create_new_character from main.py
					curses.endwin()
					try:
						# Load collections if needed
						if not self.races:
							self.races, self.subraces, self.classes, self.alignments, _, _, self.names, self.human_names, self.spells = load_character_collections()

						new_char = create_new_character(self.roster)
						self.roster.append(new_char)
						save_character(new_char, _dir=self.characters_dir)
					except Exception as e:
						print(f"Character creation error: {e}")
						input("Press Enter to continue...")
					finally:
						self.stdscr = curses.initscr()
						curses.noecho()
						curses.cbreak()
						self.stdscr.keypad(True)
						if curses.has_colors():
							curses.start_color()
							curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
							curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
							curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
							curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
						self.push_panel("Character created")
			elif self.training_cursor == 1:  # Create Random Character
				if len(self.roster) >= MAX_ROSTER:
					self.push_panel(f"Max roster ({MAX_ROSTER}) reached!")
				else:
					try:
						# Load collections if needed
						if not self.races:
							self.races, self.subraces, self.classes, self.alignments, _, _, self.names, self.human_names, self.spells = load_character_collections()

						# Validate that collections are not empty
						if not self.races or not self.classes:
							self.push_panel("Error: No races or classes available. Check data files.")
						elif not self.names:
							self.push_panel("Error: No names database available. Check data files.")
						else:
							new_char = generate_random_character(self.roster, self.races, self.subraces, self.classes, self.names, self.human_names, self.spells)
							self.roster.append(new_char)
							save_character(new_char, _dir=self.characters_dir)
							self.push_panel(f"Created {new_char.name}")
					except Exception as e:
						self.push_panel(f"Error: {str(e)[:50]}")
			elif self.training_cursor == 2:  # Character Status
				if not self.roster:
					self.push_panel("No characters in roster")
				else:
					# Switch to ncurses character selection - show all roster
					self.mode = 'char_select_roster'
					self.char_select_cursor = 0
					self.previous_mode = 'training'
			elif self.training_cursor == 3:  # Delete Character
				available_chars = [c for c in self.roster if c not in self.party]
				if not available_chars:
					self.push_panel("No characters available to delete")
				else:
					self.mode = 'character_list'
					self.roster_cursor = 0
					self.previous_mode = 'training'
			elif self.training_cursor == 4:  # Rename Character
				self.push_panel("Rename - Coming soon")
			else:  # Return to Castle
				self.location = Location.CASTLE
				self.mode = 'location'
		elif c == 27:  # Esc
			self.location = Location.CASTLE
			self.mode = 'location'

	def _handle_character_list(self, c: int) -> None:
		"""Handle character list selection"""
		available_chars = [c for c in self.roster if c not in self.party]

		if c in (curses.KEY_DOWN, ord('j')):
			self.roster_cursor = min(self.roster_cursor + 1, len(available_chars) - 1) if available_chars else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.roster_cursor = max(0, self.roster_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if available_chars and self.roster_cursor < len(available_chars):
				selected_char = available_chars[self.roster_cursor]

				if self.previous_mode == 'tavern':
					# Add to party - check if character is alive
					if selected_char.status == "DEAD":
						self.push_panel(f"{selected_char.name} is DEAD! Cannot add to party.")
					elif len(self.party) < 6:
						selected_char.id_party = len(self.party)
						self.party.append(selected_char)
						save_character(selected_char, _dir=self.characters_dir)
						self.push_panel(f"Added {selected_char.name} to party")
					else:
						self.push_panel("Party is full (max 6)")
					self.mode = 'tavern'
				elif self.previous_mode == 'training':
					# Delete character
					if delete_character_prompt_ok(selected_char):
						os.remove(f"{self.characters_dir}/{selected_char.name}.dmp")
						self.roster.remove(selected_char)
						self.push_panel(f"Deleted {selected_char.name}")
					self.mode = 'training'
				else:
					self.mode = self.previous_mode or 'location'
		elif c == 27:  # Esc
			self.mode = self.previous_mode or 'location'

	def _handle_messages(self, c: int) -> None:
		"""Handle messages view"""
		if c == 27:  # Esc
			self.mode = 'location'

	def _handle_char_select(self, c: int, char_list) -> None:
		"""Handle character selection for viewing status"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.char_select_cursor = min(self.char_select_cursor + 1, len(char_list) - 1) if char_list else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.char_select_cursor = max(0, self.char_select_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if char_list and self.char_select_cursor < len(char_list):
				self.character_viewing = char_list[self.char_select_cursor]
				self.mode = 'character_status'
		elif c == 27:  # Esc
			self.mode = self.previous_mode or 'tavern'
			self.char_select_cursor = 0

	def _handle_character_status(self, c: int) -> None:
		"""Handle character status viewing"""
		if c == ord('i'):  # Open inventory management
			self.mode = 'character_inventory'
			self.inventory_item_cursor = 0
		elif c == ord('s'):  # View spells (if spell caster)
			if self.character_viewing and hasattr(self.character_viewing, 'is_spell_caster') and self.character_viewing.is_spell_caster:
				self.mode = 'character_spells'
				self.spell_cursor = 0
			else:
				self.push_panel("This character is not a spell caster")
		elif c == 27:  # Esc
			self.character_viewing = None
			# Return to appropriate selection mode
			if self.previous_mode == 'tavern':
				self.mode = 'char_select_party'
			elif self.previous_mode == 'training':
				self.mode = 'char_select_roster'
			else:
				self.mode = self.previous_mode or 'tavern'

	def _handle_character_inventory(self, c: int) -> None:
		"""Handle character inventory management (use/equip items)"""
		if not self.character_viewing:
			self.mode = 'character_status'
			return

		# Already imported at top: from dnd_5e_core.equipment import Weapon, Armor, HealingPotion

		# Get items
		potions = [item for item in self.character_viewing.inventory if item and isinstance(item, HealingPotion)]
		weapons = [item for item in self.character_viewing.inventory if item and isinstance(item, Weapon)]
		armors = [item for item in self.character_viewing.inventory if item and isinstance(item, Armor)]
		total_items = len(potions) + len(weapons) + len(armors)

		if c in (curses.KEY_DOWN, ord('j')):
			if total_items > 0:
				self.inventory_item_cursor = min(self.inventory_item_cursor + 1, total_items - 1)
		elif c in (curses.KEY_UP, ord('k')):
			if total_items > 0:
				self.inventory_item_cursor = max(0, self.inventory_item_cursor - 1)
		elif c == ord('u'):  # Use item (potions only)
			self._use_item_from_inventory(potions, weapons, armors)
		elif c == ord('e'):  # Equip/Unequip (weapons/armors only)
			self._equip_unequip_item(potions, weapons, armors)
		elif c == 27:  # Esc - return to character status
			self.mode = 'character_status'
			self.inventory_item_cursor = 0

	def _handle_character_spells(self, c: int) -> None:
		"""Handle character spells viewing"""
		if c == 27:  # Esc - return to character status
			self.mode = 'character_status'
			self.spell_cursor = 0

	def _use_item_from_inventory(self, potions, weapons, armors) -> None:
		"""Use selected item (potions only)"""
		if not self.character_viewing:
			return

		# Only potions can be used
		if self.inventory_item_cursor < len(potions):
			# It's a potion - use it
			potion = potions[self.inventory_item_cursor]

			# Calculate healing
			try:
				if hasattr(potion, 'heal_at_slot_level'):
					heal_amount = potion.heal_at_slot_level.get(0, 0)
				else:
					heal_amount = 10  # Default

				# Apply healing
				old_hp = self.character_viewing.hit_points
				self.character_viewing.hit_points = min(self.character_viewing.hit_points + heal_amount, self.character_viewing.max_hit_points)
				actual_heal = self.character_viewing.hit_points - old_hp

				# Remove potion from inventory
				idx = self.character_viewing.inventory.index(potion)
				self.character_viewing.inventory[idx] = None

				self.push_panel(f"Used {potion.name} and recovered {actual_heal} HP!")

				# Save character
				try:
					save_character(self.character_viewing, _dir=self.characters_dir)
				except Exception:
					pass

				# Adjust cursor if needed
				remaining_potions = len([p for p in potions if p != potion])
				if self.inventory_item_cursor >= remaining_potions:
					self.inventory_item_cursor = max(0, remaining_potions - 1)
			except Exception as e:
				self.push_panel(f"Error using potion: {str(e)[:30]}")
		else:
			self.push_panel("Only potions can be used here")

	def _equip_unequip_item(self, potions, weapons, armors) -> None:
		"""Equip or unequip selected item (weapons/armors)"""
		if not self.character_viewing:
			return

		cursor = self.inventory_item_cursor

		if cursor < len(potions):
			self.push_panel("Cannot equip a potion. Use 'u' to drink it.")
		elif cursor < len(potions) + len(weapons):
			# It's a weapon
			weapon_idx = cursor - len(potions)
			weapon = weapons[weapon_idx]

			try:
				if hasattr(weapon, 'equipped') and weapon.equipped:
					# Unequip
					weapon.equipped = False
					self.push_panel(f"Unequipped {weapon.name}.")
				else:
					# Unequip all other weapons first
					for w in weapons:
						if hasattr(w, 'equipped'):
							w.equipped = False
					# Equip this one
					weapon.equipped = True
					self.push_panel(f"Equipped {weapon.name}.")

				# Save character
				try:
					save_character(self.character_viewing, _dir=self.characters_dir)
				except Exception:
					pass
			except Exception as e:
				self.push_panel(f"Error: {str(e)[:30]}")
		else:
			# It's an armor
			armor_idx = cursor - len(potions) - len(weapons)
			if armor_idx < len(armors):
				armor = armors[armor_idx]

				try:
					if hasattr(armor, 'equipped') and armor.equipped:
						# Unequip
						armor.equipped = False
						self.push_panel(f"Unequipped {armor.name}.")
					else:
						# Unequip all other armors first
						for a in armors:
							if hasattr(a, 'equipped'):
								a.equipped = False
						# Equip this one
						armor.equipped = True
						self.push_panel(f"Equipped {armor.name}.")

					# Save character
					try:
						save_character(self.character_viewing, _dir=self.characters_dir)
					except Exception:
						pass
				except Exception as e:
					self.push_panel(f"Error: {str(e)[:30]}")
			else:
				self.push_panel("Invalid selection.")

	def _handle_reorder_party(self, c: int) -> None:
		"""Handle party reordering"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.reorder_cursor = min(self.reorder_cursor + 1, len(self.party) - 1) if self.party else 0
		elif c in (curses.KEY_UP, ord('k')):
			self.reorder_cursor = max(0, self.reorder_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.reorder_selected is None:
				# Select character to move
				self.reorder_selected = self.reorder_cursor
			else:
				# Move character to new position
				if self.reorder_selected != self.reorder_cursor:
					char = self.party.pop(self.reorder_selected)
					self.party.insert(self.reorder_cursor, char)

					# Update id_party for all characters
					for i, ch in enumerate(self.party):
						ch.id_party = i
						try:
							save_character(ch, _dir=self.characters_dir)
						except Exception:
							pass

					self.push_panel("Party reordered")

				# Reset and return
				self.reorder_selected = None
				self.reorder_cursor = 0
				self.mode = self.previous_mode or 'tavern'
		elif c == 27:  # Esc
			self.reorder_selected = None
			self.reorder_cursor = 0
			self.mode = self.previous_mode or 'tavern'

	def _handle_cheat_menu(self, c: int) -> None:
		"""Handle cheat menu input"""
		if c in (curses.KEY_DOWN, ord('j')):
			self.cheat_cursor = min(self.cheat_cursor + 1, 4)  # 5 options (0-4)
		elif c in (curses.KEY_UP, ord('k')):
			self.cheat_cursor = max(0, self.cheat_cursor - 1)
		elif c in (ord('\n'), ord('\r')):
			if self.cheat_cursor == 0:  # Revive All Dead Characters
				self._cheat_revive_all()
			elif self.cheat_cursor == 1:  # Full Heal All Characters
				self._cheat_heal_all()
			elif self.cheat_cursor == 2:  # Add 1000 Gold
				self._cheat_add_gold()
			elif self.cheat_cursor == 3:  # Level Up All
				self._cheat_level_up_all()
			elif self.cheat_cursor == 4:  # Return to Main Menu
				self.mode = 'main_menu'
				self.cheat_cursor = 0
		elif c == 27:  # Esc
			self.mode = 'main_menu'
			self.cheat_cursor = 0

	def _cheat_revive_all(self):
		"""Cheat: Revive all dead characters"""
		revived_count = 0
		all_chars = self.roster + self.party

		for char in all_chars:
			if char.status in ["DEAD", "ASHES", "LOST"]:
				char.status = "OK"
				char.hit_points = max(1, char.max_hit_points // 2)  # Revive with half HP
				revived_count += 1
				try:
					save_character(char, _dir=self.characters_dir)
				except Exception:
					pass

		if revived_count > 0:
			self.push_panel(f"⚡ Revived {revived_count} character(s)!")
		else:
			self.push_panel("No dead characters to revive.")

	def _cheat_heal_all(self):
		"""Cheat: Full heal all characters"""
		healed_count = 0
		all_chars = self.roster + self.party

		for char in all_chars:
			if char.hit_points < char.max_hit_points:
				char.hit_points = char.max_hit_points
				healed_count += 1

			# Also cure any negative status
			if char.status in ["PARALYZED", "STONED", "POISONED", "ASLEEP"]:
				char.status = "OK"
				healed_count += 1

			try:
				save_character(char, _dir=self.characters_dir)
			except Exception:
				pass

		if healed_count > 0:
			self.push_panel(f"⚡ Fully healed {healed_count} character(s)!")
		else:
			self.push_panel("All characters already at full health.")

	def _cheat_add_gold(self):
		"""Cheat: Add 1000 gold to all characters"""
		count = 0
		all_chars = self.roster + self.party

		for char in all_chars:
			char.gold += 1000
			count += 1
			try:
				save_character(char, _dir=self.characters_dir)
			except Exception:
				pass

		if count > 0:
			self.push_panel(f"⚡ Added 1000 gold to {count} character(s)!")
		else:
			self.push_panel("No characters to give gold to.")

	def _cheat_level_up_all(self):
		"""Cheat: Level up all characters"""
		from populate_functions import populate, request_spell

		leveled_count = 0
		all_chars = self.roster + self.party

		for char in all_chars:
			if char.level < 20:  # Max level 20
				# Store old level for comparison
				old_level = char.level
				char.level += 1

				# Give XP for next level
				if hasattr(self, 'xp_levels') and char.level < len(self.xp_levels):
					char.xp = self.xp_levels[char.level - 1]

				# Execute level up logic (spells, abilities, etc.)
				try:
					if char.class_type.can_cast:
						# Get available spells for this class
						spell_names = populate(collection_name="spells", key_name="results")
						all_spells = [request_spell(name) for name in spell_names]
						class_tome_spells = [s for s in all_spells if s is not None and char.class_type.index in s.allowed_classes]
						display_message, new_spells = char.gain_level(tome_spells=class_tome_spells)
					else:
						display_message, new_spells = char.gain_level()

					# Update spell slots if caster
					if char.class_type.can_cast:
						if hasattr(char, 'sc') and hasattr(char.sc, 'spell_slots'):
							char.sc.spell_slots = char.class_type.spell_slots[char.level].copy()

					# Show level up message
					self.push_panel(f"⚡ {char.name} reached level {char.level}!")
					if display_message:
						self.push_panel(display_message)

				except Exception as e:
					# Fallback if gain_level fails
					self.push_panel(f"Warning: gain_level failed for {char.name}: {str(e)[:50]}")
					# Increase max HP (simple formula)
					hp_increase = 5 + (char.constitution - 10) // 2 if hasattr(char, 'constitution') else 5
					char.max_hit_points += hp_increase
					char.hit_points += hp_increase

				leveled_count += 1
				try:
					save_character(char, _dir=self.characters_dir)
				except Exception:
					pass

		if leveled_count > 0:
			self.push_panel(f"⚡ Leveled up {leveled_count} character(s)!")
		else:
			self.push_panel("All characters are max level.")

	def _handle_dungeon_explore(self, c: int) -> None:
		"""Handle dungeon exploration - full implementation matching main.py"""
		from random import randint, choice, sample

		# Initialize dungeon state if first time
		if not hasattr(self, 'dungeon_state'):
			self.dungeon_state = {'in_combat': False, 'round_num': 0, 'monsters': [], 'alive_monsters': [], 'alive_chars': [], 'attackers': [], 'encounter_levels': [], 'flee_combat': False, 'combat_ended': False}

			# Generate encounter levels
			party_level = round(sum([c.level for c in self.party]) / len(self.party))
			self.dungeon_state['encounter_levels'] = generate_encounter_levels(party_level=party_level)

			self.dungeon_log.append("=== Entering the dungeon ===")
			self.dungeon_message = "Press Enter to search for encounters..."

		state = self.dungeon_state

		# Check if all party is dead
		all_party_dead = all(c.hit_points <= 0 for c in self.party)

		if c in (ord('\n'), ord('\r')):
			# If all party dead, only allow return to castle
			if all_party_dead:
				self._exit_dungeon()
				return

			# Check if we want to leave
			if state['combat_ended'] or not state['in_combat']:
				if not state['encounter_levels']:
					# No more encounters, exit dungeon
					self.dungeon_log.append("=== You exit the dungeon safely ===")
					self._exit_dungeon()
					return

				# Ask to return to castle
				if state['combat_ended']:
					# Reset for next encounter
					state['combat_ended'] = False
					state['in_combat'] = False
					state['round_num'] = 0
					self.dungeon_message = "Press Enter for next encounter or Esc to return to castle"
					return

				# Start new encounter
				if not state['in_combat']:
					self._start_new_encounter()
					return

			# In combat - execute combat round
			if state['in_combat']:
				self._execute_combat_round()

		elif c == 27:  # Esc - flee
			if state['in_combat']:
				# Flee from combat starts a new encounter instead of returning to castle
				state['flee_combat'] = True
				state['in_combat'] = False
				state['combat_ended'] = False
				self.dungeon_log.append("=== Party flees from combat! ===")
				self.dungeon_message = "Press Enter for next encounter or Esc to return to castle"
			else:
				self._exit_dungeon()

	def _start_new_encounter(self):
		"""Start a new monster encounter"""
		from random import randint, choice
		from copy import copy

		state = self.dungeon_state

		# Generate encounter
		if not state['encounter_levels']:
			self.dungeon_message = "No more encounters! Press Enter to exit."
			return

		encounter_level = state['encounter_levels'].pop(0)
		monster_groups_count = randint(1, 2)

		monsters = []

		# Try to generate monsters with the official system
		if self.monsters and self.encounter_table and self.available_crs:
			try:
				monsters = generate_encounter(available_crs=self.available_crs, encounter_table=self.encounter_table, encounter_level=encounter_level, monsters=self.monsters, monster_groups_count=monster_groups_count, spell_casters_only=False)
				if monsters:
					self.dungeon_log.append(f"[DEBUG] Generated {len(monsters)} monsters via generate_encounter")
			except Exception as e:
				self.dungeon_log.append(f"[DEBUG] generate_encounter failed: {str(e)[:50]}")
				monsters = []

		# Fallback 1: Pick random monsters from database
		if not monsters and self.monsters:
			try:
				from copy import deepcopy
				available_monsters = [m for m in self.monsters if hasattr(m, 'name') and hasattr(m, 'hit_points')]
				if available_monsters:
					num_monsters = randint(1, 3)
					# Use deepcopy to properly clone Monster objects with all their attributes
					monsters = [deepcopy(choice(available_monsters)) for _ in range(num_monsters)]
					self.dungeon_log.append(f"[DEBUG] Fallback 1: Generated {len(monsters)} random monsters")
			except Exception as e:
				self.dungeon_log.append(f"[DEBUG] Fallback 1 failed: {str(e)[:50]}")
				monsters = []

		# Fallback 2: Create simple monsters manually
		if not monsters:
			try:
				# Create simple monsters with basic stats
				from types import SimpleNamespace
				num_monsters = randint(1, 3)
				monster_types = ["Goblin", "Orc", "Kobold", "Skeleton", "Zombie"]

				for i in range(num_monsters):
					monster = SimpleNamespace()
					monster.name = choice(monster_types)
					monster.max_hit_points = randint(10, 30)
					monster.hit_points = monster.max_hit_points
					monster.challenge_rating = encounter_level
					monster.xp = encounter_level * 50
					monster.actions = None

					# Add abilities
					monster.abilities = SimpleNamespace()
					monster.abilities.dex = randint(8, 14)

					monsters.append(monster)

				self.dungeon_log.append(f"[DEBUG] Fallback 2: Created {len(monsters)} simple monsters")
			except Exception as e:
				self.dungeon_log.append(f"[DEBUG] Fallback 2 failed: {str(e)[:50]}")

		# Final check - if still no monsters, skip this encounter
		if not monsters:
			self.dungeon_log.append("The corridor is empty...")
			self.dungeon_message = "Press Enter to continue exploring..."
			return

		state['monsters'] = monsters
		state['alive_monsters'] = [m for m in monsters if m.hit_points > 0]
		state['alive_chars'] = [c for c in self.party if c.hit_points > 0]

		# Log encounter
		monster_names = ", ".join([m.name.title() for m in monsters])
		self.dungeon_log.append(f"=== New Encounter! ===")
		self.dungeon_log.append(f"Encountered: {monster_names}")

		# Initialize combat
		attack_queue = [(c, randint(1, 20) + (c.abilities.dex if hasattr(c, 'abilities') else 0)) for c in self.party]
		attack_queue += [(m, randint(1, 20) + (m.abilities.dex if hasattr(m, 'abilities') else 0)) for m in monsters]
		attack_queue.sort(key=lambda x: x[1], reverse=True)

		state['attackers'] = [entity for entity, _ in attack_queue]
		state['in_combat'] = True
		state['round_num'] = 0
		state['flee_combat'] = False

		self.dungeon_message = "Combat started! Press Enter to continue..."

	def _execute_combat_round(self):
		"""Execute one round of combat"""
		from random import randint, choice, sample

		state = self.dungeon_state
		state['round_num'] += 1

		self.dungeon_log.append(f"--- Round {state['round_num']} ---")

		# Combat queue
		queue = [entity for entity in state['attackers'] if entity.hit_points > 0]

		while queue:
			attacker = queue.pop(0)

			if attacker.hit_points <= 0:
				continue

			# Check if combat should end
			state['alive_chars'] = [c for c in self.party if c.hit_points > 0]
			state['alive_monsters'] = [m for m in state['monsters'] if m.hit_points > 0]

			if not state['alive_monsters'] or not state['alive_chars']:
				break

			# Monster attack
			if attacker in state['monsters']:
				self._monster_attack(attacker)
			# Character attack
			else:
				self._character_attack(attacker)

		# Check end of combat
		state['alive_chars'] = [c for c in self.party if c.hit_points > 0]
		state['alive_monsters'] = [m for m in state['monsters'] if m.hit_points > 0]

		if not state['alive_chars']:
			self.dungeon_log.append("=== DEFEAT! All party members have fallen! ===")
			for char in self.party:
				char.status = "DEAD"
			self._end_combat(victory=False)
		elif not state['alive_monsters']:
			self.dungeon_log.append("=== VICTORY! All monsters defeated! ===")
			self._distribute_rewards()
			self._end_combat(victory=True)
		else:
			self.dungeon_message = f"Round {state['round_num']} complete. Press Enter to continue..."

	def _monster_attack(self, monster):
		"""Monster attacks party - using CombatSystem from dnd-5e-core"""
		from dnd_5e_core.combat import execute_combat_turn

		state = self.dungeon_state
		alive_chars = state['alive_chars']
		alive_monsters = state['alive_monsters']

		if not alive_chars:
			return

		# Use centralized combat system
		execute_combat_turn(
			attacker=monster,
			alive_chars=alive_chars,
			alive_monsters=alive_monsters,
			party=self.party,
			round_num=state['round_num'],
			verbose=False,
			message_callback=lambda msg: self.dungeon_log.append(msg)
		)

	def _character_attack(self, character):
		"""Character attacks monster - using CombatSystem from dnd-5e-core"""
		from dnd_5e_core.combat import execute_combat_turn

		state = self.dungeon_state
		alive_monsters = state['alive_monsters']
		alive_chars = state['alive_chars']

		if not alive_monsters:
			return

		# Use centralized combat system
		execute_combat_turn(
			attacker=character,
			alive_chars=alive_chars,
			alive_monsters=alive_monsters,
			party=self.party,
			round_num=state['round_num'],
			verbose=False,
			message_callback=lambda msg: self.dungeon_log.append(msg),
			weapons=self.weapons if hasattr(self, 'weapons') else [],
			armors=self.armors if hasattr(self, 'armors') else [],
			equipments=self.equipments if hasattr(self, 'equipments') else [],
			potions=self.potions if hasattr(self, 'potions') else []
		)

	def _distribute_rewards(self):
		"""Distribute XP and gold after victory"""
		from random import randint

		state = self.dungeon_state

		# Calculate rewards
		party_level = round(sum([c.level for c in self.party]) / len(self.party))

		if hasattr(self, 'encounter_gold_table') and self.encounter_gold_table:
			try:
				earned_gold = self.encounter_gold_table[min(party_level - 1, len(self.encounter_gold_table) - 1)]
			except:
				earned_gold = randint(50, 200)
		else:
			earned_gold = randint(50, 200)

		xp_gained = sum([getattr(m, 'xp', 100) for m in state['monsters']])

		# Distribute to alive characters
		alive_chars = [c for c in self.party if c.hit_points > 0]
		if alive_chars:
			for char in alive_chars:
				char.gold += earned_gold // len(self.party)
				char.xp += xp_gained // len(alive_chars)

		self.dungeon_log.append(f"Party earned {earned_gold} GP and {xp_gained} XP!")

	def _end_combat(self, victory=True):
		"""End current combat"""
		state = self.dungeon_state
		state['in_combat'] = False
		state['combat_ended'] = True

		if victory:
			self.dungeon_message = "Victory! Press Enter for next encounter or Esc to exit"
		else:
			self.dungeon_message = "Defeat! Press Enter to exit dungeon"

	def _exit_dungeon(self):
		"""Exit dungeon and return to town"""
		# Save all characters
		for char in self.party:
			if char.hit_points <= 0:
				char.status = "DEAD"
			try:
				save_character(char, _dir=self.characters_dir)
			except Exception:
				pass

		# Remove all dead members from party
		dead_members = [c for c in self.party if c.status == "DEAD"]
		for char in dead_members:
			char.id_party = -1
			try:
				save_character(char, _dir=self.characters_dir)
			except Exception:
				pass

		# Keep only alive members in party
		self.party = [c for c in self.party if c.status != "DEAD"]

		try:
			save_party(self.party, _dir=self.game_path)
		except Exception:
			pass

		# Reset state
		if hasattr(self, 'dungeon_state'):
			delattr(self, 'dungeon_state')
		self.dungeon_step = 0
		self.dungeon_log = []
		self.dungeon_message = ""

		# Return to edge of town
		self.mode = 'location'
		self.location = Location.EDGE_OF_TOWN
		self.push_panel("Returned from dungeon")


def run_dnd_curses():
	"""Entry point for ncurses interface"""

	def _wrapped(stdscr):
		ui = DnDCursesUI(stdscr)
		ui.mainloop()

	curses.wrapper(_wrapped)


if __name__ == "__main__":
	# Set TERM if not already set
	if "TERM" not in os.environ:
		os.environ["TERM"] = "xterm-256color"

	# Initialize random seed
	seed(time.time())

	# Run the game
	run_dnd_curses()
