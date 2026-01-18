import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
ROWS, COLS = 10, 10

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Labyrinthe 3D - Fil de fer")

# Fonction pour dessiner le labyrinthe en mode 3D fil de fer
def draw_maze_3d_wireframe(maze):
    for row in range(len(maze)):
        for col in range(len(maze[0])):
            if maze[row][col] == 1:
                # Calcul des coordonnées projetées pour chaque tuile
                tile_x = (col - row) * (TILE_SIZE // 2) + SCREEN_WIDTH // 2
                tile_y = (col + row) * (TILE_SIZE // 4) + TILE_SIZE

                # Dessiner les bords gauche et haut de chaque tuile
                pygame.draw.line(screen, BLACK, (tile_x, tile_y), (tile_x + TILE_SIZE, tile_y), 2)
                pygame.draw.line(screen, BLACK, (tile_x, tile_y), (tile_x, tile_y + TILE_SIZE // 2), 2)

                # Dessiner le bord droit de chaque tuile (pour le fil de fer)
                pygame.draw.line(screen, BLACK, (tile_x + TILE_SIZE, tile_y), (tile_x + TILE_SIZE, tile_y + TILE_SIZE // 2), 2)

    # Dessiner les bords bas des dernières rangées de tuiles
    for row in range(len(maze) - 1):
        col = 0
        tile_x = (col - row) * (TILE_SIZE // 2) + SCREEN_WIDTH // 2
        tile_y = (col + row) * (TILE_SIZE // 4) + TILE_SIZE + TILE_SIZE // 2
        pygame.draw.line(screen, BLACK, (tile_x, tile_y), (tile_x + TILE_SIZE, tile_y), 2)


# Labyrinthe
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Boucle de jeu
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rendu
    screen.fill(WHITE)

    # Dessiner le labyrinthe en mode 3D fil de fer
    draw_maze_3d_wireframe(maze)

    # Mise à jour de l'affichage
    pygame.display.flip()

pygame.quit()
sys.exit()
