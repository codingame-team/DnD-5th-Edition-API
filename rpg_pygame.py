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


def load_images():
    # Define paths
    sprites_images_dir = f'sprites/Animations'
    spritesheet_path = f'{sprites_images_dir}/goblin.png'
    save_dir = "sprites/cache/goblin"

    # Load sprites
    sprites = load_sprites(
        spritesheet_path=spritesheet_path,
        columns=11,
        rows=5,
        save_dir=save_dir
    )
    return sprites

def run(character_name: str = 'Brottor'):

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Add it to a sprite group
    sprites = pygame.sprite.Group()

    # Create an animated sprite
    sprite_frames = load_images()
    mud = {'down': (0, 10), 'right':  (11, 21), 'uo': (22, 32), 'left':  (33, 43), 'acrobat': (43, 48)}
    i = 0
    for status, (start, end) in mud.items():
        # start, end = mud['acrobat']
        i += 100
        animated_sprite = AnimatedSprite(sprite_frames[start:end + 1], (i, i), frame_rate=10)

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
    run()
