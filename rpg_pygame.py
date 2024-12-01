import json
import math
from random import random, randint
from typing import List

import pygame
from pygame import Surface

from tools.sprite_sheets import load_sprites

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


# AnimatedSprite class for animated enemies or the player
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], pos, frame_rate=5):
        super().__init__()
        self.animations = animation_frames  # List of animation frames
        self.current_direction = list(self.animations.keys())[0]  # Default direction
        self.images = self.animations[self.current_direction]
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=pos)
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
    def __init__(self, animation_frames: dict[str, List[Surface]], pos: tuple = (400, 300)):
        super().__init__(animation_frames, pos)
        self.previous_pos = pos
        self.speed = 5
        self.push_back_distance = 0

    def update(self, keys, enemies):
        """Update with smooth collision response."""
        self.previous_pos = self.rect.copy()
        moved = False
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

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 1 / math.sqrt(2)  # 1/√2
            dy *= 1 / math.sqrt(2)

        # Try moving on X axis
        self.rect.x += dx
        for enemy in enemies:
            if check_mask_collision(self, enemy):
                # Move back and add slight push-back
                self.rect.x = self.previous_pos.x
                if dx > 0:
                    self.rect.x -= self.push_back_distance
                else:
                    self.rect.x += self.push_back_distance
                dx = 0
                break

        # Try moving on Y axis
        self.rect.y += dy
        for enemy in enemies:
            if check_mask_collision(self, enemy):
                # Move back and add slight push-back
                self.rect.y = self.previous_pos.y
                if dy > 0:
                    self.rect.y -= self.push_back_distance
                else:
                    self.rect.y += self.push_back_distance
                dy = 0
                break

        moved = dx != 0 or dy != 0
        if moved:
            self.update_animation()


# Enemy class
class Enemy(AnimatedSprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], pos: tuple = (400, 300)):
        super().__init__(animation_frames, pos)
        self.speed = 3
        self.direction = pygame.math.Vector2()
        self.hp = randint(1, 6)  # Random initial HP between 1 and 6

    def hit(self):
        """Handle enemy hit."""
        self.hp -= 1


    def update(self):
        """Update enemy position and animation."""
        # Randomly change direction
        if random() < 0.01:  # 1% chance to change direction
            self.dir = randint(0, 7)

        # Move in the current direction
        directions = {
            0: (0, -1), 1: (1, -1), 2: (1, 0), 3: (1, 1),
            4: (0, 1), 5: (-1, 1), 6: (-1, 0), 7: (-1, -1)
        }
        previous_pos = self.rect.copy()  # Save previous position

        # Update position based on direction
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

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

        # Revert position if out of bounds
        if not screen_rect.contains(self.rect):
            self.rect = previous_pos  # Revert to the last valid position
            self.dir = randint(0, 7)  # Change to a random new direction

        # Animate enemy
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


def run():
    global screen_rect

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    screen_rect = pygame.display.get_surface().get_rect()

    # Load sounds
    collision_sound = pygame.mixer.Sound('sounds/Sword Impact Hit 1.wav')
    collision_sound.set_volume(0.4)  # Adjust volume

    # Add collision cooldown
    collision_cooldown = 20  # milliseconds
    last_collision_time = 0

    # Create player and enemies
    player = Player(animation_frames=get_animation_frames('goblinsword'))
    enemies = pygame.sprite.Group(
        Enemy(animation_frames=get_animation_frames('minion'), pos=(200, 200)),
        Enemy(animation_frames=get_animation_frames('bat'), pos=(600, 400)),
        Enemy(animation_frames=get_animation_frames('goblin'), pos=(400, 100)),
        Enemy(animation_frames=get_animation_frames('aerocephal'), pos=(600, 100)),
        Enemy(animation_frames=get_animation_frames('arcana_drake'), pos=(100, 400)),
        Enemy(animation_frames=get_animation_frames('aurum-drakueli'), pos=(600, 400)),
        Enemy(animation_frames=get_animation_frames('daemarbora'), pos=(300, 600)),
        Enemy(animation_frames=get_animation_frames('deceleon'), pos=(800, 200)),
        Enemy(animation_frames=get_animation_frames('demonic_essence'), pos=(600, 700)),
        Enemy(animation_frames=get_animation_frames('stygian_lizard'), pos=(100, 700))
    )
    all_sprites = pygame.sprite.Group(player, *enemies)

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update player and enemies
        keys = pygame.key.get_pressed()
        player.update(keys, enemies)
        for mud in enemies:
            mud.update()
        enemies.update()

        # Collision detection with cooldown and sound
        if current_time - last_collision_time > collision_cooldown:
            for enemy in enemies:
                if check_mask_collision(player, enemy):
                    print("Player collided with an enemy!")
                    enemy.hit()  # This will play the enemy hit sound
                    collision_sound.play()  # Play general collision sound
                    last_collision_time = current_time
                    if enemy.hp <= 0:
                        all_sprites.remove(enemy)
                        enemies.remove(enemy)  # Remove from enemies group

        # Draw everything
        screen.fill(WHITE)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    # Récupération du personnage choisi par l'utilisateur
    # character_name = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'
    sprites_images_dir = f'sprites/Animations'
    run()
