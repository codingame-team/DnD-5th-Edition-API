#!/usr/bin/python3
import Lab
if __name__ == "__main__" :
    # Initialisation du personnage
    perso = "X"
    pos_perso = [1, 1]
    tresor = "#"
    n_levels_total = 20
    data = {
        "po": 0,
        "pv": 25,
        "level": None
    }
    # Initialisation de l’affichage graphique
    win = Lab.init_curses(25, 41, (0, 0))
    # Initialisation des couleurs
    coul = Lab.init_colors()
    # Lancement de la partie
    for n_level in range(1, n_levels_total + 1):
        level = Lab.charge_labyrinthe("level_" + str(n_level))
        data["level"] = n_level
        Lab.jeu(level, data, perso, pos_perso, tresor, win, coul)
    win.addstr(1, 22, "Vous avez gagné !!", Lab.color("RED", coul))
    win.getch()
    Lab.close_curses()
