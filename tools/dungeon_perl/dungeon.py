import random
import pygame
from PIL import Image


def init_dungeon(width=50, height=50):
	return {"width": width, "height": height, "grid": [[0 for _ in range(width)] for _ in range(height)], "rooms": [], "connections": [], "stairs": []}

def emplace_rooms(dungeon, max_rooms=20, min_size=3, max_size=8):
    width = dungeon["width"]
    height = dungeon["height"]
    grid = dungeon["grid"]
    rooms = []

    for _ in range(max_rooms):
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(1, width - w - 1)
        y = random.randint(1, height - h - 1)

        new_room = {"x": x, "y": y, "w": w, "h": h}
        overlap = any(
            x < r["x"] + r["w"] and x + w > r["x"] and
            y < r["y"] + r["h"] and y + h > r["y"]
            for r in rooms
        )

        if not overlap:
            rooms.append(new_room)
            for i in range(x, x + w):
                for j in range(y, y + h):
                    grid[j][i] = 1  # salle

    dungeon["rooms"] = rooms

def corridors(dungeon, corridor_ratio=1.0):
    rooms = dungeon["rooms"]
    grid = dungeon["grid"]
    connections = []
    
    # Réduire le nombre de connexions selon la difficulté
    max_connections = int((len(rooms) - 1) * corridor_ratio)
    
    for i in range(max_connections):
        a = rooms[i]
        b = rooms[i + 1]
        ax, ay = a["x"] + a["w"] // 2, a["y"] + a["h"] // 2
        bx, by = b["x"] + b["w"] // 2, b["y"] + b["h"] // 2

        for x in range(min(ax, bx), max(ax, bx) + 1):
            if grid[ay][x] == 0:  # Ne pas écraser les salles
                grid[ay][x] = 2  # couloir
        for y in range(min(ay, by), max(ay, by) + 1):
            if grid[y][bx] == 0:  # Ne pas écraser les salles
                grid[y][bx] = 2

        connections.append(((ax, ay), (bx, by)))

    dungeon["connections"] = connections

def emplace_stairs(dungeon):
    rooms = dungeon["rooms"]
    grid = dungeon["grid"]
    stairs = []

    if len(rooms) < 2:
        return

    up, down = random.sample(rooms, 2)
    ux, uy = up["x"] + up["w"] // 2, up["y"] + up["h"] // 2
    dx, dy = down["x"] + down["w"] // 2, down["y"] + down["h"] // 2

    grid[uy][ux] = 3  # escalier montant
    grid[dy][dx] = 4  # escalier descendant

    stairs.append({"type": "up", "x": ux, "y": uy})
    stairs.append({"type": "down", "x": dx, "y": dy})
    dungeon["stairs"] = stairs

def print_dungeon(dungeon):
    symbols = {0: ' ', 1: '.', 2: '#', 3: '<', 4: '>'}
    for row in dungeon["grid"]:
        print(''.join(symbols.get(cell, '?') for cell in row))


def render_dungeon_image(dungeon, cell_size=10):
    width = dungeon["width"]
    height = dungeon["height"]
    grid = dungeon["grid"]

    # Crée une image RGB
    img = Image.new("RGB", (width * cell_size, height * cell_size), "black")
    pixels = img.load()

    # Définir les couleurs
    colors = {
        0: (0, 0, 0),         # vide
        1: (200, 200, 200),   # salle
        2: (100, 100, 255),   # couloir
        3: (0, 255, 0),       # escalier montant
        4: (255, 0, 0),       # escalier descendant
    }

    # Dessiner chaque cellule
    for y in range(height):
        for x in range(width):
            color = colors.get(grid[y][x], (255, 255, 0))  # jaune si inconnu
            for i in range(cell_size):
                for j in range(cell_size):
                    pixels[x * cell_size + i, y * cell_size + j] = color

    img.show()  # Affiche l’image
    # img.save("dungeon.png")  # Optionnel : sauvegarde

def select_difficulty(screen, font):
    screen.fill((0, 0, 0))
    title = font.render("CHOISISSEZ LA DIFFICULTÉ", True, (255, 255, 0))
    easy = font.render("1 - FACILE (30s, petit donjon)", True, (0, 255, 0))
    medium = font.render("2 - MOYEN (20s, donjon moyen)", True, (255, 255, 0))
    hard = font.render("3 - DIFFICILE (15s, grand donjon)", True, (255, 0, 0))
    
    title_rect = title.get_rect(center=(screen.get_width()//2, 200))
    easy_rect = easy.get_rect(center=(screen.get_width()//2, 280))
    medium_rect = medium.get_rect(center=(screen.get_width()//2, 320))
    hard_rect = hard.get_rect(center=(screen.get_width()//2, 360))
    
    screen.blit(title, title_rect)
    screen.blit(easy, easy_rect)
    screen.blit(medium, medium_rect)
    screen.blit(hard, hard_rect)
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return {"time": 30000, "size": 40, "rooms": 15, "corridors": 1.0}
                elif event.key == pygame.K_2:
                    return {"time": 20000, "size": 60, "rooms": 20, "corridors": 0.7}
                elif event.key == pygame.K_3:
                    return {"time": 15000, "size": 80, "rooms": 25, "corridors": 0.5}

def show_instructions(screen, font, difficulty):
    screen.fill((0, 0, 0))
    instructions = [
        "DUNGEON EXPLORER",
        "",
        f"OBJECTIF: Atteignez la case rouge en {difficulty['time']//1000} secondes",
        "",
        "CONTROLES:",
        "Q - Gauche    D - Droite",
        "Z - Haut      S - Bas",
        "",
        "Appuyez sur ESPACE pour commencer"
    ]
    
    for i, line in enumerate(instructions):
        color = (255, 255, 0) if i == 0 else (255, 255, 255)
        text = font.render(line, True, color)
        text_rect = text.get_rect(center=(screen.get_width()//2, 100 + i*40))
        screen.blit(text, text_rect)
    
    pygame.display.flip()

def play_dungeon(dungeon, difficulty):
    pygame.init()
    width, height = dungeon["width"], dungeon["height"]
    cell_size = 10
    screen = pygame.display.set_mode((max(800, width * cell_size), max(600, height * cell_size + 50)), pygame.RESIZABLE)
    pygame.display.set_caption("Dungeon Explorer")
    font = pygame.font.Font(None, 36)
    
    # Sélection de la difficulté
    if not difficulty:
        difficulty = select_difficulty(screen, font)
        if not difficulty:
            pygame.quit()
            return False
    
    # Afficher les instructions
    show_instructions(screen, font, difficulty)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    
    # Position initiale du joueur dans la première salle
    if dungeon["rooms"]:
        room = dungeon["rooms"][0]
        player_x = room["x"] + room["w"] // 2
        player_y = room["y"] + room["h"] // 2
    else:
        player_x, player_y = width // 2, height // 2
    
    # Cible dans la dernière salle
    if len(dungeon["rooms"]) > 1:
        target_room = dungeon["rooms"][-1]
        target_x = target_room["x"] + target_room["w"] // 2
        target_y = target_room["y"] + target_room["h"] // 2
    else:
        target_x, target_y = width - 5, height - 5
    
    # Timer (commence après les instructions)
    time_limit = difficulty["time"]
    start_time = pygame.time.get_ticks()
    
    clock = pygame.time.Clock()
    running = True
    game_won = False
    
    pygame.key.set_repeat(200, 50)  # Délai initial 200ms, répétition 50ms
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                new_x, new_y = player_x, player_y
                if event.key == pygame.K_q:  # gauche
                    new_x -= 1
                elif event.key == pygame.K_d:  # droite
                    new_x += 1
                elif event.key == pygame.K_z:  # haut
                    new_y -= 1
                elif event.key == pygame.K_s:  # bas
                    new_y += 1
                
                # Vérifier si le mouvement est valide
                if (0 <= new_x < width and 0 <= new_y < height and 
                    dungeon["grid"][new_y][new_x] != 0):
                    player_x, player_y = new_x, new_y
                    
                    # Vérifier si le joueur a atteint la cible
                    if player_x == target_x and player_y == target_y:
                        game_won = True
                        running = False
        
        # Dessiner le donjon
        screen.fill((0, 0, 0))
        colors = {1: (200, 200, 200), 2: (100, 100, 255), 3: (0, 255, 0), 4: (255, 0, 0)}
        
        for y in range(height):
            for x in range(width):
                if dungeon["grid"][y][x] in colors:
                    pygame.draw.rect(screen, colors[dungeon["grid"][y][x]], 
                                   (x * cell_size, y * cell_size, cell_size, cell_size))
        
        # Dessiner la cible
        pygame.draw.rect(screen, (255, 0, 0), 
                        (target_x * cell_size, target_y * cell_size, cell_size, cell_size))
        
        # Dessiner le joueur
        pygame.draw.rect(screen, (255, 255, 0), 
                        (player_x * cell_size, player_y * cell_size, cell_size, cell_size))
        
        # Afficher le timer
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        remaining_time = max(0, time_limit - elapsed_time)
        
        if remaining_time == 0:
            running = False
        
        time_text = font.render(f"Temps: {remaining_time // 1000}s", True, (255, 255, 255))
        screen.blit(time_text, (10, height * cell_size + 10))
        
        pygame.display.flip()
        clock.tick(30)
    
    # Afficher le résultat en incrustation
    final_time = pygame.time.get_ticks() - start_time
    
    # Créer une surface semi-transparente
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Messages de fin
    if game_won:
        title = font.render("VICTOIRE!", True, (0, 255, 0))
        time_msg = font.render(f"Temps: {final_time / 1000:.1f}s", True, (255, 255, 255))
    else:
        title = font.render("TEMPS ÉCOULÉ!", True, (255, 0, 0))
        time_msg = font.render(f"Durée: {final_time / 1000:.1f}s", True, (255, 255, 255))
    
    restart_msg = font.render("Appuyez sur R pour rejouer ou ESC pour quitter", True, (255, 255, 255))
    
    # Centrer les messages
    title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 60))
    time_rect = time_msg.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 20))
    restart_rect = restart_msg.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 20))
    
    screen.blit(title, title_rect)
    screen.blit(time_msg, time_rect)
    screen.blit(restart_msg, restart_rect)
    pygame.display.flip()
    
    # Attendre la réponse de l'utilisateur
    waiting_end = True
    while waiting_end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return True
    
    return False

def generate_dungeon():
    difficulty = None
    while True:
        if difficulty:
            dungeon = init_dungeon(difficulty["size"], difficulty["size"])
            emplace_rooms(dungeon, difficulty["rooms"])
            corridors(dungeon, difficulty["corridors"])
        else:
            dungeon = init_dungeon()
            emplace_rooms(dungeon)
            corridors(dungeon)
        emplace_stairs(dungeon)
        restart = play_dungeon(dungeon, difficulty)
        if not restart:
            break
        # Garder la même difficulté pour les parties suivantes
        if not difficulty:
            difficulty = {"time": 15000, "size": 80, "rooms": 25, "corridors": 0.5}

generate_dungeon()
