import os
import sys

import pygame
from typing import List
from pygame import Surface
import hashlib

# from dungeon_menu_pygame import SCREEN_HEIGHT
# from dungeon_pygame import SCREEN_WIDTH

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

def extract_sprites(spritesheet_path, columns, rows) -> List[Surface]:
    # Load the spritesheet
    spritesheet = pygame.image.load(resource_path(spritesheet_path)).convert_alpha()

    # Calculate the size of each sprite
    sheet_width, sheet_height = spritesheet.get_size()
    sprite_width = sheet_width // columns
    sprite_height = sheet_height // rows

    sprites: List[Surface] = []
    num_sprites: int = columns * rows

    for i in range(num_sprites):
        # Calculate the position of the sprite in the sheet
        row = i // columns
        col = i % columns

        # Create a new surface for the sprite
        sprite_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)

        # offset_x = col * sprite_width + (sprite_width - sprite_size) // 2
        # offset_y = row * sprite_height + (sprite_height - sprite_size) // 2

        # Copy the sprite from the sheet to the new surface
        sprite_surface.blit(spritesheet, (0, 0),
                            (col * sprite_width, row * sprite_height,
                             sprite_width, sprite_height))

        sprites.append(sprite_surface)

    return sprites

def get_spritesheet_hash(spritesheet_path: str) -> str:
    """Generate a hash of the spritesheet file to detect changes"""
    with open(spritesheet_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def extract_and_save_sprites(spritesheet_path: str, columns: int, rows: int, save_dir: str) -> List[Surface]:
    """
    Extract sprites from a spritesheet, save them individually, and return the loaded sprites.

    Args:
        spritesheet_path: Path to the spritesheet image
        columns: Number of columns in the spritesheet
        rows: Number of rows in the spritesheet
        save_dir: Directory to save individual sprite files
    """
    # Create hash of filename and parameters for the cache directory
    spritesheet_name = os.path.splitext(os.path.basename(spritesheet_path))[0]
    spritesheet_hash = get_spritesheet_hash(spritesheet_path)
    cache_dir = os.path.join(save_dir, f"{spritesheet_name}_{spritesheet_hash}")

    # Check if cached sprites exist and are valid
    if os.path.exists(cache_dir):
        return load_cached_sprites(cache_dir, columns * rows)

    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    # Load the spritesheet
    spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

    # Calculate sprite dimensions
    sheet_width, sheet_height = spritesheet.get_size()
    sprite_width = sheet_width // columns
    sprite_height = sheet_height // rows

    sprites: List[Surface] = []
    num_sprites: int = columns * rows

    for i in range(num_sprites):
        row = i // columns
        col = i % columns

        # Create sprite surface
        sprite_surface = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)

        # Extract sprite from sheet
        sprite_surface.blit(spritesheet, (0, 0),
                            (col * sprite_width, row * sprite_height,
                             sprite_width, sprite_height))

        # Save individual sprite
        sprite_path = os.path.join(cache_dir, f"sprite_{i}.png")
        pygame.image.save(sprite_surface, sprite_path)

        sprites.append(sprite_surface)

    # Save metadata
    save_metadata(cache_dir, columns, rows, sprite_width, sprite_height)

    return sprites


def load_cached_sprites(cache_dir: str, expected_count: int) -> List[Surface]:
    """Load sprites from cache directory"""
    sprites: List[Surface] = []

    for i in range(expected_count):
        sprite_path = os.path.join(cache_dir, f"sprite_{i}.png")
        if os.path.exists(sprite_path):
            sprite = pygame.image.load(sprite_path).convert_alpha()
            sprites.append(sprite)
        else:
            raise FileNotFoundError(f"Cached sprite {i} not found")

    return sprites


def save_metadata(cache_dir: str, columns: int, rows: int, width: int, height: int):
    """Save spritesheet metadata"""
    metadata = {
        'columns': columns,
        'rows': rows,
        'width': width,
        'height': height
    }
    with open(os.path.join(cache_dir, 'metadata.txt'), 'w') as f:
        for key, value in metadata.items():
            f.write(f"{key}={value}\n")


def load_sprites(spritesheet_path: str, columns: int, rows: int, save_dir: str) -> List[Surface]:
    """
    Main function to load sprites, either from cache or by extracting from spritesheet
    """
    try:
        return extract_and_save_sprites(spritesheet_path, columns, rows, save_dir)
    except Exception as e:
        print(f"Error loading sprites: {e}")
        # Fallback to original extraction method if caching fails
        return extract_sprites(spritesheet_path, columns, rows)


# Usage example:
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define paths
    effects_images_dir = f'../sprites/effects'
    spritesheet_path = f'{effects_images_dir}/flash04.png'
    save_dir = "../sprites/cache/flash04"

    # Load sprites
    sprites = load_sprites(
        spritesheet_path=spritesheet_path,
        columns=11,
        rows=4,
        save_dir=save_dir
    )

    # Use sprites...
    for i, sprite in enumerate(sprites):
        print(f"Loaded sprite {i}: {sprite.get_size()}")


if __name__ == "__main__":
    main()
