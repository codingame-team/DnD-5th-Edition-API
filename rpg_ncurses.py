import curses
import random
import time

# Dimensions de la carte
MAP_WIDTH = 40
MAP_HEIGHT = 20


# Classe pour le joueur
class Player:
    def __init__(self, name="Héros"):
        self.name = name
        self.hp = 100
        self.attack = 20
        self.x = MAP_WIDTH // 2
        self.y = MAP_HEIGHT // 2

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > 100:
            self.hp = 100


# Classe pour l'ennemi
class Enemy:
    def __init__(self, name="Monstre", x=0, y=0):
        self.name = name
        self.hp = 50
        self.attack = 10
        self.x = x
        self.y = y

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0


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
def draw_map(stdscr, game_map, player, enemies):
    stdscr.clear()
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if (x, y) == (player.x, player.y):
                stdscr.addstr(y, x * 2, '@')  # Représente le joueur
            elif any(e.x == x and e.y == y for e in enemies):
                stdscr.addstr(y, x * 2, 'E')  # Représente un ennemi
            else:
                stdscr.addstr(y, x * 2, game_map[y][x])

    # Afficher la fiche personnage sur le côté droit de l'écran
    display_character_sheet(stdscr, player)

    stdscr.refresh()


# Fonction pour afficher la fiche personnage
def display_character_sheet(stdscr, player):
    # Obtenir la taille de l'écran pour s'assurer que l'affichage est dans les limites
    height, width = stdscr.getmaxyx()

    # Assurez-vous que la fiche personnage est dans les limites de l'écran
    if MAP_HEIGHT < height and MAP_WIDTH * 2 + 20 < width:
        stdscr.addstr(0, MAP_WIDTH * 2 + 2, "Fiche Personnage")
        stdscr.addstr(1, MAP_WIDTH * 2 + 2, f"Nom : {player.name}")
        stdscr.addstr(2, MAP_WIDTH * 2 + 2, f"Vie : {player.hp}")
        stdscr.addstr(3, MAP_WIDTH * 2 + 2, f"Attaque : {player.attack}")
    else:
        stdscr.addstr(0, 0, "L'écran est trop petit pour afficher la fiche personnage.")


# Fonction pour gérer les entrées du joueur
def handle_input(stdscr, player, game_map, enemies):
    key = stdscr.getch()
    new_x, new_y = player.x, player.y

    if key in {curses.KEY_UP, ord('z'), ord('Z')}:
        new_y -= 1
    elif key in {curses.KEY_DOWN, ord('s'), ord('S')}:
        new_y += 1
    elif key in {curses.KEY_LEFT, ord('q'), ord('Q')}:
        new_x -= 1
    elif key in {curses.KEY_RIGHT, ord('d'), ord('D')}:
        new_x += 1

    # Empêcher le joueur de sortir de la carte ou de traverser les murs
    if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
        if game_map[new_y][new_x] != '#':
            player.x, player.y = new_x, new_y

    # Vérifier si le joueur rencontre un ennemi
    for enemy in enemies:
        if (new_x, new_y) == (enemy.x, enemy.y):
            combat(stdscr, player, enemy)
            if enemy.hp <= 0:
                enemies.remove(enemy)


# Fonction pour initialiser les ennemis
def initialize_enemies(num_enemies):
    enemies = []
    while len(enemies) < num_enemies:
        x = random.randint(1, MAP_WIDTH - 2)
        y = random.randint(1, MAP_HEIGHT - 2)
        enemies.append(Enemy(name="Monstre", x=x, y=y))
    return enemies


# Fonction pour afficher l'état du jeu
def display_status(stdscr, player, enemy):
    stdscr.clear()

    # Affichage du joueur
    stdscr.addstr(1, 1, f"Nom du joueur: {player.name}")
    stdscr.addstr(2, 1, f"Vie du joueur: {player.hp}")

    # Affichage de l'ennemi
    stdscr.addstr(4, 1, f"Nom de l'ennemi: {enemy.name}")
    stdscr.addstr(5, 1, f"Vie de l'ennemi: {enemy.hp}")

    stdscr.refresh()


# Fonction pour gérer le combat
def combat(stdscr, player, enemy):
    while player.hp > 0 and enemy.hp > 0:
        display_status(stdscr, player, enemy)

        stdscr.addstr(7, 1, "Que voulez-vous faire ? (a - Attaquer, h - Soigner, q - Quitter): ")
        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('a'):  # Attaque
            damage = random.randint(15, player.attack)
            enemy.take_damage(damage)
            stdscr.addstr(9, 1, f"Vous attaquez l'ennemi pour {damage} points de dégâts.")
            stdscr.refresh()
            time.sleep(1)

        elif key == ord('h'):  # Soigner
            heal_amount = random.randint(10, 30)
            player.heal(heal_amount)
            stdscr.addstr(9, 1, f"Vous vous soignez de {heal_amount} points de vie.")
            stdscr.refresh()
            time.sleep(1)

        elif key == ord('q'):  # Quitter
            break

        # L'ennemi riposte
        if enemy.hp > 0:
            enemy_damage = random.randint(5, enemy.attack)
            player.take_damage(enemy_damage)
            stdscr.addstr(10, 1, f"L'ennemi attaque pour {enemy_damage} points de dégâts.")
            stdscr.refresh()
            time.sleep(1)

        # Vérification de la victoire/défaite
        if player.hp <= 0:
            stdscr.addstr(12, 1, "Vous avez perdu le combat... Press any key to quit.")
            stdscr.refresh()
            stdscr.getch()
            break
        elif enemy.hp <= 0:
            stdscr.addstr(12, 1, "Vous avez vaincu l'ennemi ! Press any key to quit.")
            stdscr.refresh()
            stdscr.getch()
            break


def main(stdscr):
    # Initialisation de ncurses
    curses.curs_set(0)  # Masquer le curseur
    stdscr.nodelay(1)  # Ne pas bloquer l'exécution
    stdscr.timeout(100)  # Timeout pour les entrées clavier

    # Générer la carte
    game_map = generate_map()

    # Création du joueur
    player = Player(name="Héros")

    # Initialiser les ennemis
    enemies = initialize_enemies(5)  # Par exemple, 5 ennemis

    # Boucle principale
    while True:
        # Afficher la carte, le joueur et les ennemis
        draw_map(stdscr, game_map, player, enemies)

        # Gérer les entrées du joueur
        handle_input(stdscr, player, game_map, enemies)


if __name__ == "__main__":
    curses.wrapper(main)
