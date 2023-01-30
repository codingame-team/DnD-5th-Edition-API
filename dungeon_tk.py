import os
from dataclasses import dataclass
from random import choice, randint
from tkinter import Tk, PhotoImage, Canvas, NW
from typing import List, Tuple


@dataclass
class Character:
    x: int
    y: int
    image: PhotoImage
    id: int = None
    gold: int = 0

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    @property
    def img_pos(self):
        return self.x * (size_sprite + 1), self.y * (size_sprite + 1)


@dataclass
class Treasure:
    gold: int
    image: PhotoImage
    id: int = None

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f'{self.id} {self.gold}'


class App(Tk):
    maze: List
    width: int
    height: int
    canvas: Canvas = None
    walls: List = None
    hero: Character = None
    enemies: List[Character] = None
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
        # Initialisation du personnage
        photo_hero: PhotoImage = PhotoImage(file=f"{path}/sprites/hero.png")
        starting_positions: List[tuple] = [(x, y) for x in range(self.width) for y in range(self.height) if (x, y) not in self.walls]
        hero_x, hero_y = choice(starting_positions)
        hero_x, hero_y = 17, 18
        self.hero: Character = Character(x=hero_x, y=hero_y, image=photo_hero)

        # Initialisation du Canvas, entités de jeu et touches d'actions
        self.canvas, self.enemies, self.treasures = self.display()
        self.init_touches()

    def update_level(self, level: int):
        """
            display new level
        :param level: +/- 1
        :return: None
        """
        self.level += level
        self.title(f'Level {self.level} - Gold earned: {self.hero.gold}')
        self.maze = self.load_maze(f'level_{self.level}')
        self.height, self.width = len(self.maze), len(self.maze[0])
        self.walls = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] in ('+', '-', '|', '-', '#')]
        # self.canvas.delete("all")
        self.canvas.destroy()
        self.geometry(f'{self.width * size_sprite}x{self.height * size_sprite}')
        stair: str = '<' if level == 1 else '>'
        self.hero.x, self.hero.y = [(x, y) for y in range(self.height) for x in range(self.width) if self.maze[y][x] == stair][0]
        self.canvas, self.enemies, self.treasures = self.display()
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

    def display(self) -> Tuple[Canvas, List[Character], List[Treasure]]:
        can: Canvas = Canvas(self, width=size_sprite * self.width, height=size_sprite * self.height, bg="ivory")
        photo_wall: PhotoImage = PhotoImage(file=f"{path}/sprites/WallTile1.png")
        photo_treasure: PhotoImage = PhotoImage(file=f"{path}/sprites/treasure.png")
        photo_enemy: PhotoImage = PhotoImage(file=f"{path}/sprites/enemy.png")
        photo_exit: PhotoImage = PhotoImage(file=f"{path}/sprites/exit.png")
        photo_downstairs: PhotoImage = PhotoImage(file=f"{path}/sprites/DownStairs.png")
        photo_upstairs: PhotoImage = PhotoImage(file=f"{path}/sprites/UpStairs.png")

        enemies: List[Character] = []
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
                        gold = randint(50, 300) * self.level
                        treasure: Treasure = Treasure(gold, photo_treasure)
                        treasure.id = can.create_image(*img_pos, anchor=NW, image=photo_treasure)
                        treasures[(x, y)] = treasure
                        # can.photo_treasure = photo_treasure
                    # Ennemis
                    case '$':
                        enemy: Character = Character(x, y, photo_enemy)
                        enemy.id = can.create_image(*img_pos, anchor=NW, image=photo_enemy)
                        enemies.append(enemy)
                    # Escaliers
                    case '>':
                        can.create_image(*img_pos, anchor=NW, image=photo_downstairs)
                        can.photo_downstairs = photo_downstairs
                    case '<':
                        can.create_image(*img_pos, anchor=NW, image=photo_upstairs)
                        can.photo_upstairs = photo_upstairs
        self.hero.id = can.create_image(*self.hero.img_pos, anchor=NW, image=self.hero.image)
        can.pack()
        return can, enemies, treasures

    def init_touches(self):
        """
        Initialisation du comportement des touches du clavier
        canvas : canevas où afficher les sprites
        maze : liste contenant le labyrinthe
        hero : personnage à contrôler par le joueur
        Pas de valeur de retour
        """
        self.unbind("<Right>")
        self.unbind("<Left>")
        self.unbind("<Up>")
        self.unbind("<Down>")
        self.bind("<Right>", lambda event, can=self.canvas, m=self.maze, c=self.hero: self.move(event, can, "right", m, c))
        self.bind("<Left>", lambda event, can=self.canvas, m=self.maze, c=self.hero: self.move(event, can, "left", m, c))
        self.bind("<Up>", lambda event, can=self.canvas, m=self.maze, c=self.hero: self.move(event, can, "up", m, c))
        self.bind("<Down>", lambda event, can=self.canvas, m=self.maze, c=self.hero: self.move(event, can, "down", m, c))
        self.bind("<Escape>", lambda event, fen=self: self._destroy(event))

    def _destroy(self, event):
        """
        Fermeture de la fenêtre graphique
        event : objet décrivant l’événement ayant déclenché l’appel à cette fonction
        app : fenêtre graphique Tk
        Pas de valeur de retour
        """
        self.destroy()

    def move(self, event, can: Canvas, direction: str, maze: List, char: Character):
        dx = dy = 0
        x, y = char.x, char.y
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
                print(f'Hero blocked by a monster!')
                return
            case '1' | '2' | '3':
                if (x, y) in self.treasures:
                    print(f'Hero gained a treasure!')
                    treasure: Treasure = self.treasures[(x, y)]
                    del self.treasures[(x, y)]
                    self.canvas.delete(treasure.id)
                    self.hero.gold += treasure.gold
                    self.title(f'Level {self.level} - Gold earned: {self.hero.gold}')

        can.move(char.id, dx, dy)
        # print(f'hero pos: {(char.x, char.y)}')
        char.x, char.y = x, y

"""
    initialize all map cells to walls.
    pick a map cell as the starting point.
    turn the selected map cell into floor.
    while insufficient cells have been turned into floor,
    take one step in a random direction.
    if the new map cell is wall,
    turn the new map cell into floor and increment the count of floor tiles.
"""
if __name__ == "__main__":
    levels: List[str] = ['level_1', 'level_2']
    size_sprite = 31
    path = os.path.dirname(__file__)

    app = App('level_1')
    app.mainloop()
