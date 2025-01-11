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

# Fonction pour afficher la carte et le joueur
def draw_map(stdscr, game_map, player_x, player_y):
    stdscr.clear()
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if x == player_x and y == player_y:
                stdscr.addstr(y, x * 2, '@')  # Représente le joueur
            else:
                stdscr.addstr(y, x * 2, game_map[y][x])
    stdscr.refresh()

# Fonction pour gérer les entrées du joueur
def handle_input(stdscr, player_x, player_y, game_map):
    key = stdscr.getch()
    new_x, new_y = player_x, player_y

    if key == curses.KEY_UP:
        new_y -= 1
    elif key == curses.KEY_DOWN:
        new_y += 1
    elif key == curses.KEY_LEFT:
        new_x -= 1
    elif key == curses.KEY_RIGHT:
        new_x += 1

    # Empêcher le joueur de sortir de la carte
    if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
        if game_map[new_y][new_x] != '#':  # Le joueur ne peut pas traverser les murs
            player_x, player_y = new_x, new_y

    return player_x, player_y

def main(stdscr):
    # Initialisation de ncurses
    curses.curs_set(0)  # Masquer le curseur
    stdscr.nodelay(1)   # Ne pas bloquer l'exécution
    stdscr.timeout(100)  # Timeout pour les entrées clavier

    # Générer la carte
    game_map = generate_map()

    global player_x, player_y

    # Boucle principale
    while True:
        # Afficher la carte et le joueur
        draw_map(stdscr, game_map, player_x, player_y)

        # Gérer les entrées du joueur
        player_x, player_y = handle_input(stdscr, player_x, player_y, game_map)

if __name__ == "__main__":
    curses.wrapper(main)
