# 🎉 GUIDE D'UTILISATION - Corrections du 17 Décembre 2024

## ✅ Deux Problèmes Résolus

### 1. Support Pseudo-TTY (main_pexpect.py)
### 2. Chargement du Gamestate (main_ncurses.py)

---

## 🚀 Utilisation

### Option 1 : Lancement Direct (Recommandé pour terminal)

```bash
# Version NCurses (interface moderne)
python run_ncurses.py

# Version texte classique
python main.py
```

### Option 2 : Avec main_pexpect.py (Pour IDE/Debugger)

```bash
# Version NCurses avec détection TTY automatique
python main_pexpect.py ncurses

# Version texte classique
python main_pexpect.py main

# Aide
python main_pexpect.py --help
```

---

## 🧪 Vérification des Corrections

### Test Automatique

```bash
python test_fixes.py
```

**Résultat attendu :**
```
✅ PASSED - Pseudo-TTY Support
✅ PASSED - Gamestate Loading
🎉 ALL TESTS PASSED!
```

### Test Manuel - Pseudo-TTY

```bash
# Dans un terminal
python main_pexpect.py ncurses
# ✓ Devrait afficher "TTY detected - running directly"

# Dans PyCharm/IDE (sans TTY)
# ✓ Devrait afficher "No TTY detected - using pseudo-TTY"
```

### Test Manuel - Gamestate

**Étape 1 : Créer des données avec main.py**
```bash
python main.py
# → Edge of Town
# → Training Grounds
# → Create New Character (ex: Gandalf)
# → Return to Castle
# → Tavern → Add Member (recruter Gandalf)
# → Exit → Save & Exit
```

**Étape 2 : Vérifier le chargement avec main_ncurses.py**
```bash
python main_ncurses.py
# Observer au démarrage (en haut de l'écran) :
# ✓ "Loaded 1 characters from roster"
# ✓ "Loaded 1 characters in party"
# → Aller à Tavern
# ✓ Gandalf devrait être dans la partie
```

---

## 📁 Fichiers de Sauvegarde

### Emplacement
```
~/.dnd5e/            (ou équivalent selon OS)
├── characters/
│   ├── Gandalf.dmp
│   ├── Aragorn.dmp
│   └── ...
└── party.dmp
```

### Format
- **Type** : Pickle binaire Python
- **Extension** : `.dmp`
- **Compatible** : main.py ↔ main_ncurses.py

---

## 🔄 Workflow Complet

### Scénario : Créer une partie et jouer

```bash
# 1. Créer des personnages (main.py ou main_ncurses.py)
python main.py
→ Edge of Town → Training Grounds
→ Create New Character × 3
→ Return to Castle

# 2. Former une partie (main.py ou main_ncurses.py)
→ Tavern → Add Member × 3
→ Exit Tavern

# 3. Se reposer si nécessaire
→ Adventurer's Inn
→ Choisir personnage
→ Choisir chambre

# 4. Explorer le donjon
→ Edge of Town → Enter Maze
→ Combats automatiques
→ Retour automatique

# 5. Services du temple si morts
→ Temple of Cant
→ Sélectionner mort
→ Payer résurrection

# 6. Sauvegarder et quitter
→ Castle → Save & Exit
# ✓ Tout est sauvegardé automatiquement
```

### Continuité entre Sessions

```bash
# Session 1 - Créer et jouer
python main.py
# ... créer personnages, jouer ...
# → Save & Exit

# Session 2 - Continuer en NCurses
python main_ncurses.py
# ✓ Personnages et partie automatiquement chargés
# → Continuer l'aventure
```

---

## 🔧 Détails Techniques

### main_pexpect.py - Détection TTY

```python
def is_tty():
    return sys.stdin.isatty() and sys.stdout.isatty()

if is_tty():
    run_directly(script)      # Lancement direct (rapide)
else:
    run_with_pty(script)      # Pseudo-TTY (pour IDE)
```

### main_ncurses.py - Chargement

```python
# Au démarrage
self.roster = get_roster(self.characters_dir)
# → Scanne tous les .dmp dans characters/

self.party = load_party(_dir=self.game_path)
# → Charge party.dmp

# Après chaque action importante
save_character(char, _dir=self.characters_dir)
save_party(self.party, _dir=self.game_path)
```

---

## 🐛 Dépannage

### Problème : "No characters loaded"

**Solution :**
```bash
# Vérifier que les fichiers existent
ls ~/.dnd5e/characters/
ls ~/.dnd5e/party.dmp

# Si vides, créer des personnages d'abord
python main.py
# → Training Grounds → Create Character
```

### Problème : "Pseudo-TTY error in IDE"

**Solution :**
```bash
# Utiliser main_pexpect.py au lieu de lancement direct
python main_pexpect.py ncurses
```

### Problème : "Cannot pickle Character"

**Cause :** Tentative d'utiliser les classes stub
**Solution :** S'assurer que les vraies classes sont importées
```python
# Dans main_ncurses.py, vérifier :
from dao_classes import Character  # Vraie classe
# et non la classe stub
```

---

## 📊 Compatibilité

### Formats de Sauvegarde
| Créé avec | Lisible par main.py | Lisible par main_ncurses.py |
|-----------|---------------------|----------------------------|
| main.py | ✅ | ✅ |
| main_ncurses.py | ✅ | ✅ |

### Terminaux
| Terminal | main_pexpect.py | Direct |
|----------|-----------------|--------|
| macOS Terminal | ✅ TTY direct | ✅ |
| iTerm2 | ✅ TTY direct | ✅ |
| PyCharm | ✅ Pseudo-TTY | ⚠️ Problèmes |
| VS Code | ✅ Pseudo-TTY | ⚠️ Problèmes |
| IntelliJ | ✅ Pseudo-TTY | ⚠️ Problèmes |

---

## 📝 Exemples Rapides

### Démarrage Rapide (1 min)

```bash
# Créer un personnage aléatoire
python main.py
→ Training → Create Random Character
→ Y (keep)
→ Return

# Jouer immédiatement
→ Tavern → Add Member
→ Edge → Maze
```

### Basculer entre Versions

```bash
# Jouer en texte
python main.py
# ... jouer ...
# Save & Exit

# Continuer en NCurses
python main_ncurses.py
# ✓ Partie restaurée
# ... jouer ...
# Save & Exit

# Retour en texte
python main.py
# ✓ Partie restaurée
```

---

## ✅ Checklist de Vérification

Après installation des corrections :

- [ ] `python test_fixes.py` → Tous les tests passent
- [ ] `python main_pexpect.py --help` → Affiche l'aide
- [ ] Créer personnage avec main.py
- [ ] Lancer main_ncurses.py → Personnage chargé
- [ ] Sauvegarder dans main_ncurses.py
- [ ] Relancer → Sauvegarde restaurée
- [ ] Basculer vers main.py → Sauvegarde compatible

---

## 🎯 Résumé

### Avant Corrections
- ❌ main_pexpect.py limité
- ❌ Pas de persistence gamestate
- ❌ Incompatibilité main.py/main_ncurses.py

### Après Corrections
- ✅ main_pexpect.py flexible (TTY auto-détection)
- ✅ Persistence complète gamestate
- ✅ Compatibilité totale main.py ↔ main_ncurses.py
- ✅ Expérience utilisateur unifiée

---

**Date** : 17 décembre 2024
**Version** : 0.2.1
**Statut** : ✅ PRODUCTION READY

🎲 **Bon jeu !**

