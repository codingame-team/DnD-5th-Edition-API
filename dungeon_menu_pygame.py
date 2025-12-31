import pygame
import sys
from enum import Enum
from typing import List
import os

from game_entity import GameCharacter

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
from dnd_5e_core.entities import Character
from dnd_5e_core.ui import cprint

# Note: Data directory is now in dnd-5e-core/data and will be auto-detected

from dungeon_pygame import save_character_gamestate, Game
from main import get_roster, save_character
from tools.cheat_functions import raise_dead_roster
from tools.common import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, RED, WHITE, resource_path, get_save_game_path
import dungeon_pygame, boltac_tp_pygame, monster_kills_pygame

print("✅ [MIGRATION v2] dungeon_menu_pygame.py - Using dnd-5e-core package")
print()

# Override screen dimensions for menu
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
				print(f'✅ Personnage {char.name} importé dans {self.characters_dir}')

	def go_to_location(self, character_name: str, location: LT):
		if location == LT.DUNGEON:
			dungeon_pygame.run(character_name)
		elif location == LT.BOLTAC:
			boltac_tp_pygame.run(character_name)
		elif location == LT.MONSTER_KILLS:
			monster_kills_pygame.run(character_name)
		else:
			print('❌ Invalid location')

		# Note: Don't reinitialize Pygame here
		# Modules don't call pygame.quit() anymore, so Pygame stays initialized
		# This avoids slow reinitialization between modules

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
		# Save gamestate (Game with GameCharacter)
		save_character_gamestate(game, self.gamestate_dir)
		# Note: save_character_gamestate also saves Character entity separately

	def draw_character_menu(self, roster: List[Game], scroll_offset):
		# Ensure Pygame and font are properly initialized
		if not pygame.get_init():
			pygame.init()
		if not pygame.font.get_init():
			pygame.font.init()

		# Always recreate the font to avoid "Invalid font" error
		try:
			self.font = pygame.font.Font(None, 22)
		except:
			pygame.font.init()
			self.font = pygame.font.Font(None, 22)

		self.screen.fill(WHITE)
		text_rects = []
		for index, game in enumerate(roster):
			y_position = self.line_height * 2 + (index * self.line_height) - scroll_offset
			if 0 <= y_position < self.screen_height:
				if hasattr(game.hero.entity, 'class_type'):
					option = self.font.render(f"{game.hero.entity.name} (Level {game.hero.entity.level} {game.hero.entity.class_type})", True, RED)
				else:
					option = self.font.render(f"{game.hero.entity.name} (CR {game.hero.entity.level})", True, RED)
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
		# Ensure Pygame and font are properly initialized
		if not pygame.get_init():
			pygame.init()
		if not pygame.font.get_init():
			pygame.font.init()

		# Always recreate the font to avoid "Invalid font" error
		try:
			self.font = pygame.font.Font(None, 22)
		except:
			pygame.font.init()
			self.font = pygame.font.Font(None, 22)

		for i, option in enumerate(options):
			pos = radio_button_positions[i]
			pygame.draw.circle(self.screen, (0, 0, 0), pos, 7, 1)  # Draw the outer circle
			if selected_option == i:
				pygame.draw.circle(self.screen, (0, 0, 0), pos, 4)  # Draw the inner circle if selected
			text = self.font.render(option, True, (0, 0, 0))
			self.screen.blit(text, (pos[0] + 20, pos[1] - 10))

	def main(self, roster: List[Game]):
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
								selected_game = roster[index]
								if not selected_game.hero.is_dead:
									self.go_to_location(selected_game.hero.name, LT(selected_option))

									# OPTIMIZATION: Reload roster ONLY for the character that was modified
									print(f'🔄 Reloading gamestate for {selected_game.hero.name}...')
									updated_game = dungeon_pygame.load_character_gamestate(selected_game.hero.name, self.gamestate_dir)
									if updated_game:
										# Update the roster entry
										roster[index] = updated_game
										print(f'✅ Gamestate reloaded for {selected_game.hero.name}')

									# OPTIMIZATION: Don't reinitialize Pygame - it's already running
									# Just ensure the window is configured correctly
									pygame.display.set_caption('Choose your character')

									# Ensure we have a valid screen (in case module changed resolution)
									current_info = pygame.display.Info()
									if current_info.current_w != self.screen_width or current_info.current_h != self.screen_height:
										self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

									# Font should still be valid, but recreate if needed
									if not self.font or not pygame.font.get_init():
										pygame.font.init()
										self.font = pygame.font.Font(None, 22)
								else:
									cprint(f'Cannot select character... {selected_game.hero.name} is dead!')
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
		roster_gs: List[Game] = []
		roster: List[Character] = get_roster(self.characters_dir)
		raise_dead_roster(roster, self.characters_dir)

		# Synchronisation : si un gamestate existe pour un personnage, prendre le hero du gamestate
		# (qui contient le niveau à jour) et persister dans characters_dir pour garder une source unique.
		for char in roster:
			saved_game: Game = dungeon_pygame.load_character_gamestate(char.name, self.gamestate_dir)
			roster_gs += [saved_game] if saved_game else [Game(char)]

		self.main(roster_gs)  # except FileNotFoundError:  #     cprint(f'No characters found in {self.characters_dir}', color=RED)


if __name__ == "__main__":
	game_menu = GameMenu()
	game_menu.run()