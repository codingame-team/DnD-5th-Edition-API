import curses
from random import randint


def init_curses(lignes, cols, pos):
    """
    Initialisation des paramètres graphiques
    lignes : nombre de lignes (en caractères)
    cols : nombre de colonnes (en caractères)
    pos : tuple contenant la position du coin supérieur gauche
    de la fenêtre graphique
    Valeur de retour :
    La fenêtre training ayant été créée
    """
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    window = curses.newwin(lignes, cols, pos[0], pos[1])
    window.border(0)
    window.keypad(1)
    return window


def close_curses():
    """
    Restauration des paramètres graphiques
    """
    # Appel des fonctions inverses que celles invoquées dans init_curses
    curses.echo()
    curses.nocbreak()
    curses.curs_set(1)
    curses.endwin()


def init_colors():
    """
    Initialisation des couleurs
    Valeur de retour :
    liste contenant le nom des couleurs (index = code couleur)
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLUE)
    return ["RED", "GREEN", "BLUE"]


def color(code, l_color):
    """
    Sélectionne une couleur
    code : nom de la couleur
    l_color : liste des couleurs
    Valeur de retour :
    code de couleur training
    """
    return curses.color_pair(l_color.index(code) + 1)


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

def barre_score(data, win, coul) :
    """
    Barre de score affichant les données du jeu
    data : dictionnaire de données de la barre de score
    win : fenêtre graphique
    cou : liste de couleurs pour le mode graphique
    Pas de valeur de retour
    """
    barre = "PV : {:2d} PO : {:4d} Level : {:3d}"
    win.addstr(21, 1, barre.format(data["pv"], data["po"], data["level"]), color("BLUE", coul))

def affiche_labyrinthe(lab, perso, pos_perso, tresor, win, coul):
    """
    Affichage d’un labyrinthe
    lab : Variable contenant le labyrinthe
    perso : caractère représentant le personnage
    pos_perso : liste contenant la position du personnage [ligne, colonne]
    tresor : caractère représentant le trésor
    win : fenêtre du mode graphique
    coul : liste de couleurs pour le mode graphique
    Pas de valeur de retour
    """
    n_ligne = 0
    for ligne in lab:
        for i in range(1, 4):
            ligne = ligne.replace(str(i), tresor)
    if n_ligne == pos_perso[1]:
        win.addstr(n_ligne + 1, 10, ligne[0:pos_perso[0]] + perso + ligne[pos_perso[0] + 1:])
        # Coloration du personnage
        win.addstr(n_ligne + 1, 10, ligne[0:pos_perso[0]] + perso + ligne[pos_perso[0] + 1:])
    else:
        win.addstr(n_ligne + 1, 10, ligne)
    n_ligne += 1


def decouverte_tresor(categorie, data):
    """
    Incrémente le nombre de pièces d’or du joueur en fonction du trésor
    categorie : type de trésor
    - 1 : entre 1 et 5 po
    - 2 : entre 5 et 10 po
    - 3 : entre 0 et 25 po
    data : données de jeu (niveaux, nombre de pièces d’or et points de vie)
    """

    if categorie == "1":
        data["po"] = data["po"] + randint(1, 5)
    elif categorie == "2":
        data["po"] = data["po"] + randint(5, 10)
    else:
        data["po"] = data["po"] + randint(0, 25)


def combat(data):
    """
    Détermine le nombre de points de vie perdus lors d’un combat
    data : données de jeu (niveaux, nombre de pièces d’or et points de vie)
    """

    de = randint(1, 10)  # Tirage du dé entre 1 et 10
    if de == 1:
        data["pv"] = data["pv"] - randint(5, 10)
    elif de >= 2 and de <= 4:
        data["pv"] = data["pv"] - randint(1, 5)


def verification_deplacement(lab, pos_col, pos_ligne, data):
    """
    Indique si le déplacement du personnage est autorisé ou pas.
    lab : Labyrinthe
    pos_ligne : position du personnage sur les lignes
    pos_col : position du personnage sur les colonnes
    data : données de jeu (niveaux, nombre de pièces d’or et points de vie)
    Valeurs de retour :
    None : déplacement interdit
    [col, ligne] : déplacement autorisé sur la case indiquée par la liste
    """
    # Calcul de la taille du labyrinthe
    n_cols = len(lab[0])
    n_lignes = len(lab)
    # Teste si le déplacement conduit le personnage en dehors de l’aire de jeu
    if pos_ligne < 0 or pos_col < 0 or pos_ligne > (n_lignes - 1) or pos_col > (n_cols - 1):
        return None
    elif lab[pos_ligne][pos_col] == "O":
        # Une position hors labyrinthe indique la victoire
        return [-1, -1]
    elif lab[pos_ligne][pos_col] == "1" or lab[pos_ligne][pos_col] == "2" or \
            lab[pos_ligne][pos_col] == "3":
        # teste si le personnage se déplace sur un trésor
        # Découverte d’un trésor
        # fonction qui calcule le montant du butin
        decouverte_tresor(lab[pos_ligne][pos_col], data)
        # On supprime le trésor découvert
        lab[pos_ligne] = lab[pos_ligne][:pos_col] + " " + \
                         lab[pos_ligne][pos_col + 1:]
        return [pos_col, pos_ligne]
    elif lab[pos_ligne][pos_col] == "$":
        # Rencontre d’un ennemi
        combat(data)
        lab[pos_ligne] = lab[pos_ligne][:pos_col] + " " + \
                         lab[pos_ligne][pos_col + 1:]
        return [pos_col, pos_ligne]
    elif lab[pos_ligne][pos_col] != " ":
        return None
    else:
        return [pos_col, pos_ligne]


def choix_joueur(lab, pos_perso, data, win):
    """
    Demande au joueur de saisir son déplacement et vérifie s’il est possible.
    Si ce n’est pas le cas affiche un message, sinon modifie la position
    du perso dans la liste pos_perso
    lab : Labyrinthe
    pos_perso : liste contenant la position du personnage [colonne, ligne]
    data : données de jeu (niveaux, nombre de pièces d’or et points de vie)
    win : fenêtre graphique
    Pas de valeur de retour
    """
    dep = None
    choix = win.getch()
    if choix == curses.KEY_UP:
        dep = verification_deplacement(lab, pos_perso[0], pos_perso[1] - 1, data)
    elif choix == curses.KEY_DOWN:
        dep = verification_deplacement(lab, pos_perso[0], pos_perso[1] + 1, data)
    elif choix == curses.KEY_LEFT:
        dep = verification_deplacement(lab, pos_perso[0] - 1, pos_perso[1], data)
    elif choix == curses.KEY_RIGHT:
        dep = verification_deplacement(lab, pos_perso[0] + 1, pos_perso[1], data)
    elif choix == 27:
        close_curses()
        exit(1)
    if dep is not None:
        pos_perso[0] = dep[0]
        pos_perso[1] = dep[1]



def jeu(level, data, perso, pos_perso, tresor, win, coul):
    """
    Boucle principale du jeu. Affiche le labyrinthe dans ses différents
    états après les déplacements du joueur.
    level : Labyrinthe
    data : dictionnaire contenant
    - level : le numéro de niveau
    - po : le nombre de pièces d’or
    - pv : le nombre de points de vie
    perso : caractère représentant le personnage
    pos_perso : liste contenant la position du personnage [colonne, ligne]
    tresor : caractère représentant le trésor
    win : fenêtre graphique
    coul : liste de couleurs pour la fenêtre graphique
    """
    while True:
        affiche_labyrinthe(level, perso, pos_perso, tresor, win, coul)
        barre_score(data, win, coul)
        if data["pv"] <= 0:
            win.addstr(1, 20, "Vous avez PERDU...", color("RED", coul))
            win.getch()
            close_curses()
            exit(1)
        choix_joueur(level, pos_perso, data, win)
        if pos_perso == [-1, -1]:
            win.addstr(22, 1, "Vous avez passé le niveau !", color("RED", coul))
            win.addstr(23, 1, "Appuyez sur une touche pour continuez", color("RED", coul))
            win.getch()
            win.addstr(1, 20, " " * 50)
            win.addstr(1, 21, " " * 50)
            break
