# Définition des constantes pour la mise en page
# SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
from __future__ import annotations

import math
import os
import pickle
import re
import sys
import time
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from random import choice, randint
from typing import List, Optional, Tuple

import pygame
from pygame import Surface

from algo.brehensam import in_view_range
from algo.lee import parcours_largeur, parcours_a_star
from dao_classes import Character, Level, Spell, Weapon, Armor, HealingPotion, Monster, Equipment, Treasure, Sprite, SpecialAbility, color, ActionType, Action, SpeedPotion, Potion, StrengthPotion, DamageDice
from main import get_roster, save_character, load_xp_levels, load_character
from populate_functions import populate, request_armor, request_weapon, request_monster, request_spell, request_monster_other
from populate_rpg_functions import load_potions_collections
from tools.cell_bits_dnd import DOORSPACE, TRAPPED, STAIR_UP, STAIR_DN
from tools.common import cprint, generate_cave, generate_dungeon, Color, MAX_LEVELS, GREEN, resource_path, get_save_game_path, read
from tools.parse_json_dungeon import parse_dungeon_json
from tools import cell_bits_dnd as cb
from tools.parsing_json_monsters import get_monster_counts

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
STATS_WIDTH, ACTIONS_HEIGHT = 600, 200
STATS_HEIGHT = 250

# Paramètres de la map
UNIT_SIZE = 5
JSON_UNIT_SIZE = 10

# Paramètres de l'écran
TILE_SIZE = 32
FPS = 60

# Autres paramètres
ICON_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 0, 255)
ORANGE = (255, 165, 0)

# Directions
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

ROUND_DURATION = 6  # Duration of a round in seconds


def put_inlay(image: pygame.Surface, number: int, center=False, color=WHITE):
    # Police pour le texte
    font = pygame.font.Font(None, 18)

    # Créer la surface du texte
    text_surface = font.render(str(number), True, color)

    # Définir la position du texte sur l'image (par exemple, en bas à droite)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = image.get_rect().center
    else:
        text_rect.topleft = image.get_rect().topleft

    # Ajouter le texte sur l'image
    image.blit(text_surface, text_rect)


# Définition de la fonction pour afficher une info-bulle
def draw_tooltip(description, surface, x, y):
    font = pygame.font.Font(None, 18)
    text = font.render(description, True, BLACK)
    text_rect = text.get_rect()
    text_rect.topleft = (x, y)

    # Créer une surface pour le rectangle d'arrière-plan
    tooltip_surface = pygame.Surface((text_rect.width + 10, text_rect.height + 10), pygame.SRCALPHA)  # SRCALPHA pour la transparence
    tooltip_surface.fill((150, 150, 150, 150))  # Remplir avec une couleur grise semi-transparente

    # Dessiner le texte sur la surface d'arrière-plan
    tooltip_surface.blit(text, (5, 5))  # Décalage de 5 pixels pour laisser un espace

    # Dessiner la surface d'arrière-plan sur l'écran principal
    surface.blit(tooltip_surface, (text_rect.left - 5, text_rect.top - 5))  # Décalage de 5 pixels pour centrer le texte dans le rectangle


@dataclass
class Room:
    id: int
    x: int
    y: int
    w: int
    h: int
    inhabited: bool
    features: str
    monsters: List[Monster]
    treasure: Optional[Treasure] = None

    def __repr__(self):
        x, y, X, Y = self.x, self.y, self.x + self.w // JSON_UNIT_SIZE - 1, self.y + self.h // JSON_UNIT_SIZE - 1
        desc: str = f'Room #{self.id} - start: {(x, y)} - end: {(X, Y)} - area: {self.area}\n'
        if self.features:
            desc += f'Features: {self.features}\n' if self.features else 'Nothing special in this room'
        if self.monsters:
            desc += f'{len(self.monsters)} monsters: {[monster.name for monster in self.monsters]}\n'
        if self.treasure:
            desc += f'Treasure: {self.treasure.gold} gp and 1 item\n'
        return desc

    @property
    def inner_positions(self):
        return [(x, y) for x in range(self.x, self.x + self.w // JSON_UNIT_SIZE)
                for y in range(self.y, self.y + self.h // JSON_UNIT_SIZE)]

    @property
    def area(self):
        return self.w * self.h


class Level:
    level_no: int
    world_map: List[List[int]]
    map_height: int
    map_width: int
    monsters: List[Monster]
    treasures: List[Treasure]
    fountains: List[Sprite]
    items: List[Equipment | HealingPotion]
    cells_count: int
    explored_tiles: set[tuple]
    visible_tiles: set[tuple]
    doors: dict
    fullname: str
    rooms: List[Room]
    start_pos: tuple
    wandering_monsters: List[dict] = []

    def __init__(self, level_no: int, name: str = ''):
        self.level_no = level_no
        self.monsters = []
        self.fountains = []
        self.world_map, self.cells_count, self.doors, self.fullname, self.rooms, self.start_pos = self.load_maze(level=level_no)
        self.map_height = len(self.world_map)
        self.map_width = max([len(self.world_map[i]) for i in range(self.map_height)])
        self.items = []
        self.explored_tiles = set()
        self.visible_tiles = set()
        self.treasures = []

    def room_at(self, pos: tuple) -> Optional[Room]:
        for room in self.rooms:
            if room and pos in room.inner_positions:
                return room
        return None

    def is_stair(self, x, y):
        return self.world_map[y][x] in ['<', '>']

    def load_maze(self, level: int) -> tuple[list[str] | list[list[str]], int, dict, str, list[Room], tuple | None]:
        """
        Charge le labyrinthe depuis le fichier level.txt
        nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
        Valeur de retour :
        - un tuple avec les données du labyrinthe (maze, n_cells, doors, level_fullname, rooms, hero_start_pos)
        """
        map_type = 'cave'
        map_type = 'dungeon'
        map_type = 'dungeon.json'
        level_fullname: str = ''
        doors: dict = {}
        stair_up: tuple = None
        stair_down: tuple = None
        if map_type == 'cave':
            # min_value, max_value = (level - 3) * 4, (level - 3) * 8
            min_value, max_value = (level + 1) * 4, (level + 1) * 8
            width, height = randint(min_value, max_value), randint(min_value, max_value)
            n_cells = (width * height) // 3
            maze = generate_cave(width, height, n_cells)
        elif map_type == 'dungeon':
            min_value, max_value = (level + 1) * 10, (level + 1) * 20
            width, height = randint(min_value, max_value), randint(min_value, max_value)
            num_chambers = int(math.sqrt(width * height)) // 6
            cprint(f'num chambers: {num_chambers}')
            maze = generate_dungeon(width, height, num_chambers, 3, 10)
            maze = [['.' if cell else '#' for cell in row] for row in maze]
            n_cells = sum([row.count('.') for row in maze])
        else:
            abs_path = os.path.abspath(os.path.dirname(__file__))
            abs_project_path = os.path.abspath(os.path.join(abs_path, os.pardir))
            dungeon_levels = [f for f in os.listdir(os.path.join(abs_path, 'maze')) if f.endswith(f"{level:02}.json")]
            json_filename = choice(dungeon_levels)
            pattern = r' \d+\.json'
            level_fullname = re.sub(pattern, '', json_filename)
            # json_filename = 'dungeon.json' # generated by perl script (room+corridors without extras)
            dungeon = parse_dungeon_json(json_filename)
            cells = dungeon['cell'] if 'cell' in dungeon else dungeon['cells']
            maze = [['.' if cell & cb.OPENSPACE else '#' for cell in row] for row in cells]
            width, height = len(maze[0]), len(maze)
            if 'door' in dungeon:
                doors = {(door['col'], door['row']): False for door in dungeon['door']}
            else:
                doors = {(x, y): False for x in range(width) for y in range(height) if cells[y][x] & DOORSPACE}
            door_traps = [(x, y) for x in range(width) for y in range(height) if cells[y][x] & TRAPPED]
            stair_up = [(x, y) for x in range(width) for y in range(height) if cells[y][x] & STAIR_UP][0]
            stair_down = [(x, y) for x in range(width) for y in range(height) if cells[y][x] & STAIR_DN][0]
            # Parse corridor events
            corridor_features = dungeon['corridor_features'] if 'corridor_features' in dungeon else {}
            corridor_events: dict = {}
            if corridor_features:
                for feature_label, feature_detail in corridor_features.items():
                    for mark in feature_detail['marks']:
                        x, y = mark['col'], mark['row']
                        corridor_events[(x, y)] = feature_detail['detail']
            # Parse wandering monsters
            for monsters_detail in dungeon['wandering_monsters'].values():
                monsters_dict = get_monster_counts(text=monsters_detail)
                monsters: List[str] = []
                for monster_name, monster_count in monsters_dict.items():
                    for _ in range(monster_count):
                        monsters.append(monster_name)
                self.wandering_monsters += [monsters]
            # Parse room events
            room_traps: dict = {}
            room_door_traps: dict = {}
            rooms: List[Room] = []
            for i, room in enumerate(dungeon['rooms']):
                if room:
                    inhabited: bool = False
                    room_features: str = ''
                    monsters_in_room: dict = {}
                    if 'contents' in room:
                        # print(room)
                        if 'detail' in room['contents']:
                            details = room['contents']['detail']
                            if 'trap' in details:
                                room_traps[i] = details['trap']
                            if 'room_features' in details:
                                room_features = details['room_features']
                        if 'inhabited' in room['contents']:
                            inhabited: bool = True
                            monsters_in_room: dict = get_monster_counts(room['contents']['inhabited'])
                    if 'doors' in room:
                        for _dir, door_lst in room['doors'].items():
                            for door in door_lst:
                                if 'trap' in door:
                                    x, y = door['col'], door['row']
                                    room_door_traps[(x, y)] = door['trap']
                    monsters: List[Monster] = []
                    if monsters_in_room:
                        for monster_name in monsters_in_room:
                            try:
                                monster = request_monster(monster_name.lower().replace(' ', '-'))
                                monsters.append(monster)
                            except FileNotFoundError:
                                monster = request_monster_other(monster_name)
                                if monster:
                                    monsters.append(monster)
                                else:
                                    cprint(f'unknown monster {Color.RED}{monster_name}{Color.END}!')
                        if monsters:
                            self.monsters += monsters
                    room = Room(id=room['id'], inhabited=inhabited, features=room_features, monsters=monsters, x=room['col'], y=room['row'], w=room['width'], h=room['height'])
                    rooms.append(room)
            n_cells = sum([row.count('.') for row in maze])
        if not stair_up and not stair_down:
            cprint(f'no stair defined in dungeon!')
            walkable_cells = [(x, y) for y in range(height) for x in range(width) if maze[y][x] == '.']
            stair_up = choice(walkable_cells)
            walkable_cells.remove(stair_up)
            stair_down = choice(walkable_cells)
        hero_start_pos: Optional[tuple] = None
        if level > 1:
            maze[stair_up[1]][stair_up[0]] = '<'
        else:
            hero_start_pos: tuple = stair_up
        if level < MAX_LEVELS:
            maze[stair_down[1]][stair_down[0]] = '>'
        return maze, n_cells, doors, level_fullname, rooms, hero_start_pos

    def load(self, hero: Character):
        """
            Chargement des entités du donjon (monstres et trésors)
        :param level:
        :return:
        """

        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if
                                       self.world_map[y][x] == '.' and (x, y) != hero.pos and (x, y) not in self.doors]
        f_x, f_y = choice(open_positions)
        f: Sprite = Sprite(id=-1, x=f_x, y=f_y, old_x=f_x, old_y=f_y, image_name='fountain.png')
        self.fountains.append(f)
        open_positions.remove((f_x, f_y))

        for room in self.rooms:
            if room and room.inhabited:
                room_positions = [(x, y) for x, y in room.inner_positions if (x, y) in open_positions]
                self.place_treasure(room, room_positions)
                # self.place_monsters(room, room_positions, monster_candidates)
                self.place_monsters(room, room_positions)
                self.treasures.append(room.treasure)

    @property
    def walkable_tiles(self):
        closed_doors: List[tuple] = [pos for pos, is_open in self.doors.items() if not is_open]
        return [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] in ['.', '<', '>'] and (x, y) not in closed_doors]

    @property
    def obstacles(self):
        closed_doors: List[tuple] = [pos for pos, is_open in self.doors.items() if not is_open]
        return [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#' or (x, y) in closed_doors]

    @property
    def carte(self) -> List[List[int]]:
        obstacles = [*self.obstacles]  # + [(e.x, e.y) for e in enemies if e != enemy]
        carte = [[1] * self.map_width for _ in range(self.map_height)]
        for y in range(self.map_height):
            for x in range(self.map_width):
                if (x, y) in obstacles:
                    carte[y][x] = 0
        return carte

    def place_treasure(self, room: Room, room_positions: List[tuple]):
        # print(f'room {room.id}: {len(room_positions)} positions - area: {room.area}')
        gold: int = randint(50, 300) * self.level_no
        has_item: bool = randint(1, 3) == 2
        # print(room)
        t_x, t_y = choice(room_positions)
        room_positions.remove((t_x, t_y))
        room.treasure = Treasure(id=-1, x=t_x, y=t_y, old_x=t_x, old_y=t_y, image_name='treasure.png', gold=gold, has_item=has_item)

    def place_monsters_old(self, room: Room, room_positions: List[tuple], monster_candidates: List[Monster]):
        cr_total: int = 0
        monster_room_candidates = list(filter(lambda m: m.challenge_rating <= self.level_no / 4, monster_candidates))
        max_monster = room.area // 600
        i = 0
        while cr_total < self.level_no / 4 and monster_room_candidates and room_positions and i < max_monster:
            monster_type: Monster = choice(monster_room_candidates)
            m: Monster = request_monster(monster_type.index)
            m.x, m.y = choice(room_positions)
            cr_total += m.challenge_rating
            room_positions.remove((m.x, m.y))
            room.monsters.append(m)
            self.monsters.append(m)
            remaining_cr = self.level_no / 4 - cr_total
            monster_room_candidates = list(filter(lambda m: m.challenge_rating <= remaining_cr, monster_candidates))
            i += 1

    def place_monsters(self, room, room_positions):
        for m in room.monsters:
            m.x, m.y = choice(room_positions)
            room_positions.remove((m.x, m.y))


class Game:
    world_map: List[List[int]]
    map_width: int
    map_height: int
    screen_width: int
    screen_height: int
    view_port_width: int
    view_port_height: int
    hero: Character
    dungeon_level: int
    action_rects: dict
    levels: List[Level]
    level: Level
    school_images: dict
    xp_levels: List[int]
    timer: int
    last_round_time: float
    ready_spell: Optional[Spell]
    target_pos: tuple
    round_no: int
    last_combat_round: int
    target_pos: Optional[tuple]

    def __init__(self, char_name: str, char_dir: str, actions_panel=False, start_level=1):
        self.ready_spell = None
        self.target_pos = None
        self.round_no = 0
        self.last_combat_round = 0
        self.last_round_time = time.time()
        self.timer = 0
        # Chargement de la carte
        self.actions_panel = actions_panel
        self.dungeon_level = start_level
        self.level = Level(start_level)
        self.levels = [self.level]
        self.world_map = self.level.world_map
        self.map_height = self.level.map_height
        self.map_width = self.level.map_width
        self.walls = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#']
        # Redimensionnement de l'écran
        self.view_port_width = SCREEN_WIDTH - STATS_WIDTH
        self.view_port_height = SCREEN_HEIGHT
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.action_rects = {}
        # Création de la fenêtre
        # self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        # Initialisation du personnage
        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.']
        # hero_x, hero_y = choice(open_positions)
        hero_x, hero_y = self.level.start_pos
        open_positions.remove((hero_x, hero_y))
        self.hero = load_character(char_name=char_name, _dir=char_dir)
        self.hero.x, self.hero.y = hero_x, hero_y
        self.level.explored_tiles.add((self.hero.x, self.hero.y))
        self.update_visible_tiles()
        # cprint(f'{len(self.level.visible_tiles)} cases visibles')
        self.level.load(hero=self.hero)
        """ Load XP Levels """
        self.xp_levels = load_xp_levels()

    @property
    def time_elapsed(self):
        return self.round_no * ROUND_DURATION

    # @property
    # def days(self):
    #     return self.time_elapsed // (24 * 60 * 60)
    #
    # @property
    # def hours(self):
    #     return (self.time_elapsed % (24 * 60 * 60)) // (60 * 60)
    #
    # @property
    # def minutes(self):
    #     return (self.time_elapsed % (60 * 60)) // 60
    #
    # @property
    # def seconds(self):
    #     return self.time_elapsed % 60
    #
    # @property
    # def date_print(self):
    #     return f'{self.days}j {self.hours}h {self.minutes}m {self.seconds}s'

    @property
    def gregorian_calendar(self) -> str:
        time_elapsed = self.time_elapsed
        days = int(time_elapsed // (24 * 60 * 60))
        time_elapsed %= (24 * 60 * 60)
        hours = int(time_elapsed // (60 * 60))
        time_elapsed %= (60 * 60)
        minutes = int(time_elapsed // 60)
        time_elapsed %= 60
        seconds = int(time_elapsed)
        return f'{days}j {hours}h {minutes}m {seconds}s'

    def load_token_images(self, token_images_dir: str) -> dict:
        token_images = {}
        for filename in os.listdir(token_images_dir):
            monster_name, _ = os.path.splitext(filename)
            image_path = os.path.join(token_images_dir, filename)
            original_image = pygame.image.load(image_path)
            # Resize the image to 280x280 pixels
            token_images[monster_name] = pygame.transform.scale(original_image, (105, 105))
        return token_images

    # Define a method to calculate the view window
    def calculate_view_window(self):
        view_width = self.view_port_width // TILE_SIZE
        view_height = self.view_port_height // TILE_SIZE
        viewport_x = max(0, min(self.hero.x - view_width // 2, self.map_width - view_width))
        viewport_y = max(0, min(self.hero.y - view_height // 2, self.map_height - view_height))
        # Calculate the new view port rectangle
        view_port_rect = pygame.Rect(viewport_x * TILE_SIZE, viewport_y * TILE_SIZE, self.view_port_width, self.view_port_height)
        # cprint(viewport_x, viewport_y, view_width, view_height, view_port_rect)
        return viewport_x, viewport_y, view_width, view_height

    def draw_mini_map(self, screen):
        """
        Draw a mini-map on a separate surface.
        """
        # Set the size of the mini-map
        mini_map_width = 300
        mini_map_height = 250

        # Create a new surface for the mini-map
        OFFSET_X, OFFSET_Y = SCREEN_WIDTH - STATS_WIDTH + 10, 3 * (SCREEN_HEIGHT // 4) - 80
        mini_map_rect = pygame.Rect(OFFSET_X, OFFSET_Y, mini_map_width, mini_map_height)

        # Calculate the scale factor to fit the map onto the mini-map
        scale_x = mini_map_width / self.map_width
        scale_y = mini_map_height / self.map_height

        # Create a new surface for the mini-map
        mini_map_surface = pygame.Surface((mini_map_width, mini_map_height))

        # Draw the map tiles onto the mini-map surface
        for y in range(self.map_height):
            for x in range(self.map_width):
                if (x, y) not in self.level.visible_tiles:
                    color = BLACK
                else:
                    tile = self.world_map[y][x]
                    if tile == '#':
                        color = (128, 128, 128)  # Wall color
                    elif tile in ('<', '>'):
                        color = (0, 0, 255)  # Stairs color
                    elif any(f.pos == (x, y) for f in self.level.fountains):
                        color = (0, 255, 0)  # Fountain color
                    else:
                        color = (64, 64, 64)  # Floor color
                pygame.draw.rect(mini_map_surface, color, (x * scale_x, y * scale_y, scale_x, scale_y))

        # Draw the player's position on the mini-map
        player_x, player_y = self.hero.x, self.hero.y
        pygame.draw.circle(mini_map_surface, RED, (int(player_x * scale_x), int(player_y * scale_y)), 5)

        # Draw the treasure positions on the mini-map
        for treasure in self.level.treasures:
            if treasure.pos not in self.level.explored_tiles:
                continue
            treasure_x, treasure_y = treasure.x, treasure.y
            pygame.draw.circle(mini_map_surface, (255, 255, 0), (int(treasure_x * scale_x), int(treasure_y * scale_y)), 3)

        # Blit the mini-map onto the main game screen
        screen.blit(mini_map_surface, (OFFSET_X, OFFSET_Y))

        return mini_map_surface

    def draw_map(self, path, screen):
        photo_wall = pygame.image.load(f"{path}/sprites/TilesDungeon/Wall.png")
        photo_downstairs = pygame.image.load(f"{path}/sprites/DownStairs.png")
        photo_upstairs = pygame.image.load(f"{path}/sprites/UpStairs.png")
        photo_door_closed = pygame.image.load(f"{path}/sprites/door_closed_2.png")
        photo_door_open = pygame.image.load(f"{path}/sprites/door_open_2.png")

        # Calculate the view window
        view_x, view_y, view_width, view_height = self.calculate_view_window()

        # Draw only the portion of the map that falls within the view window
        for y in range(view_y, view_y + view_height):
            for x in range(view_x, view_x + view_width):
                tile_x, tile_y = (x - view_x) * TILE_SIZE, (y - view_y) * TILE_SIZE
                if (x, y) in self.level.visible_tiles:
                    if self.world_map[y][x] == '#':
                        screen.blit(photo_wall, (tile_x, tile_y))
                    elif self.world_map[y][x] == '<':
                        screen.blit(photo_upstairs, (tile_x, tile_y))
                    elif self.world_map[y][x] == '>':
                        screen.blit(photo_downstairs, (tile_x, tile_y))
                    elif (x, y) in self.level.doors:
                        # Draw a door tile
                        photo_door = photo_door_open if self.level.doors[(x, y)] else photo_door_closed
                        screen.blit(photo_door, (tile_x, tile_y))
                else:
                    # Draw a black square for unexplored and not in sight range tiles
                    screen.fill(BLACK, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))

    def feet_inches_to_m_cm(self, height_feet: int, height_inches: int) -> tuple[float, float]:
        total_inches = height_feet * 12 + height_inches
        height_meters = total_inches * 2.54 // 100
        height_centimeters = total_inches * 2.54 % 100
        return height_meters, height_centimeters

    # Fonction pour dessiner la feuille de stats du personnage
    def draw_character_stats(self, screen):
        stats_rect = pygame.Rect(self.view_port_width, 0, STATS_WIDTH, self.view_port_height)
        pygame.draw.rect(screen, GRAY, stats_rect)
        font = pygame.font.Font(None, 20)
        pygame.display.set_caption(f"Time: {self.gregorian_calendar} - Dungeon Level: {self.dungeon_level} ({self.level.fullname})")
        height_feet, height_inches = map(int, self.hero.height.split("'"))
        height_meters, height_centimeters = map(round, self.feet_inches_to_m_cm(height_feet, height_inches))
        weapon: Weapon = None
        armor: Armor = None
        for item in self.hero.inventory:
            if not item or isinstance(item, Potion):
                continue
            if item.equipped:
                if isinstance(item, Weapon):
                    weapon = item
                elif isinstance(item, Armor):
                    armor = item
        ranged_weapon_info: str = f' ({self.hero.weapon.range.normal}")' if self.hero.weapon and self.hero.weapon.range else ''
        if not hasattr(self.hero, 'speed'):
            self.hero.speed = 25 if self.hero.race.index in ['dwarf', 'halfling', 'gnome'] else 30
        stat_texts = [
            f"Nom: {self.hero.name}",
            f"Race: {self.hero.race.name}",
            f"Classe: {self.hero.class_type.name}",
            f"Niveau: {self.hero.level}",
            f"XP: {self.hero.xp} / {self.xp_levels[self.hero.level] if self.hero.level < 20 else self.xp_levels[self.hero.level - 1]}",
            f"Santé: {self.hero.hit_points}/{self.hero.max_hit_points} ({self.hero.status if not self.hero.is_dead else 'DEAD'})",
            # damage_dice: str = f'{self.hero.weapon.damage_dice}' if not w.damage_dice.bonus else f'{w.damage_dice.dice} + {w.damage_dice.bonus}'
            f"Attaque (x{self.hero.multi_attacks}): {weapon.damage_dice.dice}{ranged_weapon_info}" if weapon else f"Attaque: 1d2",
            # f"Défense: {self.hero.armor.ac}",
            f"Défense: {self.hero.armor_class}" if armor else "Défense: 10",
            f'Déplacement: {self.hero.speed}"',
            # f"Potions: {self.hero.potions}",
            f"Gold: {self.hero.gold}",
            f"Taille: {height_meters}m{height_centimeters:2d}",
            f"Poids: {round(int(self.hero.weight.split(' ')[0]) * 0.453592)} kg",
            f"Age: {self.hero.age // 52}",
            # Ajoutez d'autres statistiques ici
        ]
        if not hasattr(self.hero, 'st_advantages'): self.hero.st_advantages = []
        if hasattr(self.hero, 'haste_timer') and self.hero.hasted:
            has_st_advantage = lambda x: f' ** ({math.ceil((60 - (time.time() - self.hero.haste_timer)))}" left)' if x in self.hero.st_advantages else ''
        else:
            has_st_advantage = lambda x: f' **' if x in self.hero.st_advantages else ''
        str_effect_timer = f' ({math.ceil((3600 - (time.time() - self.hero.str_effect_timer)) // 60)}\' left)' if self.hero.str_effect_modifier != -1 else ''
        abilities_texts = [
            f"Force: {self.hero.strength}{has_st_advantage('str')}{str_effect_timer}",
            f"Dextérité: {self.hero.dexterity}{has_st_advantage('dex')}",
            f"Constitution: {self.hero.constitution}{has_st_advantage('con')}",
            f"Intelligence: {self.hero.intelligence}{has_st_advantage('int')}",
            f"Sagesse: {self.hero.wisdom}{has_st_advantage('wis')}",
            f"Charisme: {self.hero.charism}{has_st_advantage('cha')}"
        ]
        spells_texts = []
        if self.hero.is_spell_caster:
            slots: str = '/'.join(map(str, self.hero.sc.spell_slots))
            spells_texts.append(f"Spell slots: {self.hero.sc.spell_slots[0] if self.hero.class_type.index == 'warlock' else slots}")
            # known_spells: int = len(self.hero.sc.learned_spells)
            # learned_spells: List[Spell] = [s for s in self.hero.sc.learned_spells]
            # learned_spells.sort(key=lambda s: s.level)
            # for s in learned_spells:
            #     spells_texts.append(f"L{s.level}: {str(s)}")
        for i, text in enumerate(stat_texts):
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (stats_rect[0] + 20, stats_rect[1] + 20 + i * 20)  # Ajuster la position en fonction de la marge
            screen.blit(text_surface, text_rect)
        for i, text in enumerate(abilities_texts):
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (stats_rect[0] + 210, stats_rect[1] + 20 + i * 20)  # Ajuster la position en fonction de la marge
            screen.blit(text_surface, text_rect)
        for i, text in enumerate(spells_texts):
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (stats_rect[0] + 210, stats_rect[1] + 150 + i * 20)  # Ajuster la position en fonction de la marge
            screen.blit(text_surface, text_rect)

    def draw_spell_book(self, screen, sprites):
        # Obtenir les coordonnées de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Stocker les informations de l'info-bulle
        tooltip_text = None

        # learned_spells: List[Spell] = [s for s in self.hero.sc.learned_spells]
        # learned_spells.sort(key=lambda s: s.level)
        max_spell_level: int = max([s.level for s in self.hero.sc.learned_spells])
        for i in range(max_spell_level + 1):
            spells_by_level = [s for s in self.hero.sc.learned_spells if s.level == i]
            for j, spell in enumerate(spells_by_level):
                icon_x = self.view_port_width + 210 + j * 40
                # icon_y = 204 + 70 + i * 40
                icon_y = 170 + i * 40
                # spells_texts.append(f"L{s.level}: {str(s)}")
                image: Surface = sprites[spell.id].convert_alpha()
                put_inlay(image=image, number=spell.level)
                # Define the transparency level (0 to 255, 0 = fully transparent, 255 = fully opaque)
                transparency_level = 255 if self.hero.sc.spell_slots[i - 1] or spell.is_cantrip else 128
                # Set the transparency level of the image
                image.set_alpha(transparency_level)
                screen.blit(image, (icon_x, icon_y))
                # Test if the spell is memorized
                if self.ready_spell and self.ready_spell == spell:
                    # Draw a blue rectangle around the icon
                    pygame.draw.rect(screen, BLUE, (icon_x - 2, icon_y - 2, ICON_SIZE + 2, ICON_SIZE + 2), 2)
                # Vérifier si la souris survole la case
                if pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE).collidepoint(mouse_x, mouse_y):
                    # Stocker la description de l'objet pour l'info-bulle
                    # tooltip_text = f'{spell.name}\n{spell.desc[0]}'
                    tooltip_text = f'{spell.name} ({spell.range}")'

        # Afficher l'info-bulle avec la description du sort
        if tooltip_text:
            draw_tooltip(tooltip_text, screen, mouse_x + 10, mouse_y)

    def draw_inventory(self, screen, sprites):
        # # Afficher le titre de l'inventaire
        # draw_text("Inventaire", font, BLACK, screen, 10, 10)

        # Obtenir les coordonnées de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Stocker les informations de l'info-bulle
        tooltip_text = None

        # Afficher les cases de l'inventaire
        for i, item in enumerate(self.hero.inventory):
            # Calculer les coordonnées de l'image dans la case
            icon_x = self.view_port_width + 10 + (i % 5) * 40
            icon_y = 214 + 70 + (i // 5) * 40
            # Afficher l'icône de l'objet s'il y en a un dans la case
            if item is not None:
                try:
                    image: Surface = sprites[item.id]
                    image.set_colorkey(PINK)
                    screen.blit(image, (icon_x, icon_y))
                    frame_color: tuple = BLUE if isinstance(item, Armor | Weapon) and item.equipped else WHITE
                    pygame.draw.rect(screen, frame_color, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)
                    # Vérifier si la souris survole la case
                    if pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE).collidepoint(mouse_x, mouse_y):
                        # Stocker la description de l'objet pour l'info-bulle
                        if isinstance(item, Armor):
                            tooltip_text = f"{item.name} (AC {item.armor_class['base']})"
                        elif isinstance(item, Weapon):
                            tooltip_text = f"{item.name} ({item.damage_dice.dice})"
                        elif isinstance(item, HealingPotion):
                            tooltip_text = f"{item.name} ({item.hit_dice})"
                        elif isinstance(item, SpeedPotion):
                            tooltip_text = f"{item.name} ({item.duration} s)"
                        elif isinstance(item, StrengthPotion):
                            tooltip_text = f"{item.name} {item.value} ({item.duration // 60} min)"
                        else:
                            tooltip_text = f'{item.name}'
                except KeyError:
                    pass
            # Dessiner un cadre vide pour les cases vides
            else:
                pygame.draw.rect(screen, GRAY, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)

        # Afficher l'info-bulle avec la description de l'objet
        if tooltip_text:
            draw_tooltip(tooltip_text, screen, mouse_x + 10, mouse_y)

    # Fonction pour dessiner le panneau de commande d'actions
    def draw_action_panel(self):
        """ left: La position horizontale du coin supérieur gauche du rectangle.
            top: La position verticale du coin supérieur gauche du rectangle.
            width: La largeur du rectangle.
            height: La hauteur du rectangle.
        """
        # actions_rect = pygame.Rect(0, self.map_height * TILE_SIZE, self.screen_width, ACTIONS_HEIGHT)
        actions_rect = pygame.Rect(0, self.view_port_height, self.screen_width, ACTIONS_HEIGHT)
        left, top, width, height = actions_rect
        pygame.draw.rect(screen, (200, 200, 200), actions_rect)
        # left, top, width, height = MAP_HEIGHT, 0, STATS_WIDTH, 300
        # pygame.draw.rect(screen, (200, 200, 200), (left, top, width, height))  # Fond du panneau d'actions
        font = pygame.font.Font(None, 24)
        action_texts = [
            "Attaquer",
            "Utiliser objet",
            "Sorts",
            "Inventaire"
            # Ajoutez d'autres actions ici
        ]
        action_count = len(action_texts)
        action_height = height // action_count  # Calcul de la hauteur de chaque action
        for i, action_text in enumerate(action_texts):
            text_surface = font.render(action_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.center = (left + width // 2, top + i * action_height + action_height // 2)

            # Définir les marges intérieures
            margin_x = 10
            margin_y = 5
            # Calculer les nouvelles coordonnées du rectangle pour centrer les marges intérieures
            rect = pygame.Rect(left + margin_x, top + i * action_height + margin_y,
                               width - 2 * margin_x, action_height - 2 * margin_y)
            # Dessiner le rectangle avec des coins arrondis autour du texte avec marges intérieures
            pygame.draw.rect(screen, BLACK, rect, 1, border_radius=4)
            screen.blit(text_surface, text_rect)

            # Enregistrer les zones rectangulaires de chaque texte d'action
            self.action_rects[action_text] = rect

    def can_move(self, char: Character, dir: tuple) -> bool:
        dx, dy = dir
        x, y = char.x + dx, char.y + dy
        monster_pos: List[tuple] = [m.pos for m in self.level.monsters]
        return 0 <= x < self.map_width and 0 <= y < self.map_height and (x, y) not in self.level.obstacles + monster_pos

    def update_level(self, dir: int):
        # Chargement de la carte
        self.world_map = self.level.world_map
        self.map_height = len(self.world_map)
        self.map_width = max([len(self.world_map[i]) for i in range(self.map_height)])
        self.walls = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#']
        # Position personnage
        stair: str = '<' if dir > 0 else '>'
        stair_pos = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == stair][0]
        exit_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if
                                       self.world_map[y][x] == '.' and mh_dist((x, y), stair_pos) == 1]
        self.hero.x, self.hero.y = choice(exit_positions)
        self.level.explored_tiles.add((self.hero.x, self.hero.y))
        self.update_visible_tiles()
        # cprint(f'{len(self.level.visible_tiles)} cases visibles')

    def add_to_level(self, item, image, level_sprites) -> bool:
        possible_drop_locations: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.'
                                                and 0 < mh_dist((x, y), self.hero.pos) <= 2 and item not in self.level.items + self.level.monsters]
        if not possible_drop_locations:
            print(f'Unable to drop item {item.name} here. Please move away')
            return False
        item.x, item.y = min(possible_drop_locations, key=lambda p: mh_dist(p, self.hero.pos))
        item.id = max(level_sprites) + 1 if level_sprites else 0
        level_sprites[item.id] = image
        self.level.items.append(item)
        print(f'{item.name} dropped to ({item.pos})!')
        return True

    def remove_from_level(self, item, level_sprites):
        p_idx: int = self.level.items.index(item)
        self.level.items[p_idx] = None
        del level_sprites[item.id]

    def remove_from_inv(self, item, sprites):
        # p_idx: int = self.hero.inventory.index(item)
        p_idx: int = next(i for i, inv_item in enumerate(self.hero.inventory) if inv_item and inv_item.id == item.id)
        self.hero.inventory[p_idx] = None
        del sprites[item.id]

    def add_to_inv(self, item: Equipment, image: Surface, sprites):
        free_slots: List[int] = [i for i, item in enumerate(self.hero.inventory) if not item]
        next_slot: int = min(free_slots)
        item.x, item.y = -1, -1
        item.id = max(sprites) + 1 if sprites else 0
        self.hero.inventory[next_slot] = item
        sprites[item.id] = image

    def open_chest(self, sprites, level_sprites, potions: List[HealingPotion], item_sprites_dir):
        sound_file: str = f'{sound_effects_dir}/Chest Open 1.wav'
        # Load and play the sound effect if provided
        try:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
        print(f'Hero gained a treasure!')
        t: Treasure = [t for t in self.level.treasures if t.pos == self.hero.pos][0]
        self.level.treasures.remove(t)
        del level_sprites[t.id]
        room: Optional[Room] = self.level.room_at(t.pos)
        if room and t == room.treasure:
            # remove treasure from room's property
            room.treasure = None
        self.hero.gold += t.gold
        if t.has_item:
            potions = list(filter(lambda p: game.hero.level >= p.min_level, potions))
            roll = randint(1, 3)
            # roll = 1
            match roll:
                case 1:
                    item: Potion = copy(choice(potions))  # work on a copy to avoid sprite id colliding...
                case 2:
                    if self.hero.prof_armors:
                        item: Armor = request_armor(index_name=choice(self.hero.prof_armors).index)
                    else:
                        item: Potion = copy(choice(potions))  # work on a copy to avoid sprite id colliding...
                case 3:
                    item: Weapon = request_weapon(index_name=choice(self.hero.prof_weapons).index)
                    # item: Weapon = request_weapon('halberd')
            print(f'Hero found a {item.name}!')
            image: Surface = pygame.image.load(f"{item_sprites_dir}/{item.image_name}")
            free_slots: List[int] = [i for i, item in enumerate(self.hero.inventory) if not item]
            if free_slots:
                # Add item to inventory
                self.add_to_inv(item, image, sprites)
            else:
                # Drop item to the ground
                print(f'Inventory is full!')
                self.add_to_level(item, image, level_sprites)

    def use(self, item, sprites):
        if isinstance(item, Potion):
            can_drink: bool = self.hero.drink(item)
            if not can_drink:
                cprint(f'{game.hero.name} is too low level to drink this potion!')
                return
            self.remove_from_inv(item, sprites)
        else:
            cprint(f'Hero cannot use <{item.name}> yet! *Feature not yet implemented*')

    def drop(self, item, image, sprites, level_sprites):
        if isinstance(item, Armor | Weapon) and item.equipped:
            cprint(f'Hero cannot drop <{item.name}> - Please un-equip <{item.name}> first!')
        else:
            self.remove_from_inv(item, sprites)
            self.add_to_level(item, image, level_sprites)

    def in_map(self, x: int, y: int) -> bool:
        return 0 <= x < self.map_width and 0 <= y < self.map_height

    def in_visible_map(self, x, y) -> bool:
        view_x, view_y, view_width, view_height = self.calculate_view_window()
        return 0 <= x < view_width and 0 <= y < view_height

    @property
    def monsters_in_view_range(self, vision_range: int = 10) -> List[Monster]:
        return [m for m in self.level.monsters if mh_dist(self.hero.pos, m.pos) <= vision_range and in_view_range(*self.hero.pos, *m.pos, obstacles=self.level.obstacles)]

    @property
    def cells_in_view_range_from_hero(self, vision_range: int = 10) -> List[tuple]:
        return [(x, y) for x in range(self.level.map_width) for y in range(self.level.map_height) if mh_dist(self.hero.pos, (x, y)) <= vision_range
                and (x, y) not in self.level.obstacles and in_view_range(*self.hero.pos, x, y, obstacles=self.level.obstacles)]

    def update_visible_tiles(self, vision_range: int = 10):
        # self.level.visible_tiles = set()
        view_x, view_y, view_width, view_height = self.calculate_view_window()
        for x in range(view_x, view_x + view_width):
            for y in range(view_y, view_y + view_height):
                if (x, y) in self.level.visible_tiles or dist((x, y), self.hero.pos) > vision_range:
                    continue
                if in_view_range(*self.hero.pos, x, y, obstacles=self.level.obstacles):
                    self.level.visible_tiles.add((x, y))


def mh_dist(p1: tuple, p2: tuple):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def dist(p1, p2) -> float:
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def find_path(start: tuple, end: tuple, carte: List, obstacles: List[tuple]) -> Optional[List[tuple]]:
    dist, pred = parcours_a_star(carte, *start, *end, obstacles)

    path: List[tuple] = []

    if dist != float('inf'):
        path.append(end)
        while end != start:
            end = pred[end]
            path.append(end)

    return path[::-1]


def load_game_assets():
    # Load tiles
    tile_img = pygame.image.load(resource_path('sprites/TilesDungeon/Tile.png'))

    # Load font
    font = pygame.font.SysFont(None, 36)

    # Load inventory items
    armor_names = populate(collection_name='armors', key_name='equipment')
    armors = [request_armor(name) for name in armor_names]
    armors = list(filter(lambda a: a, armors))

    weapon_names = populate(collection_name='weapons', key_name='equipment')
    weapons = [request_weapon(name) for name in weapon_names]
    weapons = list(filter(lambda w: w, weapons))

    # https://listfist.com/list-of-dungeons-dragons-5e-potions
    potions = load_potions_collections()

    return tile_img, font, armors, weapons, potions


def save_character_gamestate(char: Character, _dir: str, gamestate: Game):
    with open(resource_path(f'{_dir}/{char.name}_gamestate.dmp'), 'wb') as f1:
        print(f'Saving {char.name} gamestate...')
        pickle.dump(gamestate, f1)


def load_character_gamestate(char_name: str, _dir: str) -> Optional[Game]:
    gs_filename = f'{_dir}/{char_name}_gamestate.dmp'
    if not os.path.exists(resource_path(gs_filename)):
        return None
    with open(resource_path(gs_filename), 'rb') as f1:
        print(f'Loading {char_name} gamestate...')
        return pickle.load(f1)


def initialize_game(char_name: str, char_dir: str) -> Game:
    # game = Game(character=selected_character, start_level=5)
    saved_game: Game = load_character_gamestate(char_name, gamestate_dir)
    if not saved_game:
        return Game(char_name, char_dir)
    if saved_game.hero.is_dead:
        hero = saved_game.hero
        hero.status = 'OK'
        hero.hit_points = 1
        if not hasattr(hero, 'speed'):
            races: dict = {'dragonborn': 30, 'human': 30, 'elf': 30, 'half-elf': 30, 'dwarf': 25, 'halfling': 25, 'gnome': 25, 'half-orc': 30, 'tiefling': 30}
            hero.speed = races[hero.race.index]
    return saved_game


# III - Réactualisation de l'affichage
def update_display(game, token_images):
    # Rendu
    screen.fill(BLACK)

    # III-0 Dessiner la carte
    map_rect = pygame.Rect(0, 0, game.map_width * TILE_SIZE, game.map_height * TILE_SIZE)
    pygame.draw.rect(screen, WHITE, map_rect)
    game.draw_map(path, screen)

    view_port_tuple = game.calculate_view_window()

    # III-1 Afficher les fontaines de mémorisation de sorts
    for t in game.level.fountains:
        if t.pos not in game.level.visible_tiles:
            continue
        image: Surface = level_sprites[t.id]
        t.draw(screen, image, TILE_SIZE, *view_port_tuple)

    # III-2 Afficher les personnages
    image: Surface = sprites[game.hero.id]
    game.hero.draw(screen, image, TILE_SIZE, *view_port_tuple)

    for monster in game.level.monsters:
        if monster.pos not in game.level.visible_tiles:
            continue
        image: Surface = level_sprites[monster.id]
        # big_image: Surface = pygame.transform.scale(image, (TILE_SIZE * 2, TILE_SIZE * 2))
        monster.draw(screen, image, TILE_SIZE, *view_port_tuple)

        monster_rect = image.get_rect()
        monster_rect.topleft = ((monster.x - view_port_tuple[0]) * TILE_SIZE, (monster.y - view_port_tuple[1]) * TILE_SIZE)
        # screen.blit(image, monster_rect)

        # Draw tooltip with monster name on mouse hover
        if monster_rect.collidepoint(pygame.mouse.get_pos()):
            draw_tooltip(monster.name, screen, *monster_rect.bottomright)

    # III-3 Afficher les trésors
    for t in game.level.treasures:
        if t.pos not in game.level.visible_tiles:
            continue
        image: Surface = level_sprites[t.id]
        t.draw(screen, image, TILE_SIZE, *view_port_tuple)

    # III-4 Afficher ou Ramasser des items laissés au sol
    for item in game.level.items:
        try:
            if item.pos not in game.level.visible_tiles:
                continue
            image: Surface = level_sprites[item.id]
            item_taken: bool = False
            if item.pos == game.hero.pos:
                free_slots: List[int] = [i for i, item in enumerate(game.hero.inventory) if not item]
                if free_slots:
                    # Grab item
                    game.remove_from_level(item, level_sprites)
                    # Add item to inventory
                    game.add_to_inv(item, image, sprites)
                    print(f'Hero gained an item! ({item.name}) #{item.id}')
                    item_taken = True
                # else:
                #     print(f'Cannot take item {item.name}. Inventory is full!')
            if not item_taken:
                image.set_colorkey(PINK)  # Set the pink color as transparent
                item.draw(screen, image, TILE_SIZE, *view_port_tuple)
        except AttributeError:
            pass

    # III-5 Dessiner la feuille de stats du personnage
    game.draw_character_stats(screen)

    # III-6 Dessiner la feuille d'inventaire du personnage
    game.draw_inventory(screen, sprites)

    # III-7 Dessiner le grimoire du personnage
    if game.hero.sc and game.hero.sc.learned_spells:
        game.draw_spell_book(screen, sprites)

    # III-8 Dessiner la mini-map
    game.draw_mini_map(screen)

    # III-9 Dessiner le message de combat
    # game.draw_combat_message(screen)

    # III-10 Afficher les tokens de monstres visibles
    if game.monsters_in_view_range:
        draw_monster_tokens(screen, game, token_images)

    # Mise à jour de l'affichage
    pygame.display.flip()


def display_game_over(game):
    global sprites
    """
    Display the "GAME OVER" message in the Pygame window.
    """
    # Change the sprite's image to the "rip" image
    sprites[game.hero.id] = pygame.image.load(f"{sprites_dir}/rip.png").convert_alpha()
    font = pygame.font.Font(None, 36)
    text = font.render("GAME OVER - Press [Space] to continue", True, (255, 0, 0))
    # text_rect = pygame.Rect((game.map_width * TILE_SIZE) // 2, 0, (game.map_width * TILE_SIZE) // 2, (game.map_height * TILE_SIZE) // 2)
    text_rect = pygame.Rect(game.map_width // 2, game.map_width // 2, SCREEN_WIDTH, SCREEN_HEIGHT)
    screen.blit(text, text_rect)
    pygame.display.flip()

    # Pause the game until the user presses a key
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                # save_character(char=game.hero, _dir=characters_dir)
                paused = False
                # pygame.quit()
                # sys.exit()
            # elif event.type == pygame.KEYDOWN:
            #     paused = False
            #     break


def create_wandering_monsters(game) -> List[Monster]:
    # Random encounter
    new_monsters_list: List[str] = choice(game.level.wandering_monsters)
    new_monsters: List[Monster] = []
    for monster_name in new_monsters_list:
        try:
            monster = request_monster(monster_name.lower().replace(' ', '-'))
            new_monsters.append(monster)
        except FileNotFoundError:
            monster = request_monster_other(monster_name)
            if monster:
                new_monsters.append(monster)
            else:
                cprint(f'unknown monster {Color.RED}{monster_name}{Color.END}!')
    # game.last_combat_round = game.round_no
    # Place monsters
    # reachable_cells = [pos for pos in game.level.visible_tiles if pos not in game.level.obstacles]
    in_view_range_cells: List[tuple] = [pos for pos in game.cells_in_view_range_from_hero if pos != game.hero.pos]
    todo_monsters = [*new_monsters]
    in_view_range_cells.sort(key=lambda c: mh_dist(c, game.hero.pos))
    while in_view_range_cells and todo_monsters:
        cell = in_view_range_cells.pop()
        monster = todo_monsters.pop()
        monster.x, monster.y = cell
    return new_monsters


def main_game_loop(game):
    global level_sprites
    running = True
    return_to_main = False
    game.last_round_time = time.time()
    token_images = game.load_token_images(token_images_dir)
    round_no: int = 1
    if not hasattr(game, 'exit'):
        game.finished = False
    while running and not return_to_main and not game.finished:
        # Calculate the time since the last frame
        current_time = time.time()

        # I - Gestion des actions utilisateur (évènements clavier/souris)
        return_to_main = handle_events(game)

        # II - Gestion des conditions de jeu
        handle_game_conditions(game)

        # III - Réactualisation de l'affichage
        update_display(game, token_images)

        # Limit frame rate
        pygame.time.Clock().tick(FPS)

        # Check if a new round has started
        if game.hero.hit_points > 0:
            if hasattr(game.hero, 'hasted') and game.hero.hasted and current_time - game.hero.haste_timer > 60:
                game.hero.cancel_haste_effect()
            if hasattr(game.hero, 'str_effect_modifier') and game.hero.str_effect_modifier > 0 and current_time - game.hero.str_effect_timer > 3600:
                game.hero.cancel_strength_effect()
            if current_time - game.last_round_time >= ROUND_DURATION:
                game.round_no += 1
                game.timer = 0
                pygame.display.set_caption(f"Time: {game.gregorian_calendar} - Dungeon Level: {game.dungeon_level} ({game.level.fullname})")
                # print(f'Round #{round_no}')
                game.last_round_time = current_time
                # Check if there are monster in range
                monsters_in_range = game.monsters_in_view_range
                if monsters_in_range:
                    # Reset attack mode for monster not in view range
                    for monster in game.level.monsters:
                        if not hasattr(monster, 'speed'):
                            monster.speed = 30
                        if any(m.id == monster.id for m in monsters_in_range):
                            monster.attack_round = 0
                    handle_combat(game=game, monsters=monsters_in_range)
                else:
                    # Gestion des rencontres aléatoires
                    if game.round_no > game.last_combat_round + 10:
                        roll_dice = randint(1, 20)
                        if roll_dice >= 18:
                            new_monsters = create_wandering_monsters(game)
                            game.level.monsters += new_monsters
                            print(f'{len(new_monsters)} new monsters appears! Enjoy :-)')
                            update_level_sprites(monsters=new_monsters, sprites=level_sprites)
                        # else:
                        #     print(f'no wandering monsters detected this time (roll: {roll_dice})...')
                game.target_pos = None
        else:
            cprint(f'{game.hero.name} has been defeated!')
            display_game_over(game)
            update_display(game, token_images)
            running = False


def handle_events(game) -> bool:
    return_to_main_menu: bool = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # save_character(char=game.hero, _dir=characters_dir)
            # save_character_gamestate(char=game.hero, _dir=gamestate_dir, gamestate=game)
            # pygame.quit()
            # sys.exit()
            return_to_main_menu = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_events(game, event)
        elif event.type == pygame.KEYDOWN:
            return_to_main_menu = handle_keyboard_events(game, event)
    return return_to_main_menu


def handle_outside_map_click(game, event):
    # Vérifier si un texte d'action a été cliqué
    for action_text, action_rect in game.action_rects.items():
        if action_rect.collidepoint(event.pos):
            print(f"Action: {action_text}")
    # Vérifier si une case de l'inventaire a été cliquée
    for i, item in enumerate(game.hero.inventory):
        if item is not None:  # pp and isinstance(item, Armor | Weapon):
            icon_x = game.view_port_width + 10 + (i % 5) * 40
            icon_y = 200 + 70 + (i // 5) * 40
            image: Surface = sprites[item.id]
            icon_rect = image.get_rect(topleft=(icon_x, icon_y))
            # cprint(icon_rect)
            if icon_rect.collidepoint(event.pos):
                if event.button == 1:  # Left mouse button
                    if isinstance(item, (Armor, Weapon)):
                        game.hero.equip(item)
                    else:
                        game.use(item, sprites)
                elif event.button == 3:  # Right mouse button
                    game.drop(item, image, sprites, level_sprites)

    # TODO: area of effect
    if game.hero.sc and game.hero.sc.learned_spells:  # and not game.ready_spell:
        # Vérifier si un sort a été sélectionné
        max_spell_level: int = max([s.level for s in game.hero.sc.learned_spells])
        for i in range(max_spell_level + 2):
            spells_by_level = [s for s in game.hero.sc.learned_spells if s.level == i]
            for j, spell in enumerate(spells_by_level):
                icon_x = game.view_port_width + 210 + j * 40
                icon_y = 170 + i * 40
                image: Surface = sprites[spell.id]
                icon_rect = image.get_rect(topleft=(icon_x, icon_y))
                if icon_rect.collidepoint(event.pos):
                    if event.button == 1 and game.hero.can_cast(spell):  # Left mouse button
                        cprint(f'hero pos: {game.hero.pos}')
                        cprint(f'select target for spell <{spell.name}>,  area of effect: {spell.area_of_effect}, range: {spell.range}')
                        frame_color = BLUE if game.hero.sc.spell_slots[i] > 0 else WHITE
                        pygame.draw.rect(screen, frame_color, (icon_x - 2, icon_y - 2, ICON_SIZE + 4, ICON_SIZE + 4), 4)
                        pygame.draw.rect(screen, RED, (icon_x - 2, icon_y - 2, ICON_SIZE + 4, ICON_SIZE + 4), 4)
                        game.ready_spell = spell


def handle_mouse_events(game, event):
    x, y = event.pos[0] // TILE_SIZE, event.pos[1] // TILE_SIZE
    if game.in_visible_map(x, y):
        handle_in_map_click(game, event, x, y)
    else:
        handle_outside_map_click(game, event)


def handle_in_map_click(game, event, x, y):
    view_x, view_y, view_width, view_height = game.calculate_view_window()
    game.target_pos = view_x + x, view_y + y
    if event.button == 3 and game.ready_spell:
        monsters_in_spell_range = [m for m in game.monsters_in_view_range if dist(game.hero.pos, m.pos) <= game.ready_spell.range // UNIT_SIZE]
        if game.ready_spell.damage_type:
            handle_combat(game=game, monsters=monsters_in_spell_range, attack_spell=game.ready_spell)
        else:
            handle_combat(game=game, monsters=monsters_in_spell_range, heal_spell=game.ready_spell)
    elif event.button == 1:
        handle_combat(game=game, monsters=game.monsters_in_view_range)
    game.last_round_time = time.time()


def draw_spell_animation_old(game, monster_pos, duration=2.5, color=(255, 255, 0)):
    start_time = time.time()
    while time.time() - start_time < duration:
        progress = (time.time() - start_time) / duration

        radius = UNIT_SIZE // 2
        # Create a surface for the spell effect
        effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(effect_surface, color + (int(255 * (1 - progress)),), (radius, radius), radius)

        # Calculate the position to draw the effect
        effect_pos = (monster_pos[0] * UNIT_SIZE + UNIT_SIZE // 2 - radius,
                      monster_pos[1] * UNIT_SIZE + UNIT_SIZE // 2 - radius)

        # # Draw the game state
        # game.draw()

        # Draw the spell effect
        screen.blit(effect_surface, effect_pos)

        pygame.display.flip()
        # game.clock.tick(60)


def draw_spell_animation(game, monster_pos, duration=0.5, color=(255, 255, 0)):
    start_time = time.time()
    radius = UNIT_SIZE // 2
    while time.time() - start_time < duration:
        progress = (time.time() - start_time) / duration

        # Create a surface for the spell effect
        effect_surface = pygame.Surface((UNIT_SIZE, UNIT_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(effect_surface, color + (int(255 * (1 - progress)),),
                           (UNIT_SIZE // 2, UNIT_SIZE // 2),
                           int(radius * (1 + progress)))

        # Calculate the position to draw the effect
        effect_pos = (monster_pos[0] * UNIT_SIZE + UNIT_SIZE // 2 - radius,
                      monster_pos[1] * UNIT_SIZE + UNIT_SIZE // 2 - radius)

        # Draw the game state
        # game.draw()

        # Draw the spell effect
        screen.blit(effect_surface, effect_pos)

        pygame.display.flip()
        # game.clock.tick(60)

    # Ensure the final game state is drawn after the animation
    # game.draw()
    # pygame.display.flip()


def handle_right_click_spell_heal(game):
    spell = game.ready_spell
    if game.hero.hit_points == game.hero.max_hit_points:
        cprint(f'{spell} not needed!', color=Color.RED)
        game.ready_spell = None
        return
    best_slot_level: int = game.hero.get_best_slot_level(heal_spell=spell, target=game.hero)
    dd: DamageDice = spell.get_heal_effect(slot_level=best_slot_level, ability_modifier=game.hero.sc.ability_modifier)
    hp_gained = min(dd.roll(), game.hero.max_hit_points - game.hero.hit_points)
    game.hero.hit_points += hp_gained
    game.hero.draw_effect(screen, extract_sprites(f'{effects_images_dir}/flash_freeze.png', columns=8, rows=12), TILE_SIZE, FPS, *game.calculate_view_window(), f'{sound_effects_dir}/magic_words.mp3', 4)
    cprint(f'healed {hp_gained} hp!')
    if not spell.is_cantrip:
        game.hero.update_spell_slots(spell, best_slot_level)
    game.ready_spell = None


def handle_right_click_spell_attack(game):
    monsters_in_range = [m for m in game.monsters_in_view_range if dist(game.hero.pos, m.pos) <= game.ready_spell.range // UNIT_SIZE]
    for monster in monsters_in_range:
        if game.target_pos in (monster.pos, monster.old_pos):
            monster.hit_points -= game.hero.cast_attack(game.ready_spell, monster)
            # Draw the spell animation
            # https://listfist.com/list-of-dungeons-dragons-5e-spells-by-damage?utm_content=cmp-true
            # damage_types = ["acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic", "piercing", "poison", "psychic", "radiant", "slashing", "thunder", "variable"]
            damage_types = {
                "acid": (15, 1, 1),
                "bludgeoning": (4, 4, 1/2),
                "cold": (4, 10, 4),
                "fire": (7, 5, 2),
                "force": None,
                "lightning": (5, 2, 1),
                "necrotic": (6, 5, 1),
                "piercing": (6, 5, 1),
                "poison": (4, 4, 1),
                "psychic": (3, 3, 2),
                "radiant": None,
                "slashing": None,
                "thunder": (6, 6, 4),
                "variable": None
            }
            # cprint(game.ready_spell.damage_type)
            damage_type = damage_types[game.ready_spell.damage_type]
            reduce_ratio = 1
            if isinstance(damage_type, tuple):
                cols, rows, reduce_ratio = damage_type
                sprites_sheet = f'{effects_images_dir}/{game.ready_spell.damage_type}.png'
                sprites: List[Surface] = extract_sprites(sprites_sheet, columns=cols, rows=rows)
            # elif isinstance(damage_type, str):
            #     sprites_sheet = f'{effects_images_dir}/{damage_type}.png'
            #     sprites: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=2)
            else:
                sprites_sheet = f'{effects_images_dir}/flash03.png'
                sprites: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=2)
            view_port_tuple = game.calculate_view_window()
            sound_file: str = f'{sound_effects_dir}/foom_0.mp3'
            monster.draw_effect(screen, sprites, TILE_SIZE, FPS, *view_port_tuple, sound_file, reduce_ratio)
            if monster.hit_points <= 0:
                # cprint(f'{monster.name} at pos {monster.pos} is *KILLED*')
                game.hero.victory(monster=monster, solo_mode=True)
                game.hero.kills.append(monster)
                game.level.monsters.remove(monster)
                room: Optional[Room] = game.level.room_at(monster.pos)
                if room and monster in room.monsters:
                    # remove monster from room's property
                    room.monsters.remove(monster)
        else:
            cprint(f'{monster.name} is out of range!')
    if not game.ready_spell.is_cantrip:
        game.hero.update_spell_slots(game.ready_spell)
    game.ready_spell = None
    game.target_pos = None


def handle_left_click_action(game):
    monsters_in_range = [m for m in game.monsters_in_view_range if game.hero.weapon and dist(game.hero.pos, m.pos) <= game.hero.weapon.range.normal // UNIT_SIZE]
    if monsters_in_range:
        attack_monsters(game, monsters_in_range)
    else:
        move_char(game, char=game.hero, pos=game.target_pos)


def attack_monsters(game, monsters):
    if not hasattr(game, 'target_pos'):
        game.target_pos = None
    for monster in monsters:
        if game.target_pos in (monster.pos, monster.old_pos):
            damage: int = game.hero.attack(monster, cast=False)
            draw_attack_effect(game, monster, damage)
            monster.hit_points -= damage
            if monster.hit_points <= 0:
                # cprint(f'{monster.name} at pos {monster.pos} is *KILLED*')
                game.hero.victory(monster=monster, solo_mode=True)
                game.hero.kills.append(monster)
                if not hasattr(monster, 'speed'):
                    monster.speed = 15
                game.level.monsters.remove(monster)
                rooms: List[Room] = [r for r in game.level.rooms if monster in r.monsters]
                if rooms:
                    # remove monster from room's property
                    rooms[0].monsters.remove(monster)


def attack_monster(game, monster):
    if not hasattr(monster, 'speed'):
        monster.speed = 30
    damage: int = game.hero.attack(monster, cast=False)
    if damage > 0:
        monster.hit_points -= damage
        sound_file: str = f'{sound_effects_dir}/Sword Impact Hit 1.wav'
    else:
        sound_file: str = f'{sound_effects_dir}/Sword Parry 1.wav'
    sound = pygame.mixer.Sound(sound_file)
    sound.play()
    if monster.hit_points <= 0:
        # cprint(f'{monster.name} at pos {monster.pos} is *KILLED*')
        game.hero.victory(monster=monster, solo_mode=True)
        game.hero.kills.append(monster)
        game.level.monsters.remove(monster)
        rooms: List[Room] = [r for r in game.level.rooms if monster in r.monsters]
        if rooms:
            # remove monster from room's property
            rooms[0].monsters.remove(monster)


def display_room_info(game: Game, pos: tuple, room_no: int) -> int:
    room: Room = game.level.room_at(pos)
    if room and room.id != room_no:
        print(f'{Color.GREEN}{room.features}{Color.END}')
        return room.id
    return room_no


def move_char(game: Game, char: Monster | Character, pos: tuple):
    global room_no
    # print(game.round_no)
    if not pos:
        return
    char.old_x, char.old_y = char.x, char.y
    game.target_pos = None
    move_position = char.pos
    if pos in game.level.walkable_tiles:
        current_time = time.time()
        if mh_dist(char.pos, pos) <= 1:
            char.x, char.y = pos
            # game.timer += UNIT_SIZE / game.hero.speed
            room_no = display_room_info(game, char.pos, room_no)
        else:
            if isinstance(char, Character):
                obstacles = [m.pos for m in game.level.monsters]
            else:
                obstacles = [m.pos for m in game.level.monsters if m != char]
            path = find_path(start=char.pos, end=pos, carte=game.level.carte, obstacles=obstacles)
            # cprint(f'path : {path}')
            if path:
                if isinstance(char, Character):
                    char.x, char.y = path[1]
                    sound_file: str = f'{sound_effects_dir}/Dirt Chain Walk 1.wav'
                    sound = pygame.mixer.Sound(sound_file)
                    sound.play()
                else:
                    speed_ratio: int = round(char.speed / game.hero.speed)
                    dist = min(speed_ratio, len(path) - 1)
                    print(f'{char.name} moves to {game.hero.name} at speed {char.speed}"')
                    char.x, char.y = path[dist] if len(path) > 3 else path[1]
                room_no = display_room_info(game, char.pos, room_no)
            else:
                cprint(f'No path found for {char.name}!')
        if isinstance(char, Character):
            game.level.explored_tiles.add(char.pos)
            game.update_visible_tiles()
    else:
        cprint(f'{char.name} cannot move to {pos}!')

    if isinstance(char, Character) and move_position != char.pos:
        sound_file: str = f'{sound_effects_dir}/Dirt Chain Walk 1.wav'
        sound = pygame.mixer.Sound(sound_file)
        sound.play()


def display_available_commands(game):
    # Print available commands in the console
    print("\nAvailable Commands:")
    commands = [
        f"{Color.GREEN}DIRECTIONAL ARROWS{Color.END} = Move up/left/down/right",
        f"{Color.GREEN}LEFT CLICK{Color.END} = Attack monster - Equip/Unequip item - Ready spell",
        f"{Color.GREEN}RIGHT CLICK{Color.END} = Cast spell - Drop Item from inventory",
        f"{Color.GREEN}P{Color.END} = Drink Healing Potion",
        f"{Color.GREEN}S{Color.END} = Drink Speed Potion",
        f"{Color.GREEN}[O|C]{Color.END} = Open/Close Door",
        f"{Color.GREEN}I{Color.END} - Gather position/status of hero",
        f"{Color.GREEN}CMD-S (Apple) - Windows-S (PC) {Color.END} = Save game",
        f"{Color.GREEN}ESC{Color.END} - Leave game (without saving)",
        f"{Color.GREEN}H{Color.END} - Show this help"
    ]

    for command in commands:
        print(command)


def handle_keyboard_events(game, event):
    return_to_main_menu: bool = False
    if event.key == pygame.K_ESCAPE:
        # save_character(char=game.hero, _dir=characters_dir)
        # save_character_gamestate(char=game.hero, _dir=gamestate_dir, gamestate=game)
        return_to_main_menu = True
        # pygame.quit()
        # sys.exit()
    elif event.key == pygame.K_s and (event.mod & pygame.KMOD_META):
        save_character(char=game.hero, _dir=characters_dir)
        save_character_gamestate(char=game.hero, _dir=gamestate_dir, gamestate=game)
        print("Character saved!")
    elif event.key == pygame.K_i:
        room: Optional[Room] = game.level.room_at(game.hero.pos)
        msg: str = f'lurking in room {room.id}' if room else 'wandering in a corridor'
        cprint(f'{game.hero.name} located at {game.hero.pos} *{msg}*')
    elif event.key == pygame.K_h:
        # print available commands
        display_available_commands(game)
    elif event.key in (pygame.K_UP, pygame.K_z):
        move_position = (game.hero.x, game.hero.y - 1)
        monsters = [m for m in game.level.monsters if m.pos == move_position]
        if monsters:
            attack_monster(game=game, monster=monsters[0])
        elif game.can_move(char=game.hero, dir=UP):
            handle_combat(game=game, monsters=game.monsters_in_view_range, move_position=(game.hero.x, game.hero.y - 1))
    elif event.key in (pygame.K_DOWN, pygame.K_s):
        move_position = (game.hero.x, game.hero.y + 1)
        monsters = [m for m in game.level.monsters if m.pos == move_position]
        if monsters:
            attack_monster(game=game, monster=monsters[0])
        elif game.can_move(char=game.hero, dir=DOWN):
            handle_combat(game=game, monsters=game.monsters_in_view_range, move_position=move_position)
    elif event.key in (pygame.K_LEFT, pygame.K_q):
        move_position = (game.hero.x - 1, game.hero.y)
        monsters = [m for m in game.level.monsters if m.pos == move_position]
        if monsters:
            attack_monster(game=game, monster=monsters[0])
        elif game.can_move(char=game.hero, dir=LEFT):
            handle_combat(game=game, monsters=game.monsters_in_view_range, move_position=move_position)
    elif event.key in (pygame.K_RIGHT, pygame.K_d):
        move_position = (game.hero.x + 1, game.hero.y)
        monsters = [m for m in game.level.monsters if m.pos == move_position]
        if monsters:
            attack_monster(game=game, monster=monsters[0])
        elif game.can_move(char=game.hero, dir=RIGHT):
            handle_combat(game=game, monsters=game.monsters_in_view_range, move_position=move_position)
    elif event.key == pygame.K_p:
        handle_healing_potion_use(game)
    elif event.key == pygame.K_s:
        handle_speed_potion_use(game)
    elif event.key == pygame.K_o:
        closed_doors = [door_pos for door_pos, door_open in game.level.doors.items() if mh_dist(door_pos, game.hero.pos) == 1 and not door_open]
        if closed_doors:
            door_pos = closed_doors[0]
            game.level.doors[door_pos] = True
            sound_file: str = f'{sound_effects_dir}/Door Open 1.wav'
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
        else:
            cprint('No closed door found!')
    elif event.key == pygame.K_c:
        open_doors = [door_pos for door_pos, door_open in game.level.doors.items() if mh_dist(door_pos, game.hero.pos) <= 1 and door_open]
        if open_doors:
            door_pos = open_doors[0]
            if any(door_pos == m.pos for m in game.level.monsters):
                cprint('Cannot close door with a monster in it!')
            elif door_pos == game.hero.pos:
                cprint('Cannot close door with the hero in it!')
            else:
                game.level.doors[door_pos] = False
                sound_file: str = f'{sound_effects_dir}/Door Close 1.wav'
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
        else:
            cprint('No open door found!')
    return return_to_main_menu


def handle_healing_potion_use(game):
    if game.hero.healing_potions:
        potion = game.hero.choose_best_potion()
        game.hero.drink(potion)
        # Draw the drink potion animation
        # sprites_sheet = f'{effects_images_dir}/flash_heal.png'
        # sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=10)
        # reduce_ratio = 4
        # sprites_sheet = f'{effects_images_dir}/fireball_blue.png'
        # sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=4, rows=10)
        # sprites_sheet = f'{effects_images_dir}/flash01.png'
        # sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=2)
        # sprites_sheet = f'{effects_images_dir}/flash03.png'
        # sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=2)
        sprites_sheet = f'{effects_images_dir}/flash_freeze.png'
        sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=8, rows=12)
        reduce_ratio = 4
        # sprites_sheet = f'{effects_images_dir}/sphere_blue.png'
        # sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=6, rows=5)
        # sprites_sheet = f'{effects_images_dir}/skull_smoke_green.png'
        # sprites_icons: List[Surface] = extract_sprites(sprites_sheet, columns=19, rows=2)
        view_port_tuple = game.calculate_view_window()
        sound_file: str = f'{sound_effects_dir}/magic_words.mp3'
        game.hero.draw_effect(screen, sprites_icons, TILE_SIZE, FPS, *view_port_tuple, sound_file, reduce_ratio)
        game.remove_from_inv(potion, sprites)
    else:
        cprint('Sorry dude! no healing potion available...')


def handle_speed_potion_use(game):
    if game.hero.speed_potions:
        potion = game.hero.speed_potions[0]
        can_drink: bool = game.hero.drink(potion)
        if not can_drink:
            cprint(f'{game.hero.name} is too low level to drink this potion!')
            return
        game.remove_from_inv(potion, sprites)
    else:
        cprint('Sorry dude! no speed potion available...')


def handle_game_conditions(game):
    handle_treasure_chests(game=game)
    handle_level_changes(game)
    handle_fountains(game)


def get_initiative_order(characters):
    """
    Determine the initiative order of the given characters.

    Args:
        characters (list): A list of characters (either party members or monsters).

    Returns:
        list: A list of characters sorted by their initiative order.
    """
    initiative_rolls = [(char, randint(1, char.abilities.dex)) for char in characters]
    initiative_rolls.sort(key=lambda x: x[1], reverse=True)
    return [char for char, _ in initiative_rolls]


def draw_attack_effect(game: Game, char: [Character|Monster], damage: int):
    if damage > 0:
        sound_file: str = f'{sound_effects_dir}/Sword Impact Hit 1.wav'
        # char_image: Surface = level_sprites[game.hero.id]
        # put_inlay(image=char_image, number=damage, center=False, color=RED)
    else:
        sound_file: str = f'{sound_effects_dir}/Sword Parry 1.wav'
    sprites_sheet = f'{effects_images_dir}/flash04.png'
    sprites: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=2)
    # sound_file: str = f'{sound_effects_dir}/foom_0.mp3'
    view_port_tuple = game.calculate_view_window()
    char.draw_effect(screen, sprites, TILE_SIZE, FPS, *view_port_tuple, sound_file)


def handle_combat(game: Game, monsters: List[Monster], attack_spell: Spell = None, heal_spell: Spell = None, move_position: tuple = None):
    """
        Handle the combat against the monsters.
    :param game:
    :param monsters:
    :param attack_spell:
    :param move_position:
    :return:
    """
    attack_order = get_initiative_order([game.hero] + monsters)
    damage: Optional[int] = None
    for char in attack_order:
        if isinstance(char, Character):
            if char.hit_points > 0:
                # Handle party member's action
                if move_position:
                    if move_position not in game.level.obstacles + game.level.monsters:
                        move_char(game=game, char=game.hero, pos=move_position)
                    else:
                        cprint(f'Path is blocked!')
                elif attack_spell:
                    handle_right_click_spell_attack(game)
                elif heal_spell:
                    handle_right_click_spell_heal(game)
                else:
                    handle_left_click_action(game)
            else:
                break
        else:
            if char.hit_points <= 0 and not any(a.can_use_after_death(char) for a in char.sa):
                if isinstance(char, Monster):
                    game.hero.kills.append(char)
                continue
            # Handle monster's attack
            damage = handle_monster_actions(game, char)
            # game.last_combat_round = game.round_no
    if damage is not None:
        game.hero.hit_points -= damage
        # Draw the damage effect
        draw_attack_effect(game, game.hero, damage)
    game.round_no += 1


def handle_monster_actions(game: Game, monster: Monster) -> Optional[int]:
    # print(monster.name)
    # Precalculate ready spells & special attacks
    range = mh_dist(game.hero.pos, monster.pos) * UNIT_SIZE
    available_spells: List[Spell] = []
    if monster.is_spell_caster:
        cantric_spells: List[Spell] = [s for s in monster.sc.learned_spells if not s.level]
        slot_spells: List[Spell] = [s for s in monster.sc.learned_spells if s.level and monster.sc.spell_slots[s.level - 1] > 0]
        castable_spells: List[Spell] = cantric_spells + slot_spells
        available_spells = list(filter(lambda s: s.area_of_effect.size >= UNIT_SIZE * range, castable_spells))
    # Check recharge status
    if monster.sa and monster.attack_round > 0:  # ou 1? (à vérifier)
        for special_attack in monster.sa:
            # print(special_attack)
            if special_attack.recharge_on_roll:
                special_attack.ready = special_attack.recharge_success
    try:
        available_special_attacks: List[SpecialAbility] = list(filter(lambda a: a.ready and a.area_of_effect.size >= UNIT_SIZE, monster.sa))
    except Exception as e:
        available_special_attacks = []
        print(e)

    monster.attack_round += 1
    damage: Optional[int] = None
    # Some monsters may have special attack after death
    after_death_special_attacks = list(filter(lambda a: a.can_use_after_death(monster), available_special_attacks))
    if monster.hit_points <= 0 and after_death_special_attacks:
        print("death", monster.name, after_death_special_attacks)
        special_attack: SpecialAbility = max(after_death_special_attacks, key=lambda a: sum([damage.dd.score(success_type=a.dc_success) for damage in a.damages]))
        cprint(f'{color.GREEN}{monster.name}{color.END} launches ** {special_attack.name.upper()} ** on {game.hero.name}!')
        damage = monster.special_attack(game.hero, special_attack)
    else:
        available_special_attacks = list(filter(lambda a: not a.can_use_after_death(monster), available_special_attacks))
        if available_spells:
            # print(f'{monster.name} - old spell slots: {monster.sc.spell_slots}')
            attack_spell: Spell = max(available_spells, key=lambda s: s.level)
            damage = monster.cast_attack(game.hero, attack_spell)
            # print(f'{monster.name} - new spell slots: {monster.sc.spell_slots}')
        elif available_special_attacks:
            special_attack: SpecialAbility = max(available_special_attacks, key=lambda a: sum([damage.dd.score(success_type=a.dc_success) for damage in a.damages]))
            # cprint(special_attack)
            cprint(f'{color.GREEN}{monster.name}{color.END} launches ** {special_attack.name.upper()} ** on {game.hero.name}!')
            # cprint('target chars: ' + '/'.join([c.name for c in target_chars]))
            damage = monster.special_attack(game.hero, special_attack)
        elif mh_dist(monster.pos, game.hero.pos) <= 1:
            melee_attacks: List[Action] = list(filter(lambda a: a.type in [ActionType.MELEE, ActionType.MIXED], monster.actions))
            # Monster attacks the hero
            damage = monster.attack(character=game.hero, actions=melee_attacks, distance=range)
        else:
            ranged_attacks: List[Action] = list(filter(lambda a: a.type in [ActionType.RANGED, ActionType.MIXED]
                                                                     and ((a.long_range and range <= a.long_range) or range <= a.normal_range), monster.actions))
            if ranged_attacks:
                damage = monster.attack(character=game.hero, actions=ranged_attacks, distance=range)
            else:
                # Monster moves towards the hero
                if not hasattr(monster, 'speed'):
                    monster.speed = 30
                move_char(game=game, char=monster, pos=game.hero.pos)
    return damage


def handle_treasure_chests(game):
    if any(t.pos == game.hero.pos for t in game.level.treasures):
        game.open_chest(sprites, level_sprites, potions=potions, item_sprites_dir=item_sprites_dir)


def handle_fountains(game):
    if any(f.pos == game.hero.pos for f in game.level.fountains):
        char = game.hero
        sound_file: str = f'{sound_effects_dir}/magic_words.mp3'
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
        if char.class_type.can_cast:
            if char.sc.spell_slots != char.class_type.spell_slots[char.level]:
                print(f'{char.name} has memorized all his spells')
                char.sc.spell_slots = copy(char.class_type.spell_slots[char.level])
        if char.level < len(game.xp_levels) and char.xp >= game.xp_levels[char.level]:
            if char.class_type.can_cast:
                spell_names: List[str] = populate(collection_name='spells', key_name='results')
                all_spells: List[Spell] = [request_spell(name) for name in spell_names]
                class_tome_spells = [s for s in all_spells if s is not None and char.class_type.index in s.allowed_classes]
                display_msg, new_spells = char.gain_level(tome_spells=class_tome_spells)
                if new_spells:
                    for spell in new_spells:
                        image = pygame.image.load(f"{spell_sprites_dir}/{spell.school}.png")
                        spell.id = max(sprites) + 1 if sprites else 1
                        sprites[spell.id] = pygame.transform.scale(image, (ICON_SIZE, ICON_SIZE))  # Resize the image
            else:
                display_msg, _ = char.gain_level()
            print(display_msg)
        save_character(char, _dir=characters_dir)


def handle_level_changes(game):
    global screen
    global level_sprites
    match game.world_map[game.hero.y][game.hero.x]:
        case '>':
            if game.level.level_no == MAX_LEVELS:
                print('You have reached the end of the dungeon!')
                response: str = read(['y', 'Y', 'n', 'N'], 'Do you want to return to the Castle? (y/n)')
                moves: List[tuple] = [p for p in game.level.walkable_tiles if mh_dist(p, game.hero.pos) == 1 and p not in game.level.obstacles]
                move_char(game, game.hero, choice(moves))
                if response in ['y', 'Y']:
                    game.finished = True
                    print(f"{Color.GREEN}Congratulations! You have vanquished {Color.RED}{len(game.hero.kills)}{Color.END} monsters and can now return to a normal life :-){Color.END}")
                    save_character(char=game.hero, _dir=characters_dir)
                    save_character_gamestate(char=game.hero, _dir=gamestate_dir, gamestate=game)
                    print("Returning to Castle :-)")
            else:
                print(f'Hero found downstairs! going to Level {game.dungeon_level + 1}')
                game.dungeon_level += 1
                # Uncomment following lines to reset level
                # if game.dungeon_level == 5:
                #     # reset level
                #     print(f'resetting level {game.dungeon_level}')
                #     game.level = Level(level_no=game.dungeon_level)
                #     game.levels[game.dungeon_level - 1] = game.level
                #     game.level.load(hero=game.hero)
                if game.dungeon_level > len(game.levels):
                    game.level = Level(level_no=game.dungeon_level)
                    game.levels.append(game.level)
                    game.level.load(hero=game.hero)
                else:
                    game.level = game.levels[game.dungeon_level - 1]
                game.update_level(dir=1)
                screen = pygame.display.set_mode((game.screen_width, game.screen_height))
                level_sprites = create_level_sprites(game.level)
        case '<':
            print(f'Hero found upstairs!')
            game.dungeon_level -= 1
            game.level = game.levels[game.dungeon_level - 1]  # if game.dungeon_level in game.levels else Level(level_no=game.dungeon_level - 1)
            game.update_level(dir=-1)
            screen = pygame.display.set_mode((game.screen_width, game.screen_height))
            level_sprites = create_level_sprites(game.level)


def extract_sprites(spritesheet_path, columns, rows) -> List[Surface]:
    # Load the spritesheet
    spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

    # Calculate the size of each sprite
    sheet_width, sheet_height = spritesheet.get_size()
    sprite_width = sheet_width // columns
    sprite_height = sheet_height // rows

    sprites: List[Surface] = []
    num_sprites: int = columns * rows

    for i in range(num_sprites):
        # Calculate the position of the sprite in the sheet
        row = i // columns
        col = i % columns

        # Create a new surface for the sprite
        sprite_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)

        # offset_x = col * sprite_width + (sprite_width - sprite_size) // 2
        # offset_y = row * sprite_height + (sprite_height - sprite_size) // 2

        # Copy the sprite from the sheet to the new surface
        sprite_surface.blit(spritesheet, (0, 0),
                            (col * sprite_width, row * sprite_height,
                             sprite_width, sprite_height))

        sprites.append(sprite_surface)

    return sprites


def create_sprites(hero: Character) -> dict[int, pygame.Surface]:
    hero.id = 1
    s: dict[int, pygame.Surface] = {hero.id: pygame.image.load(f"{char_sprites_dir}/{game.hero.image_name}").convert_alpha()}
    # print(hero.name, game.hero.id, id(sprites[hero.id]))
    if hero.is_spell_caster:
        # Afficher grimoire
        for spell in hero.sc.learned_spells:
            image = pygame.image.load(f"{spell_sprites_dir}/{spell.school}.png")
            spell.id = max(s) + 1 if s else 1
            s[spell.id] = pygame.transform.scale(image, (ICON_SIZE, ICON_SIZE))  # Resize the image
            # print(spell.name, spell.id, id(s[spell.id]))
    for i, item in enumerate(hero.inventory):
        if item:
            item.id = max(s) + 1 if s else 1
            s[item.id] = pygame.image.load(f"{item_sprites_dir}/{item.image_name}").convert_alpha()
            # print(item.name, item.id, id(s[item.id]))
    return s


def update_level_sprites(monsters: List[Monster], sprites: dict[int, pygame.Surface]):
    for m in monsters:
        m.id = max(sprites) + 1 if sprites else 1
        try:
            original_image = pygame.image.load(f"{char_sprites_dir}/{m.image_name}").convert_alpha()
        except FileNotFoundError:
            original_image = pygame.image.load(f"{sprites_dir}/enemy.png").convert_alpha()
        sprites[m.id] = pygame.transform.scale(original_image, (32, 32))


def create_level_sprites(level: Level) -> dict[int, pygame.Surface]:
    s = {}
    # Chargement du sprite de la fontaine
    f = level.fountains[0]
    f.id = 1
    s[f.id] = pygame.image.load(f"{sprites_dir}/{f.image_name}").convert_alpha()
    # Chargement des sprites de monstres
    for m in level.monsters:
        m.id = max(s) + 1 if s else 1
        try:
            original_image = pygame.image.load(f"{char_sprites_dir}/{m.image_name}").convert_alpha()
        except FileNotFoundError:
            original_image = pygame.image.load(f"{sprites_dir}/enemy.png").convert_alpha()
            # monster_name: str = choice(['monster_orog.png', 'monster_orog_2.png'])
            # original_image = pygame.image.load(f"{char_sprites_dir}/{monster_name}").convert_alpha()
        s[m.id] = pygame.transform.scale(original_image, (32, 32))
    # Chargement des sprites de trésors
    for t in level.treasures:
        t.id = max(s) + 1 if s else 1
        s[t.id] = pygame.image.load(f"{sprites_dir}/{t.image_name}").convert_alpha()
    for item in level.items:
        if item:
            item.id = max(s) + 1 if s else 1
            s[item.id] = pygame.image.load(f"{item_sprites_dir}/{item.image_name}").convert_alpha()
    return s


def draw_monster_tokens(screen, game, token_images):
    # Calculate the position for the token area
    token_area_x = SCREEN_WIDTH - 250
    token_area_y = 20

    # font = pygame.font.SysFont(None, 60)
    font = pygame.font.SysFont(None, 30)

    # Draw visible monsters' tokens
    column_height = 0
    column_width = 0
    for i, monster in enumerate(game.monsters_in_view_range):
        # token_image = game.token_images.get(monster.name.lower().replace(" ", "_"))
        token_image = token_images.get(monster.name)
        if token_image:
            token_rect = token_image.get_rect()
            # token_rect.topleft = (token_area_x, token_area_y)
            if i % 2 == 0:  # First column
                token_rect.topleft = (token_area_x, token_area_y + column_height)
                column_height += token_rect.height + 10
            else:  # Second column
                token_rect.topleft = (token_area_x + token_rect.width + 10, token_area_y + column_width)
                column_width += token_rect.height + 10

            screen.blit(token_image, token_rect)

            # Draw current hit points in the center of the token
            if not hasattr(monster, 'max_hit_points'):
                monster.max_hit_points = monster.hit_points
            text_color = GREEN if monster.hit_points == monster.max_hit_points else ORANGE if monster.hit_points > 0.25 * monster.max_hit_points else RED
            hp_text = font.render(str(monster.hit_points), True, text_color)
            # hp_text.set_alpha(100)  # Set transparency (0 is fully transparent, 255 is opaque)
            hp_rect = hp_text.get_rect()
            hp_rect.center = token_rect.bottomright[0] - 5, token_rect.bottomright[1] - 5
            screen.blit(hp_text, hp_rect)

            # Draw tooltip with monster name on mouse hover
            if token_rect.collidepoint(pygame.mouse.get_pos()):
                draw_tooltip(monster.name, screen, *token_rect.bottomleft)

            # token_area_y += token_rect.height + 10  # Adjust the position for the next token


def run(character_name: str = 'Brottor'):
    global screen, level_sprites, sprites, game, room_no
    global tile_img, font, armors, weapons, potions
    global path, characters_dir, gamestate_dir, sprites_dir, char_sprites_dir
    global item_sprites_dir, spell_sprites_dir, effects_images_dir, sound_effects_dir, token_images_dir
    path = os.path.dirname(__file__)
    # abspath = os.path.abspath(path)
    # characters_dir = f'{abspath}/gameState/characters'
    # gamestate_dir = f'{abspath}/gameState/pygame'
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'
    sprites_dir = resource_path('sprites')
    char_sprites_dir = f"{sprites_dir}/rpgcharacterspack"
    item_sprites_dir = f"{sprites_dir}/Items"
    spell_sprites_dir = f"{sprites_dir}/schools"
    effects_images_dir = resource_path('sprites/effects')
    sound_effects_dir = resource_path('sounds')
    token_images_dir = resource_path('images/monsters/tokens')
    room_no = 0  # memorize last visited room number

    # Initialisation de Pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Chargement des assets
    tile_img, font, armors, weapons, potions = load_game_assets()

    # Chargement du jeu en cours

    game = initialize_game(character_name, characters_dir)
    if not any((x, y) for y in range(game.map_height) for x in range(game.map_width) if game.world_map[y][x] == '>'):
        print('No downstairs found! Creating one')
        x, y = choice(game.level.walkable_tiles)
        game.level.world_map[y][x] = '>'

    print(f'dungeon Level: {game.level.level_no} - name = {game.level.fullname}')
    print(f'Hero: #{game.hero.id} {game.hero.name} - {game.hero.race} - {game.hero.class_type.name}')
    level_sprites = create_level_sprites(game.level)
    sprites = create_sprites(hero=game.hero)

    main_game_loop(game)


if __name__ == "__main__":
    # Récupération du personnage choisi par l'utilisateur
    # character_name = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'
    try:
        run()
    finally:
        pygame.mixer.quit()
        pygame.quit()  # Clean up all pygame modules
