import pygame
import os

def load_enemy_sprites():
    """Load all PNG enemy sprites from assets/enemies/ folder"""
    sprites = {}
    assets_path = "assets/enemies/"
    
    os.makedirs(assets_path, exist_ok=True)
    
    try:
        # Load all PNG files from enemies folder
        for filename in os.listdir(assets_path):
            if filename.lower().endswith('.png'):
                sprite_name = os.path.splitext(filename)[0]  # Remove .png extension
                sprite_path = os.path.join(assets_path, filename)
                sprites[sprite_name] = pygame.image.load(sprite_path).convert_alpha()
                # print(f"Loaded enemy sprite: {sprite_name}")
        
        # Add fallback sprites for common types if not found
        fallback_types = ["orc", "skeleton", "goblin", "troll"]
        for enemy_type in fallback_types:
            if enemy_type not in sprites:
                sprites[enemy_type] = generate_default_sprite(enemy_type)
                
    except Exception as e:
        print(f"Error loading sprites: {e}")
        # Use generated fallback sprites
        sprites = {enemy_type: generate_default_sprite(enemy_type) 
                  for enemy_type in ["orc", "skeleton", "goblin", "troll"]}
    
    print(f"Total enemy sprites loaded: {len(sprites)}")
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