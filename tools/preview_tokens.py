import os
import pygame
from pygame.locals import *


def get_screen_resolution():
    info = pygame.display.Info()
    return info.current_w, info.current_h


def load_and_resize_images_from_folder(folder, target_size, valid_extensions=('webp',)):
    images = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(valid_extensions):
            image_path = os.path.join(folder, filename)
            image = pygame.image.load(image_path)
            original_size = image.get_size()
            aspect_ratio = original_size[0] / original_size[1]
            if aspect_ratio > 1:
                new_width = target_size[0]
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = target_size[1]
                new_width = int(new_height * aspect_ratio)
            image = pygame.transform.scale(image, (new_width, new_height))
            images.append(image)
    return images


def calculate_grid_layout(screen_width, screen_height, images_per_page, padding=10):
    rows = int(images_per_page ** 0.5)
    cols = (images_per_page // rows) + (images_per_page % rows > 0)
    max_width = (screen_width - (cols + 1) * padding) // cols
    max_height = (screen_height - (rows + 1) * padding) // rows
    return rows, cols, (max_width, max_height)


def draw_images(screen, images, page, images_per_page, rows, cols, padding=10):
    screen.fill((0, 0, 0))  # Effacer l'écran avec une couleur noire
    start_idx = page * images_per_page
    end_idx = min(start_idx + images_per_page, len(images))

    for idx in range(start_idx, end_idx):
        image = images[idx]
        row = (idx - start_idx) // cols
        col = (idx - start_idx) % cols
        x = col * ((screen.get_width() - (cols + 1) * padding) // cols + padding)
        y = row * ((screen.get_height() - (rows + 1) * padding) // rows + padding)
        screen.blit(image, (x, y))


def main():
    pygame.init()

    # Détecter la résolution de l'écran
    screen_width, screen_height = get_screen_resolution()

    # Définir la taille de la fenêtre pour Pygame
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

    # Paramètres pour l'affichage des images
    folder = "../images/monsters/tokens"
    images_per_page = 50
    padding = 10

    # Calculer la disposition de la grille
    rows, cols, target_size = calculate_grid_layout(screen_width, screen_height, images_per_page, padding)

    # Charger et redimensionner les images
    images = load_and_resize_images_from_folder(folder, target_size)

    # Calculer le nombre total de pages
    total_pages = (len(images) + images_per_page - 1) // images_per_page
    pygame.display.set_caption(f'Afficher les images WebP - Page 1 / {total_pages}')

    current_page = 0

    # Variable pour suivre l'état plein écran
    fullscreen = True

    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_RIGHT:
                    current_page = (current_page + 1) % total_pages
                elif event.key == K_LEFT:
                    current_page = (current_page - 1) % total_pages
                elif event.key == K_SPACE:
                    # Basculer entre plein écran et mode fenêtre
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((screen_width, screen_height))

                # Mettre à jour le titre de la fenêtre avec le numéro de la page
                pygame.display.set_caption(f'Afficher les images WebP - Page {current_page + 1} / {total_pages}')

        # Afficher les images de la page courante
        draw_images(screen, images, current_page, images_per_page, rows, cols, padding)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()