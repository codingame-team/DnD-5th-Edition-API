import math

import pygame
from pygame.locals import *

# Initialisation de Pygame
pygame.init()

# Paramètres de l'écran
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FOV = 60  # Champ de vision (en degrés)
HALF_FOV = FOV / 2  # Moitié du champ de vision
HALF_WIDTH = SCREEN_WIDTH // 2
HALF_HEIGHT = SCREEN_HEIGHT // 2

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Définition du labyrinthe (exemple)
maze = [
    "##########",
    "#        #",
    "#  #     #",
    "#  #     #",
    "#  #     #",
    "#  #     #",
    "#        #",
    "##########"
]

# Taille des cases du labyrinthe
CELL_SIZE = 50
# Taille du labyrinthe
MAZE_WIDTH = len(maze[0]) * CELL_SIZE
MAZE_HEIGHT = len(maze) * CELL_SIZE

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vue subjective d'un labyrinthe 3D")

clock = pygame.time.Clock()

# Fonction pour dessiner le labyrinthe
def draw_maze():
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "#":
                pygame.draw.rect(screen, WHITE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))


# Fonction pour afficher la vue subjective
def render():
    screen.fill(BLACK)
    draw_maze()
    pygame.display.flip()

# Position initiale du joueur
player_x = 1
player_y = 1
player_angle = 0  # Angle de vue du joueur (en degrés)

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        print(f'turn left 5°')
        player_angle -= 5
    if keys[K_RIGHT]:
        print(f'turn right 5°')
        player_angle += 5
    if keys[K_UP]:
        print(f'go forward')
        # Déplacement du joueur vers l'avant en fonction de son angle de vue
        player_x += 0.1 * math.cos(math.radians(player_angle))
        player_y += 0.1 * math.sin(math.radians(player_angle))

    render()
    clock.tick(30)

pygame.quit()
