import json

import pygame

from tools.sprite_sheets import load_sprites

# Dimensions de la fenêtre du menu principal
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, pos, frame_rate=10):
        super().__init__()
        self.images = images  # List of frames
        self.current_frame = 0
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)
        self.frame_rate = frame_rate  # Frames per second
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 // self.frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.images)
            self.image = self.images[self.current_frame]


def load_images_old(sprite_name: str = 'goblin.png'):
    # Define paths
    spritesheet_path = f'{sprites_images_dir}/{sprite_name}'
    save_dir = "sprites/cache/goblin"

    # Load sprites
    sprites = load_sprites(
        spritesheet_path=spritesheet_path,
        columns=11,
        rows=5,
        save_dir=save_dir
    )
    return sprites


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


def run(character_name: str = 'Brottor'):

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Add it to a sprite group
    sprites = pygame.sprite.Group()

    # Create an animated sprite
    # https://opengameart.org/content/lpc-goblin
    sprite_sheets_json = load_sprite_config()
    j = 0
    for sprite_config in sprite_sheets_json['sprites']:
        sprite_name = sprite_config['name']
        sprite_sheets = sprite_config['animations']
        j += 100
        sprite_frames = load_images(sprite_name)
        # mud = {'down': (0, 10), 'right':  (11, 21), 'uo': (22, 32), 'left':  (33, 43), 'acrobat': (43, 48)}
        i = 0
        for status, boundaries in sprite_sheets.items():
            i += 100
            start, end = boundaries['start'], boundaries['end']
            animated_sprite = AnimatedSprite(sprite_frames[start:end + 1], (i, j), frame_rate=10)
            sprites.add(animated_sprite)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update and draw sprites
        sprites.update()
        screen.fill((30, 30, 30))  # Clear screen with a dark gray
        sprites.draw(screen)

        pygame.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    pygame.quit()


if __name__ == "__main__":
    # Récupération du personnage choisi par l'utilisateur
    # character_name = sys.argv[1] if len(sys.argv) > 1 else 'Brottor'
    sprites_images_dir = f'sprites/Animations'
    # Example JSON structure
    sprite_config = {
        "sprites": [
            {
                "name": "goblin",
                "filename": "goblin.png",
                "path": "sprites/Animations",
                "columns": 11,
                "rows": 5,
                "cache_dir": "sprites/cache/goblin",
                "animations": {
                    "down": {"start": 0, "end": 10},
                    "right": {"start": 11, "end": 21},
                    "up": {"start": 22, "end": 32},
                    "left": {"start": 33, "end": 43},
                    "acrobat": {"start": 43, "end": 48}
                }
            },
            {
                "name": "goblinsword",
                "filename": "goblinsword.png",
                "path": "sprites/Animations",
                "columns": 11,
                "rows": 5,
                "cache_dir": "sprites/cache/goblinsword",
                "animations": {
                    "down": {"start": 0, "end": 10},
                    "right": {"start": 11, "end": 21},
                    "up": {"start": 22, "end": 32},
                    "left": {"start": 33, "end": 43},
                    "attack": {"start": 43, "end": 48}
                }
            },
            {
                "name": "bat",
                "filename": "bat.PNG",
                "path": "sprites/Animations",
                "columns": 4,
                "rows": 4,
                "cache_dir": "sprites/cache/bat",
                "animations": {
                    "fly": {"start": 0, "end": 3},
                    "attack": {"start": 4, "end": 7},
                    "hurt": {"start": 8, "end": 11},
                    "die": {"start": 12, "end": 15}
                }
            }
        ]
    }

    # Save the JSON structure to a file
    save_sprite_config(sprite_config)
    run()
