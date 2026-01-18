import os
import random
from tkinter import *
from typing import List


def charge_labyrinthe(nom):
    """
    Charge le labyrinthe depuis le fichier nom.txt
    nom : nom du fichier contenant le labyrinthe (sans l’extension .txt)
    Valeur de retour :
    - une liste avec les données du labyrinthe
    """
    try:
        fic = open(nom + ".txt", "r")
        data = fic.readlines()
        fic.close()
    except IOError:
        print("Impossible de lire le fichier {}.txt".format(nom))
        exit(1)
    for i in range(len(data)):
        data[i] = data[i].strip()
    return data


def affiche_labyrinthe(lab, fenetre, size_sprite, pos_perso):
    """
    Affichage d’un labyrinthe.
    lab : Variable contenant le labyrinthe
    fenetre: Fenêtre graphique
    size_sprite : Taille des sprites en pixels
    pos_perso : Liste contenant la position du personnage
    Valeur de retour :
    Tuple contenant le canevas, le sprite du personnage et un
    dictionnaire des images utilisées pour les sprites
    """
    can: Canvas = Canvas(fenetre, width=600, height=600)
    photo_wall: PhotoImage = PhotoImage(file="../sprites/WallTile1.png")
    photo_treasure: PhotoImage = PhotoImage(file="../sprites/treasure.png")

    photo_enemy: PhotoImage = PhotoImage(file="../sprites/enemy.png")
    photo_exit: PhotoImage = PhotoImage(file="../sprites/exit.png")
    photo_hero: PhotoImage = PhotoImage(file="../sprites/hero.png")

    convert_pos = lambda x, y, size: (x * (size + 1), y * (size + 1))

    lab_height, lab_width = len(lab), len(lab[0])
    for y in range(lab_height):
        for x in range(lab_width):
            image: PhotoImage = None
            match lab[y][x]:
                # Murs
                case ['+', '-']:
                    image: str = photo_wall
                # Trésors
                case ['1', '2', '3']:
                    image: str = photo_treasure
                # Ennemis
                case '$':
                    image: str = photo_enemy
                # Sortie
                case 'O':
                    image: str = photo_exit
            if image is not None:
                img_pos: tuple = convert_pos(x, y, size_sprite)
                can.create_image(*img_pos, anchor=NW, image=image)

    # Affichage du personnage
    sprite_hero = can.create_image(*convert_pos(*pos_perso, size_sprite), anchor=NW, image=photo_hero)

    can.pack()

    return (can, sprite_hero, {
        "hero": photo_hero,
        "wall": photo_wall,
        "treasure": photo_treasure,
        "enemy": photo_enemy,
        "exit": photo_exit})


def deplacement(event, can: Canvas, dep: str, lab: List[str], pos_perso, perso):
    """
    Déplacement du personnage
    event : objet décrivant l’événement ayant déclenché l’appel à cette
    fonction
    can : canevas où afficher les sprites
    dep : type de déplacement ("up", "down", "left" ou "right")
    lab : liste contenant le labyrinthe
    pos_perso : position courante du personnage
    perso : sprite représentant le personnage
    Pas de valeur de retour
    """
    # Calcul de la taille du labyrinthe
    n_cols = len(lab[0])
    n_lignes = len(lab)
    pos_col, pos_ligne = [pos_perso[0], pos_perso[1]]
    # Déplacement vers la droite
    if dep == "right":
        pos_col += 1
    elif dep == "left":
        pos_col -= 1
    elif dep == "down":
        pos_ligne += 1
    elif dep == "up":
        pos_ligne -= 1
    # Teste si le déplacement conduit le personnage en dehors de l’aire de jeu
    if pos_ligne < 0 or pos_col < 0 or pos_ligne > (n_lignes - 1) or pos_col > (n_cols - 1):
        return None
    # Si le déplacement est possible sur une case vide
    if lab[pos_ligne][pos_col] == " ":
        can.coords(perso, pos_col + pos_col * 32, pos_ligne + pos_ligne * 32)
    pos_perso = [pos_col, pos_ligne]


def destroy(event, fenetre):
    """
    Fermeture de la fenêtre graphique
    event : objet décrivant l’événement ayant déclenché l’appel à cette
    fonction
    fenetre : fenêtre graphique
    Pas de valeur de retour
    """
    fenetre.destroy()


def init_touches(fenetre, canvas, lab, pos_perso, perso):
    """
    Initialisation du comportement des touches du clavier
    canvas : canevas où afficher les sprites
    lab : liste contenant le labyrinthe
    pos_perso : position courante du personnage
    perso : sprite représentant le personnage
    Pas de valeur de retour
    """
    fenetre.bind("<Right>", lambda event, can=canvas, l=lab,
                                   pos=pos_perso,
                                   p=perso: deplacement(event, can, "right", l, pos, p))
    # Autres cas
    # ...
    fenetre.bind("<Left>", lambda event, can=canvas, l=lab,
                                  pos=pos_perso,
                                  p=perso: deplacement(event, can, "left", l, pos, p))
    fenetre.bind("<Up>", lambda event, can=canvas, l=lab,
                                pos=pos_perso,
                                p=perso: deplacement(event, can, "up", l, pos, p))
    fenetre.bind("<Down>", lambda event, can=canvas, l=lab,
                                  pos=pos_perso,
                                  p=perso: deplacement(event, can, "down", l, pos, p))
    fenetre.bind("<Escape>", lambda event, fen=fenetre: destroy(event, fen))
