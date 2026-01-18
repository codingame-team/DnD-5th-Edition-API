import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Map")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Define constants for the 3D map
MAP_WIDTH = 10
MAP_HEIGHT = 10
BLOCK_SIZE = 50

# Define the 3D map (example)
map_3d = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(BLACK)

    # Draw the 3D map
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            # Calculate the position of the block
            screen_x = x * BLOCK_SIZE
            screen_y = y * BLOCK_SIZE

            # Calculate the height of the block based on its value in the map
            block_height = map_3d[y][x] * BLOCK_SIZE

            # Draw the block
            pygame.draw.rect(screen, GRAY, (screen_x, screen_y + SCREEN_HEIGHT // 2 - block_height, BLOCK_SIZE, block_height))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
