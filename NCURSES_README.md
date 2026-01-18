# DnD 5th Edition API - NCurses Interface

## Description

Cette version ncurses du jeu D&D 5th Edition API propose une interface en terminal améliorée, inspirée de l'architecture du projet DnD-5e-ncurses.

## Caractéristiques

### Interface utilisateur
- **Navigation au clavier** : Utilisez les flèches ou j/k pour naviguer dans les menus
- **Affichage optimisé** : Interface en terminal avec gestion de la taille minimale
- **Messages temporaires** : Les notifications s'affichent pendant 2 secondes dans une zone dédiée
- **Séparation des contextes** : Les messages d'exploration et les menus sont bien séparés

### Fonctionnalités principales

#### Menu Principal
- Démarrer une nouvelle partie
- Charger une partie sauvegardée
- Options (à venir)
- Quitter

#### Château (Castle)
- **Taverne de Gilgamesh** : Recrutement d'aventuriers
- **Auberge de l'Aventurier** : Repos et récupération
- **Temple de Cant** : Services de résurrection
- **Poste de commerce de Boltac** : Achat/vente d'équipement
- **Bord de ville** : Accès aux zones d'entraînement et au donjon

#### Bord de ville (Edge of Town)
- **Terrain d'entraînement** : Création de nouveaux personnages
- **Labyrinthe** : Exploration et combat
- **Retour au château**
- **Quitter le jeu**

## Installation

### Prérequis
- Python 3.10+
- Module `curses` (inclus par défaut sur Linux/macOS, nécessite windows-curses sur Windows)

### Installation des dépendances
```bash
# Sur Linux/macOS
pip install -r requirements.txt

# Sur Windows
pip install windows-curses
pip install -r requirements.txt
```

## Utilisation

### Lancer le jeu en mode ncurses
```bash
python main_ncurses.py
```

### Lancer le jeu en mode texte classique
```bash
python main.py
```

## Contrôles

### Navigation générale
- **↑/↓** ou **j/k** : Naviguer dans les menus
- **Entrée** : Sélectionner une option
- **Esc** : Retour au menu précédent
- **q** : Quitter (depuis le menu principal)

### Gestion de la partie
- **Taverne** : [↑/↓] Sélectionner, [Entrée] Recruter/Renvoyer
- **Donjon** : [w] Errer, [a] Attaquer, [r] Fuir, [i] Inventaire

## Architecture

Le code suit les principes SOLID :

### Classes principales

#### `DnDCursesUI`
- Gestion de l'interface utilisateur ncurses
- Séparation des responsabilités entre affichage et logique métier
- Système de messages dual (exploration + panneau)

#### `Location`
- Énumération des différents lieux du jeu
- Facilite la navigation entre zones

### Structure des fichiers
```
main_ncurses.py      # Interface ncurses principale
main.py              # Interface texte originale
dao_classes.py       # Classes de données (Character, etc.)
populate_functions.py # Chargement des ressources
rpg_ncurses.py       # Version antérieure du maze ncurses
```

## Fonctionnalités par rapport à l'original

### Améliorations
✅ Navigation au clavier intuitive
✅ Taille minimale de terminal appliquée (80x24)
✅ Messages temporaires pour feedback immédiat
✅ Affichage structuré avec en-têtes et pieds de page
✅ Gestion de la partie et du roster intégrée
✅ Support des couleurs (si le terminal le permet)

### À implémenter
🚧 Écrans de création de personnage
🚧 Interface de combat détaillée
🚧 Système d'inventaire et d'équipement
🚧 Exploration du donjon avec carte
🚧 Services du temple (résurrection)
🚧 Commerce au poste de Boltac
🚧 Repos à l'auberge

## Développement

### Ajouter une nouvelle fonctionnalité

1. **Créer un nouveau mode** dans `__init__` :
```python
self.mode = 'nouveau_mode'
```

2. **Ajouter une fonction de dessin** :
```python
def draw_nouveau_mode(self, lines: int, cols: int):
    self.draw_header("Nouveau Mode", lines, cols)
    # ... votre code ici
    self.draw_footer("Instructions", lines, cols)
```

3. **Ajouter un gestionnaire d'événements** :
```python
def _handle_nouveau_mode(self, c: int) -> None:
    # Gérer les entrées clavier
    pass
```

4. **Intégrer dans la boucle principale** :
```python
def mainloop(self):
    # ...
    elif self.mode == 'nouveau_mode':
        self._handle_nouveau_mode(c)
```

### Conventions de code

- **Messages d'exploration** : `push_message()` pour le log déroulant
- **Messages de panneau** : `push_panel()` pour les notifications temporaires
- **Vérification des limites** : Toujours appeler `check_bounds()` avant dessin
- **Gestion des erreurs curses** : Entourer les `addstr` dans try/except

## Compatibilité

### Testé sur
- ✅ macOS (Terminal, iTerm2)
- ✅ Linux (GNOME Terminal, xterm)
- ⚠️ Windows (Windows Terminal avec windows-curses)

### Taille minimale de terminal
- **Largeur** : 80 colonnes
- **Hauteur** : 24 lignes

## Bugs connus et limitations

1. Le redimensionnement du terminal peut causer des problèmes d'affichage temporaires
2. Certaines fonctionnalités du jeu original ne sont pas encore implémentées
3. Les animations de combat sont simplifiées

## Contribution

Pour contribuer au projet :

1. Fork le repository
2. Créez une branche pour votre fonctionnalité
3. Testez sur différents terminaux
4. Soumettez une pull request

## Licence

Même licence que le projet principal DnD-5th-Edition-API

## Remerciements

- Basé sur l'architecture de DnD-5e-ncurses
- Utilise l'API D&D 5th Edition
- Inspiré par les jeux RPG en terminal classiques comme Rogue et NetHack

## Contact

Pour toute question ou suggestion, veuillez créer une issue sur GitHub.

