from __future__ import annotations

import os, pygame
import sys
from dataclasses import dataclass, field
from random import choice, randint
from typing import List

from pygame import Surface

from dao_classes import Weapon, Armor, HealingPotion, Character, Spell, Equipment, Monster, Treasure
from main import get_roster, save_character
from populate_functions import populate, request_weapon, request_armor, request_monster
from populate_rpg_functions import load_potions_collections
from tools.common import cprint


# Fonction pour afficher du texte
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


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


# Définition de la fonction pour afficher une info-bulle
def draw_tooltip_old(description, surface, x, y):
    font = pygame.font.Font(None, 18)
    text = font.render(description, True, BLACK)
    text_rect = text.get_rect()
    text_rect.topleft = (x, y)
    pygame.draw.rect(surface, GRAY, (text_rect.left - 5, text_rect.top - 5, text_rect.width + 10, text_rect.height + 10))
    surface.blit(text, text_rect)


# Fonction pour dessiner un bouton
def draw_button(surface, rect, color, text):
    pygame.draw.rect(surface, color, rect)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def mh_dist(p1: tuple, p2: tuple):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


class Level:
    level_no: int
    world_map: List[List[int]]
    map_height: int
    map_width: int
    monsters: List[Monster]
    treasures: dict
    items: List[Equipment | HealingPotion]
    sprites: dict

    def __init__(self, level_no: int):
        self.level_no = level_no
        self.world_map = self.load_maze(level=level_no)
        self.map_height = len(self.world_map)
        self.map_width = max([len(self.world_map[i]) for i in range(self.map_height)])
        self.sprites = {}
        self.items = []

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

        self.monsters = [request_monster(choice(allowed_monster_names).lower()) for _ in range(randint(1, 5))]
        for m in self.monsters:
            m.x, m.y = choice(open_positions)
            m.id = max(self.sprites) + 1 if self.sprites else 0
            open_positions.remove((m.x, m.y))
            self.sprites[m.id] = pygame.image.load(f"{char_sprites_dir}/{m.image_name}").convert_alpha()

        self.treasures: List[Treasure] = []
        for _ in range(randint(1, 5)):
            gold: int = randint(50, 300) * self.level_no
            has_item: bool = randint(1, 3) == 2
            has_item: bool = True
            t_x, t_y = choice(open_positions)
            t: Treasure = Treasure(id=(max(self.sprites) + 1 if self.sprites else 0), x=t_x, y=t_y, image_name='treasure.png', gold=gold, has_item=has_item)
            self.treasures.append(t)
            self.sprites[t.id] = pygame.image.load(f"{sprites_dir}/{t.image_name}").convert_alpha()


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

    def __init__(self):
        # Chargement de la carte
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
        self.screen_height = self.view_port_height + ACTIONS_HEIGHT
        self.action_rects = {}
        self.sprites = {}
        # Création de la fenêtre
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        # Initialisation du personnage
        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.']
        hero_x, hero_y = choice(open_positions)
        open_positions.remove((hero_x, hero_y))
        roster: List[Character] = get_roster(characters_dir=f'{path}/gameState/characters')
        self.hero = choice(roster)
        self.sprites[self.hero.id] = pygame.image.load(f"{char_sprites_dir}/{self.hero.image_name}").convert_alpha()
        # self.hero.inventory = [None] * 20
        for char in roster:
            for item in char.inventory:
                if item:
                    self.sprites[item.id] = pygame.image.load(f"{item_sprites_dir}/{item.image_name}").convert_alpha()
        # self.hero = max(roster, key=lambda c: c.gold)
        # self.hero = [c for c in roster if c.name == 'Balasar'][0]
        self.hero.x, self.hero.y = hero_x, hero_y
        self.level.load(hero=self.hero)

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
        stat_texts = [
            f"Nom: {self.hero.name}",
            f"Race: {self.hero.race.name}",
            f"Classe: {self.hero.class_type.name}",
            f"Niveau: {self.hero.level}",
            f"XP: {self.hero.xp}",
            f"Santé: {self.hero.hit_points}/{self.hero.max_hit_points} ({self.hero.get_status})",
            # damage_dice: str = f'{self.hero.weapon.damage_dice}' if not w.damage_dice.bonus else f'{w.damage_dice.dice} + {w.damage_dice.bonus}'
            f"Attaque: {weapon.damage_dice.dice}" if weapon else f"Attaque: 1d2",
            # f"Défense: {self.hero.armor.ac}",
            f"Défense: {armor.armor_class['base']}" if armor else "Défense: 10",
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
        if self.hero.can_cast:
            slots: str = '/'.join(map(str, self.hero.sc.spell_slots))
            spells_texts.append(f"Slots: {slots}")
            known_spells: int = len(self.hero.sc.learned_spells)
            learned_spells: List[Spell] = [s for s in self.hero.sc.learned_spells]
            learned_spells.sort(key=lambda s: s.level)
            for s in learned_spells:
                spells_texts.append(f"L{s.level}: {str(s)}")
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

    def draw_inventory(self, image_dir: str):
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
            icon_y = 210 + 70 + (i // 5) * 40
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
                        tooltip_text = item.name
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
        self.view_port_height = min(self.map_height * TILE_SIZE, SCREEN_HEIGHT - ACTIONS_HEIGHT)
        self.screen_width = self.view_port_width + STATS_WIDTH
        self.screen_height = self.view_port_height + ACTIONS_HEIGHT
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
                    item: HealingPotion = choice(healing_potions)
                case 2:
                    item: Armor = choice(self.hero.allowed_armors)
                case 3:
                    item: Weapon = choice(self.hero.allowed_weapons)
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
            if self.hero.used_armor:
                if item.id == self.hero.used_armor.id:
                    # un-equip armor
                    item.equipped = not item.equipped
                else:
                    cprint(f'Hero cannot equip *{item.name}* - Please un-equip *{self.hero.used_armor.name}* first!')
            else:
                # equip armor
                item.equipped = not item.equipped
        elif isinstance(item, Weapon):
            if self.hero.used_weapon:
                if item.id == self.hero.used_weapon.id:
                    # un-equip weapon
                    item.equipped = not item.equipped
                else:
                    cprint(f'Hero cannot equip *{item.name}* - Please un-equip *{self.hero.used_armor.name}* first!')
            else:
                # equip weapon
                item.equipped = not item.equipped

    def use(self, item):
        self.hero.drink(item)
        self.remove_from_inv(item)

    def drop(self, item, image):
        if isinstance(item, Armor | Weapon) and item.equipped:
            cprint(f'Hero cannot drop *{item.name}* - Please un-equip *{item.name}* first!')
        else:
            self.remove_from_inv(item)
            self.add_to_level(item, image)


if __name__ == "__main__":

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    characters_dir = f'{abspath}/gameState/characters'
    sprites_dir = f"{path}/sprites"
    char_sprites_dir = f"{sprites_dir}/rpgcharacterspack"
    item_sprites_dir = f"{sprites_dir}/Items"
    roster: List[Character] = get_roster(characters_dir)

    # Initialisation de Pygame
    pygame.init()

    # Définition des constantes pour la mise en page
    # SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    STATS_WIDTH, ACTIONS_HEIGHT = 450, 200
    STATS_HEIGHT = 250

    # Paramètres de l'écran
    TILE_SIZE = 32
    FPS = 60

    # Autres paramètres
    ICON_SIZE = 32

    # Couleurs
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (200, 200, 200)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    PINK = (255, 0, 255)

    # Chargement des tuiles
    tile_img = pygame.image.load('sprites/TilesDungeon/Tile.png')

    UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

    game: Game = Game()

    # Font
    font = pygame.font.SysFont(None, 36)

    # Title
    # pygame.display.set_caption("RPG avec Pygame")

    # Inventaire du personnage (liste d'objets)
    # monster_names: List[str] = populate(collection_name='monsters', key_name='results')
    # monsters: List[Monster] = [request_monster(name) for name in monster_names]
    armor_names: List[str] = populate(collection_name='armors', key_name='equipment')
    armors: List[Armor] = [request_armor(name) for name in armor_names]
    weapon_names: List[str] = populate(collection_name='weapons', key_name='equipment')
    weapons: List[Weapon] = [request_weapon(name) for name in weapon_names]
    armors = list(filter(lambda a: a, armors))
    weapons = list(filter(lambda w: w, weapons))
    healing_potions: List[HealingPotion] = load_potions_collections()

    # Boucle de jeu
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Set running to False to exit the loop
                save_character(char=game.hero, _dir=characters_dir)
                pygame.quit()  # Quit Pygame
                sys.exit()  # Quit the Python script
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si un texte d'action a été cliqué
                for action_text, action_rect in game.action_rects.items():
                    if action_rect.collidepoint(event.pos):
                        print(f"Action: {action_text}")
                # Vérifier si une case de l'inventaire a été cliquée
                for i, item in enumerate(game.hero.inventory):
                    if item is not None:  # pp and isinstance(item, Armor | Weapon):
                        try:
                            icon_x = game.view_port_width + 10 + (i % 5) * 40
                            icon_y = 200 + 70 + (i // 5) * 40
                            image: Surface = game.sprites[item.id]
                            icon_rect = image.get_rect(topleft=(icon_x, icon_y))
                            # cprint(icon_rect)
                            if icon_rect.collidepoint(event.pos):
                                if event.button == 1:  # Left mouse button
                                    if isinstance(item, Armor | Weapon):
                                        game.equip(item)
                                    else:
                                        game.use(item)
                                elif event.button == 3:  # Right mouse button
                                    game.drop(item, image)
                        except KeyError:
                            pass

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.can_move(char=game.hero, dir=UP):
                    game.hero.y -= 1
                elif event.key == pygame.K_DOWN and game.can_move(char=game.hero, dir=DOWN):
                    game.hero.y += 1
                elif event.key == pygame.K_LEFT and game.can_move(char=game.hero, dir=LEFT):
                    game.hero.x -= 1
                elif event.key == pygame.K_RIGHT and game.can_move(char=game.hero, dir=RIGHT):
                    game.hero.x += 1
                elif event.key == pygame.K_p:
                    if game.hero.healing_potions:
                        p: HealingPotion = game.hero.choose_best_potion()
                        game.hero.drink(p)
                        game.remove_from_inv(p)
                    else:
                        cprint('Sorry dude! no healing potion available...')

        # Ouverture des coffres à trésor (Gold + item aléatoire éventuel)
        if any(t.pos == game.hero.pos for t in game.level.treasures):
            game.open_chest()

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

        # Vérifier les collisions avec les ennemis
        if any(game.hero.check_collision(e) for e in game.level.monsters):
            print("Combat!")

        # Rendu
        game.screen.fill(WHITE)

        # Dessiner la carte
        map_rect = pygame.Rect(0, 0, game.map_width * TILE_SIZE, game.map_height * TILE_SIZE)
        pygame.draw.rect(game.screen, WHITE, map_rect)
        game.draw_map()

        view_port_tuple = game.calculate_view_window()

        # Afficher les personnages
        image: Surface = game.sprites[game.hero.id]
        game.hero.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

        for e in game.level.monsters:
            image: Surface = game.level.sprites[e.id]
            e.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

        # Afficher les trésors
        for t in game.level.treasures:
            image: Surface = game.level.sprites[t.id]
            t.draw(game.screen, image, TILE_SIZE, *view_port_tuple)

        # Afficher ou Ramasser des items laissés au sol
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
                    else:
                        print(f'Cannot take item {item.name}. Inventory is full!')
                if not item_taken:
                    image.set_colorkey(PINK)  # Set the pink color as transparent
                    item.draw(game.screen, image, TILE_SIZE, *view_port_tuple)
            except AttributeError:
                pass

        # Dessiner la feuille de stats du personnage
        game.draw_character_stats()

        # Dessiner la feuille d'inventaire du personnage
        game.draw_inventory(image_dir=sprites_dir)

        # Dessiner le panneau de commande d'actions
        game.draw_action_panel()

        # Mise à jour de l'affichage
        # pygame.display.update()

        # Mise à jour de l'affichage
        pygame.display.flip()

        # Limiter le nombre d'images par seconde
        pygame.time.Clock().tick(FPS)
