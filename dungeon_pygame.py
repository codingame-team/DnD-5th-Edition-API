# Définition des constantes pour la mise en page
# SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
from __future__ import annotations

import os
import sys
import time
from copy import copy
from random import choice, randint
from typing import List, Optional

import pygame
from pygame import Surface

from algo.brehensam import in_view_range
from algo.lee import parcours_largeur
from dao_classes import Character, Level, Spell, Weapon, Armor, HealingPotion, Monster, Equipment, Treasure, Sprite
from main import get_roster, save_character, load_xp_levels
from populate_functions import populate, request_armor, request_weapon, request_monster, request_spell
from populate_rpg_functions import load_potions_collections
from tools.common import cprint

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
STATS_WIDTH, ACTIONS_HEIGHT = 600, 200
STATS_HEIGHT = 250

# Paramètres de la map
UNIT_SIZE = 5

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

# Directions
UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

ROUND_DURATION = 3  # Duration of a round in seconds


def put_inlay(image: Surface, number: int):
    # Police pour le texte
    font = pygame.font.Font(None, 18)

    # Créer la surface du texte
    text_surface = font.render(str(number), True, WHITE)

    # Définir la position du texte sur l'image (par exemple, en bas à droite)
    text_rect = text_surface.get_rect()
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


class Level:
    level_no: int
    world_map: List[List[int]]
    map_height: int
    map_width: int
    monsters: List[Monster]
    treasures: dict
    fountains: List[Sprite]
    items: List[Equipment | HealingPotion]
    sprites: dict

    def __init__(self, level_no: int):
        self.level_no = level_no
        self.world_map = self.load_maze(level=level_no)
        self.map_height = len(self.world_map)
        self.map_width = max([len(self.world_map[i]) for i in range(self.map_height)])
        self.sprites = {}
        self.items = []
        self.fountains = []

    def load_maze(self, level: int) -> List:
        """
        Charge le labyrinthe depuis le fichier level.txt
        nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
        Valeur de retour :
        - une liste avec les données du labyrinthe
        """
        try:
            with open(f"{path}/maze/level_{level}.txt", newline='') as fic:
                data = fic.readlines()
        except IOError:
            print("Impossible de lire le fichier {}.txt".format(level))
            exit(1)
        for i in range(len(data)):
            data[i] = data[i].strip()
        width = max([len(data[i]) for i in range(len(data))])
        for i in range(len(data)):
            data[i] = "{:{g}}".format(data[i], g=f"^{width}")
        return data

    def load(self, hero: Character):
        """
            Chargement des entités du donjon (monstres et trésors)
        :param level:
        :return:
        """
        # photo_exit: PhotoImage = PhotoImage(file=f"{path}/sprites/exit.png")

        # rating = lambda m: m.cr < (hero.level / 4 if hero.level < 5 else hero.level / 2)
        monster_names: List[str] = ['ankheg', 'baboon', 'bat', 'crab', 'ghost', 'goblin', 'harpy', 'lizard', 'mimic', 'owl', 'rat', 'skeleton', 'spider', 'wolf']
        monster_candidates: List[Monster] = [request_monster(name) for name in monster_names]
        monster_candidates = list(filter(None, monster_candidates))
        monster_candidates = list(filter(lambda m: m.challenge_rating < self.level_no, monster_candidates))
        allowed_monster_names: list[str] = [m.name for m in monster_candidates]

        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.' and (x, y) != hero.pos]
        # Placement des fontaines sur la carte
        if hero.is_spell_caster:
            # has_fountain: bool = randint(1, 3) == 2
            has_fountain: bool = True
            if has_fountain:
                f_x, f_y = choice(open_positions)
                f: Sprite = Sprite(id=(max(self.sprites) + 1 if self.sprites else 0), x=f_x, y=f_y, old_x=f_x, old_y=f_y, image_name='fountain.png')
                self.fountains.append(f)
                open_positions.remove((f_x, f_y))
                self.sprites[f.id] = pygame.image.load(f"{sprites_dir}/{f.image_name}").convert_alpha()
        # Placement des monstres sur la carte
        self.monsters = [request_monster(choice(allowed_monster_names).lower()) for _ in range(randint(1, 5))]
        for m in self.monsters:
            m.x, m.y = choice(open_positions)
            m.id = max(self.sprites) + 1 if self.sprites else 0
            open_positions.remove((m.x, m.y))
            self.sprites[m.id] = pygame.image.load(f"{char_sprites_dir}/{m.image_name}").convert_alpha()

        #  Placement des trésors sur la carte
        self.treasures: List[Treasure] = []
        for _ in range(randint(1, 5)):
            gold: int = randint(50, 300) * self.level_no
            # has_item: bool = randint(1, 3) == 2
            has_item: bool = True
            t_x, t_y = choice(open_positions)
            t: Treasure = Treasure(id=(max(self.sprites) + 1 if self.sprites else 0), x=t_x, y=t_y, old_x=t_x, old_y=t_y, image_name='treasure.png', gold=gold, has_item=has_item)
            self.treasures.append(t)
            self.sprites[t.id] = pygame.image.load(f"{sprites_dir}/{t.image_name}").convert_alpha()

    @property
    def walkable_tiles(self):
        return [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] in ['.', '<', '>']]

    @property
    def obstacles(self):
        return [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#']

    @property
    def carte(self) -> List[List[int]]:
        obstacles = [*self.obstacles]  # + [(e.x, e.y) for e in enemies if e != enemy]
        carte = [[1] * self.map_width for _ in range(self.map_height)]
        for y in range(self.map_height):
            for x in range(self.map_width):
                if (x, y) in obstacles:
                    carte[y][x] = 0
        return carte


class Game:
    screen: Surface
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
    sprites: dict
    levels: List[Level]
    level: Level
    school_images: dict
    xp_levels: List[int]
    ready_spell: Spell = None
    target_pos: tuple = None
    last_round_time: float = 0


    def __init__(self, character: Character, actions_panel=False):
        self.last_round_time = time.time()
        # Chargement de la carte
        self.actions_panel = actions_panel
        self.dungeon_level = 1
        self.level = Level(1)
        self.levels = [self.level]
        self.world_map = self.level.world_map
        self.map_height = self.level.map_height
        self.map_width = self.level.map_width
        self.walls = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#']
        # Redimensionnement de l'écran
        self.view_port_width = min(self.map_width * TILE_SIZE, SCREEN_WIDTH - STATS_WIDTH)
        self.view_port_height = min(self.map_height * TILE_SIZE, SCREEN_HEIGHT - ACTIONS_HEIGHT)
        self.screen_width = self.view_port_width + STATS_WIDTH
        self.screen_height = self.view_port_height + ACTIONS_HEIGHT if actions_panel else self.view_port_height
        self.action_rects = {}
        self.sprites = {}
        # Création de la fenêtre
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        # Initialisation du personnage
        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.']
        hero_x, hero_y = choice(open_positions)
        open_positions.remove((hero_x, hero_y))
        self.hero = character
        self.sprites[self.hero.id] = pygame.image.load(f"{char_sprites_dir}/{self.hero.image_name}").convert_alpha()
        print(self.hero.name, self.hero.id, id(self.sprites[self.hero.id]))
        if self.hero.is_spell_caster:
            # Afficher grimoire
            for s in self.hero.sc.learned_spells:
                image = pygame.image.load(f"{spell_sprites_dir}/{s.school}.png")
                s.id = max(self.sprites) + 1
                self.sprites[s.id] = pygame.transform.scale(image, (ICON_SIZE, ICON_SIZE))  # Resize the image
                print(s.name, s.id, id(self.sprites[s.id]))
        for item in self.hero.inventory:
            if item:
                self.sprites[item.id] = pygame.image.load(f"{item_sprites_dir}/{item.image_name}").convert_alpha()
        self.hero.x, self.hero.y = hero_x, hero_y
        self.level.load(hero=self.hero)
        """ Load XP Levels """
        self.xp_levels = load_xp_levels()

    # Define a method to calculate the view window
    def calculate_view_window(self):
        view_width = self.view_port_width // TILE_SIZE
        view_height = self.view_port_height // TILE_SIZE
        viewport_x = max(0, min(self.hero.x - view_width // 2, self.map_width - view_width))
        viewport_y = max(0, min(self.hero.y - view_height // 2, self.map_height - view_height))
        return viewport_x, viewport_y, view_width, view_height

    def draw_map(self):
        photo_wall = pygame.image.load(f"{path}/sprites/TilesDungeon/Wall.png")
        photo_downstairs = pygame.image.load(f"{path}/sprites/DownStairs.png")
        photo_upstairs = pygame.image.load(f"{path}/sprites/UpStairs.png")

        # Calculate the view window
        view_x, view_y, view_width, view_height = self.calculate_view_window()

        # Draw only the portion of the map that falls within the view window
        for row in range(view_y, view_y + view_height):
            for col in range(view_x, view_x + view_width):
                tile_x, tile_y = (col - view_x) * TILE_SIZE, (row - view_y) * TILE_SIZE
                if self.world_map[row][col] == '#':
                    self.screen.blit(photo_wall, (tile_x, tile_y))
                elif self.world_map[row][col] == '<':
                    self.screen.blit(photo_upstairs, (tile_x, tile_y))
                elif self.world_map[row][col] == '>':
                    self.screen.blit(photo_downstairs, (tile_x, tile_y))

    def feet_inches_to_m_cm(self, height_feet: int, height_inches: int):
        total_inches = height_feet * 12 + height_inches
        height_meters = total_inches * 2.54 / 100
        height_centimeters = total_inches * 2.54 % 100
        return height_meters, height_centimeters

    # Fonction pour dessiner la feuille de stats du personnage
    def draw_character_stats(self):
        stats_rect = pygame.Rect(self.view_port_width, 0, STATS_WIDTH, self.view_port_height)
        pygame.draw.rect(self.screen, GRAY, stats_rect)
        font = pygame.font.Font(None, 20)
        pygame.display.set_caption(f"Dungeon Level: {self.dungeon_level}")
        height_feet, height_inches = map(int, self.hero.height.split("'"))
        height_meters, height_centimeters = map(round, self.feet_inches_to_m_cm(height_feet, height_inches))
        weapon: Weapon = None
        armor: Armor = None
        for item in self.hero.inventory:
            if not item or isinstance(item, HealingPotion):
                continue
            if item.equipped:
                if isinstance(item, Weapon):
                    weapon = item
                elif isinstance(item, Armor):
                    armor = item
        ranged_weapon_info: str = f' ({self.hero.weapon.range.normal}")' if self.hero.weapon and self.hero.weapon.range else ''
        stat_texts = [
            f"Nom: {self.hero.name}",
            f"Race: {self.hero.race.name}",
            f"Classe: {self.hero.class_type.name}",
            f"Niveau: {self.hero.level}",
            f"XP: {self.hero.xp} / {self.xp_levels[self.hero.level]}",
            f"Santé: {self.hero.hit_points}/{self.hero.max_hit_points} ({self.hero.get_status})",
            # damage_dice: str = f'{self.hero.weapon.damage_dice}' if not w.damage_dice.bonus else f'{w.damage_dice.dice} + {w.damage_dice.bonus}'
            f"Attaque: {weapon.damage_dice.dice}{ranged_weapon_info}" if weapon else f"Attaque: 1d2",
            # f"Défense: {self.hero.armor.ac}",
            f"Défense: {self.hero.armor_class}" if armor else "Défense: 10",
            # f"Potions: {self.hero.potions}",
            f"Gold: {self.hero.gold}",
            f"Taille: {height_meters}m{height_centimeters:2d}",
            f"Poids: {round(int(self.hero.weight.split(' ')[0]) * 0.453592)} kg",
            f"Age: {self.hero.age // 52}",
            # Ajoutez d'autres statistiques ici
        ]
        abilities_texts = [
            f"Force: {self.hero.strength}",
            f"Dextérité: {self.hero.dexterity}",
            f"Constitution: {self.hero.constitution}",
            f"Intelligence: {self.hero.intelligence}",
            f"Sagesse: {self.hero.wisdom}",
            f"Charisme: {self.hero.charism}"
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
            self.screen.blit(text_surface, text_rect)
        for i, text in enumerate(abilities_texts):
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (stats_rect[0] + 210, stats_rect[1] + 20 + i * 20)  # Ajuster la position en fonction de la marge
            self.screen.blit(text_surface, text_rect)
        for i, text in enumerate(spells_texts):
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (stats_rect[0] + 210, stats_rect[1] + 150 + i * 20)  # Ajuster la position en fonction de la marge
            self.screen.blit(text_surface, text_rect)

    def draw_spell_book(self):
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
                image: Surface = self.sprites[spell.id].convert_alpha()
                put_inlay(image=image, number=spell.level)
                # Define the transparency level (0 to 255, 0 = fully transparent, 255 = fully opaque)
                transparency_level = 255 if self.hero.sc.spell_slots[i - 1] or spell.is_cantrip else 128
                # Set the transparency level of the image
                image.set_alpha(transparency_level)
                self.screen.blit(image, (icon_x, icon_y))
                # Test if the spell is memorized
                if self.ready_spell and game.ready_spell == spell:
                    # Draw a blue rectangle around the icon
                    pygame.draw.rect(self.screen, BLUE, (icon_x - 2, icon_y - 2, ICON_SIZE + 2, ICON_SIZE + 2), 2)
                # Vérifier si la souris survole la case
                if pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE).collidepoint(mouse_x, mouse_y):
                    # Stocker la description de l'objet pour l'info-bulle
                    # tooltip_text = f'{spell.name}\n{spell.desc[0]}'
                    tooltip_text = f'{spell.name} ({spell.range}")'

        # Afficher l'info-bulle avec la description du sort
        if tooltip_text:
            draw_tooltip(tooltip_text, self.screen, mouse_x + 10, mouse_y)

    def draw_inventory(self):
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
            icon_y = 204 + 70 + (i // 5) * 40
            # Afficher l'icône de l'objet s'il y en a un dans la case
            if item is not None:
                try:
                    image: Surface = self.sprites[item.id]
                    image.set_colorkey(PINK)
                    self.screen.blit(image, (icon_x, icon_y))
                    frame_color: tuple = BLUE if isinstance(item, Armor | Weapon) and item.equipped else WHITE
                    pygame.draw.rect(self.screen, frame_color, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)
                    # Vérifier si la souris survole la case
                    if pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE).collidepoint(mouse_x, mouse_y):
                        # Stocker la description de l'objet pour l'info-bulle
                        if isinstance(item, Armor):
                            tooltip_text = f"{item.name} (AC {item.armor_class['base']})"
                        elif isinstance(item, Weapon):
                            tooltip_text = f"{item.name} ({item.damage_dice.dice})"
                        elif isinstance(item, HealingPotion):
                            tooltip_text = f"{item.name} ({item.hit_dice})"
                        else:
                            tooltip_text = f'{item.name}'
                except KeyError:
                    pass
            # Dessiner un cadre vide pour les cases vides
            else:
                pygame.draw.rect(self.screen, GRAY, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)

        # Afficher l'info-bulle avec la description de l'objet
        if tooltip_text:
            draw_tooltip(tooltip_text, self.screen, mouse_x + 10, mouse_y)

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
        pygame.draw.rect(self.screen, (200, 200, 200), actions_rect)
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
            pygame.draw.rect(self.screen, BLACK, rect, 1, border_radius=4)
            self.screen.blit(text_surface, text_rect)

            # Enregistrer les zones rectangulaires de chaque texte d'action
            self.action_rects[action_text] = rect

    def can_move(self, char: Character | Monster, dir: tuple) -> bool:
        dx, dy = dir
        x, y = char.x + dx, char.y + dy
        return 0 <= x < self.map_width and 0 <= y < self.map_height and self.world_map[y][x] != '#'

    def update_level(self, dir: int):
        # Chargement de la carte
        self.world_map = self.level.world_map
        self.map_height = len(self.world_map)
        self.map_width = max([len(self.world_map[i]) for i in range(self.map_height)])
        self.walls = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#']
        # Redimensionnement de l'écran
        self.view_port_width = min(self.map_width * TILE_SIZE, SCREEN_WIDTH - STATS_WIDTH)
        self.view_port_height = min(self.map_height * TILE_SIZE, SCREEN_HEIGHT - ACTIONS_HEIGHT) if self.actions_panel else self.map_height * TILE_SIZE
        self.screen_width = self.view_port_width + STATS_WIDTH
        self.screen_height = self.view_port_height + ACTIONS_HEIGHT if self.actions_panel else self.view_port_height
        # # Redimensionnement de l'écran
        # self.screen_width = TILE_SIZE * self.map_width + STATS_WIDTH
        # self.screen_height = TILE_SIZE * self.map_height + ACTIONS_HEIGHT
        # Position personnage
        stair: str = '<' if dir > 0 else '>'
        stair_pos = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == stair][0]
        exit_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if
                                       self.world_map[y][x] == '.' and mh_dist((x, y), stair_pos) == 1]
        self.hero.x, self.hero.y = choice(exit_positions)

    def add_to_level(self, item, image) -> bool:
        possible_drop_locations: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.'
                                                and 0 < mh_dist((x, y), self.hero.pos) <= 2 and item not in self.level.items + self.level.monsters]
        if not possible_drop_locations:
            print(f'Unable to drop item {item.name} here. Please move away')
            return False
        item.x, item.y = min(possible_drop_locations, key=lambda p: mh_dist(p, self.hero.pos))
        item.id = max(self.level.sprites) + 1 if self.level.sprites else 0
        self.level.sprites[item.id] = image
        self.level.items.append(item)
        print(f'{item.name} dropped to ({item.pos})!')
        return True

    def remove_from_level(self, item):
        p_idx: int = self.level.items.index(item)
        self.level.items[p_idx] = None
        del self.level.sprites[item.id]

    def remove_from_inv(self, item):
        p_idx: int = self.hero.inventory.index(item)
        self.hero.inventory[p_idx] = None
        del self.sprites[item.id]

    def add_to_inv(self, item: Equipment, image: Surface):
        free_slots: List[int] = [i for i, item in enumerate(self.hero.inventory) if not item]
        next_slot: int = min(free_slots)
        item.x, item.y = -1, -1
        item.id = max(self.sprites) + 1 if self.sprites else 0
        self.hero.inventory[next_slot] = item
        self.sprites[item.id] = image

    def open_chest(self):
        print(f'Hero gained a treasure!')
        t: Treasure = [t for t in self.level.treasures if t.pos == self.hero.pos][0]
        self.level.treasures.remove(t)
        del self.level.sprites[t.id]
        self.hero.gold += t.gold
        if t.has_item:
            match randint(1, 3):
                case 1:
                    item: HealingPotion = copy(choice(healing_potions))
                case 2:
                    if self.hero.allowed_armors:
                        item: Armor = request_armor(index_name=choice(self.hero.allowed_armors).index)
                    else:
                        item: Armor = request_armor(index_name='skin-armor')
                case 3:
                    item: Weapon = request_weapon(index_name=choice(self.hero.allowed_weapons).index)
                    # item: Weapon = request_weapon('halberd')
            print(f'Hero found a {item.name}!')
            image: Surface = pygame.image.load(f"{item_sprites_dir}/{item.image_name}")
            free_slots: List[int] = [i for i, item in enumerate(self.hero.inventory) if not item]
            if free_slots:
                # Add item to inventory
                self.add_to_inv(item, image)
            else:
                # Drop item to the ground
                print(f'Inventory is full!')
                self.add_to_level(item, image)

    def equip(self, item):
        if isinstance(item, Armor):
            if item.index == 'shield':
                if self.hero.used_shield:
                    if item.id == self.hero.used_shield.id:
                        # un-equip shield
                        item.equipped = not item.equipped
                    else:
                        cprint(f'Hero cannot equip <{item.name}> - Please un-equip <{self.hero.used_shield.name}> first!')
                else:
                    if self.hero.used_weapon:
                        is_two_handed = [p for p in self.hero.used_weapon.properties if p.index == 'two-handed']
                        if is_two_handed:
                            cprint(f'Hero cannot equip <{item.name}> with a 2-handed weapon - Please un-equip <{self.hero.used_weapon}> first!')
                        else:
                            # equip shield
                            item.equipped = not item.equipped
            else:
                if self.hero.used_armor:
                    if item.id == self.hero.used_armor.id:
                        # un-equip armor
                        item.equipped = not item.equipped
                    else:
                        cprint(f'Hero cannot equip <{item.name}> - Please un-equip <{self.hero.used_armor.name}> first!')
                else:
                    if self.hero.strength < item.str_minimum:
                        cprint(f'Hero cannot equip <{item.name}> - Minimum strength required is <{item.str_minimum}>!')
                    else:
                        # equip armor
                        item.equipped = not item.equipped
        elif isinstance(item, Weapon):
            if self.hero.used_weapon:
                if item.id == self.hero.used_weapon.id:
                    # un-equip weapon
                    item.equipped = not item.equipped
                else:
                    cprint(f'Hero cannot equip <{item.name}> - Please un-equip <{self.hero.used_weapon.name}> first!')
            else:
                is_two_handed = [p for p in item.properties if p.index == 'two-handed']
                if is_two_handed and self.hero.used_shield:
                    cprint(f'Hero cannot equip <{item.name}> with a shield - Please un-equip <{self.hero.used_shield}> first!')
                else:
                    # equip weapon
                    item.equipped = not item.equipped

    def use(self, item):
        if isinstance(item, HealingPotion):
            self.hero.drink(item)
            self.remove_from_inv(item)
        else:
            cprint(f'Hero cannot use <{item.name}> yet! *Feature not yet implemented*')

    def drop(self, item, image):
        if isinstance(item, Armor | Weapon) and item.equipped:
            cprint(f'Hero cannot drop <{item.name}> - Please un-equip <{item.name}> first!')
        else:
            self.remove_from_inv(item)
            self.add_to_level(item, image)

    def in_map(self, x: int, y: int) -> bool:
        return 0 <= x < self.map_width and 0 <= y < self.map_height

    def in_visible_map(self, x, y) -> bool:
        view_x, view_y, view_width, view_height = self.calculate_view_window()
        return 0 <= x < view_width and 0 <= y < view_height

    @property
    def monsters_in_view_range(self) -> List[Monster]:
        return [m for m in self.level.monsters if in_view_range(*self.hero.pos, *m.pos, obstacles=game.level.obstacles)]


def mh_dist(p1: tuple, p2: tuple):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def dist(p1, p2) -> float:
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def find_path(start: tuple, end: tuple, carte: List, obstacles: List[tuple]) -> Optional[List[tuple]]:
    dist, pred = parcours_largeur(carte, *start, *end, obstacles)

    path: List[tuple] = []

    if dist != float('inf'):
        path.append(end)
        while end != start:
            end = pred[end]
            path.append(end)

    return path[::-1]


def load_game_assets():
    # Load tiles
    tile_img = pygame.image.load('sprites/TilesDungeon/Tile.png')

    # Load font
    font = pygame.font.SysFont(None, 36)

    # Load inventory items
    armor_names = populate(collection_name='armors', key_name='equipment')
    armors = [request_armor(name) for name in armor_names]
    armors = list(filter(lambda a: a, armors))

    weapon_names = populate(collection_name='weapons', key_name='equipment')
    weapons = [request_weapon(name) for name in weapon_names]
    weapons = list(filter(lambda w: w, weapons))

    healing_potions = load_potions_collections()

    return tile_img, font, armors, weapons, healing_potions


def initialize_game(selected_character):
    game = Game(character=selected_character)
    return game


# III - Réactualisation de l'affichage
def update_display(game):
    # Rendu
    game.screen.fill(WHITE)

    # III-0 Dessiner la carte
    map_rect = pygame.Rect(0, 0, game.map_width * TILE_SIZE, game.map_height * TILE_SIZE)
    pygame.draw.rect(game.screen, WHITE, map_rect)
    game.draw_map()

    view_port_tuple = game.calculate_view_window()

    # III-1 Afficher les fontaines de mémorisation de sorts
    for t in game.level.fountains:
        image: Surface = game.level.sprites[t.id]
        t.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

    # III-2 Afficher les personnages
    image: Surface = game.sprites[game.hero.id]
    game.hero.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

    for e in game.level.monsters:
        image: Surface = game.level.sprites[e.id]
        e.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

    # III-3 Afficher les trésors
    for t in game.level.treasures:
        image: Surface = game.level.sprites[t.id]
        t.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

    # III-4 Afficher ou Ramasser des items laissés au sol
    for item in game.level.items:
        try:
            image: Surface = game.level.sprites[item.id]
            item_taken: bool = False
            if item.pos == game.hero.pos:
                free_slots: List[int] = [i for i, item in enumerate(game.hero.inventory) if not item]
                if free_slots:
                    # Grab item
                    game.remove_from_level(item)
                    # Add item to inventory
                    game.add_to_inv(item, image)
                    print(f'Hero gained an item! ({item.name}) #{item.id}')
                    item_taken = True
                # else:
                #     print(f'Cannot take item {item.name}. Inventory is full!')
            if not item_taken:
                image.set_colorkey(PINK)  # Set the pink color as transparent
                item.draw(game.screen, image, TILE_SIZE, *view_port_tuple)
        except AttributeError:
            pass

    # III-5 Dessiner la feuille de stats du personnage
    game.draw_character_stats()

    # III-6 Dessiner la feuille d'inventaire du personnage
    game.draw_inventory()

    # III-7 Dessiner le grimoire du personnage
    if game.hero.sc:
        game.draw_spell_book()

    # Mise à jour de l'affichage
    pygame.display.flip()


def display_game_over(game):
    """
    Display the "GAME OVER" message in the Pygame window.
    """
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, (255, 0, 0))
    text_rect = pygame.Rect(0, game.view_port_height, game.screen_width, SCREEN_HEIGHT)
    game.screen.blit(text, text_rect)
    pygame.display.flip()

    # Pause the game until the user presses a key
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_character(char=game.hero, _dir=characters_dir)
                pygame.quit()
                sys.exit()
            # elif event.type == pygame.KEYDOWN:
            #     paused = False
            #     break


def main_game_loop(game):
    running = True
    last_frame_time = time.time()
    while running:
        # Calculate the time since the last frame
        current_time = time.time()

        # I - Gestion des événements
        handle_events(game)
        # II - Gestion des conditions de jeu
        handle_game_conditions(game)

        # III - Réactualisation de l'affichage
        update_display(game)

        # Limit frame rate
        pygame.time.Clock().tick(FPS)

        # Check if a new round has started
        if game.hero.hit_points > 0:
            if current_time - game.last_round_time >= ROUND_DURATION:
                game.last_round_time = current_time
                handle_combat(monsters=game.monsters_in_view_range)
        else:
            cprint(f'{game.hero.name} has been defeated!')
            display_game_over(game)
            running = False


def handle_events(game):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_character(char=game.hero, _dir=characters_dir)
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_events(game, event)
        elif event.type == pygame.KEYDOWN:
            handle_keyboard_events(game, event)


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
            image: Surface = game.sprites[item.id]
            icon_rect = image.get_rect(topleft=(icon_x, icon_y))
            # cprint(icon_rect)
            if icon_rect.collidepoint(event.pos):
                if event.button == 1:  # Left mouse button
                    if isinstance(item, (Armor, Weapon)):
                        game.equip(item)
                    else:
                        game.use(item)
                elif event.button == 3:  # Right mouse button
                    game.drop(item, image)

    # TODO: area of effect
    if game.hero.sc:# and not game.ready_spell:
        # Vérifier si un sort a été sélectionné
        max_spell_level: int = max([s.level for s in game.hero.sc.learned_spells])
        for i in range(max_spell_level + 2):
            spells_by_level = [s for s in game.hero.sc.learned_spells if s.level == i]
            for j, spell in enumerate(spells_by_level):
                icon_x = game.view_port_width + 210 + j * 40
                icon_y = 170 + i * 40
                image: Surface = game.sprites[spell.id]
                icon_rect = image.get_rect(topleft=(icon_x, icon_y))
                if icon_rect.collidepoint(event.pos):
                    if event.button == 1 and game.hero.can_cast(spell):  # Left mouse button
                        cprint(f'hero pos: {game.hero.pos}')
                        cprint(f'select target for spell <{spell.name}>,  area of effect: {spell.area_of_effect}, range: {spell.range}')
                        frame_color = BLUE if game.hero.sc.spell_slots[i] > 0 else WHITE
                        pygame.draw.rect(game.screen, frame_color, (icon_x - 2, icon_y - 2, ICON_SIZE + 4, ICON_SIZE + 4), 4)
                        pygame.draw.rect(game.screen, RED, (icon_x - 2, icon_y - 2, ICON_SIZE + 4, ICON_SIZE + 4), 4)
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
        handle_combat(party=[game.hero], monsters=monsters_in_spell_range, attack_spell=game.ready_spell)
    elif event.button == 1:
        handle_combat(party=[game.hero], monsters=game.monsters_in_view_range)
    game.last_round_time = time.time()


def handle_right_click_spell_attack(game):
    monsters_in_range = [m for m in game.monsters_in_view_range if dist(game.hero.pos, m.pos) <= game.ready_spell.range // UNIT_SIZE]
    if monsters_in_range:
        for monster in monsters_in_range:
            if game.target_pos in (monster.pos, monster.old_pos):
                monster.hit_points -= game.hero.cast(game.ready_spell, monster)
                if monster.hit_points <= 0:
                    cprint(f'{monster.name} at pos {monster.pos} is *KILLED*')
                    game.hero.victory(monster=monster, solo_mode=True)
                    game.level.monsters.remove(monster)
    else:
        cprint('No monster in range!')
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
    for monster in monsters:
        if game.target_pos in (monster.pos, monster.old_pos):
            monster.hit_points -= game.hero.attack(monster, cast=False)
            if monster.hit_points <= 0:
                cprint(f'{monster.name} at pos {monster.pos} is *KILLED*')
                game.hero.victory(monster=monster, solo_mode=True)
                game.level.monsters.remove(monster)


def move_char(game: Game, char: Monster | Character, pos: tuple):
    x, y = pos
    if (x, y) in game.level.walkable_tiles:
        if mh_dist(char.pos, (x, y)) <= 1:
            char.old_x, char.old_y = char.x, char.y
            char.x, char.y = x, y
        else:
            if isinstance(char, Character):
                obstacles = [m.pos for m in game.level.monsters]
            else:
                obstacles = [m.pos for m in game.level.monsters if m != char]
            path = find_path(start=char.pos, end=(x, y), carte=game.level.carte, obstacles=obstacles)
            # cprint(f'path : {path}')
            if path:
                char.old_x, char.old_y = char.x, char.y
                char.x, char.y = path[1]
            else:
                cprint(f'No path found for {char.name}!')


def handle_keyboard_events(game, event):
    if event.key == pygame.K_ESCAPE:
        save_character(char=game.hero, _dir=characters_dir)
        pygame.quit()
        sys.exit()
    elif event.key == pygame.K_UP and game.can_move(char=game.hero, dir=UP):
        handle_combat(monsters=game.monsters_in_view_range, party=[game.hero], move_action=(game.hero.x, game.hero.y - 1))
    elif event.key == pygame.K_DOWN and game.can_move(char=game.hero, dir=DOWN):
        handle_combat(monsters=game.monsters_in_view_range, party=[game.hero], move_action=(game.hero.x, game.hero.y + 1))
    elif event.key == pygame.K_LEFT and game.can_move(char=game.hero, dir=LEFT):
        handle_combat(monsters=game.monsters_in_view_range, party=[game.hero], move_action=(game.hero.x - 1, game.hero.y))
    elif event.key == pygame.K_RIGHT and game.can_move(char=game.hero, dir=RIGHT):
        handle_combat(monsters=game.monsters_in_view_range, party=[game.hero], move_action=(game.hero.x + 1, game.hero.y))
    elif event.key == pygame.K_p:
        handle_potion_use(game)


def handle_potion_use(game):
    if game.hero.healing_potions:
        potion = game.hero.choose_best_potion()
        game.hero.drink(potion)
        game.remove_from_inv(potion)
    else:
        cprint('Sorry dude! no healing potion available...')


def handle_game_conditions(game):
    handle_treasure_chests(game)
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


def handle_combat(monsters: List[Monster], party=None, attack_spell: Spell = None, move_action: tuple = None):
    """
    Handle the combat between the party and the monsters.

    Args:
        party (list): A list of party members.
        monsters (list): A list of monsters.
    """
    if party is None:
        party = []
    attack_order = get_initiative_order(party + monsters)
    for char in attack_order:
        if char in party and char.hit_points > 0:
            # Handle party member's action
            if move_action:
                move_char(game, char, move_action)
            elif attack_spell:
                handle_right_click_spell_attack(game)
            else:
                handle_left_click_action(game)
        else:
            if char.hit_points <= 0:
                continue
            # Handle monster's attack
            handle_monster_actions(game, char)


def handle_monster_actions(game, monster):
    if mh_dist(monster.pos, game.hero.pos) <= 1:
        # Monster attacks the hero
        game.hero.hit_points -= monster.melee_attack(game.hero)
    else:
        # Monster moves towards the hero
        move_char(game, monster, game.hero.pos)


# def handle_monster_attacks(game) -> bool:
#     for monster in game.level.monsters:
#         if mh_dist(monster.pos, game.hero.pos) == 1:
#             game.hero.hit_points -= monster.melee_attack(game.hero)
#             if game.hero.hit_points <= 0:
#                 # Handle hero's defeat
#                 return False
#     return True


def handle_treasure_chests(game):
    if any(t.pos == game.hero.pos for t in game.level.treasures):
        game.open_chest()


def handle_fountains(game):
    if any(f.pos == game.hero.pos for f in game.level.fountains):
        char = game.hero
        if char.class_type.can_cast:
            if char.sc.spell_slots != char.class_type.spell_slots[char.level]:
                print(f'{char.name} has memorized all his spells')
                char.sc.spell_slots = copy(char.class_type.spell_slots[char.level])
        if char.level < len(game.xp_levels) and char.xp > game.xp_levels[char.level]:
            if char.class_type.can_cast:
                spell_names: List[str] = populate(collection_name='spells', key_name='results')
                all_spells: List[Spell] = [request_spell(name) for name in spell_names]
                class_tome_spells = [s for s in all_spells if s is not None and char.class_type.index in s.allowed_classes]
                char.gain_level(tome_spells=class_tome_spells)
            else:
                char.gain_level()
        save_character(char, _dir=characters_dir)


def handle_level_changes(game):
    match game.world_map[game.hero.y][game.hero.x]:
        case '>':
            print(f'Hero found downstairs!')
            game.dungeon_level += 1
            if game.dungeon_level > len(game.levels):
                game.level = Level(level_no=game.dungeon_level)
                game.levels.append(game.level)
                game.level.load(hero=game.hero)
            else:
                game.level = game.levels[game.dungeon_level - 1]
            game.update_level(dir=1)
            game.screen = pygame.display.set_mode((game.screen_width, game.screen_height))
        case '<':
            print(f'Hero found upstairs!')
            game.dungeon_level -= 1
            game.level = game.levels[game.dungeon_level - 1]
            game.update_level(dir=-1)
            game.screen = pygame.display.set_mode((game.screen_width, game.screen_height))


if __name__ == "__main__":
    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    sprites_dir = f"{path}/sprites"
    char_sprites_dir = f"{sprites_dir}/rpgcharacterspack"
    item_sprites_dir = f"{sprites_dir}/Items"
    spell_sprites_dir = f"{sprites_dir}/schools"
    roster: List[Character] = get_roster(characters_dir=f'{path}/gameState/characters')

    # Récupération du personnage choisi par l'utilisateur
    if len(sys.argv) > 1:
        character_name = sys.argv[1]
        try:
            selected_character: Character = [c for c in roster if c.name == character_name][0]
            # print(f"Character name: {character_name}")
            # for i, item in enumerate(selected_character.inventory):
            #     if item:
            #         print(f"#{i} (id #{item.id}) - {item.name}")
        except IndexError:
            print(f"Character name <{character_name}> not found in roster")
    else:
        character_name = 'Brottor'
        selected_character: Character = [c for c in roster if c.name == character_name][0]

        # print("No character name provided")
        # selected_character: Character = choice(list(filter(lambda c: c.is_spell_caster, roster)))
        # character = max(roster, key=lambda c: c.gold)
        # character = [c for c in roster if c.name == 'Balasar'][0]
        # character.inventory = [None] * 20
        # character.abilities.str = 12

    # Initialisation de Pygame
    pygame.init()

    tile_img, font, armors, weapons, healing_potions = load_game_assets()
    game = initialize_game(selected_character)
    main_game_loop(game)
