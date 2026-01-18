import pygame
import sys

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TILE_SIZE = 32

m = 2
# Example map
game_map = [
    "##############################" * m,
    "#............##..............#" * m,
    "#............................#" * m,
    "....P........................." * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "#............................#" * m,
    "##############################" * m,
]

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)

# Define the Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def can_move(self, dir: tuple) -> bool:
        dx, dy = dir
        x, y = self.x + dx, self.y + dy
        return 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT and game_map[y][x] != '#'

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Auto-Scrolling Map")

# Create the player
player = Player(3, 3)

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and player.can_move(UP):
                player.move(0, -1)
            elif event.key == pygame.K_DOWN and player.can_move(DOWN):
                player.move(0, 1)
            elif event.key == pygame.K_LEFT and player.can_move(LEFT):
                player.move(-1, 0)
            elif event.key == pygame.K_RIGHT and player.can_move(RIGHT):
                player.move(1, 0)


    MAP_WIDTH, MAP_HEIGHT = len(game_map[0]), len(game_map)

    # Calculate the viewport position based on the player's position
    viewport_x = max(0, min(player.x - SCREEN_WIDTH // (2 * TILE_SIZE), MAP_WIDTH - SCREEN_WIDTH // TILE_SIZE))
    viewport_y = max(0, min(player.y - SCREEN_HEIGHT // (2 * TILE_SIZE), MAP_HEIGHT - SCREEN_HEIGHT // TILE_SIZE))

    # Clear the screen
    screen.fill(BLACK)


    # Draw the portion of the map that falls within the viewport
    for y in range(viewport_y, min(MAP_HEIGHT, viewport_y + SCREEN_HEIGHT // TILE_SIZE + 1)):
        for x in range(viewport_x, min(MAP_WIDTH, viewport_x + SCREEN_WIDTH // TILE_SIZE + 1)):
            if game_map[y][x] == "#":
                pygame.draw.rect(screen, WHITE, (x * TILE_SIZE - viewport_x * TILE_SIZE, y * TILE_SIZE - viewport_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    # Draw the player
    pygame.draw.circle(screen, (255, 0, 0), ((player.x - viewport_x) * TILE_SIZE + TILE_SIZE // 2, (player.y - viewport_y) * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 2)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
