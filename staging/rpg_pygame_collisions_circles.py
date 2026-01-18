import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen and Clock
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Player Sprite with a Transparent Background
# Player Sprite with a Transparent Background
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (25, 25), 25)  # Draw a circle
        self.rect = self.image.get_rect(center=(400, 300))
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask

    def update(self, keys, enemies):
        # Store the current position
        original_position = self.rect.topleft

        # Attempt to move
        if keys[pygame.K_UP]: self.rect.y -= 5
        if keys[pygame.K_DOWN]: self.rect.y += 5
        if keys[pygame.K_LEFT]: self.rect.x -= 5
        if keys[pygame.K_RIGHT]: self.rect.x += 5

        # Check for collisions
        for enemy in enemies:
            if check_mask_collision(self, enemy):
                # Calculate the direction of pushback
                pushback_x = self.rect.centerx - enemy.rect.centerx
                pushback_y = self.rect.centery - enemy.rect.centery

                # Normalize the pushback vector
                magnitude = max(1, (pushback_x ** 2 + pushback_y ** 2) ** 0.5)
                pushback_x /= magnitude
                pushback_y /= magnitude

                # Apply pushback
                self.rect.x += int(pushback_x * 5)
                self.rect.y += int(pushback_y * 5)
                break

# Enemy Sprite with a Transparent Background
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (25, 25), 25)  # Draw a circle
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask

# Groups
player = Player()
enemies = pygame.sprite.Group(
    Enemy(200, 200),
    Enemy(600, 400),
    Enemy(400, 100)
)
all_sprites = pygame.sprite.Group(player, *enemies)

# Function for Mask Collision
def check_mask_collision(sprite1, sprite2):
    offset = (sprite2.rect.x - sprite1.rect.x, sprite2.rect.y - sprite1.rect.y)
    return sprite1.mask.overlap(sprite2.mask, offset) is not None

# Game Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    keys = pygame.key.get_pressed()
    player.update(keys, enemies)

    # Draw
    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
