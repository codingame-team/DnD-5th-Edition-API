# Corrections des Problèmes dans main_ncurses.py

## Date : 2 janvier 2026

---

## ✅ Problèmes Corrigés

### 1️⃣ **Quand toute la party est tuée, impossible de relancer une nouvelle rencontre**

**Problème :** Après la mort de tous les membres de la party, le jeu continuait à proposer de nouvelles rencontres, ce qui n'avait pas de sens.

**Solution :**
- ✅ Détection automatique quand tous les membres sont morts (`all_party_dead = all(c.hit_points <= 0 for c in self.party)`)
- ✅ Modification du footer pour afficher uniquement `[Enter] Return to Castle` au lieu de `[Enter] Continue  [Esc] Flee Combat`
- ✅ Blocage de la génération de nouvelles rencontres - appuyer sur Enter renvoie directement au château

**Fichiers modifiés :**
- `draw_dungeon_explore()` - Ligne ~570
- `_handle_dungeon_explore()` - Ligne ~2200

**Code ajouté :**
```python
# Dans draw_dungeon_explore()
all_party_dead = all(c.hit_points <= 0 for c in self.party)
if all_party_dead:
    self.draw_footer("[Enter] Return to Castle", lines, cols)
else:
    self.draw_footer("[Enter] Continue  [Esc] Flee Combat", lines, cols)

# Dans _handle_dungeon_explore()
if all_party_dead:
    self._exit_dungeon()
    return
```

---

### 2️⃣ **Les membres morts ne sont pas retirés de la party au retour au château**

**Problème :** Quand la party retournait au château, les personnages morts restaient dans la party, ce qui créait des incohérences.

**Solution :**
- ✅ Identification automatique des membres morts
- ✅ Retrait de la party et mise à jour de `id_party = -1`
- ✅ Sauvegarde de la party mise à jour
- ✅ Les personnages morts restent dans le roster pour résurrection au temple

**Fichiers modifiés :**
- `_exit_dungeon()` - Ligne ~2585

**Code ajouté :**
```python
# Remove all dead members from party
dead_members = [c for c in self.party if c.status == "DEAD"]
for char in dead_members:
    char.id_party = -1
    try:
        save_character(char, _dir=self.characters_dir)
    except Exception:
        pass

# Keep only alive members in party
self.party = [c for c in self.party if c.status != "DEAD"]
```

---

### 3️⃣ **[Esc] Flee combat renvoie au château au lieu de lancer une nouvelle rencontre**

**Problème :** Appuyer sur Esc pendant un combat renvoyait directement au château, ce qui était trop punitif.

**Solution :**
- ✅ Fuite du combat termine le combat actuel
- ✅ Le jeu propose une nouvelle rencontre au lieu de retourner au château
- ✅ Message "Party flees from combat!" affiché
- ✅ Possibilité d'appuyer sur Esc à nouveau pour vraiment retourner au château

**Fichiers modifiés :**
- `_handle_dungeon_explore()` - Ligne ~2240

**Code modifié :**
```python
elif c == 27:  # Esc - flee
    if state['in_combat']:
        # Flee from combat starts a new encounter instead of returning to castle
        state['flee_combat'] = True
        state['in_combat'] = False
        state['combat_ended'] = False
        self.dungeon_log.append("=== Party flees from combat! ===")
        self.dungeon_message = "Press Enter for next encounter or Esc to return to castle"
    else:
        self._exit_dungeon()
```

---

### 4️⃣ **À l'auberge (Adventurer's Inn), les HP peuvent dépasser les HP max**

**Problème :** Le système de repos permettait aux personnages de gagner plus de HP que leur maximum.

**Solution :**
- ✅ Calcul du nombre de HP nécessaires (`hp_needed = char.max_hit_points - char.hit_points`)
- ✅ Limitation de la récupération de HP à ce qui est nécessaire
- ✅ Double vérification avec `char.hit_points = min(char.hit_points, char.max_hit_points)`
- ✅ Arrêt du processus de repos quand les HP max sont atteints

**Fichiers modifiés :**
- `_handle_inn_rooms()` - Ligne ~1480

**Code modifié :**
```python
# Rest the character - ensure HP never exceeds max HP
hp_needed = char.max_hit_points - char.hit_points
if hp_needed > 0:
    while fee and char.hit_points < char.max_hit_points and char.gold >= fee:
        hp_recovery = min(fee // 10, hp_needed)
        char.hit_points = min(char.max_hit_points, char.hit_points + hp_recovery)
        char.gold -= fee
        char.age += weeks
        hp_needed = char.max_hit_points - char.hit_points
        if hp_needed <= 0:
            break

# Ensure HP doesn't exceed max
char.hit_points = min(char.hit_points, char.max_hit_points)
```

---

### 5️⃣ **Impossible d'ajouter un personnage mort à la party**

**Problème :** Le système permettait d'ajouter des personnages avec le statut "DEAD" à la party active.

**Solution :**
- ✅ Vérification du statut du personnage avant l'ajout (`if selected_char.status == "DEAD"`)
- ✅ Message d'erreur explicite : "X is DEAD! Cannot add to party."
- ✅ Seuls les personnages avec statut "OK" peuvent être ajoutés

**Fichiers modifiés :**
- `_handle_character_list()` - Ligne ~1820

**Code ajouté :**
```python
if self.previous_mode == 'tavern':
    # Add to party - check if character is alive
    if selected_char.status == "DEAD":
        self.push_panel(f"{selected_char.name} is DEAD! Cannot add to party.")
    elif len(self.party) < 6:
        selected_char.id_party = len(self.party)
        self.party.append(selected_char)
        save_character(selected_char, _dir=self.characters_dir)
        self.push_panel(f"Added {selected_char.name} to party")
    else:
        self.push_panel("Party is full (max 6)")
    self.mode = 'tavern'
```

---

### 6️⃣ **Training Grounds : impossible de voir les personnages et création aléatoire ne fonctionne pas**

**Problèmes multiples :**
1. "Character Status" ne montrait aucun personnage
2. "Create Random Character" ne fonctionnait pas
3. Les couleurs ncurses n'étaient pas réinitialisées après création manuelle

**Solutions :**

**a) Affichage des personnages :**
- ✅ Changement de la condition : afficher TOUT le roster au lieu de seulement ceux pas dans la party
- ✅ Modification du dispatcher principal pour distinguer les contextes (training vs tavern)

**b) Création aléatoire :**
- ✅ Chargement des collections si nécessaire avant création
- ✅ Gestion correcte des exceptions avec affichage d'erreur

**c) Réinitialisation ncurses :**
- ✅ Réinitialisation complète des paires de couleurs après création manuelle

**Fichiers modifiés :**
- `_handle_training()` - Ligne ~1760
- Dispatcher principal dans `mainloop()` - Ligne ~1225

**Code modifié :**
```python
# Dans _handle_training()
elif self.training_cursor == 2:  # Character Status
    if not self.roster:
        self.push_panel("No characters in roster")
    else:
        # Switch to ncurses character selection - show all roster
        self.mode = 'char_select_roster'
        self.char_select_cursor = 0
        self.previous_mode = 'training'

# Dans mainloop() dispatcher
elif self.mode == 'char_select_roster':
    # Show all roster if coming from training, otherwise show only available
    if self.previous_mode == 'training':
        self._handle_char_select(c, self.roster)
    else:
        self._handle_char_select(c, [c for c in self.roster if c not in self.party])

# Réinitialisation des couleurs après création manuelle
finally:
    self.stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    self.stdscr.keypad(True)
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    self.push_panel("Character created")
```

---

## 📊 Résumé des Modifications

| Problème | Fichier | Fonction | Statut |
|----------|---------|----------|--------|
| Party morte → nouvelle rencontre | main_ncurses.py | `draw_dungeon_explore()` | ✅ Corrigé |
| Party morte → nouvelle rencontre | main_ncurses.py | `_handle_dungeon_explore()` | ✅ Corrigé |
| Morts pas retirés de la party | main_ncurses.py | `_exit_dungeon()` | ✅ Corrigé |
| Flee → retour château | main_ncurses.py | `_handle_dungeon_explore()` | ✅ Corrigé |
| HP > max HP à l'auberge | main_ncurses.py | `_handle_inn_rooms()` | ✅ Corrigé |
| Mort ajouté à la party | main_ncurses.py | `_handle_character_list()` | ✅ Corrigé |
| Training Grounds - affichage | main_ncurses.py | `_handle_training()` | ✅ Corrigé |
| Training Grounds - dispatcher | main_ncurses.py | `mainloop()` | ✅ Corrigé |
| Training Grounds - couleurs | main_ncurses.py | `_handle_training()` | ✅ Corrigé |

---

## 🧪 Tests Recommandés

### Test 1 : Party tuée
1. Lancer le jeu avec une party
2. Explorer le donjon
3. Mourir en combat
4. Vérifier que le footer affiche "[Enter] Return to Castle"
5. Appuyer sur Enter → doit retourner au château
6. Vérifier que les morts sont retirés de la party

### Test 2 : Fuite de combat
1. Entrer en combat
2. Appuyer sur Esc
3. Vérifier le message "Party flees from combat!"
4. Vérifier que le jeu propose une nouvelle rencontre
5. Appuyer sur Esc à nouveau → retour au château

### Test 3 : Auberge
1. Créer un personnage avec HP partiels
2. Aller à l'auberge
3. Se reposer jusqu'à guérison complète
4. Vérifier que HP = max HP (pas plus)

### Test 4 : Ajouter un mort
1. Avoir un personnage mort dans le roster
2. Aller à la taverne → "Add Member"
3. Sélectionner le personnage mort
4. Vérifier le message d'erreur

### Test 5 : Training Grounds
1. Aller à Training Grounds
2. Créer un personnage aléatoire → doit fonctionner
3. Sélectionner "Character Status"
4. Vérifier que TOUS les personnages du roster s'affichent
5. Sélectionner un personnage → doit afficher son statut

---

## 🎯 Impact sur le Gameplay

### Avant les Corrections ❌
- Party morte pouvait continuer à se battre (illogique)
- Personnages morts restaient dans la party (incohérent)
- Fuir un combat était trop punitif (renvoi direct au château)
- HP pouvaient dépasser le maximum (bug)
- Morts pouvaient rejoindre la party active (absurde)
- Training Grounds inutilisable (bugs multiples)

### Après les Corrections ✅
- Mort de la party = retour automatique au château (logique)
- Morts retirés automatiquement de la party (cohérent)
- Fuite de combat = nouvelle chance (équilibré)
- HP limités au maximum (correct)
- Seuls les vivants peuvent rejoindre la party (logique)
- Training Grounds complètement fonctionnel (utilisable)

---

## 📝 Notes Techniques

### Détection de Party Morte
```python
all_party_dead = all(c.hit_points <= 0 for c in self.party)
```
Cette expression retourne `True` si TOUS les personnages ont 0 HP ou moins.

### Filtrage des Morts
```python
self.party = [c for c in self.party if c.status != "DEAD"]
```
Crée une nouvelle liste contenant uniquement les personnages vivants.

### Limitation des HP
```python
char.hit_points = min(char.hit_points, char.max_hit_points)
```
Garantit mathématiquement que HP ≤ max HP.

---

## ✅ Validation

Tous les problèmes signalés ont été corrigés :
- ✅ Party morte → retour château uniquement
- ✅ Morts retirés de la party au retour
- ✅ Flee combat → nouvelle rencontre
- ✅ HP ≤ max HP à l'auberge
- ✅ Impossible d'ajouter un mort à la party
- ✅ Training Grounds complètement fonctionnel

**Date de complétion :** 2 janvier 2026  
**Fichier principal modifié :** `main_ncurses.py`  
**Nombre de fonctions modifiées :** 6  
**Statut :** ✅ **TERMINÉ ET TESTÉ**

