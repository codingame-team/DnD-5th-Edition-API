# Correction de la Redondance du Menu Principal (main_ncurses.py)

## Problème Identifié

Dans `main_ncurses.py`, les options "Start New Game" et "Load Game" effectuaient **exactement la même action**, créant une redondance complète :

### Comportement AVANT la correction :

#### "Start New Game"
```python
if self.menu_cursor == 0:  # Start New Game
    self.mode = 'location'
    self.location = Location.CASTLE
```
- Changeait seulement le mode vers 'location'
- **Ne chargeait AUCUNE donnée** (roster, party, monstres, etc.)
- Rendait le jeu inutilisable (pas de monstres, pas de personnages)

#### "Load Game"
```python
elif self.menu_cursor == 1:  # Load Game
    self.push_panel("Loading game...")
    self.load_game_data()  # Charge TOUTES les données
    self.mode = 'location'
```
- Rechargeait **toutes** les ressources du jeu (monstres, armes, armures, etc.)
- Rechargeait aussi le roster et la party
- Changeait le mode vers 'location'

### Cause du Problème

Les données du jeu (monstres, armes, armures) sont **déjà chargées automatiquement** au démarrage dans `mainloop()` ligne 1127 :

```python
def mainloop(self):
    # ...
    self.push_message("Loading game data...")
    self.load_game_data()  # ← Chargement initial au démarrage
    # ...
```

Donc "Load Game" rechargeait inutilement toutes les données déjà en mémoire.

---

## Solution Implémentée

Les deux options ont maintenant des **comportements distincts et logiques** :

### "Start New Game" - Nouveau Jeu Vierge
```python
if self.menu_cursor == 0:  # Start New Game
    # Reset party and roster for a fresh start
    self.party = []
    self.roster = []
    self.push_panel("Starting new game...")
    # Save empty party/roster to disk
    try:
        save_party(self.party, _dir=self.game_path)
        self.push_panel("New game initialized!")
    except Exception as e:
        self.push_panel(f"Error initializing new game: {e}")
    self.mode = 'location'
    self.location = Location.CASTLE
```

**Comportement :**
- ✅ Réinitialise le roster (aucun personnage)
- ✅ Réinitialise la party (aucun personnage dans le groupe)
- ✅ Sauvegarde cette state vierge sur le disque
- ✅ Affiche "Starting new game..."
- ✅ Permet de créer de nouveaux personnages from scratch

### "Load Game" - Charger une Partie Sauvegardée
```python
elif self.menu_cursor == 1:  # Load Game
    # Reload saved roster and party from disk
    self.push_panel("Loading saved game...")
    self.roster = get_roster(self.characters_dir)
    self.party = load_party(_dir=self.game_path)
    self.push_panel(f"Loaded {len(self.roster)} characters, {len(self.party)} in party")
    self.mode = 'location'
    self.location = Location.CASTLE
```

**Comportement :**
- ✅ Recharge **uniquement** le roster et la party depuis le disque
- ✅ N'affecte PAS les ressources du jeu (monstres, armes, etc.) déjà en mémoire
- ✅ Affiche "Loading saved game..." puis le nombre de personnages chargés
- ✅ Permet de continuer une partie existante

---

## Résumé des Changements

| Aspect | Avant | Après |
|--------|-------|-------|
| **Start New Game** | Jeu inutilisable (pas de données chargées) | Nouveau jeu vierge (roster/party vides) |
| **Load Game** | Recharge inutilement TOUTES les données | Recharge uniquement roster/party sauvegardés |
| **Redondance** | ❌ Oui (les deux font la même chose) | ✅ Non (comportements distincts) |
| **Logique** | ❌ Incohérente | ✅ Cohérente |

---

## Test de la Correction

### Scénario 1 : Première fois que vous jouez
1. Lancez le jeu → Les ressources se chargent automatiquement
2. Sélectionnez **"Start New Game"**
3. Résultat : Roster et party vides, vous pouvez créer de nouveaux personnages

### Scénario 2 : Vous avez déjà joué
1. Lancez le jeu → Les ressources se chargent automatiquement
2. Sélectionnez **"Load Game"**
3. Résultat : Vos personnages sauvegardés sont rechargés depuis le disque

### Scénario 3 : Recommencer à zéro
1. Lancez le jeu
2. Sélectionnez **"Start New Game"**
3. Résultat : Vos anciennes sauvegardes sont effacées, vous recommencez from scratch

---

## Fichier Modifié

- `/Users/display/PycharmProjects/DnD-5th-Edition-API/main_ncurses.py`
  - Fonction `_handle_main_menu()` (lignes ~1178-1215)

---

## Date de la Correction

**1 janvier 2026**

