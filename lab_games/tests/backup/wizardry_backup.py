import pygame
import sys

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
tile_img = pygame.image.load('TilesDungeon/Tile.png')

# Carte du monde
world_map_old = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0]
]

# Carte du monde
world_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


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


# Fonction pour dessiner le joueur
def draw_player():
    screen.blit(player_img, (player_x * TILE_SIZE, player_y * TILE_SIZE))


# Fonction pour dessiner l'ennemi
def draw_enemy():
    screen.blit(enemy_img, (enemy_x * TILE_SIZE, enemy_y * TILE_SIZE))


# Fonction pour vérifier si le joueur entre en collision avec un ennemi
def check_collision():
    return player_x == enemy_x and player_y == enemy_y

# Fonction pour dessiner la feuille de stats du personnage
def draw_character_stats():
    left = MAP_WIDTH
    top = 0
    width = STATS_WIDTH
    height = MAP_HEIGHT
    pygame.draw.rect(screen, (200, 200, 200), (left, top, width, height))  # Fond de la feuille de stats
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
        text_rect.topleft = (left + 20, top + 20 + i * 30)  # Ajuster la position en fonction de la marge
        screen.blit(text_surface, text_rect)

# Fonction pour dessiner le panneau de commande d'actions
def draw_action_panel():
    left, top, width, height = MAP_HEIGHT, 0, STATS_WIDTH, 300
    pygame.draw.rect(screen, (200, 200, 200), (left, top, width, height))  # Fond du panneau d'actions
    font = pygame.font.Font(None, 24)
    action_texts = [
        "Attaquer",
        "Utiliser objet",
        "Sorts",
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



# Fonction pour dessiner la feuille de stats du personnage
def draw_character_stats_old():
    """ left: La position horizontale du coin supérieur gauche du rectangle.
        top: La position verticale du coin supérieur gauche du rectangle.
        width: La largeur du rectangle.
        height: La hauteur du rectangle.
    """
    left, top, width, height = 0, MAP_WIDTH, STATS_WIDTH, 200
    pygame.draw.rect(screen, (200, 200, 200), (left, top, width, height))  # Fond de la feuille de stats
    font = pygame.font.Font(None, 24)
    stat_texts = [
        "Santé: 100/100",
        "Force: 10",
        "Défense: 5",
        # Ajoutez d'autres statistiques ici
    ]
    for i, stat_text in enumerate(stat_texts):
        text_surface = font.render(stat_text, True, (0, 0, 0))
        screen.blit(text_surface, (100, 70 + i * 30))

# Fonction pour dessiner le panneau de commande d'actions
def draw_action_panel_old():
    left, top, width, height = MAP_HEIGHT, 0, STATS_WIDTH, 300
    pygame.draw.rect(screen, (200, 200, 200), (left, top, width, height))  # Fond du panneau d'actions
    font = pygame.font.Font(None, 24)
    action_texts = [
        "Attaquer",
        "Utiliser objet",
        "Sorts",
        # Ajoutez d'autres actions ici
    ]
    for i, action_text in enumerate(action_texts):
        text_surface = font.render(action_text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (50 + i * 120, MAP_HEIGHT + ACTIONS_HEIGHT // 2)

        # Définir les marges intérieures
        margin_x = 10
        margin_y = 5
        # Calculer les nouvelles coordonnées du rectangle pour centrer les marges intérieures
        rect = pygame.Rect(text_rect.left - margin_x, text_rect.top - margin_y,
                           text_rect.width + margin_x * 2, text_rect.height + margin_y * 2)
        # Dessiner le rectangle avec des coins arrondis autour du texte avec marges intérieures
        pygame.draw.rect(screen, BLACK, rect, 1, border_radius=4)
        screen.blit(text_surface, text_rect)

        # Enregistrer les zones rectangulaires de chaque texte d'action
        action_rects[action_text] = rect


# Chargement de l'image du personnage joueur
player_img = pygame.image.load('Characters/hero.png')
player_x, player_y = 1, 1  # Position initiale du joueur

# Chargement de l'image de l'ennemi
enemy_img = pygame.image.load('Characters/enemy.png')
enemy_x, enemy_y = 3, 3  # Position initiale de l'ennemi

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
            if event.key == pygame.K_UP:
                player_y -= 1
            elif event.key == pygame.K_DOWN:
                player_y += 1
            elif event.key == pygame.K_LEFT:
                player_x -= 1
            elif event.key == pygame.K_RIGHT:
                player_x += 1

    # Vérifier les collisions avec les ennemis
    if check_collision():
        print("Combat!")

    # Rendu
    screen.fill(WHITE)

    # Dessiner la carte
    map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 200), map_rect)
    draw_map()

    # Afficher les personnages
    draw_player()
    draw_enemy()

    # Dessiner la feuille de stats du personnage
    stats_rect = pygame.Rect(MAP_WIDTH, 0, STATS_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 200), stats_rect)
    draw_character_stats()

    # Dessiner le panneau de commande d'actions
    actions_rect = pygame.Rect(0, MAP_HEIGHT, MAP_WIDTH + STATS_WIDTH, ACTIONS_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 200), actions_rect)
    draw_action_panel()

    # # Test
    # rect = pygame.Rect(100, 100, 200, 150)
    # RED = (255, 0, 0)
    # pygame.draw.rect(screen, RED, rect)

    # Mise à jour de l'affichage
    pygame.display.flip()

    # Limiter le nombre d'images par seconde
    pygame.time.Clock().tick(FPS)
