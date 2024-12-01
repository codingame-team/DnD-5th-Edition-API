import json
import math
from random import random, randint, choice
from typing import List

import pygame
from pygame import Surface

from tools.sprite_sheets import load_sprites

TILE_SIZE = 64

# Screen dimensions
# SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900
SCREEN_WIDTH, SCREEN_HEIGHT = 30 * TILE_SIZE, 15 * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Add health bar colors
HEALTH_BAR_GREEN = (0, 255, 0)
HEALTH_BAR_RED = (255, 0, 0)

directions = {
    0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1),
    4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)
}

# 0 = empty, 1 = wall
level_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
    [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill((100, 100, 100))  # Gray color for walls
        pos = (x * TILE_SIZE, y * TILE_SIZE)
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)


def create_level(grid: List[List[int]]):
    walls = pygame.sprite.Group()

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell == 1:
                walls.add(Tile(j, i, TILE_SIZE))
    return walls


# AnimatedSprite class for animated enemies or the player
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], x, y, frame_rate=5):
        super().__init__()
        self.animations = animation_frames  # List of animation frames
        self.current_direction = list(self.animations.keys())[0]  # Default direction
        self.images = self.animations[self.current_direction]
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        pos = (x * TILE_SIZE, y * TILE_SIZE)
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask
        self.frame_rate = frame_rate  # Frames per second
        self.last_update = pygame.time.get_ticks()

    @property
    def pos(self):
        return self.rect.topleft

    def change_animation(self, direction: str):
        """Change the animation sequence based on direction."""
        if direction in self.animations and direction != self.current_direction:
            self.current_direction = direction
            self.images = self.animations[direction]
            self.current_frame = 0  # Reset frame index when changing direction
            self.image = self.images[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)

    def update_animation(self):
        """Update animation frames based on elapsed time."""
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 // self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)  # Update mask


# Player class
class Player(AnimatedSprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], x: int, y: int):
        super().__init__(animation_frames, x, y)
        pos = (x * TILE_SIZE, y * TILE_SIZE)
        self.previous_pos = pos
        self.speed = 5
        self.push_back_distance = 0
        # New features
        self.hp = 100  # Starting health
        self.max_hp = 100
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1000  # 1 second of invulnerability after hit
        self.damage_taken = 10  # Damage taken from enemies

    def take_damage(self, amount):
        if not self.invulnerable:
            self.hp -= amount
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            # Prevent HP from going below 0
            self.hp = max(0, self.hp)

    def get_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        # Calculate movement
        if keys[pygame.K_UP]:
            dy -= self.speed
            if self.current_direction in ('up', 'down', 'right', 'left'):
                if self.current_direction != 'up':
                    self.change_animation('up')
                    self.current_direction = 'up'
        if keys[pygame.K_DOWN]:
            dy += self.speed
            if self.current_direction in ('up', 'down', 'right', 'left'):
                if self.current_direction != 'down':
                    self.change_animation('down')
                    self.current_direction = 'down'
        if keys[pygame.K_LEFT]:
            dx -= self.speed
            if self.current_direction in ('up', 'down', 'right', 'left'):
                if self.current_direction != 'left':
                    self.change_animation('left')
                    self.current_direction = 'left'
        if keys[pygame.K_RIGHT]:
            dx += self.speed
            if self.current_direction in ('up', 'down', 'right', 'left'):
                if self.current_direction != 'right':
                    self.change_animation('right')
                    self.current_direction = 'right'
        return dx, dy

    def update(self, enemies, walls):
        current_time = pygame.time.get_ticks()

        # Check invulnerability
        if self.invulnerable:
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False

        # Save previous position for collision handling
        self.previous_pos = self.rect.copy()

        # Get movement input
        dx, dy = self.get_input()

        # Try moving on X axis
        self.rect.x += dx
        # Check wall collisions on X axis
        for wall in walls:
            if check_mask_collision(self, wall):
                if dx > 0:  # Moving right
                    self.rect.right = wall.rect.left
                else:  # Moving left
                    self.rect.left = wall.rect.right
                dx = 0
                break

        # Check enemy collisions on X axis
        for enemy in enemies:
            if check_mask_collision(self, enemy):
                self.rect.x = self.previous_pos.x
                dx = 0
                break

        # Try moving on Y axis
        self.rect.y += dy
        # Check wall collisions on Y axis
        for wall in walls:
            if check_mask_collision(self, wall):
                if dy > 0:  # Moving down
                    self.rect.bottom = wall.rect.top
                else:  # Moving up
                    self.rect.top = wall.rect.bottom
                dy = 0
                break

        # Check enemy collisions on Y axis
        for enemy in enemies:
            if check_mask_collision(self, enemy):
                self.rect.y = self.previous_pos.y
                dy = 0
                break

        # Update animation if moved
        if dx != 0 or dy != 0:
            self.update_animation()


# Enemy class
class Enemy(AnimatedSprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], x, y):
        pos = (x * TILE_SIZE, y * TILE_SIZE)
        super().__init__(animation_frames, x, y)
        self.speed = randint(1, 3)
        self.direction = pygame.math.Vector2(0, 0)  # or whatever class you're using for vectors
        self.dir = randint(0, 7)
        dx, dy = directions[self.dir]
        self.direction.x = dx
        self.direction.y = dy
        self.hp = randint(1, 6)  # Random initial HP between 1 and 6
        self.previous_pos = pos

    def hit(self):
        """Handle enemy hit."""
        self.hp -= 1

    def update(self, walls):
        # Get current screen dimensions
        screen_width, screen_height = pygame.display.get_surface().get_size()
        margin = 10  # Margin to keep enemy visible

        # Save previous position for collision handling
        self.previous_pos = self.rect.copy()

        # Randomly change direction
        if random() < 0.01:  # 1% chance to change direction
            self.dir = randint(0, 7)
            dx, dy = directions[self.dir]
            self.direction.x = dx
            self.direction.y = dy

        # Calculate new position
        new_x = self.rect.x + (self.direction.x * self.speed)
        new_y = self.rect.y + (self.direction.y * self.speed)

        # Try moving on X axis
        self.rect.x = new_x
        wall_collision = False
        for wall in walls:
            if check_mask_collision(self, wall):
                wall_collision = True
                self.direction.x *= -1
                break
        if wall_collision:
            self.rect.x = self.previous_pos.x

        # Try moving on Y axis
        self.rect.y = new_y
        wall_collision = False
        for wall in walls:
            if check_mask_collision(self, wall):
                wall_collision = True
                self.direction.y *= -1
                break
        if wall_collision:
            self.rect.y = self.previous_pos.y

        # Update animation based on movement direction
        if abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x > 0:
                self.change_animation('right')
            elif self.direction.x < 0:
                self.change_animation('left')
        else:
            if self.direction.y > 0:
                self.change_animation('down')
            elif self.direction.y < 0:
                self.change_animation('up')

        # Update the animation
        self.update_animation()


# Helper function to check mask collision
def check_mask_collision(sprite1, sprite2):
    offset = (sprite2.rect.x - sprite1.rect.x, sprite2.rect.y - sprite1.rect.y)
    return sprite1.mask.overlap(sprite2.mask, offset) is not None


# Function to save sprite configuration to JSON
def save_sprite_config(config):
    filename = f'{sprites_images_dir}/sprite_config.json'
    with open(filename, 'w') as f:
        json.dump(config, f, indent=4)


# Function to load sprite configuration from JSON
def load_sprite_config():
    filename = f'{sprites_images_dir}/sprite_config.json'
    with open(filename, 'r') as f:
        return json.load(f)


# Modified load_images function to use JSON config
def load_images(sprite_name: str = 'goblin'):
    # Load config
    config = load_sprite_config()

    # Find sprite configuration
    sprite_data = next(
        (sprite for sprite in config['sprites'] if sprite['name'] == sprite_name),
        None
    )

    if sprite_data is None:
        raise ValueError(f"No configuration found for sprite: {sprite_name}")

    # Load sprites using configuration
    sprites = load_sprites(
        spritesheet_path=f"{sprite_data['path']}/{sprite_data['filename']}",
        columns=sprite_data['columns'],
        rows=sprite_data['rows'],
        save_dir=sprite_data['cache_dir']
    )
    return sprites


def get_animation_frames(sprite_name: str) -> dict[str, List[Surface]]:
    animation_frames: dict[str, List[Surface]] = {}
    sprite_sheets_json = load_sprite_config()
    animations_frames: dict = [sprite_config['animations'] for sprite_config in sprite_sheets_json['sprites'] if sprite_config['name'] == sprite_name][0]
    sprite_frames: List[Surface] = load_images(sprite_name)
    for animation_name, boundaries in animations_frames.items():
        start, end = boundaries['start'], boundaries['end']
        animation_frames[animation_name] = sprite_frames[start:end + 1]
    return animation_frames


def show_pause_screen(screen):
    # Set up fonts
    font_big = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 36)

    # Create text surfaces
    pause_text = font_big.render('PAUSED', True, (50, 50, 255))
    continue_text = font_small.render('Press P to Continue', True, (255, 255, 255))
    quit_text = font_small.render('Press Q to Quit', True, (255, 255, 255))

    # Get screen dimensions
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Position text
    pause_rect = pause_text.get_rect(center=(screen_width / 2, screen_height / 2 - 50))
    continue_rect = continue_text.get_rect(center=(screen_width / 2, screen_height / 2 + 20))
    quit_rect = quit_text.get_rect(center=(screen_width / 2, screen_height / 2 + 60))

    # Create semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)

    # Draw overlay and text
    screen.blit(overlay, (0, 0))
    screen.blit(pause_text, pause_rect)
    screen.blit(continue_text, continue_rect)
    screen.blit(quit_text, quit_rect)
    pygame.display.flip()


def show_game_over_screen(screen):
    # Set up fonts
    font_big = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 36)

    # Create text surfaces
    game_over_text = font_big.render('GAME OVER', True, (255, 0, 0))
    restart_text = font_small.render('Press R to Restart', True, (255, 255, 255))
    quit_text = font_small.render('Press Q to Quit', True, (255, 255, 255))

    # Get screen dimensions
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Position text
    game_over_rect = game_over_text.get_rect(center=(screen_width / 2, screen_height / 2 - 50))
    restart_rect = restart_text.get_rect(center=(screen_width / 2, screen_height / 2 + 20))
    quit_rect = quit_text.get_rect(center=(screen_width / 2, screen_height / 2 + 60))

    # Create semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)

    # Draw overlay and text
    screen.blit(overlay, (0, 0))
    screen.blit(game_over_text, game_over_rect)
    screen.blit(restart_text, restart_rect)
    screen.blit(quit_text, quit_rect)
    pygame.display.flip()

    # Wait for player input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    return False
    return False


def reset_game():
    # Create walls
    walls = create_level(level_map)

    rows, cols = len(level_map), len(level_map[0])
    walkable_tiles = [(x, y) for x in range(cols) for y in range(rows) if level_map[y][x] == 0]

    pos_1 = choice(walkable_tiles)
    walkable_tiles.remove(pos_1)
    pos_2 = choice(walkable_tiles)
    walkable_tiles.remove(pos_2)
    pos_3 = choice(walkable_tiles)
    walkable_tiles.remove(pos_3)
    pos_4 = choice(walkable_tiles)
    walkable_tiles.remove(pos_4)
    pos_5 = choice(walkable_tiles)
    walkable_tiles.remove(pos_5)
    pos_6 = choice(walkable_tiles)
    walkable_tiles.remove(pos_6)

    # Create player and enemies
    player = Player(animation_frames=get_animation_frames('goblinsword'), x=pos_1[0], y=pos_1[1])
    enemies = pygame.sprite.Group(
        Enemy(animation_frames=get_animation_frames('minion'), x=pos_2[0], y=pos_2[1]),
        Enemy(animation_frames=get_animation_frames('bat'), x=pos_3[0], y=pos_3[1]),
        Enemy(animation_frames=get_animation_frames('goblin'), x=pos_4[0], y=pos_4[1]),
        Enemy(animation_frames=get_animation_frames('minion'), x=pos_5[0], y=pos_5[1]),
        Enemy(animation_frames=get_animation_frames('bat'), x=pos_6[0], y=pos_6[1])
        # Enemy(animation_frames=get_animation_frames('aerocephal'), pos=(600, 100)),
        # Enemy(animation_frames=get_animation_frames('arcana_drake'), pos=(100, 400)),
        # Enemy(animation_frames=get_animation_frames('aurum-drakueli'), pos=(600, 400)),
        # Enemy(animation_frames=get_animation_frames('daemarbora'), pos=(300, 600)),
        # Enemy(animation_frames=get_animation_frames('deceleon'), pos=(800, 200)),
        # Enemy(animation_frames=get_animation_frames('demonic_essence'), pos=(600, 700)),
        # Enemy(animation_frames=get_animation_frames('stygian_lizard'), pos=(100, 700))
    )

    # Create all_sprites group
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    all_sprites.add(enemies)
    all_sprites.add(walls)

    return player, enemies, all_sprites


def run():
    global screen_rect

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    screen_rect = pygame.display.get_surface().get_rect()

    # Initialize game objects
    collision_sound = pygame.mixer.Sound('sounds/Sword Impact Hit 1.wav')
    collision_sound.set_volume(0.4)
    collision_cooldown = 20
    last_collision_time = 0

    walls = create_level(level_map)

    # Initial game setup
    player, enemies, all_sprites = reset_game()

    running = True
    paused = False
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # P key toggles pause
                    paused = not paused
                elif event.key == pygame.K_q and paused:  # Q key quits while paused
                    running = False

        # Only update game if not paused
        if not paused:
            # Update game objects
            player.update(enemies, walls)
            for enemy in enemies:
                enemy.update(walls)

            # Collision detection with cooldown and sound
            if current_time - last_collision_time > collision_cooldown:
                for enemy in enemies:
                    if check_mask_collision(player, enemy):
                        print("Player collided with an enemy!")
                        # Player takes damage instead of dying
                        player.take_damage(enemy.damage if hasattr(enemy, 'damage') else 50)
                        collision_sound.play()
                        last_collision_time = current_time

                        # Enemy still takes damage/dies as before
                        enemy.hit()
                        if enemy.hp <= 0:
                            all_sprites.remove(enemy)
                            enemies.remove(enemy)

        # Draw everything
        screen.fill(WHITE)
        all_sprites.draw(screen)

        # Draw health bar
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 10

        pygame.draw.rect(screen, HEALTH_BAR_RED,
                         (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        current_health_width = (player.hp / player.max_hp) * health_bar_width
        pygame.draw.rect(screen, HEALTH_BAR_GREEN,
                         (health_bar_x, health_bar_y, current_health_width, health_bar_height))

        # If game is paused, show pause screen
        if paused:
            show_pause_screen(screen)
        else:
            pygame.display.flip()

        clock.tick(60)

        # Check if player is dead
        if player.hp <= 0:
            # Show game over screen and handle restart
            if show_game_over_screen(screen):
                # Reset the game
                player, enemies, all_sprites = reset_game()
            else:
                running = False

    pygame.quit()


if __name__ == "__main__":
    # Récupération du personnage choisi par l'utilisateur
    # character_name = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'
    sprites_images_dir = f'sprites/Animations'
    run()
