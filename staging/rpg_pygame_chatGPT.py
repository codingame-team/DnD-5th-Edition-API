import json
from random import random, randint
from typing import List

import pygame
from pygame import Surface

from tools.sprite_sheets import load_sprites

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)


# AnimatedSprite class for animated enemies or the player
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], pos, frame_rate=5):
        super().__init__()
        self.animation_frames = animation_frames  # Dictionary of animations
        self.current_anim = list(animation_frames.keys())[0]  # Default animation name
        self.images = animation_frames[self.current_anim]
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask
        self.frame_rate = frame_rate  # Frames per second
        self.last_update = pygame.time.get_ticks()  # Time since last frame update

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

    def update(self, keys):
        """Update player position and animation based on key inputs."""
        moved = False
        if keys[pygame.K_UP]:
            self.rect.y -= 5
            moved = True
        if keys[pygame.K_DOWN]:
            self.rect.y += 5
            moved = True
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
            moved = True
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
            moved = True

        if moved:
            self.update_animation()  # Animate only when moving


# Enemy class
class Enemy(AnimatedSprite):
    def __init__(self, animation_frames: dict[str, List[Surface]], pos: tuple = (400, 300)):
        super().__init__(animation_frames, pos)
        self.dir = randint(0, 7)  # Random direction

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
        self.rect.move_ip(*directions[self.dir])

        # Boundary check
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.dir = 1 - self.dir
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.dir = 5 - self.dir

        # Animate enemy
        self.update_animation()


# Helper function to check mask collision
def check_mask_collision(sprite1, sprite2):
    offset = (sprite2.rect.x - sprite1.rect.x, sprite2.rect.y - sprite1.rect.y)
    return sprite1.mask.overlap(sprite2.mask, offset) is not None


# Function to load animation frames for a sprite
def get_animation_frames(sprite_name: str) -> dict[str, List[Surface]]:
    animation_frames = {}
    sprite_sheets_json = load_sprite_config()
    animations_frames = [
        sprite_config["animations"]
        for sprite_config in sprite_sheets_json["sprites"]
        if sprite_config["name"] == sprite_name
    ][0]
    sprite_frames = load_images(sprite_name)
    for animation_name, boundaries in animations_frames.items():
        start, end = boundaries["start"], boundaries["end"]
        animation_frames[animation_name] = sprite_frames[start : end + 1]
    return animation_frames


# Main game loop
def run():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Load animations
    player_frames = get_animation_frames("player")
    enemy_frames = get_animation_frames("goblin")

    # Create player and enemies
    player = Player(animation_frames=player_frames)
    enemies = pygame.sprite.Group(
        Enemy(animation_frames=enemy_frames, pos=(200, 200)),
        Enemy(animation_frames=enemy_frames, pos=(600, 400)),
        Enemy(animation_frames=enemy_frames, pos=(400, 100)),
    )
    all_sprites = pygame.sprite.Group(player, *enemies)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update player and enemies
        keys = pygame.key.get_pressed()
        player.update(keys)
        enemies.update()

        # Collision detection
        for enemy in enemies:
            if check_mask_collision(player, enemy):
                print("Player collided with an enemy!")

        # Draw everything
        screen.fill(WHITE)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    sprites_images_dir = f"../sprites/Animations"
    run()
