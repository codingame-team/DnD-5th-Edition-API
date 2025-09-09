import random
import pygame
import math
from load_assets import load_enemy_sprites, load_textures

# Initialiser le mixer pour les sons
pygame.mixer.init()

def init_dungeon(width=20, height=20):
    return {"width": width, "height": height, "grid": [[0] * width for _ in range(height)], "rooms": []}

def room_overlaps(new_room, existing_rooms):
    x, y, w, h = new_room["x"], new_room["y"], new_room["w"], new_room["h"]
    return any(x < r["x"] + r["w"] and x + w > r["x"] and y < r["y"] + r["h"] and y + h > r["y"] for r in existing_rooms)

def create_room(grid, room):
    for i in range(room["x"], room["x"] + room["w"]):
        for j in range(room["y"], room["y"] + room["h"]):
            grid[j][i] = 1

def emplace_rooms(dungeon, max_rooms=10, min_size=3, max_size=6):
    width, height = dungeon["width"], dungeon["height"]
    grid = dungeon["grid"]
    rooms = []

    for _ in range(max_rooms):
        w, h = random.randint(min_size, max_size), random.randint(min_size, max_size)
        x, y = random.randint(1, width - w - 1), random.randint(1, height - h - 1)
        new_room = {"x": x, "y": y, "w": w, "h": h}
        
        if not room_overlaps(new_room, rooms):
            rooms.append(new_room)
            create_room(grid, new_room)

    dungeon["rooms"] = rooms

def create_corridor(grid, x1, y1, x2, y2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if grid[y1][x] == 0:
            grid[y1][x] = 1
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if grid[y][x2] == 0:
            grid[y][x2] = 1

def corridors(dungeon):
    rooms = dungeon["rooms"]
    grid = dungeon["grid"]
    
    for i in range(len(rooms) - 1):
        a, b = rooms[i], rooms[i + 1]
        ax, ay = a["x"] + a["w"] // 2, a["y"] + a["h"] // 2
        bx, by = b["x"] + b["w"] // 2, b["y"] + b["h"] // 2
        create_corridor(grid, ax, ay, bx, by)

class Player3D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.fov = math.pi / 3
        self.hp = 100
        self.max_hp = 100
        self.shoot_cooldown = 0
        self.potions = 0
        self.shoot_flash = 0
        
    def move(self, dx, dy, dungeon):
        new_x = self.x + dx * 0.1
        new_y = self.y + dy * 0.1
        
        if dungeon["width"] > int(new_x) >= 0 != dungeon["grid"][int(new_y)][int(new_x)] and 0 <= int(new_y) < dungeon["height"]:
            self.x, self.y = new_x, new_y
    
    def rotate(self, angle_delta):
        self.angle += angle_delta
    
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
    
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.shoot_flash > 0:
            self.shoot_flash -= 1
    
    def use_potion(self):
        if self.potions > 0 and self.hp < self.max_hp:
            self.potions -= 1
            heal_amount = random.randint(20, 40)
            self.hp = min(self.max_hp, self.hp + heal_amount)
            try:
                heal_sound = pygame.mixer.Sound(buffer=b'\x00\x40' * 800)
                heal_sound.set_volume(0.6)
                heal_sound.play()
            except:
                pass
            return True
        return False
    
    def _calculate_shoot_angle(self, mouse_x, screen_width):
        center_x = screen_width // 2
        angle_offset = (mouse_x - center_x) / center_x * (self.fov / 2)
        return self.angle + angle_offset
    
    def _play_shoot_sound(self):
        try:
            shoot_sound = pygame.mixer.Sound(buffer=b'\x00\x80' * 1500)
            shoot_sound.set_volume(0.8)
            shoot_sound.play()
        except:
            pass
    
    def shoot(self, mouse_x, mouse_y, screen_width, screen_height, enemies, dungeon):
        if self.shoot_cooldown > 0:
            return None
        
        shoot_angle = self._calculate_shoot_angle(mouse_x, screen_width)
        self.shoot_cooldown = 30
        self.shoot_flash = 8
        self._play_shoot_sound()
        
        return Bullet(self.x, self.y, shoot_angle, True)

class Bullet:
    def __init__(self, x, y, angle, is_player_bullet=True):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.3
        self.life = 60  # 1 seconde à 60 FPS
        self.is_player_bullet = is_player_bullet
    
    def update(self, dungeon):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        
        return not is_wall_collision(self.x, self.y, dungeon) and self.life > 0

class HealthPotion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heal_amount = random.randint(20, 40)

class Enemy:
    def __init__(self, x, y, enemy_type="orc"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.move_timer = 0
        self.shoot_timer = 0
        self.is_shooting = False
        self.shoot_animation = 0
        self.hit_animation = 0
    
    def _try_move(self, dungeon):
        self.move_timer += 1
        if self.move_timer > 60:
            dx, dy = random.choice([-0.5, 0, 0.5]), random.choice([-0.5, 0, 0.5])
            new_x, new_y = self.x + dx, self.y + dy
            
            if not is_wall_collision(new_x, new_y, dungeon):
                self.x, self.y = new_x, new_y
            self.move_timer = 0
    
    def _try_shoot(self, player):
        distance = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        if distance < 8:
            self.shoot_timer += 1
            if self.shoot_timer > 120:
                self.is_shooting = True
                self.shoot_animation = 15
                self.shoot_timer = 0
                try:
                    shoot_sound = pygame.mixer.Sound(buffer=b'\x00\xFF' * 2000)
                    shoot_sound.set_volume(1.0)
                    shoot_sound.play()
                except:
                    pass
                
                angle_to_player = math.atan2(player.y - self.y, player.x - self.x)
                return Bullet(self.x, self.y, angle_to_player, False)
        return None
    
    def _update_animations(self):
        if self.shoot_animation > 0:
            self.shoot_animation -= 1
            if self.shoot_animation == 0:
                self.is_shooting = False
        
        if self.hit_animation > 0:
            self.hit_animation -= 1
    
    def update(self, player, dungeon):
        self._try_move(dungeon)
        bullet = self._try_shoot(player)
        self._update_animations()
        return bullet or 0

def generate_enemy_sprite():
    """Génère un sprite d'ennemi simple"""
    sprite = pygame.Surface((64, 64))
    sprite.fill((0, 0, 0, 0))  # Transparent
    
    # Corps (cercle rouge)
    pygame.draw.circle(sprite, (200, 0, 0), (32, 40), 24)
    # Tête (cercle plus petit)
    pygame.draw.circle(sprite, (150, 0, 0), (32, 20), 16)
    # Yeux
    pygame.draw.circle(sprite, (255, 255, 0), (26, 16), 4)
    pygame.draw.circle(sprite, (255, 255, 0), (38, 16), 4)
    
    return sprite

def cast_ray(player, angle, dungeon, max_distance=20, step=0.1):
    x, y = player.x, player.y
    dx = math.cos(angle) * step
    dy = math.sin(angle) * step
    
    steps = int(max_distance / step)
    for _ in range(steps):
        x += dx
        y += dy
        
        if is_wall_collision(x, y, dungeon):
            distance = math.sqrt((x - player.x)**2 + (y - player.y)**2)
            return distance, x, y
    
    return max_distance, x, y

def is_wall_collision(x, y, dungeon):
    return (x < 0 or x >= dungeon["width"] or y < 0 or y >= dungeon["height"] or 
            dungeon["grid"][int(y)][int(x)] == 0)

def has_line_of_sight(player, enemy, dungeon):
    dx = enemy.x - player.x
    dy = enemy.y - player.y
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance == 0:
        return True
    
    steps = max(1, int(distance * 10))
    step_x, step_y = dx / steps, dy / steps
    
    x, y = player.x, player.y
    for _ in range(steps):
        x += step_x
        y += step_y
        if is_wall_collision(x, y, dungeon):
            return False
    
    return True

def render_3d(screen, player, dungeon, enemies, enemy_sprites, health_potions, bullets):
    width, height = screen.get_size()
    
    # Ciel et sol
    screen.fill((50, 50, 100))  # Ciel sombre
    pygame.draw.rect(screen, (100, 50, 0), (0, height//2, width, height//2))  # Sol
    
    # Raycasting avec rendu optimisé
    for x in range(0, width, 2):  # Réduire la résolution
        angle = player.angle - player.fov/2 + (x / width) * player.fov
        distance, hit_x, hit_y = cast_ray(player, angle, dungeon)
        
        # Correction de la distorsion
        distance *= math.cos(angle - player.angle)
        
        if distance > 0:
            wall_height = int(height / (distance + 0.1))
            wall_top = (height - wall_height) // 2
            wall_bottom = wall_top + wall_height
            
            # Texture simple basée sur la position
            wall_x = hit_x - math.floor(hit_x)
            if abs(math.cos(angle)) > abs(math.sin(angle)):
                wall_x = hit_y - math.floor(hit_y)
            
            # Couleur de base avec variation
            base_color = 120 if int(wall_x * 8) % 2 == 0 else 100
            brightness = max(50, 255 - int(distance * 12))
            color = (min(255, base_color + brightness//3), min(255, base_color//2 + brightness//4), min(255, base_color//3 + brightness//5))
            
            # Dessiner une ligne plus large pour compenser la résolution réduite
            pygame.draw.line(screen, color, (x, wall_top), (x, wall_bottom), 2)
    
    # Rendu des ennemis
    for enemy in enemies:
        # Calculer la distance et l'angle vers l'ennemi
        dx = enemy.x - player.x
        dy = enemy.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 10:  # Seulement si proche
            enemy_angle = math.atan2(dy, dx)
            angle_diff = enemy_angle - player.angle
            
            # Normaliser l'angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            # Vérifier si l'ennemi est dans le champ de vision ET visible (pas de mur)
            if abs(angle_diff) < player.fov / 2 and has_line_of_sight(player, enemy, dungeon):
                screen_x = int(width/2 + (angle_diff / (player.fov/2)) * width/2)
                enemy_size = max(40, int(250 / (distance + 0.1)))
                enemy_y = height//2 - enemy_size//2
                
                # Dessiner le sprite d'ennemi
                if 0 <= screen_x < width and enemy_size > 10:
                    # Redimensionner le sprite selon la distance
                    sprite_surface = enemy_sprites.get(enemy.enemy_type, enemy_sprites.get('orc', generate_enemy_sprite()))
                    scaled_sprite = pygame.transform.scale(sprite_surface, (enemy_size, enemy_size))
                    
                    # Appliquer l'ombrage selon la distance
                    brightness = max(0.3, 1.0 - distance / 10)
                    dark_sprite = scaled_sprite.copy()
                    
                    # Animation ennemi touché (flash rouge)
                    if enemy.hit_animation > 0:
                        hit_intensity = enemy.hit_animation / 10.0
                        red_tint = (255, int(100 * hit_intensity), int(100 * hit_intensity))
                        dark_sprite.fill(red_tint, special_flags=pygame.BLEND_MULT)
                    else:
                        dark_sprite.fill((int(255 * brightness), int(255 * brightness), int(255 * brightness)), special_flags=pygame.BLEND_MULT)
                    
                    screen.blit(dark_sprite, (screen_x - enemy_size//2, enemy_y))
                    
                    # Animation de tir
                    if enemy.is_shooting and enemy.shoot_animation > 0:
                        # Flash jaune qui diminue avec l'animation
                        flash_intensity = enemy.shoot_animation / 15.0
                        flash_size = int((enemy_size + 20) * flash_intensity)
                        flash_color = (int(255 * flash_intensity), int(255 * flash_intensity), 0)
                        
                        # Flash principal
                        pygame.draw.circle(screen, flash_color, (screen_x, enemy_y + enemy_size//2), flash_size//3)
                        
                        # Particules de tir
                        for i in range(3):
                            particle_x = screen_x + random.randint(-flash_size//2, flash_size//2)
                            particle_y = enemy_y + enemy_size//2 + random.randint(-flash_size//3, flash_size//3)
                            particle_size = max(1, int(flash_size//6 * flash_intensity))
                            pygame.draw.circle(screen, (255, 200, 0), (particle_x, particle_y), particle_size)
    
    # Rendu des potions de vie
    for potion in health_potions:
        dx = potion.x - player.x
        dy = potion.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 8:
            potion_angle = math.atan2(dy, dx)
            angle_diff = potion_angle - player.angle
            
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            if abs(angle_diff) < player.fov / 2 and has_line_of_sight(player, potion, dungeon):
                screen_x = int(width/2 + (angle_diff / (player.fov/2)) * width/2)
                potion_size = max(20, int(150 / (distance + 0.1)))
                potion_y = height//2 - potion_size//2
                
                if 0 <= screen_x < width and potion_size > 5:
                    # Dessiner la potion flottante (croix verte)
                    pygame.draw.circle(screen, (0, 255, 0), (screen_x, potion_y + potion_size//2), potion_size//3)
                    pygame.draw.line(screen, (255, 255, 255), 
                                   (screen_x - potion_size//4, potion_y + potion_size//2), 
                                   (screen_x + potion_size//4, potion_y + potion_size//2), 3)
                    pygame.draw.line(screen, (255, 255, 255), 
                                   (screen_x, potion_y + potion_size//2 - potion_size//4), 
                                   (screen_x, potion_y + potion_size//2 + potion_size//4), 3)
    
    # Rendu des balles
    for bullet in bullets:
        dx = bullet.x - player.x
        dy = bullet.y - player.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 8:
            bullet_angle = math.atan2(dy, dx)
            angle_diff = bullet_angle - player.angle
            
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            
            if abs(angle_diff) < player.fov / 2:
                screen_x = int(width/2 + (angle_diff / (player.fov/2)) * width/2)
                bullet_size = max(3, int(20 / (distance + 0.1)))
                bullet_y = height//2
                
                if 0 <= screen_x < width:
                    # Couleur selon qui a tiré
                    bullet_color = (255, 255, 0) if bullet.is_player_bullet else (255, 100, 100)
                    pygame.draw.circle(screen, bullet_color, (screen_x, bullet_y), bullet_size)
    
    # Afficher la jauge de vie (en haut à droite)
    health_bar_width = 200
    health_bar_height = 20
    health_x = width - health_bar_width - 10
    health_y = 10
    
    # Barre de fond (rouge)
    pygame.draw.rect(screen, (100, 0, 0), (health_x, health_y, health_bar_width, health_bar_height))
    
    # Barre de vie (verte)
    health_ratio = player.hp / player.max_hp
    health_width = int(health_bar_width * health_ratio)
    pygame.draw.rect(screen, (0, 255, 0), (health_x, health_y, health_width, health_bar_height))
    
    # Contour de la barre
    pygame.draw.rect(screen, (255, 255, 255), (health_x, health_y, health_bar_width, health_bar_height), 2)
    
    # Texte HP
    font = pygame.font.Font(None, 24)
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
    screen.blit(hp_text, (health_x, health_y + health_bar_height + 5))
    
    # Afficher le nombre de potions (à gauche de la jauge de vie)
    potion_text = font.render(f"Potions: {player.potions}", True, (0, 255, 0))
    screen.blit(potion_text, (health_x - 120, health_y + 5))
    
    # Crosshair (viseur)
    center_x, center_y = width // 2, height // 2
    crosshair_size = 10
    crosshair_color = (255, 255, 255) if player.shoot_cooldown == 0 else (255, 0, 0)
    
    # Lignes du crosshair
    pygame.draw.line(screen, crosshair_color, 
                    (center_x - crosshair_size, center_y), 
                    (center_x + crosshair_size, center_y), 2)
    pygame.draw.line(screen, crosshair_color, 
                    (center_x, center_y - crosshair_size), 
                    (center_x, center_y + crosshair_size), 2)
    
    # Animation de tir du joueur
    if player.shoot_flash > 0:
        flash_intensity = player.shoot_flash / 8.0
        flash_size = int(30 * flash_intensity)
        flash_color = (255, int(255 * flash_intensity), 0)
        
        # Flash au centre de l'écran
        pygame.draw.circle(screen, flash_color, (center_x, center_y), flash_size//2)
        
        # Particules de tir
        for i in range(5):
            particle_x = center_x + random.randint(-flash_size, flash_size)
            particle_y = center_y + random.randint(-flash_size//2, flash_size//2)
            particle_size = max(1, int(flash_size//4 * flash_intensity))
            pygame.draw.circle(screen, (255, 200, 0), (particle_x, particle_y), particle_size)

def show_3d_instructions(screen, font):
    screen.fill((0, 0, 0))
    instructions = [
        "DUNGEON EXPLORER 3D",
        "",
        "CONTROLES:",
        "Z/S - Avancer/Reculer",
        "Q/D - Tourner gauche/droite",
        "Flèches - Déplacement latéral",
        "Clic gauche - Tirer sur les ennemis",
        "P - Utiliser une potion",
        "",
        "Éliminez tous les ennemis!",
        "",
        "Appuyez sur ESPACE pour commencer"
    ]
    
    for i, line in enumerate(instructions):
        color = (255, 255, 0) if i == 0 else (255, 255, 255)
        text = font.render(line, True, color)
        text_rect = text.get_rect(center=(screen.get_width()//2, 100 + i*30))
        screen.blit(text, text_rect)
    
    pygame.display.flip()

def play_3d_dungeon():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dungeon Explorer 3D")
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    
    # Charger les assets
    try:
        enemy_sprites = load_enemy_sprites()
        textures = load_textures()
    except:
        # Fallback si load_assets échoue
        enemy_sprites = {'orc': generate_enemy_sprite()}
        textures = {}
    
    # Instructions
    show_3d_instructions(screen, font)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    
    # Générer le donjon
    dungeon = init_dungeon(20, 20)
    emplace_rooms(dungeon)
    corridors(dungeon)
    
    # Placer le joueur
    if dungeon["rooms"]:
        room = dungeon["rooms"][0]
        player = Player3D(room["x"] + 1, room["y"] + 1)
    else:
        player = Player3D(1, 1)
    

    
    # Placer les ennemis
    enemies = []
    for i in range(3):  # 3 ennemis
        if len(dungeon["rooms"]) > i + 1:
            room = dungeon["rooms"][i + 1]
            enemy = Enemy(room["x"] + 1, room["y"] + 1)
            enemies.append(enemy)
    
    # Initialiser les balles
    bullets = []
    
    # Placer les potions de vie
    health_potions = []
    for _ in range(3):  # 3 potions
        attempts = 0
        while attempts < 50:
            x = random.randint(1, dungeon["width"] - 2)
            y = random.randint(1, dungeon["height"] - 2)
            if dungeon["grid"][y][x] != 0:
                # Vérifier qu'il n'y a pas d'ennemi ou de joueur trop proche
                too_close = False
                if abs(x - player.x) < 2 and abs(y - player.y) < 2:
                    too_close = True
                for enemy in enemies:
                    if abs(x - enemy.x) < 2 and abs(y - enemy.y) < 2:
                        too_close = True
                        break
                if not too_close:
                    health_potions.append(HealthPotion(x, y))
                    break
            attempts += 1
    
    running = True
    while running:
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                mouse_x, mouse_y = event.pos
                bullet = player.shoot(mouse_x, mouse_y, 800, 600, enemies, dungeon)
                if bullet:
                    bullets.append(bullet)
        
        # Contrôles
        if keys[pygame.K_z]:  # Avancer
            dx = math.cos(player.angle)
            dy = math.sin(player.angle)
            player.move(dx, dy, dungeon)
        if keys[pygame.K_s]:  # Reculer
            dx = -math.cos(player.angle)
            dy = -math.sin(player.angle)
            player.move(dx, dy, dungeon)
        if keys[pygame.K_q]:  # Tourner gauche
            player.rotate(-0.05)
        if keys[pygame.K_d]:  # Tourner droite
            player.rotate(0.05)
        if keys[pygame.K_LEFT]:  # Déplacement latéral gauche
            dx = math.cos(player.angle - math.pi/2)
            dy = math.sin(player.angle - math.pi/2)
            player.move(dx, dy, dungeon)
        if keys[pygame.K_RIGHT]:  # Déplacement latéral droite
            dx = math.cos(player.angle + math.pi/2)
            dy = math.sin(player.angle + math.pi/2)
            player.move(dx, dy, dungeon)
        if keys[pygame.K_p]:  # Utiliser une potion
            player.use_potion()
        
        # Vérifier si tous les ennemis sont éliminés
        if len(enemies) == 0:
            # Écran de victoire
            screen.fill((0, 0, 0))
            win_text = font.render("VICTOIRE! Tous les ennemis éliminés!", True, (0, 255, 0))
            restart_text = pygame.font.Font(None, 24).render("Appuyez sur R pour rejouer ou ESC pour quitter", True, (255, 255, 255))
            win_rect = win_text.get_rect(center=(400, 280))
            restart_rect = restart_text.get_rect(center=(400, 320))
            screen.blit(win_text, win_rect)
            screen.blit(restart_text, restart_rect)
            pygame.display.flip()
            
            waiting_end = True
            while waiting_end:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        return play_3d_dungeon()  # Redémarrer
        
        # Mettre à jour le joueur
        player.update()
        
        # Vérifier la collecte de potions
        for potion in health_potions[:]:
            if abs(player.x - potion.x) < 0.5 and abs(player.y - potion.y) < 0.5:
                player.potions += 1
                health_potions.remove(potion)
                try:
                    pickup_sound = pygame.mixer.Sound(buffer=b'\x00\x20' * 600)
                    pickup_sound.set_volume(0.4)
                    pickup_sound.play()
                except:
                    pass
        
        # Mettre à jour les balles
        for bullet in bullets[:]:
            if not bullet.update(dungeon):
                bullets.remove(bullet)
                continue
            
            # Vérifier collisions
            if bullet.is_player_bullet:
                # Balle du joueur vs ennemis
                for enemy in enemies[:]:
                    if abs(bullet.x - enemy.x) < 0.3 and abs(bullet.y - enemy.y) < 0.3:
                        enemy.hit_animation = 10
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        break
            else:
                # Balle d'ennemi vs joueur
                if abs(bullet.x - player.x) < 0.3 and abs(bullet.y - player.y) < 0.3:
                    player.take_damage(random.randint(15, 25))
                    bullets.remove(bullet)
        
        # Mettre à jour les ennemis et gérer les tirs
        for enemy in enemies:
            bullet = enemy.update(player, dungeon)
            if bullet:
                bullets.append(bullet)
        

        
        # Vérifier si le joueur est mort
        if player.hp <= 0:
            screen.fill((0, 0, 0))
            
            # Messages de game over
            title_text = font.render("VOUS ÊTES MORT!", True, (255, 0, 0))
            subtitle_text = pygame.font.Font(None, 28).render("Les ennemis ont eu raison de vous...", True, (255, 255, 255))
            restart_text = pygame.font.Font(None, 24).render("Appuyez sur R pour rejouer ou ESC pour quitter", True, (200, 200, 200))
            
            title_rect = title_text.get_rect(center=(400, 250))
            subtitle_rect = subtitle_text.get_rect(center=(400, 300))
            restart_rect = restart_text.get_rect(center=(400, 350))
            
            screen.blit(title_text, title_rect)
            screen.blit(subtitle_text, subtitle_rect)
            screen.blit(restart_text, restart_rect)
            pygame.display.flip()
            
            waiting_death = True
            while waiting_death:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        return
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        return play_3d_dungeon()  # Redémarrer
        
        # Rendu 3D
        render_3d(screen, player, dungeon, enemies, enemy_sprites, health_potions, bullets)
        
        # Mini-carte
        mini_size = 150
        mini_scale = mini_size / max(dungeon["width"], dungeon["height"])
        pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, mini_size, mini_size))
        
        for y in range(dungeon["height"]):
            for x in range(dungeon["width"]):
                if dungeon["grid"][y][x] != 0:
                    color = (100, 100, 100)
                    pygame.draw.rect(screen, color, 
                                   (10 + x * mini_scale, 10 + y * mini_scale, mini_scale, mini_scale))
        
        # Position du joueur sur la mini-carte
        player_map_x = int(10 + player.x * mini_scale)
        player_map_y = int(10 + player.y * mini_scale)
        pygame.draw.circle(screen, (255, 255, 0), (player_map_x, player_map_y), 3)
        
        # Direction du joueur (flèche)
        direction_length = 8
        end_x = player_map_x + int(math.cos(player.angle) * direction_length)
        end_y = player_map_y + int(math.sin(player.angle) * direction_length)
        pygame.draw.line(screen, (255, 255, 255), (player_map_x, player_map_y), (end_x, end_y), 2)
        

        
        # Ennemis sur la mini-carte
        for enemy in enemies:
            pygame.draw.circle(screen, (255, 0, 0), 
                              (int(10 + enemy.x * mini_scale), int(10 + enemy.y * mini_scale)), 2)
        
        # Potions sur la mini-carte
        for potion in health_potions:
            pygame.draw.circle(screen, (0, 255, 0), 
                              (int(10 + potion.x * mini_scale), int(10 + potion.y * mini_scale)), 2)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    play_3d_dungeon()

def init_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Dungeon Explorer 3D")
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    
    try:
        enemy_sprites = load_enemy_sprites()
        textures = load_textures()
    except:
        enemy_sprites = {'orc': generate_enemy_sprite()}
        textures = {}
    
    return screen, font, clock, enemy_sprites, textures

def setup_dungeon():
    dungeon = init_dungeon(20, 20)
    emplace_rooms(dungeon)
    corridors(dungeon)
    return dungeon

def place_entities(dungeon):
    # Player
    if dungeon["rooms"]:
        room = dungeon["rooms"][0]
        player = Player3D(room["x"] + 1, room["y"] + 1)
    else:
        player = Player3D(1, 1)
    
    # Enemies
    enemies = []
    for i in range(3):
        if len(dungeon["rooms"]) > i + 1:
            room = dungeon["rooms"][i + 1]
            enemies.append(Enemy(room["x"] + 1, room["y"] + 1))
    
    # Health potions
    health_potions = []
    for _ in range(3):
        for _ in range(50):
            x, y = random.randint(1, dungeon["width"] - 2), random.randint(1, dungeon["height"] - 2)
            if (dungeon["grid"][y][x] != 0 and 
                abs(x - player.x) >= 2 and abs(y - player.y) >= 2 and
                all(abs(x - e.x) >= 2 and abs(y - e.y) >= 2 for e in enemies)):
                health_potions.append(HealthPotion(x, y))
                break
    
    return player, enemies, health_potions

def handle_input(keys, player, dungeon):
    if keys[pygame.K_z]:
        player.move(math.cos(player.angle), math.sin(player.angle), dungeon)
    if keys[pygame.K_s]:
        player.move(-math.cos(player.angle), -math.sin(player.angle), dungeon)
    if keys[pygame.K_q]:
        player.rotate(-0.05)
    if keys[pygame.K_d]:
        player.rotate(0.05)
    if keys[pygame.K_LEFT]:
        player.move(math.cos(player.angle - math.pi/2), math.sin(player.angle - math.pi/2), dungeon)
    if keys[pygame.K_RIGHT]:
        player.move(math.cos(player.angle + math.pi/2), math.sin(player.angle + math.pi/2), dungeon)
    if keys[pygame.K_p]:
        player.use_potion()

def update_bullets(bullets, dungeon, player, enemies):
    for bullet in bullets[:]:
        if not bullet.update(dungeon):
            bullets.remove(bullet)
            continue
        
        if bullet.is_player_bullet:
            for enemy in enemies[:]:
                if abs(bullet.x - enemy.x) < 0.3 and abs(bullet.y - enemy.y) < 0.3:
                    enemy.hit_animation = 10
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    break
        else:
            if abs(bullet.x - player.x) < 0.3 and abs(bullet.y - player.y) < 0.3:
                player.take_damage(random.randint(15, 25))
                bullets.remove(bullet)

def collect_potions(player, health_potions):
    for potion in health_potions[:]:
        if abs(player.x - potion.x) < 0.5 and abs(player.y - potion.y) < 0.5:
            player.potions += 1
            health_potions.remove(potion)
            try:
                pickup_sound = pygame.mixer.Sound(buffer=b'\x00\x20' * 600)
                pickup_sound.set_volume(0.4)
                pickup_sound.play()
            except:
                pass

def show_end_screen(screen, font, message, color):
    screen.fill((0, 0, 0))
    title_text = font.render(message, True, color)
    restart_text = pygame.font.Font(None, 24).render("Appuyez sur R pour rejouer ou ESC pour quitter", True, (255, 255, 255))
    
    title_rect = title_text.get_rect(center=(400, 280))
    restart_rect = restart_text.get_rect(center=(400, 320))
    
    screen.blit(title_text, title_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return True

def draw_minimap(screen, player, dungeon, enemies, health_potions):
    mini_size = 150
    mini_scale = mini_size / max(dungeon["width"], dungeon["height"])
    pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, mini_size, mini_size))
    
    for y in range(dungeon["height"]):
        for x in range(dungeon["width"]):
            if dungeon["grid"][y][x] != 0:
                pygame.draw.rect(screen, (100, 100, 100), 
                               (10 + x * mini_scale, 10 + y * mini_scale, mini_scale, mini_scale))
    
    # Player
    player_map_x = int(10 + player.x * mini_scale)
    player_map_y = int(10 + player.y * mini_scale)
    pygame.draw.circle(screen, (255, 255, 0), (player_map_x, player_map_y), 3)
    
    # Direction
    end_x = player_map_x + int(math.cos(player.angle) * 8)
    end_y = player_map_y + int(math.sin(player.angle) * 8)
    pygame.draw.line(screen, (255, 255, 255), (player_map_x, player_map_y), (end_x, end_y), 2)
    
    # Enemies
    for enemy in enemies:
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(10 + enemy.x * mini_scale), int(10 + enemy.y * mini_scale)), 2)
    
    # Potions
    for potion in health_potions:
        pygame.draw.circle(screen, (0, 255, 0), 
                          (int(10 + potion.x * mini_scale), int(10 + potion.y * mini_scale)), 2)

def play_3d_dungeon():
    screen, font, clock, enemy_sprites, textures = init_game()
    
    # Instructions
    show_3d_instructions(screen, font)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    
    dungeon = setup_dungeon()
    player, enemies, health_potions = place_entities(dungeon)
    bullets = []
    
    running = True
    while running:
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                bullet = player.shoot(mouse_x, mouse_y, 800, 600, enemies, dungeon)
                if bullet:
                    bullets.append(bullet)
        
        handle_input(keys, player, dungeon)
        
        # Check win condition
        if not enemies:
            if show_end_screen(screen, font, "VICTOIRE! Tous les ennemis éliminés!", (0, 255, 0)):
                return play_3d_dungeon()
            return
        
        player.update()
        collect_potions(player, health_potions)
        update_bullets(bullets, dungeon, player, enemies)
        
        # Update enemies
        for enemy in enemies:
            bullet = enemy.update(player, dungeon)
            if bullet:
                bullets.append(bullet)
        
        # Check death
        if player.hp <= 0:
            if show_end_screen(screen, font, "VOUS ÊTES MORT!", (255, 0, 0)):
                return play_3d_dungeon()
            return
        
        render_3d(screen, player, dungeon, enemies, enemy_sprites, health_potions, bullets)
        draw_minimap(screen, player, dungeon, enemies, health_potions)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()