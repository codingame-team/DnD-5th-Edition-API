import pygame
import numpy as np

# Dimensions de la fenêtre
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Taille des cellules du labyrinthe
CELL_SIZE = 40


def create_maze(width, height):
    maze = np.ones((width, height))
    maze[1:-1, 1:-1] = 0
    maze[1, 1] = 1
    maze[width - 2, height - 2] = 1
    return maze


def draw_cube(surface, position):
    x, y, z = position
    points = [
        (x, y - z),
        (x + CELL_SIZE, y - z),
        (x + CELL_SIZE, y + CELL_SIZE - z),
        (x, y + CELL_SIZE - z),
        (x, y + CELL_SIZE - z + CELL_SIZE),
        (x + CELL_SIZE, y + CELL_SIZE - z + CELL_SIZE)
    ]

    # Dessiner les lignes du cube
    pygame.draw.line(surface, BLACK, points[0], points[1])
    pygame.draw.line(surface, BLACK, points[1], points[2])
    pygame.draw.line(surface, BLACK, points[2], points[3])
    pygame.draw.line(surface, BLACK, points[3], points[0])
    pygame.draw.line(surface, BLACK, points[3], points[4])
    pygame.draw.line(surface, BLACK, points[2], points[5])
    pygame.draw.line(surface, BLACK, points[1], points[5])
    pygame.draw.line(surface, BLACK, points[0], points[4])
    pygame.draw.line(surface, BLACK, points[4], points[5])


def display_maze(surface, maze):
    width, height = maze.shape
    for x in range(width):
        for y in range(height):
            if maze[x, y] == 1:
                draw_cube(surface, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('3D Maze with Pygame')

    width, height = 10, 10
    maze = create_maze(width, height)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        display_maze(screen, maze)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
