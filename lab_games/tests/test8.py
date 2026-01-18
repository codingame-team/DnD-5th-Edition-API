import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cube Perspective")

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
angle_x = 0
angle_y = 0
angle_z = 0
rotation_speed = 0.1
camera_distance = 200
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                angle_y += rotation_speed
            elif event.key == pygame.K_RIGHT:
                angle_y -= rotation_speed
            elif event.key == pygame.K_UP:
                angle_x += rotation_speed
            elif event.key == pygame.K_DOWN:
                angle_x -= rotation_speed
            elif event.key == pygame.K_PAGEUP:
                angle_z += rotation_speed
            elif event.key == pygame.K_PAGEDOWN:
                angle_z -= rotation_speed

    # Clear the screen
    screen.fill(BLACK)

    # Rotate the cube
    rotated_vertices = []
    for vertex in vertices:
        x, y, z = vertex
        # Rotate around the x-axis
        new_y = y * math.cos(angle_x) - z * math.sin(angle_x)
        new_z = y * math.sin(angle_x) + z * math.cos(angle_x)
        y, z = new_y, new_z
        # Rotate around the y-axis
        new_x = x * math.cos(angle_y) - z * math.sin(angle_y)
        z = x * math.sin(angle_y) + z * math.cos(angle_y)
        x = new_x
        # Rotate around the z-axis
        new_x = x * math.cos(angle_z) - y * math.sin(angle_z)
        new_y = x * math.sin(angle_z) + y * math.cos(angle_z)
        rotated_vertices.append((new_x, new_y, z))

    # Project and draw the edges of the cube
    for edge in edges:
        start_x, start_y, start_z = rotated_vertices[edge[0]]
        end_x, end_y, end_z = rotated_vertices[edge[1]]
        start_x += SCREEN_WIDTH / 2
        start_y += SCREEN_HEIGHT / 2
        end_x += SCREEN_WIDTH / 2
        end_y += SCREEN_HEIGHT / 2

        # Apply perspective projection
        start_x = start_x / (1 + start_z / camera_distance)
        start_y = start_y / (1 + start_z / camera_distance)
        end_x = end_x / (1 + end_z / camera_distance)
        end_y = end_y / (1 + end_z / camera_distance)

        pygame.draw.line(screen, WHITE, (start_x, start_y), (end_x, end_y))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
