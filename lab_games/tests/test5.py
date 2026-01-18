import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rotating Isometric Cube")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define the size of the cube
CUBE_SIZE = 100

# Define the initial vertices of the cube
vertices = [
    (-CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2),
    (CUBE_SIZE / 2, -CUBE_SIZE / 2, -CUBE_SIZE / 2),
    (CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2),
    (-CUBE_SIZE / 2, CUBE_SIZE / 2, -CUBE_SIZE / 2),
    (-CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2),
    (CUBE_SIZE / 2, -CUBE_SIZE / 2, CUBE_SIZE / 2),
    (CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2),
    (-CUBE_SIZE / 2, CUBE_SIZE / 2, CUBE_SIZE / 2)
]

# Define the edges of the cube
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Main loop
angle = 0
rotation_speed = 0.01
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(BLACK)

    # Rotate the cube around the y-axis
    rotated_vertices = []
    for vertex in vertices:
        x, y, z = vertex
        # Rotate around the y-axis
        new_x = x * math.cos(angle) - z * math.sin(angle)
        new_z = x * math.sin(angle) + z * math.cos(angle)
        rotated_vertices.append((new_x, y, new_z))

    # Draw the edges of the cube
    for edge in edges:
        start_x, start_y, start_z = rotated_vertices[edge[0]]
        end_x, end_y, end_z = rotated_vertices[edge[1]]
        # Apply isometric projection
        start_iso_x = (start_x - start_y) + SCREEN_WIDTH / 2
        start_iso_y = (start_z + (start_x + start_y) / 2) + SCREEN_HEIGHT / 2
        end_iso_x = (end_x - end_y) + SCREEN_WIDTH / 2
        end_iso_y = (end_z + (end_x + end_y) / 2) + SCREEN_HEIGHT / 2
        pygame.draw.line(screen, WHITE, (start_iso_x, start_iso_y), (end_iso_x, end_iso_y))

    # Update the display
    pygame.display.flip()

    # Increment the angle for rotation
    angle += rotation_speed

# Quit Pygame
pygame.quit()
sys.exit()
