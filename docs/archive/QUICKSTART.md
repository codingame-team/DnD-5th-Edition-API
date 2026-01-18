# Guide de démarrage rapide - DnD 5E NCurses

## Installation rapide

### 1. Vérifier Python
```bash
python --version  # Doit être 3.10+
```

### 2. Tester ncurses
```bash
cd /Users/display/PycharmProjects/DnD-5th-Edition-API
python test_ncurses.py
```

Si le test réussit, vous verrez :
```
✓ All tests passed!
You can now run: python main_ncurses.py
```

### 3. Lancer le jeu
```bash
# Méthode 1 : Script de lancement
python run_ncurses.py

# Méthode 2 : Directe
python main_ncurses.py

# Méthode 3 : Exécutable (si chmod +x)
./run_ncurses.py
```

## Premiers pas

### Menu principal
```
=========================== D&D 5E - Main Menu ============================
Party: 0 | Location: castle

  ► Start New Game
    Load Game
    Options
    Quit

────────────────────────────────────────────────────────────────────────────

[↑/↓] Navigate  [Enter] Select  [q] Quit
```

**Commandes :**
- `↑` / `↓` ou `j` / `k` : Naviguer
- `Entrée` : Sélectionner
- `q` : Quitter

### Au château
```
================================= CASTLE ==================================

What would you like to do?

    ► Gilgamesh's Tavern
      Adventurer's Inn
      Temple of Cant
      Boltac's Trading Post
      Edge of Town
      Save & Exit

CURRENT PARTY:
  (No characters in party)

────────────────────────────────────────────────────────────────────────────

[↑/↓] Navigate  [Enter] Select  [Esc] Back
```

### Gestion de la partie
```
======================= Party & Roster Management =========================

CURRENT PARTY
    (No characters in party)

AVAILABLE ROSTER
    (No available characters)

────────────────────────────────────────────────────────────────────────────

[↑/↓] Navigate  [Enter] Add/Remove  [Esc] Back
```

## Contrôles complets

### Navigation générale
| Touche | Action |
|--------|--------|
| `↑` ou `k` | Haut |
| `↓` ou `j` | Bas |
| `Enter` | Sélectionner |
| `Esc` | Retour |
| `q` | Quitter (menu principal) |

### Raccourcis spécifiques
| Contexte | Touche | Action |
|----------|--------|--------|
| Exploration | `w` | Errer |
| Combat | `a` | Attaquer |
| Combat | `r` | Fuir |
| Partout | `i` | Inventaire |
| Partout | `m` | Menu |

## Dépannage

### Erreur : "Terminal too small"
**Solution :** Redimensionner le terminal à au moins 80x24

```bash
# Vérifier la taille actuelle
tput cols  # Largeur
tput lines # Hauteur
```

### Erreur : "No module named 'curses'"
**Sur Windows :**
```bash
pip install windows-curses
```

**Sur Linux/macOS :**
```bash
# Curses est inclus par défaut
# Si problème, réinstaller Python
```

### Erreur : "Unresolved reference 'load_dungeon_collections'"
**Solution :** Le jeu fonctionne en mode stub (sans données complètes)

Pour utiliser les vraies données du jeu :
1. Assurez-vous que tous les fichiers de `populate_functions.py` sont présents
2. Vérifiez que `dao_classes.py` est accessible
3. Relancez le jeu

### Affichage corrompu
**Solution :**
1. Redimensionner le terminal
2. Appuyer sur `Ctrl+L` pour rafraîchir (dans certains terminaux)
3. Relancer le programme

## Fonctionnalités disponibles

### ✅ Implémenté
- Menu principal
- Navigation château / bord de ville
- Affichage de la partie et du roster
- Système de messages
- Gestion de la taille du terminal

### 🚧 En cours
- Création de personnage
- Combat détaillé
- Exploration du donjon
- Inventaire complet

### 📋 Planifié
- Services de la taverne
- Repos à l'auberge
- Résurrection au temple
- Commerce au poste

## Exemples d'utilisation

### Créer une nouvelle partie
1. Lancer `python run_ncurses.py`
2. Sélectionner "Start New Game"
3. Naviguer vers "Training Grounds"
4. Créer des personnages
5. Retourner au château
6. Former une partie à la taverne

### Charger une partie existante
1. Lancer `python run_ncurses.py`
2. Sélectionner "Load Game"
3. La partie et le roster sont chargés automatiquement

### Explorer le donjon
1. Aller à "Edge of Town"
2. Sélectionner "Enter Maze"
3. Utiliser `w` pour errer
4. Combattre les monstres avec `a`
5. Fuir avec `r` si nécessaire

## Astuces

### Performance
- Utilisez un terminal moderne (iTerm2, GNOME Terminal, Windows Terminal)
- Évitez les redimensionnements pendant le jeu
- Fermez les autres applications gourmandes

### Expérience
- Agrandissez le terminal pour plus de confort (recommandé : 100x30)
- Activez les couleurs dans votre terminal
- Utilisez un fond sombre pour moins de fatigue oculaire

### Développement
- Consultez `NCURSES_README.md` pour la documentation complète
- Lisez `NCURSES_COMPARISON.md` pour comprendre les différences
- Testez avec `test_ncurses.py` avant de modifier le code

## Ressources

### Documentation
- `NCURSES_README.md` - Documentation complète
- `NCURSES_COMPARISON.md` - Comparaison avec main.py
- `main_ncurses.py` - Code source commenté

### Fichiers importants
- `run_ncurses.py` - Script de lancement
- `test_ncurses.py` - Tests de compatibilité
- `main.py` - Version originale (référence)

## Obtenir de l'aide

### Problèmes courants
1. Consulter la section Dépannage ci-dessus
2. Lancer `python test_ncurses.py` pour diagnostiquer
3. Vérifier les logs d'erreur

### Rapporter un bug
1. Noter le message d'erreur exact
2. Indiquer la taille du terminal (`tput cols` et `tput lines`)
3. Préciser le système d'exploitation
4. Fournir les étapes pour reproduire

## Prochaines étapes

Une fois familiarisé avec l'interface :

1. **Créer des personnages** (quand implémenté)
   - Training Grounds → Create Character
   
2. **Former une partie**
   - Taverne → Recruit Adventurers
   
3. **Explorer**
   - Edge of Town → Enter Maze
   
4. **Progresser**
   - Combattre, gagner XP, améliorer équipement
   
5. **Sauvegarder**
   - Castle → Save & Exit

Bon jeu ! 🎲

