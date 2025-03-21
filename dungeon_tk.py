import json
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from random import choice, randint
from tkinter import Tk, PhotoImage, Canvas, NW
from typing import List, Tuple, Optional

from numpy import array

from algo.brehensam import in_view_range
from algo.lee import parcours_largeur
from tools.gene_maze_dfs import generate_maze


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

@dataclass
class Weapon:
    name: str
    damage_dice: str
    image: PhotoImage


@dataclass
class Armor:
    name: str
    ac: str
    image: PhotoImage


class PotionType(Enum):
    LIGHT_HEAL = '1d6'
    MEDIUM_HEAL = '2d6'
    HEAVY_HEAL = '3d6'
    CURE = 'Poison'
    SPEED = 'Speed'


@dataclass
class Potion:
    name: str
    type: PotionType
    image: PhotoImage


@dataclass
class MonsterType:
    name: str
    hit_dice: str
    damage_dice: str
    attack_bonus: int
    ac: int
    speed: int
    xp: int
    cr: int


@dataclass
class Monster(MonsterType):
    x: int
    y: int
    id: int = None
    image: PhotoImage = None
    hp: int = field(init=False)
    max_hp: int = field(init=False)

    def __post_init__(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        print(dice_count)
        self.hp = sum([randint(1, roll_dice) for _ in range(dice_count)])
        self.max_hp = self.hp

    def __repr__(self):
        return f'{self.name} {(self.x, self.y)}'

    @property
    def damage_roll(self) -> int:
        if 'd' not in self.damage_dice:
            return int(self.damage_dice)
        dice_count, damage_dice = self.damage_dice.split('d')
        if '+' in damage_dice:
            damage_dice, bonus_damage = map(int, damage_dice.split('+'))
            return sum([randint(1, damage_dice) + bonus_damage for _ in range(int(dice_count))])
        elif '-' in damage_dice:
            damage_dice, bonus_damage = map(int, damage_dice.split('-'))
            return sum([randint(1, damage_dice) - bonus_damage for _ in range(int(dice_count))])

    def attack(self, hero, can: Canvas):
        attack_roll = randint(1, 20) + self.attack_bonus
        if self.hp > 0 and attack_roll > hero.armor.ac:
            damage: int = self.damage_roll
            print(f'{self.name.title()} hits hero for {damage} hp')
            hero.hp -= damage
            if hero.hp <= 0:
                print(f'Hero is killed!')
                print(f'GAME OVER!!!')
                photo_rip: PhotoImage = PhotoImage(file=f"{path}/sprites/rip.png")
                can.itemconfigure(hero.id, image=photo_rip)
                # can.photo_hero = photo_rip
                can.dead = photo_rip
        else:
            print(f'{self.name.title()} misses hero')


@dataclass
class Character:
    x: int
    y: int
    speed: int
    hp: int
    max_hp: int
    weapon: Weapon
    armor: Armor
    gold: int = 0
    xp: int = 0
    potions: int = 0
    level: int = 1
    image: PhotoImage = None
    id: int = None

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f'Hero {(self.x, self.y)}'

    @property
    def img_pos(self):
        return self.x * (size_sprite + 1), self.y * (size_sprite + 1)

    def drink_potion(self, event, app):
        if self.potions:
            hp_recovered = randint(1, 80)
            self.hp = min(self.hp + hp_recovered, self.max_hp)
            status: str = 'fully' if self.hp == self.max_hp else 'partially'
            print(f'Hero drinks potion and is ** {status} ** healed!')
            self.potions -= 1
            app.refresh_title()
        else:
            print(f'Hero has ** no potion ** left!')

    @property
    def damage_roll(self) -> int:
        dice_count, roll_dice = map(int, self.weapon.damage_dice.split('d'))
        return sum([randint(1, roll_dice) for _ in range(dice_count)])

    def attack(self, monster: Monster):
        attack_roll = randint(1, 20)
        if attack_roll > monster.ac:
            damage: int = self.damage_roll
            print(f'Hero hits {monster.name.title()} for {damage} hp')
            monster.hp -= damage
            if monster.hp < 0:
                print(f'{monster.name.title()} is killed!')
                self.xp += monster.xp
                if self.xp > 500 * self.level:
                    self.level += 1
                    print(f'Hero ** gained a level! **')
                    new_hp = randint(1, 10)
                    print(f'Hero ** gained {new_hp} HP! **')
                    self.hp += new_hp
                    self.max_hp += new_hp
        else:
            print(f'Hero misses {monster.name.title()}')


@dataclass
class Treasure:
    # type: Potion | Armor | Weapon
    gold: int
    potion: bool
    id: int = None
    image: PhotoImage = None

    def __repr__(self):
        return f'{self.gold} {self.potion} {self.id}'


def find_path(start: tuple, end: tuple, carte: List) -> Optional[List[tuple]]:
    dist, pred = parcours_largeur(carte, *start, *end)

    path: List[tuple] = []

    if dist != float('inf'):
        path.append(end)
        while end != start:
            end = pred[end]
            path.append(end)

    return path[::-1]


def load_new_maze(level: int):
    width = height = 30
    maze, start, end = generate_maze(width, height)
    new_maze = [['.'] * width for _ in range(height)]
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            new_maze[i][j] = '#' if cell else '.'
    x, y = start
    if level > 1:
        new_maze[y][x] = '<'
    x, y = end
    new_maze[y - 1][x] = '>'
    return [''.join(row) for row in new_maze][:-1]


class App(Tk):
    maze: List
    width: int
    height: int
    canvas: Canvas = None
    walls: List = None
    hero: Character = None
    monsters: List[MonsterType] = None
    enemies: List[Monster] = None
    treasures: List[Treasure] = None
    level: int = 1

    def __init__(self):
        super().__init__()

        ## Setting up Initial Things
        self.title("Level 1")
        self.geometry("640x640")
        self.resizable(True, True)
        self.iconphoto(False, PhotoImage(file=f"{path}/sprites/beholder.png"))

        self.maze = self.load_maze(self.level) if not REMI else load_new_maze(self.level)

        self.height = len(self.maze)

        self.width = max([len(self.maze[i]) for i in range(self.height)])
        self.walls = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] == '#']

        monster_names: List[str] = ['ankheg', 'baboon', 'bat', 'blob', 'crab', 'ghost', 'goblin', 'eagle', 'harpy', 'lizard', 'mimic', 'owl', 'rat', 'rat_scull', 'skeleton', 'snake',
                                    'spider', 'tentacle', 'wasp', 'wolf']
        monsters: List[MonsterType] = [request_monster_type(name) for name in monster_names]
        self.monsters = list(filter(None, monsters))

        # Initialisation du Canvas, entités de jeu et touches d'actions
        self.canvas, self.hero, self.enemies, self.treasures = self.display(stair_pos=(1, 1))

        # Initialisation des fonctions événementielles
        self.init_touches()

    def update_level(self, level: int, remi=False):
        """
            display new level
        :param level: +/- 1
        :return: None
        """
        self.level += level
        self.refresh_title()
        self.maze = self.load_maze(self.level) if not REMI else load_new_maze(self.level)
        self.height, self.width = len(self.maze), len(self.maze[0])
        self.walls = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] in ('+', '-', '|', '-', '#')]
        # self.canvas.delete("all")
        self.canvas.destroy()
        self.geometry(f'{self.width * size_sprite}x{self.height * size_sprite}')
        stair: str = '<' if level == 1 else '>'
        stair_pos = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] == stair][0]
        self.canvas, self.hero, self.enemies, self.treasures = self.display(stair_pos)
        self.init_touches()

    def load_maze(self, level: int) -> List:
        """
        Charge le labyrinthe depuis le fichier level.txt
        nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
        Valeur de retour :
        - une liste avec les données du labyrinthe
        """
        try:
            with open(resource_path(f"{path}/maze_tk/level_{level}.txt"), newline='') as fic:
                data = fic.readlines()
        except IOError:
            print("Impossible de lire le fichier {}.txt".format(level))
            exit(1)
        for i in range(len(data)):
            data[i] = data[i].strip()
        width = max([len(data[i]) for i in range(len(data))])
        for i in range(len(data)):
            data[i] = "{:{g}}".format(data[i], g = f"^{width}")
        return data

    def display(self, stair_pos) -> Tuple[Canvas, List[Character], List[Treasure]]:
        can: Canvas = Canvas(self, width=size_sprite * self.width, height=size_sprite * self.height, bg="ivory")
        photo_wall: PhotoImage = PhotoImage(file=resource_path(f"{path}/sprites/WallTile1.png"))
        photo_treasure: PhotoImage = PhotoImage(file=resource_path(f"{path}/sprites/treasure.png"))
        # photo_enemy: PhotoImage = PhotoImage(file=f"{path}/sprites/enemy.png")
        # photo_exit: PhotoImage = PhotoImage(file=f"{path}/sprites/exit.png")
        photo_downstairs: PhotoImage = PhotoImage(file=resource_path(f"{path}/sprites/DownStairs.png"))
        photo_upstairs: PhotoImage = PhotoImage(file=resource_path(f"{path}/sprites/UpStairs.png"))
        photo_hero: PhotoImage = PhotoImage(file=resource_path(f"{path}/sprites/hero.png"))

        if not self.hero:
            # Initialisation du personnage
            starting_positions: List[tuple] = [(x, y) for x in range(self.width) for y in range(self.height) if self.maze[y][x] == '.']
            hero_x, hero_y = choice(starting_positions)
            # hero_x, hero_y = 0, 0
            start_armor: Armor = Armor(name='Plate Armor', ac=18, image=PhotoImage(file=resource_path(f'{path}/sprites/beholder.png')))
            start_weapon: Weapon = Weapon(name='Greatsword', damage_dice='2d6', image=PhotoImage(file=resource_path(f'{path}/sprites/beholder.png')))
            hero: Character = Character(x=hero_x, y=hero_y, speed=15, hp=10, max_hp=10, weapon=start_weapon, armor=start_armor, image=photo_hero)
            hero.id = can.create_image(*hero.img_pos, anchor=NW, image=hero.image)
            can.photo_hero = photo_hero
        else:
            hero = self.hero
            hero.x, hero.y = stair_pos
            hero.id = can.create_image(*hero.img_pos, anchor=NW, image=hero.image)
            can.hero_id = hero.id
            can.photo_hero = photo_hero

        rating = lambda m: m.cr < (hero.level / 4 if hero.level < 5 else hero.level / 2)
        # monster_candidates: List[MonsterType] = list(filter(lambda m: m.cr < self.level, self.monsters))
        monster_candidates: List[MonsterType] = list(filter(rating, self.monsters))

        enemies: List[Monster] = []
        treasures: dict = {}
        for y in range(self.height):
            for x in range(self.width):
                image: PhotoImage = None
                img_pos: tuple = x * size_sprite, y * size_sprite
                # img_pos: tuple = x * size_sprite + 1, y * size_sprite + 1
                match self.maze[y][x]:
                    # Murs
                    case '+' | '-' | '|' | '-' | '#':
                        can.create_image(*img_pos, anchor=NW, image=photo_wall)
                        can.photo_wall = photo_wall
                    # Trésors
                    case '1' | '2' | '3':
                        gold: int = randint(50, 300) * self.level
                        has_potion: bool = randint(1, 3) == 2
                        treasure: Treasure = Treasure(gold=gold, potion=has_potion, image=photo_treasure)
                        treasure.id = can.create_image(*img_pos, anchor=NW, image=photo_treasure)
                        treasures[(x, y)] = treasure
                        # can.photo_treasure = photo_treasure
                    # Ennemis
                    case '$':
                        m: MonsterType = choice(monster_candidates)
                        photo_enemy: PhotoImage = PhotoImage(file=resource_path(f"{path}/sprites/rpgcharacterspack/monster_{m.name}.png"))
                        enemy: Monster = Monster(name=m.name,
                                                 image=photo_enemy,
                                                 hit_dice=m.hit_dice,
                                                 damage_dice=m.damage_dice,
                                                 attack_bonus=m.attack_bonus,
                                                 ac=m.ac,
                                                 speed=m.speed,
                                                 xp=m.xp,
                                                 cr=m.cr,
                                                 x=x,
                                                 y=y)
                        enemy.id = can.create_image(*img_pos, anchor=NW, image=photo_enemy)
                        # can.enemy_id = enemy.id
                        enemies.append(enemy)
                    # Escaliers
                    case '>':
                        can.create_image(*img_pos, anchor=NW, image=photo_downstairs)
                        can.photo_downstairs = photo_downstairs
                    case '<':
                        can.create_image(*img_pos, anchor=NW, image=photo_upstairs)
                        can.photo_upstairs = photo_upstairs

        can.pack()
        return can, hero, enemies, treasures

    def disable_touches(self):
        self.unbind('p')
        self.unbind("<Right>")
        self.unbind("<Left>")
        self.unbind("<Up>")
        self.unbind("<Down>")

    def init_touches(self):
        """
        Initialisation du comportement des touches du clavier
        canvas : canevas où afficher les sprites
        maze : liste contenant le labyrinthe
        hero : personnage à contrôler par le joueur
        Pas de valeur de retour
        """
        self.disable_touches()
        self.bind('p', lambda event, c=self.hero, app=self: c.drink_potion(event, app))
        self.bind("d", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "right", m, h, M))
        self.bind("q", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "left", m, h, M))
        self.bind("z", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "up", m, h, M))
        self.bind("s", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "down", m, h, M))
        self.bind("<Right>", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "right", m, h, M))
        self.bind("<Left>", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "left", m, h, M))
        self.bind("<Up>", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "up", m, h, M))
        self.bind("<Down>", lambda event, can=self.canvas, m=self.maze, h=self.hero, M=self.enemies: self.move(event, can, "down", m, h, M))
        self.bind("<Escape>", lambda event, fen=self: self._destroy(event))

    def _destroy(self, event):
        """
        Fermeture de la fenêtre graphique
        event : objet décrivant l’événement ayant déclenché l’appel à cette fonction
        app : fenêtre graphique Tk
        Pas de valeur de retour
        """
        self.destroy()

    def refresh_title(self):
        if self.hero.hp > 0:
            self.title(
                f'Dungeon Level {self.level} | LVL {self.hero.level} HERO (XP = {self.hero.xp}) -> HP: {self.hero.hp}/{self.hero.max_hp} - Gold earned: {self.hero.gold} - Nb potions: {self.hero.potions}')
        else:
            self.title('** GAME OVER **')

    def move_enemies(self, can: Canvas, hero: Character, enemies: List[Character]):
        for enemy in enemies:
            # print(f'{enemy.name} {can.coords(enemy.id)} vs {(enemy.x, enemy.y)}')
            if hero.hp <= 0:
                break
            if enemy.hp <= 0:
                continue
            if abs(enemy.x - hero.x) + abs(enemy.y - hero.y) == 1:
                enemy.attack(hero, can)
                if hero.hp <= 0:
                    self.disable_touches()
                    return
                continue
            obstacles = [*self.walls] + [(e.x, e.y) for e in enemies if e != enemy]
            carte = [[1] * self.width for _ in range(self.height)]
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) in obstacles:
                        carte[y][x] = 0
            if in_view_range(enemy.x, enemy.y, hero.x, hero.y, self.walls):
                # print(f'{enemy.name} sees Hero on {(hero.x, hero.y)}!')
                path = find_path(start=(enemy.x, enemy.y), end=(hero.x, hero.y), carte=carte)
                # print(f'{enemy.name} path to hero: {path}')
                if not path or len(path) == 1:
                    continue
                speed_ratio: int = (enemy.speed - hero.speed) // hero.speed
                #print(f'speed_ratio: {speed_ratio} - path: {path}')
                dist = min(speed_ratio, len(path))
                new_x, new_y = path[dist + 1] if len(path) > 3 else path[1]
                can.moveto(enemy.id, new_x * size_sprite, new_y * size_sprite)
                # print(f'{enemy.name} moves from {(enemy.x, enemy.y)} to {(new_x, new_y)}')
                enemy.x, enemy.y = new_x, new_y
        can.update()
        self.refresh_title()

    def move(self, event, can: Canvas, direction: str, maze: List, hero: Character, enemies: List[Character]):
        x, y = hero.x, hero.y
        match direction:
            case 'R' | 'r' | 'right':
                if x == self.width - 1:
                    return
                x += 1
            case 'L' | 'l' | 'left':
                if x == 0:
                    return
                x -= 1
            case 'D' | 'd' | 'down':
                if y == self.height - 1:
                    return
                y += 1
            case 'U' | 'u' | 'up':
                if y == 0:
                    return
                y -= 1

        match maze[y][x]:
            case '#':
                print(f'Invalid move!')
                return
            case '>':
                print(f'Hero found downstairs!')
                self.update_level(level=1)
            case '<':
                print(f'Hero found upstairs!')
                self.update_level(level=-1)
            case '1' | '2' | '3':
                if (x, y) in self.treasures:
                    print(f'Hero gained a treasure!')
                    treasure: Treasure = self.treasures[(x, y)]
                    del self.treasures[(x, y)]
                    self.canvas.delete(treasure.id)
                    hero.gold += treasure.gold
                    if treasure.potion:
                        hero.potions += 1
                        print(f'Hero found a potion!')
                    self.refresh_title()

        enemy_pos = [(e.x, e.y) for e in enemies]
        if (x, y) in enemy_pos:
            monster: Monster = [m for m in enemies if (m.x, m.y) == (x, y)][0]
            # Hero has initiative!
            hero.attack(monster)
            # print(f'{monster} vs {hero}')
            if monster.hp < 0:
                enemies.remove(monster)
                enemy_pos.remove((x, y))
                # self.maze[y][x] = '.'
                can.delete(monster.id)
            else:
                # Monster fights back!
                monster.attack(hero, can)
                if hero.hp <= 0:
                    can.update()
                    self.disable_touches()
                self.refresh_title()
                return
        can.moveto(hero.id, x * size_sprite, y * size_sprite)
        # print(f'hero pos: {(char.x, char.y)}')
        hero.x, hero.y = x, y
        self.move_enemies(can, hero, enemies)
        can.update()


"""
    initialize all map cells to walls.
    pick a map cell as the starting point.
    turn the selected map cell into floor.
    while insufficient cells have been turned into floor,
    take one step in a random direction.
    if the new map cell is wall,
    turn the new map cell into floor and increment the count of floor tiles.
"""



def request_monster_type(index_name: str) -> Optional[MonsterType]:
    try:
        with open(resource_path(f"{path}/data/monsters/{index_name}.json"), "r") as f:
            data = json.loads(f.read())
        attack_bonus: int = 0
        match index_name:
            case 'ankheg':
                damage_dice = '2d6+3'
                speed = data['speed']['walk']
            case 'baboon':
                damage_dice = '1d4-1'
                speed = data['speed']['walk']
            case 'bat':
                damage_dice = '1'
                speed = data['speed']['fly']
            case 'blob':
                return None
            case 'crab':
                damage_dice = '1'
                speed = data['speed']['walk']
            case 'ghost':
                damage_dice = '4d6+3'
                speed = data['speed']['fly']
                attack_bonus = 5
            case 'goblin':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
                attack_bonus = 4
            case 'harpy':
                damage_dice = '2d4+1'
                speed = data['speed']['fly']
                attack_bonus = 3
            case 'lizard':
                damage_dice = '1'
                speed = data['speed']['walk']
            case 'mimic':
                damage_dice = '1d8+3'
                speed = data['speed']['walk']
                attack_bonus = 3
            case 'owl':
                damage_dice = '1d6+2'
                speed = data['speed']['fly']
                attack_bonus = 3
            case 'eagle':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
            case 'goblin':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
            case 'rat':
                damage_dice = '1'
                speed = data['speed']['walk']
            case 'rat_scull':
                return None
            case 'skeleton':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
                attack_bonus = 4
            case 'snake':
                return None
            case 'spider':
                damage_dice = '1'
                speed = data['speed']['walk']
                attack_bonus = 4
            case 'tentacle':
                return None
            case 'wasp':
                return None
            case 'wolf':
                damage_dice = '2d4+2'
                speed = data['speed']['walk']
                attack_bonus = 4
        return MonsterType(name=index_name,
                           hit_dice=data['hit_dice'],
                           damage_dice=damage_dice,
                           attack_bonus=attack_bonus,
                           ac=data['armor_class'],
                           speed=int(speed.split()[0]),
                           xp=data['xp'],
                           cr=data['challenge_rating'])
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    levels: List[str] = ['level_1', 'level_2']
    size_sprite = 32
    path = os.path.dirname(__file__)
    REMI = False

    # Uncomment these lines to generate levels on output console
    # w, h = 40, 20
    # n = w * h // 2  # could be modified but 50% of walkable cells seems a good ratio - Do not keep maps with too big open fields, it is ugly :-)
    # random_level: List[str] = generate_maze(width=w, height=h, n_cells=n)
    #
    # for line in random_level:
    #     print(''.join(line))
    #
    # exit(0)

    app = App()
    app.mainloop()
