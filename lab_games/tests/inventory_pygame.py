import os

import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Définition des constantes
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300
ICON_SIZE = 32
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 0, 255)

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gestion d'inventaire")

path = os.path.dirname(__file__)


# Définition de la classe Item pour représenter un objet dans l'inventaire
class Item:
    def __init__(self, name, description, image):
        self.name = name
        self.description = description
        self.image = image
        self.image.set_colorkey(PINK)  # Définir le fond rose comme transparent
        self.selected = False


# Inventaire du personnage (liste d'objets)

inventory = [
    Item("Épée", "Une épée tranchante", pygame.image.load(f"{path}/sprites/Items/Sword01.PNG")),
    Item("Potion de santé", "Restaure 50 points de vie", pygame.image.load(f"{path}/sprites/Items/PotionRed.PNG")),
    Item("Potion de vitesse", "Accélère la vitesse", pygame.image.load(f"{path}/sprites/Items/PotionTallTan.PNG")),
    Item("Armure", "Une armure solide", pygame.image.load(f"{path}/sprites/Items/ArmorChainMail.PNG")),
    Item("Bottes", "Une paire de bottes dorée", pygame.image.load(f"{path}/sprites/Items/BootsGolden.PNG")),
    Item("Arc", "Un arc long", pygame.image.load(f"{path}/sprites/Items/Bow.PNG")),
    Item("Clef", "Une clef en cuivre", pygame.image.load(f"{path}/sprites/Items/KeyCopper.PNG")),
    Item("Bouclier", "Un bouclier rayé rouge", pygame.image.load(f"{path}/sprites/Items/ShieldStripeRed.PNG")),
    Item("Épée à 2 mains", "Une épée à 2 mains", pygame.image.load(f"{path}/sprites/Items/SwordTwoHanded.PNG")),
    Item("Mace", "Une mace magique", pygame.image.load(f"{path}/sprites/Items/MaceMagic.PNG")),
    Item("Bâton", "Un bâton magique", pygame.image.load(f"{path}/sprites/Items/Staff01.PNG")),
    Item("Fléau", "Un fléau", pygame.image.load(f"{path}/sprites/Items/Flail01.PNG")),
    Item("Sort", "Un méchant sort", pygame.image.load(f"{path}/sprites/Items/Scroll0010.PNG")),
]
inventory += [None] * (20 - len(inventory))


# Fonction pour afficher du texte
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


# Définition de la fonction pour afficher une info-bulle
def draw_tooltip(description, surface, x, y):
    font = pygame.font.Font(None, 18)
    text = font.render(description, True, BLACK)
    text_rect = text.get_rect()
    text_rect.topleft = (x, y)
    pygame.draw.rect(surface, GRAY, (text_rect.left - 5, text_rect.top - 5, text_rect.width + 10, text_rect.height + 10))
    surface.blit(text, text_rect)


# Fonction principale
def main():
    font = pygame.font.Font(None, 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Vérifier si une case de l'inventaire a été cliquée
                    for i, item in enumerate(inventory):
                        if item is not None:
                            icon_rect = item.image.get_rect(topleft=(50 + (i % 5) * 40, 70 + (i // 5) * 40))
                            if icon_rect.collidepoint(event.pos):
                                if item.selected:
                                    item.selected = False
                                else:
                                    item.selected = True
                                break

        # Effacer l'écran
        screen.fill(WHITE)

        # Afficher le titre de l'inventaire
        draw_text("Inventaire", font, BLACK, screen, 10, 10)

        # Obtenir les coordonnées de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Stocker les informations de l'info-bulle
        tooltip_text = None

        # Afficher les cases de l'inventaire
        for i, item in enumerate(inventory):
            # Calculer les coordonnées de l'image dans la case
            icon_x = 50 + (i % 5) * 40
            icon_y = 70 + (i // 5) * 40
            # Afficher l'icône de l'objet s'il y en a un dans la case
            if item is not None:
                screen.blit(item.image, (icon_x, icon_y))
                frame_color: tuple = BLUE if item.selected else GRAY
                pygame.draw.rect(screen, frame_color, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)
                # Vérifier si la souris survole la case
                if pygame.Rect(icon_x, icon_y, ICON_SIZE, ICON_SIZE).collidepoint(mouse_x, mouse_y):
                    # Stocker la description de l'objet pour l'info-bulle
                    tooltip_text = item.description
            # Dessiner un cadre vide pour les cases vides
            else:
                pygame.draw.rect(screen, GRAY, (icon_x, icon_y, ICON_SIZE, ICON_SIZE), 2)

        # Afficher l'info-bulle avec la description de l'objet
        if tooltip_text:
            draw_tooltip(tooltip_text, screen, mouse_x + 10, mouse_y)

        # Mise à jour de l'affichage
        pygame.display.update()


# Exécuter la fonction principale
if __name__ == "__main__":
    main()
