Je vais fusionner les deux codes pour produire un personnage qui se promène sur une carte et affronte des ennemis. Voici le code complet :

```python
import curses
import random

# Dimensions de la carte
MAP_WIDTH = 40
MAP_HEIGHT = 20

# Position initiale du joueur
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2

# Carte ASCII (exemple simple avec des murs et des espaces vides)
def generate_map():
    game_map = []
    for y in range(MAP_HEIGHT):
        row = []
        for x in range(MAP_WIDTH):
            if x == 0 or y == 0 or x == MAP_WIDTH - 1 or y == MAP_HEIGHT - 1:
                row.append('#')  # Mur
            else:
                row.append(' ')  # Espace vide
        game_map.append(row)
    return game_map

# Fonction pour afficher la carte, le joueur et les ennemis
def draw_map(stdscr, game_map, player_x, player_y, enemies):
    stdscr.clear()
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if (x, y) in enemies:
                stdscr.addstr(y, x * 2, 'E')  # Représente un ennemi
            elif x == player_x and y == player_y:
                stdscr.addstr(y, x * 2, '@')  # Représente le joueur
            else:
                stdscr.addstr(y, x * 2, game_map[y][x])
    stdscr.refresh()

# Fonction pour gérer les entrées du joueur
def handle_input(stdscr, player_x, player_y, game_map, enemies):
    key = stdscr.getch()
    new_x, new_y = player_x, player_y

    if key in {curses.KEY_UP, ord('z'), ord('Z')}:
        new_y -= 1
    elif key in {curses.KEY_DOWN, ord('s'), ord('S')}:
        new_y += 1
    elif key in {curses.KEY_LEFT, ord('q'), ord('Q')}:
        new_x -= 1
    elif key in {curses.KEY_RIGHT, ord('d'), ord('D')}:
        new_x += 1

    # Empêcher le joueur de sortir de la carte
    if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
        if game_map[new_y][new_x] != '#' and (new_x, new_y) not in enemies:  # Le joueur ne peut pas traverser les murs ni les ennemis
            player_x, player_y = new_x, new_y

    return player_x, player_y

# Fonction pour initialiser les ennemis
def initialize_enemies(num_enemies):
    enemies = set()
    while len(enemies) < num_enemies:
        x = random.randint(1, MAP_WIDTH - 2)
        y = random.randint(1, MAP_HEIGHT - 2)
        enemies.add((x, y))
    return enemies

def main(stdscr):
    # Initialisation de ncurses
    curses.curs_set(0)  # Masquer le curseur
    stdscr.nodelay(1)   # Ne pas bloquer l'exécution
    stdscr.timeout(100)  # Timeout pour les entrées clavier

    # Générer la carte
    game_map = generate_map()

    global player_x, player_y

    # Initialiser les ennemis
    enemies = initialize_enemies(10)  # Par exemple, 10 ennemis

    # Boucle principale
    while True:
        # Afficher la carte, le joueur et les ennemis
        draw_map(stdscr, game_map, player_x, player_y, enemies)

        # Gérer les entrées du joueur
        player_x, player_y = handle_input(stdscr, player_x, player_y, game_map, enemies)

if __name__ == "__main__":
    curses.wrapper(main)
```

### Ce code inclut :
1. **Génération de la carte** : Utilise `generate_map` pour créer une carte avec des murs (`#`) et des espaces vides (` `).
2. **Affichage de la carte, du joueur et des ennemis** : Utilise `draw_map` pour afficher la carte, le joueur (`@`) et les ennemis (`E`).
3. **Gestion des entrées du joueur** : Utilise `handle_input` pour permettre au joueur de se déplacer avec les touches fléchées ou `z`, `s`, `q`, `d` (ou `Z`, `S`, `Q`, `D`).
4. **Initialisation des ennemis** : Utilise `initialize_enemies` pour placer des ennemis à des positions aléatoires sur la carte.

Essayez ce code pour voir comment il fonctionne pour créer une expérience de jeu simple avec un personnage et des ennemis sur une carte. 😊