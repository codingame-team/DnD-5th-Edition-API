import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Paramètres de l'écran
WIDTH, HEIGHT = 800, 600
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Création de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interface Utilisateur Pygame")

# Font
font = pygame.font.SysFont(None, 36)

# Fonction pour dessiner un bouton
def draw_button(surface, rect, color, text):
    pygame.draw.rect(surface, color, rect)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

# Boucle de jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                print("Bouton cliqué!")

    # Rendu
    screen.fill(WHITE)

    # Dessiner le bouton
    button_rect = pygame.Rect(300, 250, 200, 100)
    draw_button(screen, button_rect, (100, 100, 255), "Cliquez ici")

    # Mise à jour de l'affichage
    pygame.display.flip()

    # Limiter le nombre d'images par seconde
    pygame.time.Clock().tick(FPS)

# Quitter Pygame
pygame.quit()
sys.exit()
