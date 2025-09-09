import pygame
import os

def load_enemy_sprites():
    """Charge les sprites d'ennemis depuis le dossier assets"""
    sprites = {}
    assets_path = "assets/enemies/"
    
    # Créer le dossier s'il n'existe pas
    os.makedirs(assets_path, exist_ok=True)
    
    try:
        # Charger différents types d'ennemis
        enemy_types = ["orc", "skeleton", "goblin", "troll"]
        
        for enemy_type in enemy_types:
            sprite_path = os.path.join(assets_path, f"{enemy_type}.png")
            if os.path.exists(sprite_path):
                sprites[enemy_type] = pygame.image.load(sprite_path).convert_alpha()
            else:
                # Générer un sprite par défaut si l'image n'existe pas
                sprites[enemy_type] = generate_default_sprite(enemy_type)
                
    except Exception as e:
        print(f"Erreur lors du chargement des sprites: {e}")
        # Utiliser les sprites générés par défaut
        sprites = {
            "orc": generate_default_sprite("orc"),
            "skeleton": generate_default_sprite("skeleton"),
            "goblin": generate_default_sprite("goblin")
        }
    
    return sprites

def generate_default_sprite(enemy_type):
    """Génère un sprite par défaut selon le type d'ennemi"""
    sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    if enemy_type == "orc":
        # Orc vert
        pygame.draw.circle(sprite, (100, 150, 50), (32, 40), 24)
        pygame.draw.circle(sprite, (80, 120, 40), (32, 20), 16)
        pygame.draw.circle(sprite, (255, 0, 0), (26, 16), 4)
        pygame.draw.circle(sprite, (255, 0, 0), (38, 16), 4)
    elif enemy_type == "skeleton":
        # Squelette blanc
        pygame.draw.circle(sprite, (240, 240, 240), (32, 40), 24)
        pygame.draw.circle(sprite, (220, 220, 220), (32, 20), 16)
        pygame.draw.circle(sprite, (0, 0, 0), (26, 16), 4)
        pygame.draw.circle(sprite, (0, 0, 0), (38, 16), 4)
    elif enemy_type == "goblin":
        # Gobelin rouge
        pygame.draw.circle(sprite, (200, 0, 0), (32, 40), 20)
        pygame.draw.circle(sprite, (150, 0, 0), (32, 20), 14)
        pygame.draw.circle(sprite, (255, 255, 0), (26, 16), 3)
        pygame.draw.circle(sprite, (255, 255, 0), (38, 16), 3)
    else:
        # Ennemi par défaut
        pygame.draw.circle(sprite, (200, 0, 0), (32, 40), 24)
        pygame.draw.circle(sprite, (150, 0, 0), (32, 20), 16)
        pygame.draw.circle(sprite, (255, 255, 0), (26, 16), 4)
        pygame.draw.circle(sprite, (255, 255, 0), (38, 16), 4)
    
    return sprite

def load_textures():
    """Charge les textures pour les murs"""
    textures = {}
    assets_path = "assets/textures/"
    
    os.makedirs(assets_path, exist_ok=True)
    
    texture_files = ["wall_brick.png", "wall_stone.png", "floor.png"]
    
    for texture_file in texture_files:
        texture_path = os.path.join(assets_path, texture_file)
        if os.path.exists(texture_path):
            textures[texture_file.split('.')[0]] = pygame.image.load(texture_path).convert()
    
    return textures