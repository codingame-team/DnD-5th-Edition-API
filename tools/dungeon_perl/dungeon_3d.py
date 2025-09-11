import random
import pygame
import math
from load_assets import load_enemy_sprites, load_textures

pygame.mixer.init()

class Dungeon:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.grid = [[0] * width for _ in range(height)]
        self.rooms = []
    
    def _room_overlaps(self, new_room, existing_rooms):
        x, y, w, h = new_room["x"], new_room["y"], new_room["w"], new_room["h"]
        return any(x < r["x"] + r["w"] and x + w > r["x"] and y < r["y"] + r["h"] and y + h > r["y"] for r in existing_rooms)
    
    def _create_room(self, room):
        for i in range(room["x"], room["x"] + room["w"]):
            for j in range(room["y"], room["y"] + room["h"]):
                self.grid[j][i] = 1
    
    def _create_corridor(self, x1, y1, x2, y2):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.grid[y1][x] == 0:
                self.grid[y1][x] = 1
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.grid[y][x2] == 0:
                self.grid[y][x2] = 1
    
    def generate_rooms(self, max_rooms=10, min_size=3, max_size=6):
        for _ in range(max_rooms):
            w, h = random.randint(min_size, max_size), random.randint(min_size, max_size)
            x, y = random.randint(1, self.width - w - 1), random.randint(1, self.height - h - 1)
            new_room = {"x": x, "y": y, "w": w, "h": h}
            
            if not self._room_overlaps(new_room, self.rooms):
                self.rooms.append(new_room)
                self._create_room(new_room)
    
    def generate_corridors(self):
        for i in range(len(self.rooms) - 1):
            a, b = self.rooms[i], self.rooms[i + 1]
            ax, ay = a["x"] + a["w"] // 2, a["y"] + a["h"] // 2
            bx, by = b["x"] + b["w"] // 2, b["y"] + b["h"] // 2
            self._create_corridor(ax, ay, bx, by)
    
    def generate(self):
        self.generate_rooms()
        self.generate_corridors()
    
    def is_wall(self, x, y):
        return (x < 0 or x >= self.width or y < 0 or y >= self.height or 
                self.grid[int(y)][int(x)] == 0)

class Player3D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0.0  # Ground level
        self.eye_height = 2.0  # Eye height above ground
        self.angle = 0
        self.fov = math.pi / 3
        self.hp = 250
        self.max_hp = 250
        self.shoot_cooldown = 0
        self.potions = 0
        self.shoot_flash = 0
        
    def move(self, dx, dy, dungeon):
        new_x = self.x + dx * 0.1
        new_y = self.y + dy * 0.1
        
        if not dungeon.is_wall(new_x, new_y):
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
        
        # Hauteur d'épaule (un peu plus bas que les yeux)
        shoulder_height = self.eye_height - 0.2
        
        # Calculer la hauteur cible basée sur la position verticale de la souris
        center_y = screen_height // 2
        vertical_offset = (mouse_y - center_y) / center_y
        target_height = shoulder_height - vertical_offset * 2.0  # Ajuster la sensibilité
        
        # Calculer la distance approximative vers le mur/cible
        distance, _, _ = cast_ray(self, shoot_angle, dungeon)
        
        # Calculer la vélocité verticale pour atteindre la cible
        z_velocity = (target_height - shoulder_height) / (distance / 0.3) if distance > 0 else 0
        
        return Bullet(self.x, self.y, shoot_angle, True, shoulder_height, z_velocity)

class Bullet:
    def __init__(self, x, y, angle, is_player_bullet=True, z=1.0, z_velocity=0.0):
        self.x = x
        self.y = y
        self.z = z  # Height above ground
        self.angle = angle
        self.z_velocity = z_velocity  # Vertical velocity
        self.speed = 0.3
        self.life = 60
        self.is_player_bullet = is_player_bullet
    
    def update(self, dungeon):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.z += self.z_velocity
        self.life -= 1
        
        # Hit ground or wall
        return (not dungeon.is_wall(self.x, self.y) and self.life > 0 and self.z >= 0)

class HealthPotion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.heal_amount = random.randint(20, 40)

class Enemy:
    def __init__(self, x, y, enemy_type=None, available_types=None):
        self.x = x
        self.y = y
        self.z = 0.0  # Ground level
        self.height = 1.8  # Enemy height
        self.ground_level = True  # Flag for ground-level rendering
        
        # Use available types from loaded sprites or fallback
        if available_types is None:
            available_types = ["orc", "skeleton", "goblin", "troll"]
        
        # Random enemy type if not specified
        if enemy_type is None:
            self.enemy_type = random.choice(available_types)
        else:
            self.enemy_type = enemy_type
            
        self.move_timer = 0
        self.shoot_timer = 0
        self.is_shooting = False
        self.shoot_animation = 0
        self.hit_animation = 0
    
    def _try_move(self, dungeon):
        self.move_timer += 1
        if self.move_timer > 30:  # Move more frequently
            dx, dy = random.choice([-0.1, 0, 0.1]), random.choice([-0.1, 0, 0.1])  # Smaller steps
            new_x, new_y = self.x + dx, self.y + dy
            
            if not dungeon.is_wall(new_x, new_y):
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
                # Shoot from enemy center height
                bullet_z = self.z + self.height / 2
                return Bullet(self.x, self.y, angle_to_player, False, bullet_z, 0.0)
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

# Global sprite cache
_enemy_sprites_cache = None

def get_all_enemy_sprites():
    """Get all loaded enemy sprites (cached)"""
    global _enemy_sprites_cache
    if _enemy_sprites_cache is None:
        _enemy_sprites_cache = load_enemy_sprites()
    return _enemy_sprites_cache

def get_enemy_sprite(enemy_type="orc"):
    """Get enemy sprite from cache or generate fallback"""
    sprites = get_all_enemy_sprites()
    return sprites.get(enemy_type, generate_enemy_sprite(enemy_type))

def get_available_enemy_types():
    """Get list of all available enemy types"""
    return list(get_all_enemy_sprites().keys())

def generate_enemy_sprite(enemy_type="orc"):
    sprite = pygame.Surface((64, 64), pygame.SRCALPHA)
    
    if enemy_type == "orc":
        # Orc vert
        pygame.draw.circle(sprite, (100, 150, 50), (32, 50), 24)
        pygame.draw.circle(sprite, (80, 120, 40), (32, 30), 16)
        pygame.draw.circle(sprite, (255, 0, 0), (26, 26), 4)
        pygame.draw.circle(sprite, (255, 0, 0), (38, 26), 4)
        pygame.draw.ellipse(sprite, (60, 90, 30), (24, 58, 16, 6))
        pygame.draw.ellipse(sprite, (60, 90, 30), (40, 58, 16, 6))
    elif enemy_type == "skeleton":
        # Squelette blanc
        pygame.draw.circle(sprite, (240, 240, 240), (32, 50), 24)
        pygame.draw.circle(sprite, (220, 220, 220), (32, 30), 16)
        pygame.draw.circle(sprite, (0, 0, 0), (26, 26), 4)
        pygame.draw.circle(sprite, (0, 0, 0), (38, 26), 4)
        pygame.draw.ellipse(sprite, (200, 200, 200), (24, 58, 16, 6))
        pygame.draw.ellipse(sprite, (200, 200, 200), (40, 58, 16, 6))
    elif enemy_type == "goblin":
        # Gobelin rouge (plus petit)
        pygame.draw.circle(sprite, (200, 0, 0), (32, 50), 20)
        pygame.draw.circle(sprite, (150, 0, 0), (32, 30), 14)
        pygame.draw.circle(sprite, (255, 255, 0), (26, 26), 3)
        pygame.draw.circle(sprite, (255, 255, 0), (38, 26), 3)
        pygame.draw.ellipse(sprite, (120, 0, 0), (26, 58, 12, 6))
        pygame.draw.ellipse(sprite, (120, 0, 0), (38, 58, 12, 6))
    elif enemy_type == "troll":
        # Troll brun (plus grand)
        pygame.draw.circle(sprite, (139, 69, 19), (32, 48), 28)
        pygame.draw.circle(sprite, (101, 67, 33), (32, 28), 18)
        pygame.draw.circle(sprite, (255, 0, 0), (26, 24), 5)
        pygame.draw.circle(sprite, (255, 0, 0), (38, 24), 5)
        pygame.draw.ellipse(sprite, (85, 53, 15), (22, 58, 20, 6))
        pygame.draw.ellipse(sprite, (85, 53, 15), (42, 58, 20, 6))

    return sprite

def create_random_enemy(x, y):
    """Create random enemy type"""
    enemy_types = ["orc", "skeleton", "goblin", "troll"]
    enemy_type = random.choice(enemy_types)
    return Enemy(x, y, enemy_type)

def render_sprite(screen, sprite, x, y, distance, screen_height):
    """Render sprite with correct ground positioning"""
    if distance <= 0:
        return
    
    # Get original sprite dimensions to preserve aspect ratio
    original_width, original_height = sprite.get_size()
    aspect_ratio = original_width / original_height
    
    # Calculate sprite size based on distance - LARGER SIZE
    sprite_height = int(screen_height / distance * 1.5)
    sprite_width = int(sprite_height * aspect_ratio)  # Preserve aspect ratio
    
    # Scale sprite
    scaled_sprite = pygame.transform.scale(sprite, (sprite_width, sprite_height))
    
    # Position sprite on ground - bottom of sprite AT horizon line
    horizon_y = screen_height // 2
    sprite_y = horizon_y  # Bottom edge of sprite at horizon = ground level
    sprite_x = x - sprite_width // 2
    
    screen.blit(scaled_sprite, (sprite_x, sprite_y))

def cast_ray(player, angle, dungeon, max_distance=20, step=0.1):
    x, y = player.x, player.y
    dx = math.cos(angle) * step
    dy = math.sin(angle) * step
    
    steps = int(max_distance / step)
    for _ in range(steps):
        x += dx
        y += dy
        
        if dungeon.is_wall(x, y):
            distance = math.sqrt((x - player.x)**2 + (y - player.y)**2)
            return distance, x, y
    
    return max_distance, x, y

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
        if dungeon.is_wall(x, y):
            return False
    
    return True

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Dungeon Explorer 3D")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        
        try:
            self.enemy_sprites = load_enemy_sprites()
            self.textures = load_textures()
        except:
            self.enemy_sprites = {'orc': generate_enemy_sprite()}
            self.textures = {}
        
        self.dungeon = None
        self.player = None
        self.enemies = []
        self.health_potions = []
        self.bullets = []
    
    def setup_dungeon(self):
        self.dungeon = Dungeon(20, 20)
        self.dungeon.generate()
    
    def place_entities(self):
        if self.dungeon.rooms:
            room = self.dungeon.rooms[0]
            self.player = Player3D(room["x"] + 1, room["y"] + 1)
        else:
            self.player = Player3D(1, 1)
        
        # Augmenter drastiquement la densité de monstres
        self.enemies = []
        available_types = get_available_enemy_types()
        
        # 1 ennemi par salle (sauf la première)
        for room in self.dungeon.rooms[1:]:
            # Position aléatoire dans la salle
            x = random.randint(room["x"], room["x"] + room["w"] - 1)
            y = random.randint(room["y"], room["y"] + room["h"] - 1)
            self.enemies.append(Enemy(x, y, available_types=available_types))
        
        # Ajouter quelques ennemis dans les couloirs
        for _ in range(3):
            for _ in range(100):  # Tentatives de placement
                x = random.randint(1, self.dungeon.width - 2)
                y = random.randint(1, self.dungeon.height - 2)
                if (not self.dungeon.is_wall(x, y) and 
                    abs(x - self.player.x) >= 3 and abs(y - self.player.y) >= 3):
                    self.enemies.append(Enemy(x, y, available_types=available_types))
                    break
        
        # Plus de potions pour compenser la difficulté
        self.health_potions = []
        for _ in range(6):
            for _ in range(50):
                x, y = random.randint(1, self.dungeon.width - 2), random.randint(1, self.dungeon.height - 2)
                if (not self.dungeon.is_wall(x, y) and 
                    abs(x - self.player.x) >= 2 and abs(y - self.player.y) >= 2 and
                    all(abs(x - e.x) >= 1.5 and abs(y - e.y) >= 1.5 for e in self.enemies)):
                    self.health_potions.append(HealthPotion(x, y))
                    break
    
    def handle_input(self, keys):
        if keys[pygame.K_z]:
            self.player.move(math.cos(self.player.angle), math.sin(self.player.angle), self.dungeon)
        if keys[pygame.K_s]:
            self.player.move(-math.cos(self.player.angle), -math.sin(self.player.angle), self.dungeon)
        if keys[pygame.K_q]:
            self.player.rotate(-0.05)
        if keys[pygame.K_d]:
            self.player.rotate(0.05)
        if keys[pygame.K_LEFT]:
            self.player.move(math.cos(self.player.angle - math.pi/2), math.sin(self.player.angle - math.pi/2), self.dungeon)
        if keys[pygame.K_RIGHT]:
            self.player.move(math.cos(self.player.angle + math.pi/2), math.sin(self.player.angle + math.pi/2), self.dungeon)
        if keys[pygame.K_p]:
            self.player.use_potion()
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            if not bullet.update(self.dungeon):
                self.bullets.remove(bullet)
                continue
            
            if bullet.is_player_bullet:
                for enemy in self.enemies[:]:
                    if abs(bullet.x - enemy.x) < 0.3 and abs(bullet.y - enemy.y) < 0.3:
                        enemy.hit_animation = 10
                        self.enemies.remove(enemy)
                        self.bullets.remove(bullet)
                        break
            else:
                if abs(bullet.x - self.player.x) < 0.3 and abs(bullet.y - self.player.y) < 0.3:
                    self.player.take_damage(random.randint(15, 25))
                    self.bullets.remove(bullet)
    
    def collect_potions(self):
        for potion in self.health_potions[:]:
            if abs(self.player.x - potion.x) < 0.5 and abs(self.player.y - potion.y) < 0.5:
                self.player.potions += 1
                self.health_potions.remove(potion)
                try:
                    pickup_sound = pygame.mixer.Sound(buffer=b'\x00\x20' * 600)
                    pickup_sound.set_volume(0.4)
                    pickup_sound.play()
                except:
                    pass
    
    def show_instructions(self):
        self.screen.fill((0, 0, 0))
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
            text = self.font.render(line, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width()//2, 100 + i*30))
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def show_end_screen(self, message, color):
        self.screen.fill((0, 0, 0))
        title_text = self.font.render(message, True, color)
        restart_text = pygame.font.Font(None, 24).render("Appuyez sur R pour rejouer ou ESC pour quitter", True, (255, 255, 255))
        
        title_rect = title_text.get_rect(center=(400, 280))
        restart_rect = restart_text.get_rect(center=(400, 320))
        
        self.screen.blit(title_text, title_rect)
        self.screen.blit(restart_text, restart_rect)
        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    return False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    return True
    
    def render_3d(self):
        width, height = self.screen.get_size()
        
        self.screen.fill((50, 50, 100))
        pygame.draw.rect(self.screen, (100, 50, 0), (0, height//2, width, height//2))
        
        for x in range(0, width, 2):
            angle = self.player.angle - self.player.fov/2 + (x / width) * self.player.fov
            distance, hit_x, hit_y = cast_ray(self.player, angle, self.dungeon)
            
            distance *= math.cos(angle - self.player.angle)
            
            if distance > 0:
                wall_height = int(height / (distance + 0.1))
                wall_top = (height - wall_height) // 2
                wall_bottom = wall_top + wall_height
                
                wall_x = hit_x - math.floor(hit_x)
                if abs(math.cos(angle)) > abs(math.sin(angle)):
                    wall_x = hit_y - math.floor(hit_y)
                
                base_color = 120 if int(wall_x * 8) % 2 == 0 else 100
                brightness = max(50, 255 - int(distance * 12))
                color = (min(255, base_color + brightness//3), min(255, base_color//2 + brightness//4), min(255, base_color//3 + brightness//5))
                
                pygame.draw.line(self.screen, color, (x, wall_top), (x, wall_bottom), 2)
        
        # Render entities
        for enemy in self.enemies:
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 10:
                enemy_angle = math.atan2(dy, dx)
                angle_diff = enemy_angle - self.player.angle
                
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                if abs(angle_diff) < self.player.fov / 2 and has_line_of_sight(self.player, enemy, self.dungeon):
                    screen_x = int(width/2 + (angle_diff / (self.player.fov/2)) * width/2)
                    enemy_size = max(60, int(400 / (distance + 0.1)))
                    
                    # Horizon = niveau des yeux du joueur, sol est plus bas
                    eye_level = height // 2
                    ground_level = eye_level + int(height * 0.3)  # Sol à 30% sous les yeux
                    enemy_y = ground_level - enemy_size

                    # 1. Taille du sprite
                    enemy_size = max(40, int(250 / (distance + 0.1)))

                    # 2. Déplacement vertical ajusté selon la distance
                    v_move = enemy_size  # ou une constante, ex. 64, à ajuster selon ton sprite
                    v_move_screen = v_move / (distance + 0.1)

                    # 3. Ligne d'horizon (sol)
                    horizon_y = height // 2

                    # 4. Position verticale finale : pieds au sol
                    sprite_y = int(-enemy_size // 2 + horizon_y + v_move_screen)

                    # Horizontal : centrer le sprite
                    sprite_x = screen_x - enemy_size // 2

                    # # 5. Affichage
                    # self.screen.blit(dark_sprite, (sprite_x, sprite_y))

                    if 0 <= screen_x < width and enemy_size > 10:
                        sprite_surface = self.enemy_sprites.get(enemy.enemy_type, self.enemy_sprites.get('orc', generate_enemy_sprite()))
                        scaled_sprite = pygame.transform.scale(sprite_surface, (enemy_size, enemy_size))
                        
                        brightness = max(0.3, 1.0 - distance / 10)
                        dark_sprite = scaled_sprite.copy()
                        
                        if enemy.hit_animation > 0:
                            hit_intensity = enemy.hit_animation / 10.0
                            red_tint = (255, int(100 * hit_intensity), int(100 * hit_intensity))
                            dark_sprite.fill(red_tint, special_flags=pygame.BLEND_MULT)
                        else:
                            dark_sprite.fill((int(255 * brightness), int(255 * brightness), int(255 * brightness)), special_flags=pygame.BLEND_MULT)
                        
                        # self.screen.blit(dark_sprite, (screen_x - enemy_size//2, enemy_y))
                        self.screen.blit(dark_sprite, (sprite_x, sprite_y))

        # Render health potions
        for potion in self.health_potions:
            dx = potion.x - self.player.x
            dy = potion.y - self.player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 8:
                potion_angle = math.atan2(dy, dx)
                angle_diff = potion_angle - self.player.angle
                
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                if abs(angle_diff) < self.player.fov / 2 and has_line_of_sight(self.player, potion, self.dungeon):
                    screen_x = int(width/2 + (angle_diff / (self.player.fov/2)) * width/2)
                    potion_size = max(20, int(150 / (distance + 0.1)))
                    
                    # Perspective au sol comme les ennemis
                    vertical_angle = math.atan(self.player.eye_height / distance) if distance > 0.1 else 0
                    screen_offset = int(height * vertical_angle / self.player.fov)
                    potion_y = height // 2 + screen_offset - potion_size
                    
                    if 0 <= screen_x < width and potion_size > 5:
                        # Dessiner la potion flottante (croix verte)
                        pygame.draw.circle(self.screen, (0, 255, 0), (screen_x, potion_y + potion_size//2), potion_size//3)
                        pygame.draw.line(self.screen, (255, 255, 255), 
                                       (screen_x - potion_size//4, potion_y + potion_size//2), 
                                       (screen_x + potion_size//4, potion_y + potion_size//2), 3)
                        pygame.draw.line(self.screen, (255, 255, 255), 
                                       (screen_x, potion_y + potion_size//2 - potion_size//4), 
                                       (screen_x, potion_y + potion_size//2 + potion_size//4), 3)
        
        # Render bullets
        for bullet in self.bullets:
            dx = bullet.x - self.player.x
            dy = bullet.y - self.player.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < 8:
                bullet_angle = math.atan2(dy, dx)
                angle_diff = bullet_angle - self.player.angle
                
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                while angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                if abs(angle_diff) < self.player.fov / 2:
                    screen_x = int(width/2 + (angle_diff / (self.player.fov/2)) * width/2)
                    bullet_size = max(3, int(20 / (distance + 0.1)))
                    bullet_y = height//2
                    
                    if 0 <= screen_x < width:
                        bullet_color = (255, 255, 0) if bullet.is_player_bullet else (255, 100, 100)
                        pygame.draw.circle(self.screen, bullet_color, (screen_x, bullet_y), bullet_size)
        
        # UI elements
        health_bar_width = 200
        health_bar_height = 20
        health_x = width - health_bar_width - 10
        health_y = 10
        
        pygame.draw.rect(self.screen, (100, 0, 0), (health_x, health_y, health_bar_width, health_bar_height))
        
        health_ratio = self.player.hp / self.player.max_hp
        health_width = int(health_bar_width * health_ratio)
        pygame.draw.rect(self.screen, (0, 255, 0), (health_x, health_y, health_width, health_bar_height))
        
        pygame.draw.rect(self.screen, (255, 255, 255), (health_x, health_y, health_bar_width, health_bar_height), 2)
        
        font = pygame.font.Font(None, 24)
        hp_text = font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_text, (health_x, health_y + health_bar_height + 5))
        
        potion_text = font.render(f"Potions: {self.player.potions}", True, (0, 255, 0))
        self.screen.blit(potion_text, (health_x - 120, health_y + 5))
        
        # Crosshair
        center_x, center_y = width // 2, height // 2
        crosshair_size = 10
        crosshair_color = (255, 255, 255) if self.player.shoot_cooldown == 0 else (255, 0, 0)
        
        pygame.draw.line(self.screen, crosshair_color, 
                        (center_x - crosshair_size, center_y), 
                        (center_x + crosshair_size, center_y), 2)
        pygame.draw.line(self.screen, crosshair_color, 
                        (center_x, center_y - crosshair_size), 
                        (center_x, center_y + crosshair_size), 2)
        
        # Player shoot flash animation
        if self.player.shoot_flash > 0:
            flash_intensity = self.player.shoot_flash / 8.0
            flash_size = int(30 * flash_intensity)
            flash_color = (255, int(255 * flash_intensity), 0)
            
            pygame.draw.circle(self.screen, flash_color, (center_x, center_y), flash_size//2)
            
            for i in range(5):
                particle_x = center_x + random.randint(-flash_size, flash_size)
                particle_y = center_y + random.randint(-flash_size//2, flash_size//2)
                particle_size = max(1, int(flash_size//4 * flash_intensity))
                pygame.draw.circle(self.screen, (255, 200, 0), (particle_x, particle_y), particle_size)
    
    def draw_minimap(self):
        mini_size = 150
        mini_scale = mini_size / max(self.dungeon.width, self.dungeon.height)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (10, 10, mini_size, mini_size))
        
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                if self.dungeon.grid[y][x] != 0:
                    pygame.draw.rect(self.screen, (100, 100, 100), 
                                   (10 + x * mini_scale, 10 + y * mini_scale, mini_scale, mini_scale))
        
        player_map_x = int(10 + self.player.x * mini_scale)
        player_map_y = int(10 + self.player.y * mini_scale)
        pygame.draw.circle(self.screen, (255, 255, 0), (player_map_x, player_map_y), 3)
        
        end_x = player_map_x + int(math.cos(self.player.angle) * 8)
        end_y = player_map_y + int(math.sin(self.player.angle) * 8)
        pygame.draw.line(self.screen, (255, 255, 255), (player_map_x, player_map_y), (end_x, end_y), 2)
        
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, (255, 0, 0), 
                              (int(10 + enemy.x * mini_scale), int(10 + enemy.y * mini_scale)), 2)
        
        for potion in self.health_potions:
            pygame.draw.circle(self.screen, (0, 255, 0), 
                              (int(10 + potion.x * mini_scale), int(10 + potion.y * mini_scale)), 2)
    
    def run(self):
        self.show_instructions()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
        
        self.setup_dungeon()
        self.place_entities()
        self.bullets = []
        
        running = True
        while running:
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    bullet = self.player.shoot(mouse_x, mouse_y, 800, 600, self.enemies, self.dungeon)
                    if bullet:
                        self.bullets.append(bullet)
            
            self.handle_input(keys)
            
            if not self.enemies:
                if self.show_end_screen("VICTOIRE! Tous les ennemis éliminés!", (0, 255, 0)):
                    return self.run()
                return
            
            self.player.update()
            self.collect_potions()
            self.update_bullets()
            
            for enemy in self.enemies:
                bullet = enemy.update(self.player, self.dungeon)
                if bullet:
                    self.bullets.append(bullet)
            
            if self.player.hp <= 0:
                if self.show_end_screen("VOUS ÊTES MORT!", (255, 0, 0)):
                    return self.run()
                return
            
            self.render_3d()
            self.draw_minimap()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()