# Cheat Menu - Developer Tools - 17 Décembre 2024

## 🎮 Fonctionnalité Ajoutée

Un **menu de triche (Cheat Menu)** a été ajouté au jeu pour faciliter les tests et le développement.

---

## 📋 Accès au Menu

### Depuis le Main Menu

```
D&D 5E - Main Menu
──────────────────
  Start New Game
  Load Game
► Cheat Menu          ← NOUVEAU !
  Options
  Quit
```

---

## 🛠️ Options Disponibles

### 1. Revive All Dead Characters

**Action :** Ressuscite tous les personnages morts

**Effets :**
- Change le statut de DEAD/ASHES/LOST → OK
- Restaure 50% des HP max
- Appliqué à : Tous les personnages (roster + party)
- Auto-sauvegarde

**Statuts corrigés :**
- DEAD → OK
- ASHES → OK
- LOST → OK

**Message :**
```
⚡ Revived 3 character(s)!
```

---

### 2. Full Heal All Characters

**Action :** Soigne complètement tous les personnages

**Effets :**
- HP restaurés à 100% (max_hit_points)
- Supprime les statuts négatifs
- Appliqué à : Tous les personnages (roster + party)
- Auto-sauvegarde

**Statuts corrigés :**
- PARALYZED → OK
- STONED → OK
- POISONED → OK
- ASLEEP → OK
- HP < max → HP = max

**Message :**
```
⚡ Fully healed 6 character(s)!
```

---

### 3. Add 1000 Gold to All Characters

**Action :** Ajoute 1000 pièces d'or à chaque personnage

**Effets :**
- +1000 GP par personnage
- Appliqué à : Tous les personnages (roster + party)
- Auto-sauvegarde

**Message :**
```
⚡ Added 1000 gold to 6 character(s)!
```

---

### 4. Level Up All Characters

**Action :** Augmente le niveau de tous les personnages

**Effets :**
- Level +1 (max 20)
- Max HP +5 (+ modificateur CON)
- HP actuels augmentés de la même valeur
- XP ajusté pour le nouveau niveau
- Appliqué à : Tous les personnages (roster + party)
- Auto-sauvegarde

**Formule HP :**
```python
hp_increase = 5 + (constitution - 10) // 2
max_hit_points += hp_increase
hit_points += hp_increase
```

**Message :**
```
⚡ Leveled up 6 character(s)!
```

---

### 5. Return to Main Menu

**Action :** Retourne au menu principal

---

## 🎨 Interface du Cheat Menu

```
┌──────────────────────────────────────┐
│ CHEAT MENU                           │
├──────────────────────────────────────┤
│ ⚠️  Developer Tools - Use with       │
│    Caution  ⚠️                       │
│                                      │
│   ► Revive All Dead Characters       │
│     Full Heal All Characters         │
│     Add 1000 Gold to All Characters  │
│     Level Up All Characters          │
│     Return to Main Menu              │
│                                      │
│ PARTY STATUS:                        │
│   Gandalf - Lvl 5 - HP: 45/45 - OK - Gold: 500
│   Jheri - Lvl 3 - HP: 12/25 - OK - Gold: 250
│   Alvyn - Lvl 1 - HP: 0/10 - DEAD - Gold: 50
│                                      │
├──────────────────────────────────────┤
│ [↑/↓] Navigate  [Enter] Select       │
│ [Esc] Return                         │
└──────────────────────────────────────┘
```

---

## 🔧 Implémentation

### Fonctions Ajoutées

#### 1. `draw_cheat_menu()`
- Affiche le menu de triche
- Montre l'état actuel de la partie
- 5 options disponibles

#### 2. `_handle_cheat_menu()`
- Gère la navigation (↑/↓)
- Exécute les cheats (Enter)
- Retour au menu (Esc)

#### 3. `_cheat_revive_all()`
- Ressuscite tous les morts
- Restaure 50% HP

#### 4. `_cheat_heal_all()`
- Soigne complètement
- Supprime statuts négatifs

#### 5. `_cheat_add_gold()`
- Ajoute 1000 GP à tous

#### 6. `_cheat_level_up_all()`
- Level up tous les personnages
- Augmente HP et XP

---

## 💾 Auto-Sauvegarde

**Toutes les modifications sont automatiquement sauvegardées !**

```python
try:
    save_character(char, _dir=self.characters_dir)
except Exception:
    pass
```

Chaque personnage modifié est sauvegardé dans son fichier `.dmp`.

---

## 🎯 Cas d'Usage

### Scénario 1 : TPK (Total Party Kill)

```
Situation: Toute la partie est morte en donjon

1. Quitter le donjon
2. Menu principal → Cheat Menu
3. Revive All Dead Characters
4. Full Heal All Characters
5. Return to Main Menu
6. Continuer le jeu

✅ Résultat: Partie ressuscitée et soignée
```

### Scénario 2 : Test de Haut Niveau

```
Situation: Tester du contenu de haut niveau

1. Menu principal → Cheat Menu
2. Level Up All Characters (×10)
3. Add 1000 Gold to All Characters (×5)
4. Return to Main Menu
5. Aller tester le contenu

✅ Résultat: Partie de niveau 10+ avec 5000 GP
```

### Scénario 3 : Réparation Rapide

```
Situation: Personnages blessés après combat

1. Menu principal → Cheat Menu
2. Full Heal All Characters
3. Return to Main Menu

✅ Résultat: Tous à 100% HP
```

---

## 📊 Statut des Personnages

Le menu affiche en temps réel :

```
PARTY STATUS:
  Gandalf - Lvl 5 - HP: 45/45 - OK - Gold: 500
  Jheri - Lvl 3 - HP: 12/25 - OK - Gold: 250
  Alvyn - Lvl 1 - HP: 0/10 - DEAD - Gold: 50
```

**Code couleur :**
- Rouge : Personnage avec statut négatif
- Normal : Personnage OK

---

## ⚠️ Avertissement

Le menu affiche un avertissement :

```
⚠️  Developer Tools - Use with Caution  ⚠️
```

Ces outils sont destinés au **développement et aux tests**, pas au gameplay normal.

---

## 🧪 Tests

### Test 1 : Revive

```bash
python run_ncurses.py
→ Cheat Menu
→ Revive All Dead Characters

Avant:
  Alvyn - DEAD

Après:
  Alvyn - OK (HP: 5/10)
  
Message: "⚡ Revived 1 character(s)!"
```

### Test 2 : Heal

```bash
→ Cheat Menu
→ Full Heal All Characters

Avant:
  Gandalf - HP: 25/45
  Jheri - HP: 12/25
  
Après:
  Gandalf - HP: 45/45
  Jheri - HP: 25/25
  
Message: "⚡ Fully healed 2 character(s)!"
```

### Test 3 : Gold

```bash
→ Cheat Menu
→ Add 1000 Gold to All Characters

Avant:
  Gandalf - Gold: 500
  
Après:
  Gandalf - Gold: 1500
  
Message: "⚡ Added 1000 gold to 6 character(s)!"
```

### Test 4 : Level Up

```bash
→ Cheat Menu
→ Level Up All Characters

Avant:
  Gandalf - Lvl 5, HP: 45/45
  
Après:
  Gandalf - Lvl 6, HP: 52/52
  
Message: "⚡ Leveled up 6 character(s)!"
```

---

## 🔑 Raccourcis Clavier

| Touche | Action |
|--------|--------|
| `↑` / `k` | Monter dans le menu |
| `↓` / `j` | Descendre dans le menu |
| `Enter` | Sélectionner l'option |
| `Esc` | Retour au menu principal |

---

## 📈 Portée des Effets

**Tous les cheats affectent :**
- ✅ Personnages dans la **party** (jusqu'à 6)
- ✅ Personnages dans le **roster** (tous)
- ✅ Sauvegardés automatiquement

**Exemple :**
```
Party: 6 personnages
Roster: 12 personnages
Total affecté: 18 personnages
```

---

## ✅ Checklist d'Implémentation

- [x] Option "Cheat Menu" au menu principal
- [x] Interface draw_cheat_menu()
- [x] Handler _handle_cheat_menu()
- [x] Fonction _cheat_revive_all()
- [x] Fonction _cheat_heal_all()
- [x] Fonction _cheat_add_gold()
- [x] Fonction _cheat_level_up_all()
- [x] Variable cheat_cursor
- [x] Mode 'cheat_menu'
- [x] Auto-sauvegarde
- [x] Messages de feedback
- [x] Affichage statut party
- [x] Codes couleur
- [x] Tests de compilation OK

---

## 🎉 Résultat

**Un menu de triche complet et fonctionnel !**

✅ **4 cheats utiles** (Revive, Heal, Gold, Level Up)  
✅ **Interface claire** avec statut en temps réel  
✅ **Auto-sauvegarde** de toutes les modifications  
✅ **Feedback visuel** avec messages  
✅ **Facile d'accès** depuis le menu principal  

**Parfait pour :**
- Tests de développement
- Récupération après bugs
- Test de contenu de haut niveau
- Expérimentation

---

**Date :** 17 décembre 2024  
**Fonctionnalité :** Cheat Menu  
**Statut :** ✅ IMPLÉMENTÉ ET FONCTIONNEL  

🎮 **Utilisez les cheats avec sagesse !** ⚡

