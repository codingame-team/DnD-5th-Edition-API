#!/usr/bin/python3
import Lab_tk
from tkinter import *

if __name__ == "__main__":
    # Initialisation du personnage
    perso = "X"
    pos_perso = [1, 1]
    tresor = "#"
    n_levels_total = 20
    data = {
        "po": 0,
        "pv": 25,
        "level": 1
    }
    size_sprite = 31

    # Initialisation de l’affichage graphique
    fenetre = Tk()
    fenetre.title("Jeu Labyrinthe")
    # Lancement de la partie
    level = Lab_tk.charge_labyrinthe("level_1")
    (canvas, sprite_perso, photos) = Lab_tk.affiche_labyrinthe(level, fenetre,
                                                               size_sprite, pos_perso)
    Lab_tk.init_touches(fenetre, canvas, level, pos_perso, sprite_perso)
    # Boucle événementielle
    fenetre.mainloop()
