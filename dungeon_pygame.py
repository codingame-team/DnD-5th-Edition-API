from __future__ import annotations

import os, pygame
from dataclasses import dataclass, field
from random import choice, randint
from typing import List

from pygame import Surface

from dao_rpg_classes import Character, Monster, Armor, Weapon, Treasure
from dao_classes import Weapon as Weapon2, Armor as Armor2, Potion, Character as Char2
from main import get_roster
from populate_functions import populate, request_weapon, request_armor
from populate_rpg_functions import request_monster, load_armor_image, load_potions_collections, load_potion_image, load_weapon_image


# Définition de la classe Item pour représenter un objet dans l'inventaire
class Item:
    def __init__(self, name, description, image):
        self.name = name
        self.description = description
        self.image = image
        self.image.set_colorkey(PINK)  # Définir le fond rose comme transparent
        self.selected = False



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


class Game:
    world_map: List[List[int]]
    map_width: int
    map_height: int
    screen_width: int
    screen_height: int
    view_port_width: int
    view_port_height: int
    hero: Char2
    monsters: List[Monster]
    treasures: dict
    dungeon_level: int
    action_rects: dict

    def __init__(self):
        # Chargement de la carte
        self.dungeon_level = 1
        self.world_map = self.load_maze(level=self.dungeon_level)
        self.map_height = len(self.world_map)
        self.map_width = max([len(self.world_map[i]) for i in range(self.map_height)])
        self.walls = [(x, y) for y in range(self.map_height) for x in range(self.map_width) if self.world_map[y][x] == '#']
        # Redimensionnement de l'écran
        self.view_port_width = min(self.map_width * TILE_SIZE, SCREEN_WIDTH - STATS_WIDTH)
        self.view_port_height = min(self.map_height * TILE_SIZE, SCREEN_HEIGHT - ACTIONS_HEIGHT)
        self.screen_width = self.view_port_width + STATS_WIDTH
        self.screen_height = self.view_port_height + ACTIONS_HEIGHT
        self.action_rects = {}
        # Initialisation du personnage
        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.']
        hero_x, hero_y = choice(open_positions)
        open_positions.remove((hero_x, hero_y))
        start_armor: Armor = Armor(name='Plate Armor', ac=18, img=pygame.image.load(f'{path}/sprites/beholder.png'))
        start_weapon: Weapon = Weapon(name='Greatsword', damage_dice='2d6', img=pygame.image.load(f'{path}/sprites/beholder.png'))
        self.hero: Character = Character(x=hero_x, y=hero_y, speed=15, hp=10, max_hp=10, weapon=start_weapon, armor=start_armor, img=pygame.image.load(f'{path}/sprites/hero.png'))
        roster: List[Character] = get_roster(characters_dir=f'{path}/gameState/characters')
        self.hero = choice(roster)
        self.hero.x, self.hero.y = hero_x, hero_y
        self.load(level=1)

    # Define a method to calculate the view window
    def calculate_view_window(self):
        view_width = self.view_port_width // TILE_SIZE
        view_height = self.view_port_height // TILE_SIZE
        viewport_x = max(0, min(self.hero.x - view_width // 2, self.map_width - view_width))
        viewport_y = max(0, min(self.hero.y - view_height // 2, self.map_height - view_height))
        return viewport_x, viewport_y, view_width, view_height


    def draw_map(self, screen):
        # photo_wall = pygame.image.load(f"{path}/sprites/WallTile1.png")
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
                    screen.blit(photo_wall, (tile_x, tile_y))
                elif self.world_map[row][col] == '<':
                    screen.blit(photo_upstairs, (tile_x, tile_y))
                elif self.world_map[row][col] == '>':
                    screen.blit(photo_downstairs, (tile_x, tile_y))

    def draw_map_old(self):
        # photo_wall = pygame.image.load(f"{path}/sprites/WallTile1.png")
        photo_wall = pygame.image.load(f"{path}/sprites/TilesDungeon/Wall.png")
        photo_downstairs = pygame.image.load(f"{path}/sprites/DownStairs.png")
        photo_upstairs = pygame.image.load(f"{path}/sprites/UpStairs.png")
        for row in range(self.map_height):
            for col in range(self.map_width):
                tile_x, tile_y = col * TILE_SIZE, row * TILE_SIZE
                if self.world_map[row][col] == '#':
                    screen.blit(photo_wall, (tile_x, tile_y))
                elif self.world_map[row][col] == '<':
                    screen.blit(photo_upstairs, (tile_x, tile_y))
                elif self.world_map[row][col] == '>':
                    screen.blit(photo_downstairs, (tile_x, tile_y))

    # Fonction pour dessiner la feuille de stats du personnage
    def draw_character_stats(self, screen):
        #stats_rect = pygame.Rect(self.map_width * TILE_SIZE, 0, STATS_WIDTH, self.map_height * TILE_SIZE)
        stats_rect = pygame.Rect(self.view_port_width, 0, STATS_WIDTH, self.view_port_height)

        pygame.draw.rect(screen, GRAY, stats_rect)
        font = pygame.font.Font(None, 24)
        pygame.display.set_caption(f"Dungeon Level: {self.dungeon_level}")
        stat_texts = [
            f"Nom: {self.hero.name}",
            f"Race: {self.hero.race.name}",
            f"Classe: {self.hero.class_type.name}",
            # f"Santé: {self.hero.hp}/{self.hero.max_hp}",
            f"Santé: {self.hero.hit_points}/{self.hero.max_hit_points}",
            # damage_dice: str = f'{self.hero.weapon.damage_dice}' if not w.damage_dice.bonus else f'{w.damage_dice.dice} + {w.damage_dice.bonus}'
            f"Attaque: {self.hero.weapon.damage_dice.dice}",
            # f"Défense: {self.hero.armor.ac}",
            f"Défense: {self.hero.armor.armor_class['base']}",
            #f"Potions: {self.hero.potions}",
            f"Gold: {self.hero.gold}"
            # Ajoutez d'autres statistiques ici
        ]
        for i, stat_text in enumerate(stat_texts):
            text_surface = font.render(stat_text, True, (0, 0, 0))
            text_rect = text_surface.get_rect()
            text_rect.topleft = (stats_rect[0] + 20, stats_rect[1] + 20 + i * 30)  # Ajuster la position en fonction de la marge
            screen.blit(text_surface, text_rect)

    def draw_inventory(self, screen):
        # # Afficher le titre de l'inventaire
        # draw_text("Inventaire", font, BLACK, screen, 10, 10)

        # Obtenir les coordonnées de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Stocker les informations de l'info-bulle
        tooltip_text = None

        # Afficher les cases de l'inventaire
        for i, item in enumerate(inventory):
            # Calculer les coordonnées de l'image dans la case
            icon_x = self.view_port_width + 10 + (i % 5) * 40
            icon_y = 150 + 70 + (i // 5) * 40
            # Afficher l'icône de l'objet s'il y en a un dans la case
            if item is not None:
                screen.blit(item.image, (icon_x, icon_y))
                frame_color: tuple = BLUE if item.selected else WHITE
                pygame.draw.rect(screen, frame_color, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)
                # Vérifier si la souris survole la case
                if pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE).collidepoint(mouse_x, mouse_y):
                    # Stocker la description de l'objet pour l'info-bulle
                    tooltip_text = item.description
            # Dessiner un cadre vide pour les cases vides
            else:
                pygame.draw.rect(screen, GRAY, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)

        # Afficher l'info-bulle avec la description de l'objet
        if tooltip_text:
            draw_tooltip(tooltip_text, screen, mouse_x + 10, mouse_y)

    # Fonction pour dessiner le panneau de commande d'actions
    def draw_action_panel(self, screen):
        """ left: La position horizontale du coin supérieur gauche du rectangle.
            top: La position verticale du coin supérieur gauche du rectangle.
            width: La largeur du rectangle.
            height: La hauteur du rectangle.
        """
        #actions_rect = pygame.Rect(0, self.map_height * TILE_SIZE, self.screen_width, ACTIONS_HEIGHT)
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

    def can_move(self, char: Character | Monster, dir: tuple) -> bool:
        dx, dy = dir
        x, y = char.x + dx, char.y + dy
        return 0 <= x < self.map_width and 0 <= y < self.map_height and self.world_map[y][x] != '#'

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

    def load(self, level: int):
        """
            Chargement des entités du donjon (monstres et trésors)
        :param level:
        :return:
        """
        photo_treasure = pygame.image.load(f"{path}/sprites/treasure.png")
        # photo_exit: PhotoImage = PhotoImage(file=f"{path}/sprites/exit.png")

        # rating = lambda m: m.cr < (hero.level / 4 if hero.level < 5 else hero.level / 2)
        monster_names: List[str] = ['ankheg', 'baboon', 'bat', 'blob', 'crab', 'ghost', 'goblin', 'eagle', 'harpy', 'lizard', 'mimic', 'owl', 'rat', 'rat_scull', 'skeleton',
                                    'snake', 'spider', 'tentacle', 'wasp', 'wolf']
        monster_candidates: List[Monster] = [request_monster(name) for name in monster_names]
        monster_candidates = list(filter(None, monster_candidates))
        monster_candidates = list(filter(lambda m: m.cr < self.dungeon_level, monster_candidates))
        allowed_monster_names: list[str] = [m.name for m in monster_candidates]

        open_positions: List[tuple] = [(x, y) for x in range(self.map_width) for y in range(self.map_height) if self.world_map[y][x] == '.' and (x, y) != self.hero.pos]

        self.monsters = [request_monster(choice(allowed_monster_names)) for _ in range(randint(1, 5))]
        for m in self.monsters:
            m.x, m.y = choice(open_positions)
            open_positions.remove((m.x, m.y))

        self.treasures: List[Treasure] = []
        for _ in range(randint(1, 5)):
            gold: int = randint(50, 300) * self.dungeon_level
            # has_potion: bool = randint(1, 3) == 2
            has_potion: bool = False
            t_x, t_y = choice(open_positions)
            treasure: Treasure = Treasure(x=t_x, y=t_y, img=photo_treasure, gold=gold, potion=has_potion)
            self.treasures.append(treasure)

    def update_level(self, dir: int, screen):
        # Chargement de la carte
        self.dungeon_level += 1 if dir > 0 else -1
        self.world_map = self.load_maze(level=self.dungeon_level)
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
        self.load(level=self.dungeon_level)
        screen = pygame.display.set_mode((game.screen_width, game.screen_height))


if __name__ == "__main__":

    path = os.path.dirname(__file__)

    # Initialisation de Pygame
    pygame.init()

    # Définition des constantes pour la mise en page
    # SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    STATS_WIDTH, ACTIONS_HEIGHT = 350, 200

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

    # Création de la fenêtre
    screen = pygame.display.set_mode((game.screen_width, game.screen_height))
    pygame.display.set_caption("RPG avec Pygame")

    # Font
    font = pygame.font.SysFont(None, 36)

    # Inventaire du personnage (liste d'objets)
    inventory: List[Item] = []
    # inventory += [
    #     Item("Épée", "Une épée tranchante", pygame.image.load(f"{path}/sprites/Items/Sword01.PNG")),
    #     Item("Potion de santé", "Restaure 50 points de vie", pygame.image.load(f"{path}/sprites/Items/PotionRed.PNG")),
    #     Item("Potion de vitesse", "Accélère la vitesse", pygame.image.load(f"{path}/sprites/Items/PotionTallTan.PNG")),
    #     Item("Armure", "Une armure solide", pygame.image.load(f"{path}/sprites/Items/ArmorChainMail.PNG")),
    #     Item("Bottes", "Une paire de bottes dorée", pygame.image.load(f"{path}/sprites/Items/BootsGolden.PNG")),
    #     Item("Arc", "Un arc long", pygame.image.load(f"{path}/sprites/Items/Bow.PNG")),
    #     Item("Clef", "Une clef en cuivre", pygame.image.load(f"{path}/sprites/Items/KeyCopper.PNG")),
    #     Item("Bouclier", "Un bouclier rayé rouge", pygame.image.load(f"{path}/sprites/Items/ShieldStripeRed.PNG")),
    #     Item("Épée à 2 mains", "Une épée à 2 mains", pygame.image.load(f"{path}/sprites/Items/SwordTwoHanded.PNG")),
    #     Item("Mace", "Une mace magique", pygame.image.load(f"{path}/sprites/Items/MaceMagic.PNG")),
    #     Item("Bâton", "Un bâton magique", pygame.image.load(f"{path}/sprites/Items/Staff01.PNG")),
    #     Item("Fléau", "Un fléau", pygame.image.load(f"{path}/sprites/Items/Flail01.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Clef", "Une clef en cuivre", pygame.image.load(f"{path}/sprites/Items/KeyCopper.PNG")),
    #     Item("Bouclier", "Un bouclier rayé rouge", pygame.image.load(f"{path}/sprites/Items/ShieldStripeRed.PNG")),
    #     Item("Épée à 2 mains", "Une épée à 2 mains", pygame.image.load(f"{path}/sprites/Items/SwordTwoHanded.PNG")),
    #     Item("Mace", "Une mace magique", pygame.image.load(f"{path}/sprites/Items/MaceMagic.PNG")),
    #     Item("Bâton", "Un bâton magique", pygame.image.load(f"{path}/sprites/Items/Staff01.PNG")),
    #     Item("Fléau", "Un fléau", pygame.image.load(f"{path}/sprites/Items/Flail01.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Mace", "Une mace magique", pygame.image.load(f"{path}/sprites/Items/MaceMagic.PNG")),
    #     Item("Bâton", "Un bâton magique", pygame.image.load(f"{path}/sprites/Items/Staff01.PNG")),
    #     Item("Fléau", "Un fléau", pygame.image.load(f"{path}/sprites/Items/Flail01.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Mace", "Une mace magique", pygame.image.load(f"{path}/sprites/Items/MaceMagic.PNG")),
    #     Item("Bâton", "Un bâton magique", pygame.image.load(f"{path}/sprites/Items/Staff01.PNG")),
    #     Item("Fléau", "Un fléau", pygame.image.load(f"{path}/sprites/Items/Flail01.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Fléau", "Un fléau", pygame.image.load(f"{path}/sprites/Items/Flail01.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
    #     Item("Mace", "Une mace magique", pygame.image.load(f"{path}/sprites/Items/MaceMagic.PNG")),
    # ]
    # inventory += [None] * (20 - len(inventory))


    # monster_names: List[str] = populate(collection_name='monsters', key_name='results')
    # monsters: List[Monster] = [request_monster(name) for name in monster_names]
    armor_names: List[str] = populate(collection_name='armors', key_name='equipment')
    armors: List[Armor] = [request_armor(name) for name in armor_names]
    weapon_names: List[str] = populate(collection_name='weapons', key_name='equipment')
    weapons: List[Weapon] = [request_weapon(name) for name in weapon_names]
    armors = list(filter(lambda a: a, armors))
    weapons = list(filter(lambda w: w, weapons))
    potions: List[Potion] = load_potions_collections()

    for _ in range(10):
        a: Armor2 = choice(armors)
        a_image: Surface = load_armor_image(a.index)
        desc: str = f'{a.name} (AC: {a.armor_class['base']})'
        inventory += [Item(a.name, desc, a_image)]

    for _ in range(10):
        w: Weapon2 = choice(weapons)
        w_image: Surface = load_weapon_image(w.index)
        damage_dice: str = f'{w.damage_dice.dice}' if not w.damage_dice.bonus else f'{w.damage_dice.dice} + {w.damage_dice.bonus}'
        desc: str = f'{w.name} ({damage_dice})'
        inventory += [Item(w.name, desc, w_image)]

    for _ in range(10):
        p: Potion = choice(potions)
        p_image: Surface = load_potion_image(p.name)
        hit_dice: str = f'{p.hit_dice}' if not p.bonus else f'{p.hit_dice} + {p.bonus}'
        desc: str = f'{p.name} ({hit_dice})'
        inventory += [Item(p.name, desc, p_image)]

    inventory += [None] * (20 - len(inventory))

    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    # print(f'path = {path}')
    # print(f'abspath = {abspath}')
    characters_dir = f'{abspath}/gameState/characters'
    roster: List[Character] = get_roster(characters_dir)

    # Boucle de jeu
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier si un texte d'action a été cliqué
                for action_text, action_rect in game.action_rects.items():
                    if action_rect.collidepoint(event.pos):
                        print(f"Action: {action_text}")
                # Vérifier si une case de l'inventaire a été cliquée
                for i, item in enumerate(inventory):
                    if item is not None:
                        icon_x = game.view_port_width + 10 + (i % 5) * 40
                        icon_y = 150 + 70 + (i // 5) * 40
                        icon_rect = item.image.get_rect(topleft=(icon_x, icon_y))
                        if icon_rect.collidepoint(event.pos):
                            if item.selected:
                                item.selected = False
                                if item.name == 'Épée':
                                    game.hero.weapon.damage_dice = '1d4'
                            else:
                                item.selected = True
                                if item.name == 'Épée':
                                    game.hero.weapon.damage_dice = '2d10'
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.can_move(char=game.hero, dir=UP):
                    game.hero.y -= 1
                elif event.key == pygame.K_DOWN and game.can_move(char=game.hero, dir=DOWN):
                    game.hero.y += 1
                elif event.key == pygame.K_LEFT and game.can_move(char=game.hero, dir=LEFT):
                    game.hero.x -= 1
                elif event.key == pygame.K_RIGHT and game.can_move(char=game.hero, dir=RIGHT):
                    game.hero.x += 1

        is_treasure: List[Treasure] = [t for t in game.treasures if t.pos == game.hero.pos]
        if any(t for t in game.treasures if t.pos == game.hero.pos):
            print(f'Hero gained a treasure!')
            treasure: Treasure = is_treasure[0]
            game.treasures.remove(treasure)
            game.hero.gold += treasure.gold
            if treasure.potion:
                game.hero.potions += 1
                print(f'Hero found a potion!')

        match game.world_map[game.hero.y][game.hero.x]:
            case '>':
                print(f'Hero found downstairs!')
                game.update_level(dir=1, screen=screen)
            case '<':
                print(f'Hero found upstairs!')
                game.update_level(dir=-1, screen=screen)

        # Vérifier les collisions avec les ennemis
        if any(game.hero.check_collision(e) for e in game.monsters):
            print("Combat!")

        # Rendu
        screen.fill(WHITE)

        # Dessiner la carte
        map_rect = pygame.Rect(0, 0, game.map_width * TILE_SIZE, game.map_height * TILE_SIZE)
        pygame.draw.rect(screen, WHITE, map_rect)
        game.draw_map(screen)

        view_port_tuple = game.calculate_view_window()
        # Afficher les personnages
        game.hero.draw(screen, TILE_SIZE, *view_port_tuple)
        # game.hero.draw_old(screen, TILE_SIZE)
        for e in game.monsters:
            e.draw(screen, TILE_SIZE, *view_port_tuple)

        # Afficher les trésors
        for t in game.treasures:
            t.draw(screen, TILE_SIZE, *view_port_tuple)

        # Dessiner la feuille de stats du personnage
        game.draw_character_stats(screen)

        # Dessiner la feuille d'inventaire du personnage
        game.draw_inventory(screen)

        # Dessiner le panneau de commande d'actions
        game.draw_action_panel(screen)

        # Mise à jour de l'affichage
        # pygame.display.update()

        # Mise à jour de l'affichage
        pygame.display.flip()

        # Limiter le nombre d'images par seconde
        pygame.time.Clock().tick(FPS)