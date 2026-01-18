import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Taille de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Définition des zones
ZONE_WIDTH = SCREEN_WIDTH // 2
ZONE_HEIGHT = SCREEN_HEIGHT // 2

ZONE_TOP_LEFT = pygame.Rect(0, 0, ZONE_WIDTH, ZONE_HEIGHT)
ZONE_TOP_RIGHT = pygame.Rect(ZONE_WIDTH, 0, ZONE_WIDTH, ZONE_HEIGHT)
ZONE_BOTTOM_LEFT = pygame.Rect(0, ZONE_HEIGHT, ZONE_WIDTH, ZONE_HEIGHT)
ZONE_BOTTOM_RIGHT = pygame.Rect(ZONE_WIDTH, ZONE_HEIGHT, ZONE_WIDTH, ZONE_HEIGHT)

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zones de jeu Pygame")

clock = pygame.time.Clock()

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Efface l'écran avec la couleur de fond
        screen.fill(WHITE)

        # Dessine des rectangles pour représenter les zones
        pygame.draw.rect(screen, RED, ZONE_TOP_LEFT)
        pygame.draw.rect(screen, GREEN, ZONE_TOP_RIGHT)
        pygame.draw.rect(screen, BLUE, ZONE_BOTTOM_LEFT)
        pygame.draw.rect(screen, BLACK, ZONE_BOTTOM_RIGHT)

        # Met à jour l'affichage
        pygame.display.flip()

        # Limite la vitesse de rafraîchissement de l'écran
        clock.tick(60)

if __name__ == "__main__":
    main()
