import pygame
import sys

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


# Player Sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(400, 300))

    def update(self, keys):
        if keys[pygame.K_UP]: self.rect.y -= 5
        if keys[pygame.K_DOWN]: self.rect.y += 5
        if keys[pygame.K_LEFT]: self.rect.x -= 5
        if keys[pygame.K_RIGHT]: self.rect.x += 5


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_x = 0
        self.velocity_y = 0

    def update(self):
        # Apply velocity
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        # Add friction/damping
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95

        # Get screen dimensions
        screen_width = 800  # Replace with your actual screen width
        screen_height = 600  # Replace with your actual screen height

        # Prevent leaving screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = abs(self.velocity_x)  # Reverse x direction
        elif self.rect.right > screen_width:
            self.rect.right = screen_width
            self.velocity_x = -abs(self.velocity_x)  # Reverse x direction

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = abs(self.velocity_y)  # Reverse y direction
        elif self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity_y = -abs(self.velocity_y)  # Reverse y direction

        # Remove the original movement code that kills the enemy when off screen
        # self.rect.move_ip(-self.speed, 0)
        # if self.rect.right < 0:
        #     self.kill()


def handle_collision(player, enemy):
    # Calculate direction vector from player to enemy
    dx = enemy.rect.centerx - player.rect.centerx
    dy = enemy.rect.centery - player.rect.centery

    # Normalize the direction vector
    length = (dx ** 2 + dy ** 2) ** 0.5
    if length != 0:
        dx = dx / length
        dy = dy / length

    # Bounce force
    bounce_force = 10

    # Apply bounce to enemy
    enemy.velocity_x = dx * bounce_force
    enemy.velocity_y = dy * bounce_force

    enemy.update()
    print("Player collided with an enemy!")


def handle_collision_old(player, enemy):
    # Calculate direction vector from player to enemy
    dx = enemy.rect.centerx - player.rect.centerx
    dy = enemy.rect.centery - player.rect.centery

    # Normalize the direction vector
    length = (dx ** 2 + dy ** 2) ** 0.5
    if length != 0:
        dx = dx / length
        dy = dy / length

    # Bounce force
    bounce_force = 10

    # Apply bounce to enemy
    enemy.velocity_x = dx * bounce_force
    enemy.velocity_y = dy * bounce_force

    # Push player away from enemy to prevent overlap
    push_distance = 5  # Adjust this value as needed
    player.rect.x -= dx * push_distance
    player.rect.y -= dy * push_distance

    # Ensure player stays within screen bounds after being pushed
    screen_width = 800  # Replace with your actual screen width
    screen_height = 600  # Replace with your actual screen height

    # Constrain player position to screen bounds
    player.rect.clamp_ip(pygame.Rect(0, 0, screen_width, screen_height))

    print("Player collided with an enemy!")


# In your game loop, add continuous collision checking:
def check_collisions(player, enemies):
    # Check for collisions and handle them
    collisions = pygame.sprite.spritecollide(player, enemies, False)
    if collisions:
        for enemy in collisions:
            handle_collision(player, enemy)

        # Additional separation to prevent sticking
        while pygame.sprite.spritecollideany(player, enemies):
            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                # Calculate separation vector
                sep_x = player.rect.centerx - enemy.rect.centerx
                sep_y = player.rect.centery - enemy.rect.centery

                # Normalize
                length = (sep_x ** 2 + sep_y ** 2) ** 0.5
                if length != 0:
                    sep_x = sep_x / length
                    sep_y = sep_y / length

                # Push player away until no overlap
                player.rect.x += sep_x
                player.rect.y += sep_y

                # Keep player in bounds
                player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))


def run():
    # Initialize Pygame
    pygame.init()

    # Screen and Clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Groups
    player = Player()
    enemies = pygame.sprite.Group(
        Enemy(200, 200),
        Enemy(600, 400),
        Enemy(400, 100)
    )
    all_sprites = pygame.sprite.Group(player, *enemies)

    # Game Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Collision Detection
        check_collisions(player, enemies)

        # Draw
        screen.fill(WHITE)
        all_sprites.draw(screen)
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()
