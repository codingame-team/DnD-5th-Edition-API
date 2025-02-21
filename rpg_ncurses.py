import random
import sys
import time
from _curses import KEY_RESIZE, resizeterm, start_color, resize_term

from curses import wrapper, curs_set, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_EXIT
from typing import List

from tools.gene_maze_dfs import generate_maze


class Camera:
    def __init__(self, map_width, map_height, view_width, view_height):
        self.map_width = map_width
        self.map_height = map_height
        self.view_width = view_width // 2  # Divide by 2 because of doubled spacing
        self.view_height = view_height
        self.x = 0
        self.y = 0

    def follow(self, target):
        # Center the camera on the target (player)
        self.x = target.x - self.view_width // 2
        self.y = target.y - self.view_height // 2

        # Keep camera within map bounds
        self.x = max(0, min(self.x, self.map_width - self.view_width))
        self.y = max(0, min(self.y, self.map_height - self.view_height))


# Classe pour le joueur
class Player:
    def __init__(self, name="Héros", x=0, y=0):
        self.name = name
        self.hp = 100
        self.attack = 20
        self.x = x
        self.y = y

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > 100:
            self.hp = 100


# Classe pour l'ennemi
class Enemy:
    def __init__(self, name="Monstre", x=0, y=0):
        self.name = name
        self.hp = 50
        self.attack = 10
        self.x = x
        self.y = y

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0


import fcntl
import termios
import struct


# Carte ASCII (exemple simple avec des murs et des espaces vides)
# def generate_map() -> List[str]:
#     game_map = []
#     for y in range(MAP_HEIGHT):
#         row = []
#         for x in range(MAP_WIDTH):
#             if x == 0 or y == 0 or x == MAP_WIDTH - 1 or y == MAP_HEIGHT - 1:
#                 row.append("#")  # Mur
#             else:
#                 row.append(" ")  # Espace vide
#         game_map.append(row)
#     return game_map


def load_new_maze(level: int = 1) -> List[str]:
    width = height = 30
    maze, start, end = generate_maze(width, height)
    new_maze = [["."] * width for _ in range(height)]
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            new_maze[i][j] = "#" if cell else " "
    return ["".join(row) for row in new_maze][:-1]


# Fonction pour afficher la fiche personnage
# def display_character_sheet(stdscr, player):
#     # Obtenir la taille de l'écran pour s'assurer que l'affichage est dans les limites
#     height, width = stdscr.getmaxyx()
#
#     # Assurez-vous que la fiche personnage est dans les limites de l'écran
#     if MAP_HEIGHT < height and MAP_WIDTH * 2 + 20 < width:
#         stdscr.addstr(0, MAP_WIDTH * 2 + 2, "Fiche Personnage")
#         stdscr.addstr(1, MAP_WIDTH * 2 + 2, f"Nom : {player.name}")
#         stdscr.addstr(2, MAP_WIDTH * 2 + 2, f"Vie : {player.hp}")
#         stdscr.addstr(3, MAP_WIDTH * 2 + 2, f"Attaque : {player.attack}")
#     else:
#         stdscr.addstr(0, 0, "L'écran est trop petit pour afficher la fiche personnage.")


# Fonction pour gérer les entrées du joueur
def handle_input(stdscr, player, game_map, enemies) -> bool:
    map_width, map_height = len(game_map[0]), len(game_map)

    key = stdscr.getch()
    new_x, new_y = player.x, player.y

    if key in {KEY_UP, ord("z"), ord("Z")}:
        new_y -= 1
    elif key in {KEY_DOWN, ord("s"), ord("S")}:
        new_y += 1
    elif key in {KEY_LEFT, ord("q"), ord("Q")}:
        new_x -= 1
    elif key in {KEY_RIGHT, ord("d"), ord("D")}:
        new_x += 1
    # elif key == 27:
    #     pass
    #     #return False

    # Empêcher le joueur de sortir de la carte ou de traverser les murs
    if 0 <= new_x < map_width and 0 <= new_y < map_height:
        if game_map[new_y][new_x] != "#":
            player.x, player.y = new_x, new_y

    # Vérifier si le joueur rencontre un ennemi
    for enemy in enemies:
        if (new_x, new_y) == (enemy.x, enemy.y):
            combat(stdscr, player, enemy)
            if enemy.hp <= 0:
                enemies.remove(enemy)

    # return True


# Fonction pour initialiser les ennemis
def initialize_enemies(num_enemies, game_map):
    map_width, map_height = len(game_map[0]), len(game_map)
    enemies = []
    while len(enemies) < num_enemies:
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)
        enemies.append(Enemy(name="Monstre", x=x, y=y))
    return enemies


# Fonction pour afficher l'état du jeu
def display_status(stdscr, player, enemy):
    stdscr.clear()

    # Affichage du joueur
    stdscr.addstr(1, 1, f"Nom du joueur: {player.name}")
    stdscr.addstr(2, 1, f"Vie du joueur: {player.hp}")

    # Affichage de l'ennemi
    stdscr.addstr(4, 1, f"Nom de l'ennemi: {enemy.name}")
    stdscr.addstr(5, 1, f"Vie de l'ennemi: {enemy.hp}")

    stdscr.refresh()


# Fonction pour gérer le combat
def combat(stdscr, player, enemy):
    while player.hp > 0 and enemy.hp > 0:
        display_status(stdscr, player, enemy)

        stdscr.addstr(
            7, 1, "Que voulez-vous faire ? (a - Attaquer, h - Soigner, q - Quitter): "
        )
        stdscr.refresh()
        key = stdscr.getch()

        if key == ord("a"):  # Attaque
            damage = random.randint(15, player.attack)
            enemy.take_damage(damage)
            stdscr.addstr(
                9, 1, f"Vous attaquez l'ennemi pour {damage} points de dégâts."
            )
            stdscr.refresh()
            time.sleep(1)

        elif key == ord("h"):  # Soigner
            heal_amount = random.randint(10, 30)
            player.heal(heal_amount)
            stdscr.addstr(9, 1, f"Vous vous soignez de {heal_amount} points de vie.")
            stdscr.refresh()
            time.sleep(1)

        elif key == ord("q"):  # Quitter
            break

        # L'ennemi riposte
        if enemy.hp > 0:
            enemy_damage = random.randint(5, enemy.attack)
            player.take_damage(enemy_damage)
            stdscr.addstr(
                10, 1, f"L'ennemi attaque pour {enemy_damage} points de dégâts."
            )
            stdscr.refresh()
            time.sleep(1)

        # Vérification de la victoire/défaite
        if player.hp <= 0:
            stdscr.addstr(12, 1, "Vous avez perdu le combat... Press any key to quit.")
            stdscr.refresh()
            stdscr.getch()
            break
        elif enemy.hp <= 0:
            stdscr.addstr(12, 1, "Vous avez vaincu l'ennemi ! Press any key to quit.")
            stdscr.refresh()
            stdscr.getch()
            break


def draw_map(stdscr, game_map, player, enemies, camera):
    map_width, map_height = len(game_map[0]), len(game_map)
    # Get the visible portion of the map
    for y in range(camera.view_height):
        for x in range(camera.view_width):
            # Convert screen coordinates to map coordinates
            map_x = x + camera.x
            map_y = y + camera.y

            # Calculate screen position with spacing
            screen_x = x * SPACING

            # Check if the position is within map bounds
            if 0 <= map_x < map_width and 0 <= map_y < map_height:
                # # Draw map tile
                # stdscr.addch(y, x, game_map[map_y][map_x])
                # Draw map tile with spacing
                stdscr.addch(y, screen_x, game_map[map_y][map_x])

    # Draw player if in view
    player_screen_x = (player.x - camera.x) * SPACING
    player_screen_y = player.y - camera.y
    if (
        0 <= player_screen_x < camera.view_width * SPACING
        and 0 <= player_screen_y < camera.view_height
    ):
        stdscr.addch(player_screen_y, player_screen_x, "@")

    # Draw enemies if in view
    for enemy in enemies:
        enemy_screen_x = (enemy.x - camera.x) * SPACING
        enemy_screen_y = enemy.y - camera.y
        if (
            0 <= enemy_screen_x < camera.view_width * SPACING
            and 0 <= enemy_screen_y < camera.view_height
        ):
            stdscr.addch(enemy_screen_y, enemy_screen_x, "E")


def main(stdscr):
    # Initialisation de ncurses
    curs_set(0)  # Masquer le curseur
    stdscr.nodelay(1)  # Ne pas bloquer l'exécution
    stdscr.timeout(100)  # Timeout pour les entrées clavier
    start_color()

    # Get terminal size
    term_height, term_width = stdscr.getmaxyx()

    # Générer la carte
    # game_map = generate_map()
    game_map = load_new_maze()
    map_width, map_height = len(game_map[0]), len(game_map)

    # Create camera with adjusted width for spacing
    camera = Camera(
        map_width=map_width,
        map_height=map_height,
        view_width=min(term_width // 2, map_width),  # Divide width by 2 for spacing
        view_height=min(term_height - 2, map_height),
    )

    player = Player(name="Héros", x=map_width // 2, y=map_height // 2)
    enemies = initialize_enemies(5, game_map)

    while True:
        # Update camera position to follow player
        camera.follow(player)

        # Clear and redraw
        stdscr.clear()
        draw_map(stdscr, game_map, player, enemies, camera)

        # Draw status line below map
        status = f"HP: {player.hp} | Pos: ({player.x},{player.y})"
        stdscr.addstr(camera.view_height, 0, status)

        # Handle input and update game state
        key = stdscr.getch()
        if key == KEY_RESIZE:
            # Update camera view size on terminal resize
            term_height, term_width = stdscr.getmaxyx()
            camera.view_width = min(term_width, map_width)
            camera.view_height = min(term_height - 2, map_height)

        handle_input(stdscr, player, game_map, enemies)


if __name__ == "__main__":
    SPACING = 2
    wrapper(main)
