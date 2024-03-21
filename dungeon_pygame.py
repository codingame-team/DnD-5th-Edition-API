from __future__ import annotations

from dataclasses import dataclass

import pygame
import sys

from pygame import SurfaceType, Surface

# Initialisation de Pygame
pygame.init()

# Définition des constantes pour la mise en page
STATS_WIDTH = 200
ACTIONS_HEIGHT = 200

# Paramètres de l'écran
TILE_SIZE = 32
# ROWS, COLS = HEIGHT // TILE_SIZE, WIDTH // TILE_SIZE
# ROWS, COLS = 5, 5
ROWS, COLS = 10, 10
MAP_WIDTH, MAP_HEIGHT = TILE_SIZE * ROWS, TILE_SIZE * COLS
SCREEN_WIDTH = MAP_WIDTH + STATS_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT + ACTIONS_HEIGHT
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RPG avec Pygame")

# Font
font = pygame.font.SysFont(None, 36)

# Chargement des tuiles
tile_img = pygame.image.load('sprites/TilesDungeon/Tile.png')

# Carte du monde
# world_map_old = [
#     [0, 0, 0, 0, 0],
#     [0, 1, 1, 1, 0],
#     [0, 1, 0, 1, 0],
#     [0, 1, 1, 1, 0],
#     [0, 0, 0, 0, 0]
# ]

# Carte du monde
world_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

UP, DOWN, LEFT, RIGHT = (0, -1), (0, 1), (-1, 0), (1, 0)


@dataclass
class Character:
    x: int
    y: int
    img: Surface | SurfaceType

    def draw(self, screen):
        screen.blit(self.img, (self.x * TILE_SIZE, self.y * TILE_SIZE))

    def can_move(self, dir: tuple) -> bool:
        dx, dy = dir
        x, y = self.x + dx, self.y + dy
        return 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT and world_map[y][x] == 1

    def check_collision(self, other: "Character"):
        return self.x == other.x and self.y == other.y


# Fonction pour dessiner la carte
def draw_map():
    for row in range(ROWS):
        for col in range(COLS):
            tile_x, tile_y = col * TILE_SIZE, row * TILE_SIZE
            if world_map[row][col] == 0:
                screen.blit(tile_img, (tile_x, tile_y))


# Fonction pour dessiner un bouton
def draw_button(surface, rect, color, text):
    pygame.draw.rect(surface, color, rect)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


# Fonction pour dessiner la feuille de stats du personnage
def draw_character_stats():
    stats_rect = pygame.Rect(MAP_WIDTH, 0, STATS_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 200), stats_rect)
    font = pygame.font.Font(None, 24)
    stat_texts = [
        "Santé: 100/100",
        "Force: 10",
        "Défense: 5",
        # Ajoutez d'autres statistiques ici
    ]
    for i, stat_text in enumerate(stat_texts):
        text_surface = font.render(stat_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.topleft = (stats_rect[0] + 20, stats_rect[1] + 20 + i * 30)  # Ajuster la position en fonction de la marge
        screen.blit(text_surface, text_rect)


# Fonction pour dessiner le panneau de commande d'actions
def draw_action_panel():
    """ left: La position horizontale du coin supérieur gauche du rectangle.
        top: La position verticale du coin supérieur gauche du rectangle.
        width: La largeur du rectangle.
        height: La hauteur du rectangle.
    """
    actions_rect = pygame.Rect(0, MAP_HEIGHT, SCREEN_WIDTH, ACTIONS_HEIGHT)
    left, top, width, height = actions_rect
    pygame.draw.rect(screen, (200, 200, 200), actions_rect)
    # left, top, width, height = MAP_HEIGHT, 0, STATS_WIDTH, 300
    # pygame.draw.rect(screen, (200, 200, 200), (left, top, width, height))  # Fond du panneau d'actions
    font = pygame.font.Font(None, 24)
    action_texts = [
        "Attaquer",
        "Utiliser objet",
        "Sorts",
        "Inventaire"
        # Ajoutez d'autres actions ici
    ]
    action_count = len(action_texts)
    action_height = height // action_count  # Calcul de la hauteur de chaque action
    for i, action_text in enumerate(action_texts):
        text_surface = font.render(action_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (left + width // 2, top + i * action_height + action_height // 2)

        # Définir les marges intérieures
        margin_x = 10
        margin_y = 5
        # Calculer les nouvelles coordonnées du rectangle pour centrer les marges intérieures
        rect = pygame.Rect(left + margin_x, top + i * action_height + margin_y,
                           width - 2 * margin_x, action_height - 2 * margin_y)
        # Dessiner le rectangle avec des coins arrondis autour du texte avec marges intérieures
        pygame.draw.rect(screen, BLACK, rect, 1, border_radius=4)
        screen.blit(text_surface, text_rect)

        # Enregistrer les zones rectangulaires de chaque texte d'action
        action_rects[action_text] = rect


# Chargement de l'image du personnage joueur
player_img = pygame.image.load('sprites/hero.png')
player_x, player_y = 1, 1  # Position initiale du joueur
player: Character = Character(x=player_x, y=player_y, img=player_img)

# Chargement de l'image de l'ennemi
enemy_img = pygame.image.load('sprites/enemy.png')
enemy_x, enemy_y = 3, 3  # Position initiale de l'ennemi
enemy: Character = Character(x=enemy_x, y=enemy_y, img=enemy_img)

# Initialiser le dictionnaire pour enregistrer les zones rectangulaires de chaque texte d'action
action_rects = {}

# Boucle de jeu
running = True
while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifier si un texte d'action a été cliqué
            for action_text, action_rect in action_rects.items():
                if action_rect.collidepoint(event.pos):
                    print(f"Action: {action_text}")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and player.can_move(UP):
                player.y -= 1
            elif event.key == pygame.K_DOWN and player.can_move(DOWN):
                player.y += 1
            elif event.key == pygame.K_LEFT and player.can_move(LEFT):
                player.x -= 1
            elif event.key == pygame.K_RIGHT and player.can_move(RIGHT):
                player.x += 1

    # Vérifier les collisions avec les ennemis
    if player.check_collision(enemy):
        print("Combat!")

    # Rendu
    screen.fill(WHITE)

    # Dessiner la carte
    map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 200), map_rect)
    draw_map()

    # Afficher les personnages
    player.draw(screen)
    enemy.draw(screen)

    # Dessiner la feuille de stats du personnage
    draw_character_stats()

    # Dessiner le panneau de commande d'actions
    draw_action_panel()

    # Mise à jour de l'affichage
    pygame.display.flip()

    # Limiter le nombre d'images par seconde
    pygame.time.Clock().tick(FPS)
