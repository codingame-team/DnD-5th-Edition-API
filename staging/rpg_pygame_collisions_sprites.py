import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


# Function to Handle Collision
def handle_collision(player, enemy):
    # Calculate direction vector from enemy to player
    direction = pygame.math.Vector2(
        player.rect.centerx - enemy.rect.centerx,
        player.rect.centery - enemy.rect.centery
    )

    # Normalize the direction vector
    if direction.length() > 0:
        direction = direction.normalize()

    # Push back settings
    push_strength = 1
    player.velocity = direction * push_strength
    # print("Player collided with an enemy!")


# Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, BLUE, (25, 25), 25)  # Draw a circle
        self.rect = self.image.get_rect(center=(400, 300))
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask
        self.velocity = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 5

    # @property
    # def speed(self):
    #     return self.velocity.length()

    def update(self, keys):
        # Apply pushback velocity
        self.pos += self.velocity

        # Apply friction to pushback
        self.velocity *= 0.85  # Knockback friction

        # Normal movement if pushback velocity is minimal
        if self.velocity.length() < 0.5:
            if keys[pygame.K_LEFT]:
                self.pos.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.pos.x += self.speed
            if keys[pygame.K_UP]:
                self.pos.y -= self.speed
            if keys[pygame.K_DOWN]:
                self.pos.y += self.speed

        # Update sprite position
        self.rect.center = self.pos

        # # Keep player within screen bounds
        # if self.rect.left < 0:
        #     self.rect.left = 0
        #     self.pos.x = self.rect.centerx
        #     self.velocity.x = 0
        # elif self.rect.right > SCREEN_WIDTH:
        #     self.rect.right = SCREEN_WIDTH
        #     self.pos.x = self.rect.centerx
        #     self.velocity.x = 0
        #
        # if self.rect.top < 0:
        #     self.rect.top = 0
        #     self.pos.y = self.rect.centery
        #     self.velocity.y = 0
        # elif self.rect.bottom > SCREEN_HEIGHT:
        #     self.rect.bottom = SCREEN_HEIGHT
        #     self.pos.y = self.rect.centery
        #     self.velocity.y = 0


# Enemy Class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (25, 25), 25)  # Draw a circle
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

    keys = pygame.key.get_pressed()

    # Update player
    player.update(keys)

    # Check for collisions
    for enemy in enemies:
        if check_mask_collision(player, enemy):
            handle_collision(player, enemy)

    # Draw everything
    screen.fill(WHITE)
    all_sprites.draw(screen)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
sys.exit()
