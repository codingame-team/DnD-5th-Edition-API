import os
from dataclasses import dataclass, field
from time import sleep
from tkinter import Tk, Canvas, PhotoImage
from tkinter.constants import NW
from typing import List


@dataclass
class Character:
    x: int
    y: int
    image: PhotoImage
    id: int = None

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    @property
    def img_pos(self):
        return self.x * (size_sprite + 1), self.y * (size_sprite + 1)


def load_maze(level: str) -> List:
    """
    Charge le labyrinthe depuis le fichier level.txt
    nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
    Valeur de retour :
    - une liste avec les données du labyrinthe
    """
    try:
        with open(f"{path}/maze//{level}.txt", newline='') as fic:
            data = fic.readlines()
    except IOError:
        print("Impossible de lire le fichier {}.txt".format(level))
        exit(1)
    for i in range(len(data)):
        data[i] = data[i].strip()
    return data


def move(event, can: Canvas, direction: str, maze: List, char: Character):
    dx = dy = 0
    x, y = char.x, char.y
    match direction:
        case 'R' | 'r' | 'right':
            if x == width - 1:
                return
            x += 1
            dx = size_sprite + 1
        case 'L' | 'l' | 'left':
            if x == 0:
                return
            x -= 1
            dx = -size_sprite - 1
        case 'D' | 'd' | 'down':
            if y == height - 1:
                return
            y += 1
            dy = size_sprite + 1
        case 'U' | 'u' | 'up':
            if y == 0:
                return
            y -= 1
            dy = -size_sprite - 1
    if (x, y) in walls:
        return
    blocking_enemy_pos = [(e.x, e.y) for e in enemies]
    if (x, y) in blocking_enemy_pos:
        print(f'blocked by a monster!')
        return
    can.move(char.id, dx, dy)
    char.x, char.y = x, y
    # can.coords(char.id, char.x, char.y)
    # print(f'hero pos: {(char.x, char.y)}')
    if maze[y][x] == 'O':
        print(f'Hero found the exit!')


def destroy(event, fenetre):
    """
    Fermeture de la fenêtre graphique
    event : objet décrivant l’événement ayant déclenché l’appel à cette
    fonction
    fenetre : fenêtre graphique
    Pas de valeur de retour
    """
    fenetre.destroy()


def init_touches(app: Tk, can: Canvas, maze: List, hero: Character):
    """
    Initialisation du comportement des touches du clavier
    canvas : canevas où afficher les sprites
    maze : liste contenant le labyrinthe
    hero : personnage à contrôler par le joueur
    perso : sprite représentant le personnage
    Pas de valeur de retour
    """
    app.bind("<Right>", lambda event, can=can, m=maze, char=hero: move(event, can, "right", m, char))
    app.bind("<Left>", lambda event, can=can, m=maze, char=hero: move(event, can, "left", m, char))
    app.bind("<Up>", lambda event, can=can, m=maze, char=hero: move(event, can, "up", m, char))
    app.bind("<Down>", lambda event, can=can, m=maze, char=hero: move(event, can, "down", m, char))
    app.bind("<Escape>", lambda event, fen=app: destroy(event, fen))


def display(maze: List, app: Tk, size_sprite: int, hero: Character) -> Canvas:
    can: Canvas = Canvas(app, width=620, height=620, bg="ivory")
    photo_wall: PhotoImage = PhotoImage(file=f"{path}/sprites/WallTile1.png")
    photo_treasure: PhotoImage = PhotoImage(file=f"{path}/sprites/treasure.png")
    photo_enemy: PhotoImage = PhotoImage(file=f"{path}/sprites/enemy.png")
    photo_exit: PhotoImage = PhotoImage(file=f"{path}/sprites/exit.png")

    enemies: List[Character] = []
    for y in range(height):
        for x in range(width):
            image: PhotoImage = None
            img_pos: tuple = x * (size_sprite + 1), y * (size_sprite + 1)
            match maze[y][x]:
                # Murs
                case '+' | '-' | '|' | '-':
                    can.create_image(*img_pos, anchor=NW, image=photo_wall)
                    can.photo_wall = photo_wall
                # Trésors
                case '1' | '2' | '3':
                    can.create_image(*img_pos, anchor=NW, image=photo_treasure)
                    can.photo_treasure = photo_treasure
                # Ennemis
                case '$':
                    enemy: Character = Character(x, y, photo_enemy)
                    enemy.id = can.create_image(*img_pos, anchor=NW, image=photo_enemy)
                    enemies.append(enemy)
                # Sortie
                case 'O':
                    can.create_image(*img_pos, anchor=NW, image=photo_exit)
                    can.photo_exit = photo_exit

    hero.id = can.create_image(*hero.img_pos, anchor=NW, image=hero.image)

    can.pack()

    return can, enemies


if __name__ == "__main__":
    path = os.path.dirname(__file__)

    # Initialisation environnement graphique
    app = Tk()
    app.title("Tryout Tk")
    size_sprite = 30

    # Chargement du labyrinthe
    maze: List[str] = load_maze("level_1")
    height, width = len(maze), len(maze[0])
    walls = [(x, y) for y in range(height) for x in range(width) if maze[y][x] in ('+', '-', '|', '-')]

    # Initialisation du personnage
    photo_hero: PhotoImage = PhotoImage(file=f"{path}/sprites/hero.png")
    hero: Character = Character(x=1, y=1, image=photo_hero)

    canvas, enemies = display(maze=maze, app=app, size_sprite=size_sprite, hero=hero)

    init_touches(app=app, can=canvas, maze=maze, hero=hero)

    app.mainloop()
