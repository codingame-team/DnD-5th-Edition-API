import os
import random
import sys
import time
import curses
from logging import debug
from typing import List
# from tools.gene_maze_dfs import generate_maze

from tools.common import resource_path

SPACING = 2

class Camera:
    def __init__(self, map_width, map_height, view_width, view_height):
        self.map_width = map_width
        self.map_height = map_height
        self.view_width = view_width // 2  # Adjust for double spacing
        self.view_height = view_height
        self.x = 0
        self.y = 0

    def follow(self, target):
        self.x = max(0, min(target.x - self.view_width // 2, self.map_width - self.view_width))
        self.y = max(0, min(target.y - self.view_height // 2, self.map_height - self.view_height))

class Entity:
    def __init__(self, name, x, y, hp, attack):
        self.name = name
        self.x = x
        self.y = y
        self.hp = hp
        self.attack = attack

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

    def heal(self, amount):
        self.hp = min(100, self.hp + amount)

class Player(Entity):
    def __init__(self, name="Héros", x=0, y=0):
        super().__init__(name, x, y, 100, 20)

class Enemy(Entity):
    def __init__(self, name="Monstre", x=0, y=0):
        super().__init__(name, x, y, 50, 10)

def load_new_maze_old(level: int = 1) -> List[str]:
    width = height = 30
    maze, _, _ = generate_maze(width, height)
    return ["".join("#" if cell else " " for cell in row) for row in maze][:-1]

def load_maze(level: int = 1) -> List:
	"""
	Charge le labyrinthe depuis le fichier level.txt
	nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
	Valeur de retour :
	- une liste avec les données du labyrinthe
	"""
	try:
		path = os.path.dirname(__file__)
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

def handle_input(stdscr, player, game_map, enemies):
    key = stdscr.getch()
    move_map = {curses.KEY_UP: (0, -1), ord("z"): (0, -1),
                curses.KEY_DOWN: (0, 1), ord("s"): (0, 1),
                curses.KEY_LEFT: (-1, 0), ord("q"): (-1, 0),
                curses.KEY_RIGHT: (1, 0), ord("d"): (1, 0)}
    if key in move_map:
        dx, dy = move_map[key]
        new_x, new_y = player.x + dx, player.y + dy
        if game_map[new_y][new_x] != "#":
            player.x, player.y = new_x, new_y
        for enemy in enemies:
            if (new_x, new_y) == (enemy.x, enemy.y):
                combat(stdscr, player, enemy)
                if enemy.hp <= 0:
                    enemies.remove(enemy)

def initialize_enemies(num_enemies, game_map):
    map_width, map_height = len(game_map[0]), len(game_map)
    return [Enemy(x=random.randint(1, map_width - 2), y=random.randint(1, map_height - 2)) for _ in range(num_enemies)]

def display_status(stdscr, player, enemy):
    stdscr.clear()
    stdscr.addstr(1, 1, f"Nom du joueur: {player.name}")
    stdscr.addstr(2, 1, f"Vie du joueur: {player.hp}")
    stdscr.addstr(4, 1, f"Nom de l'ennemi: {enemy.name}")
    stdscr.addstr(5, 1, f"Vie de l'ennemi: {enemy.hp}")
    stdscr.refresh()

def combat(stdscr, player, enemy):
    while player.hp > 0 and enemy.hp > 0:
        display_status(stdscr, player, enemy)
        stdscr.addstr(7, 1, "(a - Attaquer, h - Soigner, q - Quitter): ")
        key = stdscr.getch()
        if key == ord("a"):
            enemy.take_damage(random.randint(15, player.attack))
        elif key == ord("h"):
            player.heal(random.randint(10, 30))
        elif key == ord("q"):
            break
        if enemy.hp > 0:
            player.take_damage(random.randint(5, enemy.attack))
    stdscr.addstr(12, 1, "Combat terminé! Press any key to continue.")
    stdscr.refresh()
    stdscr.getch()

def draw_map(stdscr, game_map, player, enemies, camera):
    for y in range(camera.view_height):
        for x in range(camera.view_width):
            map_x, map_y = x + camera.x, y + camera.y
            screen_x = x * SPACING
            if 0 <= map_x < len(game_map[0]) and 0 <= map_y < len(game_map):
                stdscr.addch(y, screen_x, game_map[map_y][map_x])
    stdscr.addch((player.y - camera.y), (player.x - camera.x) * SPACING, "@")
    for enemy in enemies:
        stdscr.addch((enemy.y - camera.y), (enemy.x - camera.x) * SPACING, "E")

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)
    curses.start_color()
    term_height, term_width = stdscr.getmaxyx()
    game_map = load_maze()
    camera = Camera(len(game_map[0]), len(game_map), term_width // 2, term_height - 2)
    player = Player(x=len(game_map[0]) // 2, y=len(game_map) // 2)
    enemies = initialize_enemies(5, game_map)
    while True:
        camera.follow(player)
        stdscr.clear()
        draw_map(stdscr, game_map, player, enemies, camera)
        stdscr.addstr(camera.view_height, 0, f"HP: {player.hp} | Pos: ({player.x},{player.y})")
        if stdscr.getch() == curses.KEY_RESIZE:
            term_height, term_width = stdscr.getmaxyx()
            camera.view_width = min(term_width, len(game_map[0]))
            camera.view_height = min(term_height - 2, len(game_map))
        handle_input(stdscr, player, game_map, enemies)

if __name__ == "__main__":
    curses.wrapper(main)
