import curses
import random
import time

# Définitions des constantes
WIDTH = 50
HEIGHT = 20


# Classe pour le joueur
class Player:
    def __init__(self, name="Héros"):
        self.name = name
        self.hp = 100
        self.attack = 20

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
    def __init__(self, name="Monstre"):
        self.name = name
        self.hp = 50
        self.attack = 10

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0


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
    # Initialiser ncurses
    curses.curs_set(0)  # Masquer le curseur
    stdscr.nodelay(1)  # Ne pas bloquer l'exécution
    stdscr.timeout(100)  # Timeout pour les entrées clavier

    # Création du joueur et de l'ennemi
    player = Player(name="Héros")
    enemy = Enemy(name="Orc")

    # Démarrer le combat
    combat(stdscr, player, enemy)


if __name__ == "__main__":
    curses.wrapper(main)
