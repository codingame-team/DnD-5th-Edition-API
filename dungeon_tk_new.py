import json
import os
from dataclasses import dataclass, field
from enum import Enum
from random import choice, randint
from tkinter import Tk, PhotoImage, Canvas, NW
from typing import List, Tuple, Optional


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


@dataclass
class Character:
    x: int
    y: int
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

    @property
    def img_pos(self):
        return self.x * (size_sprite + 1), self.y * (size_sprite + 1)

    def drink_potion(self, event, app):
        if self.potions:
            hp_recovered = randint(1, 8)
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


@dataclass
class Treasure:
    # type: Potion | Armor | Weapon
    gold: int
    potion: bool
    id: int = None
    image: PhotoImage = None

    def __repr__(self):
        return f'{self.gold} {self.potion} {self.id}'


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

    def __init__(self, level: str):
        super().__init__()

        ## Setting up Initial Things
        self.title("Level 1")
        self.geometry("640x640")
        self.resizable(True, True)
        self.iconphoto(False, PhotoImage(file=f"{path}/sprites/beholder.png"))

        self.maze = self.load_maze(level)
        self.height, self.width = len(self.maze), len(self.maze[0])
        self.walls = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] in ('+', '-', '|', '-', '#')]

        monster_names: List[str] = ['ankheg', 'baboon', 'bat', 'blob', 'crab', 'ghost', 'goblin', 'harpy', 'lizard', 'mimic', 'owl', 'rat', 'rat_scull', 'skeleton', 'snake',
                                    'spider', 'tentacle', 'wasp', 'wolf']
        monsters: List[MonsterType] = [request_monster_type(name) for name in monster_names]
        self.monsters = list(filter(None, monsters))

        # Initialisation du Canvas, entités de jeu et touches d'actions
        self.canvas, self.hero, self.enemies, self.treasures = self.display(stair_pos=(1, 1))

        # Initialisation des fonctions événementielles
        self.init_touches()

    def update_level(self, level: int):
        """
            display new level
        :param level: +/- 1
        :return: None
        """
        self.level += level
        self.refresh_title()
        self.maze = self.load_maze(f'level_{self.level}')
        self.height, self.width = len(self.maze), len(self.maze[0])
        self.walls = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] in ('+', '-', '|', '-', '#')]
        # self.canvas.delete("all")
        self.canvas.destroy()
        self.geometry(f'{self.width * size_sprite}x{self.height * size_sprite}')
        stair: str = '<' if level == 1 else '>'
        stair_pos = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] == stair][0]
        self.canvas, self.hero, self.enemies, self.treasures = self.display(stair_pos)
        self.init_touches()

    def load_maze(self, level: str) -> List:
        """
        Charge le labyrinthe depuis le fichier level.txt
        nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
        Valeur de retour :
        - une liste avec les données du labyrinthe
        """
        try:
            with open(f"{path}/maze/{level}.txt", newline='') as fic:
                data = fic.readlines()
        except IOError:
            print("Impossible de lire le fichier {}.txt".format(level))
            exit(1)
        for i in range(len(data)):
            data[i] = data[i].strip()
        return data

    def display(self, stair_pos) -> Tuple[Canvas, List[Character], List[Treasure]]:
        can: Canvas = Canvas(self, width=size_sprite * self.width, height=size_sprite * self.height, bg="ivory")
        photo_wall: PhotoImage = PhotoImage(file=f"{path}/sprites/WallTile1.png")
        photo_treasure: PhotoImage = PhotoImage(file=f"{path}/sprites/treasure.png")
        photo_enemy: PhotoImage = PhotoImage(file=f"{path}/sprites/enemy.png")
        photo_exit: PhotoImage = PhotoImage(file=f"{path}/sprites/exit.png")
        photo_downstairs: PhotoImage = PhotoImage(file=f"{path}/sprites/DownStairs.png")
        photo_upstairs: PhotoImage = PhotoImage(file=f"{path}/sprites/UpStairs.png")

        monster_candidates: List[MonsterType] = list(filter(lambda m: m.cr < self.level, self.monsters))

        enemies: List[Monster] = []
        treasures: dict = {}
        for y in range(self.height):
            for x in range(self.width):
                image: PhotoImage = None
                img_pos: tuple = x * (size_sprite + 1), y * (size_sprite + 1)
                match self.maze[y][x]:
                    # Murs
                    case '+' | '-' | '|' | '-' | '#':
                        can.create_image(*img_pos, anchor=NW, image=photo_wall)
                        can.photo_wall = photo_wall
                    # Trésors
                    case '1' | '2' | '3':
                        gold: int = randint(50, 300) * self.level
                        has_potion: bool = randint(1, 4) == 3
                        treasure: Treasure = Treasure(gold=gold, potion=has_potion, image=photo_treasure)
                        treasure.id = can.create_image(*img_pos, anchor=NW, image=photo_treasure)
                        treasures[(x, y)] = treasure
                        # can.photo_treasure = photo_treasure
                    # Ennemis
                    case '$':
                        m: MonsterType = choice(monster_candidates)
                        photo_enemy: PhotoImage = PhotoImage(file=f"{path}/sprites/rpgcharacterspack/monster_{m.name}.png")
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
                        can.enemy_id = enemy.id
                        enemies.append(enemy)
                    # Escaliers
                    case '>':
                        can.create_image(*img_pos, anchor=NW, image=photo_downstairs)
                        can.photo_downstairs = photo_downstairs
                    case '<':
                        can.create_image(*img_pos, anchor=NW, image=photo_upstairs)
                        can.photo_upstairs = photo_upstairs

        photo_hero: PhotoImage = PhotoImage(file=f"{path}/sprites/hero.png")

        if not self.hero:
            # Initialisation du personnage
            enemy_pos = [(e.x, e.y) for e in enemies]
            starting_positions: List[tuple] = [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in self.walls + enemy_pos]
            hero_x, hero_y = choice(starting_positions)
            # hero_x, hero_y = 17, 18
            start_armor: Armor = Armor(name='leather_armor', ac=6, image=PhotoImage(file=f'{path}/sprites/beholder.png'))
            start_weapon: Weapon = Weapon(name='dagger', damage_dice='1d4', image=PhotoImage(file=f'{path}/sprites/beholder.png'))
            hero: Character = Character(x=hero_x, y=hero_y, hp=10, max_hp=10, weapon=start_weapon, armor=start_armor, image=photo_hero)
            hero.id = can.create_image(*hero.img_pos, anchor=NW, image=hero.image)
            can.photo_hero = photo_hero
        else:
            hero = self.hero
            hero.x, hero.y = stair_pos
            hero.id = can.create_image(*hero.img_pos, anchor=NW, image=hero.image)
            can.hero_id = hero.id
            can.photo_hero = photo_hero
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

    def move(self, event, can: Canvas, direction: str, maze: List, hero: Character, enemies: List[Character]):
        dx = dy = 0
        x, y = hero.x, hero.y
        match direction:
            case 'R' | 'r' | 'right':
                if x == self.width - 1:
                    return
                x += 1
                dx = size_sprite + 1
            case 'L' | 'l' | 'left':
                if x == 0:
                    return
                x -= 1
                dx = -size_sprite - 1
            case 'D' | 'd' | 'down':
                if y == self.height - 1:
                    return
                y += 1
                dy = size_sprite + 1
            case 'U' | 'u' | 'up':
                if y == 0:
                    return
                y -= 1
                dy = -size_sprite - 1

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
            case '$':
                enemy_pos = [(e.x, e.y) for e in enemies]
                if (x, y) in enemy_pos:
                    monster: Monster = [m for m in enemies if (m.x, m.y) == (x, y)][0]
                    # Hero has initiative!
                    attack_roll = randint(1, 20)
                    if attack_roll > monster.ac:
                        damage: int = hero.damage_roll
                        print(f'Hero hits {monster.name.title()} for {damage} hp')
                        monster.hp -= damage
                        if monster.hp < 0:
                            print(f'{monster.name.title()} is killed!')
                            hero.xp += 10
                            if hero.xp > 500 * hero.level:
                                hero.level += 1
                                print(f'Hero ** gained a level! **')
                                new_hp = randint(1, 10)
                                print(f'Hero ** gained {new_hp} HP! **')
                                hero.hp += new_hp
                                hero.max_hp += new_hp
                                self.refresh_title()
                            enemies.remove(monster)
                            enemy_pos.remove((x, y))
                            # self.maze[y][x] = '.'
                            can.delete(monster.id)
                        else:
                            return
                    else:
                        print(f'Hero misses {monster.name.title()}')
                    attack_roll = randint(1, 20) + monster.attack_bonus
                    if monster.hp > 0 and attack_roll > hero.armor.ac:
                        damage: int = monster.damage_roll
                        print(f'{monster.name.title()} hits hero for {damage} hp')
                        hero.hp -= damage
                        if hero.hp < 0:
                            print(f'Hero is killed!')
                            print(f'GAME OVER!!!')
                            photo_rip: PhotoImage = PhotoImage(file=f"{path}/sprites/rip.png")
                            can.itemconfigure(hero.id, image=photo_rip)
                            # can.photo_hero = photo_rip
                            can.dead = photo_rip
                            can.update()
                            self.disable_touches()
                        self.refresh_title()
                    else:
                        print(f'{monster.name.title()} misses hero')
                    if (x, y) in enemy_pos:
                        return
                    # print(f'Hero blocked by a monster!')
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

        can.move(hero.id, dx, dy)
        # print(f'hero pos: {(char.x, char.y)}')
        hero.x, hero.y = x, y


"""
    initialize all map cells to walls.
    pick a map cell as the starting point.
    turn the selected map cell into floor.
    while insufficient cells have been turned into floor,
    take one step in a random direction.
    if the new map cell is wall,
    turn the new map cell into floor and increment the count of floor tiles.
"""


def generate_maze(width: int, height: int, n_cells: int) -> List[str]:
    """
        Method used to generate levels with shapes of caves (walls only)
    :param width: parameter to adjust to get nice looking caves
    :param height: parameter to adjust to get nice looking caves
    :param n_cells: parameter to adjust to get nice looking caves
    :return:
    """
    maze: List[str] = [['#'] * width for _ in range(height)]
    x, y = randint(1, width - 2), randint(1, height - 2)
    maze[y][x] = '.'
    dirs = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    while n_cells:
        candidates = [(x + dx, y + dy) for dx, dy in dirs if 0 < x + dx < width - 1 and 0 < y + dy < height - 1]
        x, y = choice(candidates)
        if maze[y][x] == '#':
            maze[y][x] = '.'
            n_cells -= 1
    return maze


def request_monster_type(index_name: str) -> Optional[MonsterType]:
    try:
        with open(f"{path}/data/monsters/{index_name}.json", "r") as f:
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
                speed = data['speed']['walk']
                attack_bonus = 3
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
                           speed=speed,
                           xp=data['xp'],
                           cr=data['challenge_rating'])
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    levels: List[str] = ['level_1', 'level_2']
    size_sprite = 31
    path = os.path.dirname(__file__)

    # Uncomment these lines to generate levels on output console
    # w, h = 40, 20
    # n = w * h // 2  # could be modified but 50% of walkable cells seems a good ratio - Do not keep maps with too big open fields, it is ugly :-)
    # random_level: List[str] = generate_maze(width=w, height=h, n_cells=n)
    #
    # for line in random_level:
    #     print(''.join(line))
    #
    # exit(0)

    app = App('level_1')
    app.mainloop()
