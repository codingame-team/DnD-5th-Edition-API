import json
import math
import os
import sys
from random import random, randint, choice
from typing import List

import pygame
from pygame import Surface

from tools.sprite_sheets import load_sprites

TILE_SIZE = 64 + 20

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


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled executable
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in development environment
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Navigate up to the project root (assuming this file is in a subdirectory)
        project_root = os.path.dirname(current_dir)

        # Join the project root with the relative path
        return os.path.join(project_root, relative_path)


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

    # @property
    # def pos(self):
    #     return self.rect.topleft

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
        self.push_back_distance = 10
        # New features
        self.hp = 100  # Starting health
        self.max_hp = 100
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1000  # 1 second of invulnerability after hit
        self.damage_taken = 10  # Damage taken from enemies
        # Added
        self.velocity = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(x * TILE_SIZE, y * TILE_SIZE)
        self.acceleration = 5  # 0.5
        self.max_speed = 40  # 8.0
        self.friction = 0.5  # 0.92
        self.knockback_friction = 0 #0.85

    def take_damage(self, amount):
        if not self.invulnerable:
            self.hp -= amount
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()
            # Prevent HP from going below 0
            self.hp = max(0, self.hp)

    def move_with_collision(self, dx, dy, walls, enemies):
        """Handle movement with stable collision detection"""
        if dx == 0 and dy == 0:
            return

        # Save original position
        original_x = self.rect.x
        original_y = self.rect.y

        # Check wall collisions after movement
        can_move = True
        if pygame.sprite.spritecollideany(self, walls):
            # If collision occurred, handle it
            handle_wall_collision(self, walls)
            can_move = False

        if can_move:
            self.rect.x += dx
            self.rect.y += dy

        # Handle enemy collisions only if we actually moved
        if can_move:
            self.handle_enemy_collision(enemies, original_x, original_y, walls)

    def handle_enemy_collision(self, enemies, original_x, original_y, walls):
        """Handle enemy collisions with push back"""
        for enemy in enemies:
            if not check_mask_collision(self, enemy):
                continue

            if not self.invulnerable:
                self.take_damage(self.damage_taken)

                # Calculate push back direction
                push_dx = self.rect.centerx - enemy.rect.centerx
                push_dy = self.rect.centery - enemy.rect.centery

                # Only push back if there's a valid direction
                if push_dx == 0 and push_dy == 0:
                    continue

                # Normalize push back vector
                length = math.sqrt(push_dx ** 2 + push_dy ** 2)
                push_dx = (push_dx / length) * self.push_back_distance
                push_dy = (push_dy / length) * self.push_back_distance

                # Test new position
                test_rect = self.rect.copy()
                test_rect.x += push_dx
                test_rect.y += push_dy

                # Check if push back position would cause wall collision
                wall_collision = False
                for wall in walls:
                    if wall.rect.colliderect(test_rect):
                        wall_collision = True
                        break

                if not wall_collision:
                    # Apply push back if no wall collision would occur
                    self.rect.x = test_rect.x
                    self.rect.y = test_rect.y
                else:
                    # If push back would cause wall collision, just revert to pre-collision position
                    self.rect.x = original_x
                    self.rect.y = original_y
            break

    def update(self, keys, walls):
        current_time = pygame.time.get_ticks()

        # Update invulnerability
        if self.invulnerable:
            if current_time - self.invulnerable_timer > self.invulnerable_duration:
                self.invulnerable = False

        # Store previous position
        old_pos = pygame.math.Vector2(self.pos)

        # Apply velocity
        self.pos += self.velocity
        self.rect.center = self.pos

        # Check wall collisions after movement
        if pygame.sprite.spritecollideany(self, walls):
            # If collision occurred, handle it
            handle_wall_collision(self, walls)

        # Apply friction to velocity
        self.velocity *= self.knockback_friction

        # Normal movement if velocity is minimal
        if self.velocity.length() < 0.5:
            # Calculate acceleration based on input
            acceleration = pygame.math.Vector2(0, 0)

            if keys[pygame.K_LEFT]:
                acceleration.x = -self.acceleration
                if self.current_direction in ('up', 'down', 'right', 'left'):
                    if self.current_direction != 'left':
                        self.change_animation('left')
                        self.current_direction = 'left'
            if keys[pygame.K_RIGHT]:
                acceleration.x = self.acceleration
                if self.current_direction in ('up', 'down', 'right', 'left'):
                    if self.current_direction != 'right':
                        self.change_animation('right')
                        self.current_direction = 'right'
            if keys[pygame.K_UP]:
                acceleration.y = -self.acceleration
                if self.current_direction in ('up', 'down', 'right', 'left'):
                    if self.current_direction != 'up':
                        self.change_animation('up')
                        self.current_direction = 'up'
            if keys[pygame.K_DOWN]:
                acceleration.y = self.acceleration
                if self.current_direction in ('up', 'down', 'right', 'left'):
                    if self.current_direction != 'down':
                        self.change_animation('down')
                        self.current_direction = 'down'

            # Normalize diagonal movement
            if acceleration.length() > 0:
                acceleration.normalize_ip()
                acceleration *= self.acceleration

            # Apply acceleration to velocity
            self.velocity += acceleration

            # Apply friction when no input
            if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                self.velocity.x *= self.friction
            if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
                self.velocity.y *= self.friction

            # Limit maximum speed
            if self.velocity.length() > self.max_speed:
                self.velocity.scale_to_length(self.max_speed)

        # Update animation only if actually moved
        if self.velocity.length() > 0:
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


# Function to save sprite configuration to JSON
def save_sprite_config(config):
    filename = f'{sprites_images_dir}/sprite_config.json'
    with open(resource_path(filename), 'w') as f:
        json.dump(config, f, indent=4)


# Function to load sprite configuration from JSON
def load_sprite_config():
    filename = f'{base_dir}/{sprites_images_dir}/sprite_config.json'
    with open(resource_path(filename), 'r') as f:
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
        # Enemy(animation_frames=get_animation_frames('minion'), x=pos_2[0], y=pos_2[1]),
        Enemy(animation_frames=get_animation_frames('bat'), x=pos_3[0], y=pos_3[1]),
        Enemy(animation_frames=get_animation_frames('goblin'), x=pos_2[0], y=pos_2[1]),
        Enemy(animation_frames=get_animation_frames('bat'), x=pos_5[0], y=pos_5[1]),
        Enemy(animation_frames=get_animation_frames('goblin'), x=pos_4[0], y=pos_4[1]),
        # Enemy(animation_frames=get_animation_frames('minion'), x=pos_5[0], y=pos_5[1]),
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


def handle_wall_collision(player, walls):
    # Check collisions with walls
    wall_hits = pygame.sprite.spritecollide(player, walls, False)
    if wall_hits:
        for wall in wall_hits:
            # Calculate overlap and direction
            dx = player.rect.centerx - wall.rect.centerx
            dy = player.rect.centery - wall.rect.centery

            # Convert to vector for easier handling
            push_vector = pygame.math.Vector2(dx, dy)
            if push_vector.length() > 0:
                push_vector.normalize_ip()

            # Strong immediate push back
            push_strength = 5
            player.velocity = push_vector * push_strength

            # Move player out of wall
            while pygame.sprite.spritecollideany(player, walls):
                player.pos += push_vector
                player.rect.center = player.pos


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
    push_strength = 10
    player.velocity = direction * push_strength
    # print("Player collided with an enemy!")


# Helper function to check mask collision
def check_mask_collision(sprite1, sprite2):
    offset = (sprite2.rect.x - sprite1.rect.x, sprite2.rect.y - sprite1.rect.y)
    return sprite1.mask.overlap(sprite2.mask, offset) is not None


def run():
    global screen_rect

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    screen_rect = pygame.display.get_surface().get_rect()

    # Add camera coordinates
    camera_x = 0
    camera_y = 0

    # Initialize game objects
    # Get the directory where your script is located
    sound_path = os.path.join(base_dir, 'sounds', 'Sword Impact Hit 1.wav')
    collision_sound = pygame.mixer.Sound(resource_path(sound_path))
    collision_sound.set_volume(0.4)
    collision_cooldown = 20
    last_collision_time = 0

    walls = create_level(level_map)

    # Initial game setup
    player, enemies, all_sprites = reset_game()

    running = True
    paused = False
    while running:
        # Update camera position to follow player
        camera_x = player.rect.centerx - (SCREEN_WIDTH // 4)  # Center horizontally
        camera_y = player.rect.centery - (SCREEN_HEIGHT // 4)  # Center vertically

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
            # player.update(enemies, walls)

            keys = pygame.key.get_pressed()
            # Update player with walls reference
            player.update(keys, walls)

            for enemy in enemies:
                enemy.update(walls)

            # Collision detection with cooldown and sound
            if current_time - last_collision_time > collision_cooldown:
                for enemy in enemies:
                    if check_mask_collision(player, enemy):
                        print("Player collided with an enemy!")
                        # Player takes damage instead of dying
                        handle_collision(player, enemy)
                        player.take_damage(enemy.damage if hasattr(enemy, 'damage') else 30)
                        collision_sound.play()
                        last_collision_time = current_time

                        # Enemy still takes damage/dies as before
                        enemy.hit()
                        if enemy.hp <= 0:
                            all_sprites.remove(enemy)
                            enemies.remove(enemy)

        # Draw everything
        screen.fill(WHITE)
        # all_sprites.draw(screen)

        # Draw all sprites with camera offset
        for sprite in all_sprites:
            screen_pos = sprite.rect.copy()
            screen_pos.x -= camera_x
            screen_pos.y -= camera_y
            screen.blit(sprite.image, screen_pos)

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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sprites_images_dir = f'sprites/Animations'
    run()
