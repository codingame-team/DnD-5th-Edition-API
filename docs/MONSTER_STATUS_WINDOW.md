# Ajout de la Fenêtre MONSTER STATUS dans main_ncurses.py

## Fonctionnalité Ajoutée

Une nouvelle fenêtre **MONSTER STATUS** a été ajoutée à l'écran d'exploration du donjon (`draw_dungeon_explore`), affichée à droite de la fenêtre **PARTY STATUS**.

---

## Disposition de l'Écran

### AVANT l'ajout
```
┌────────────────────────────────────────────────────────┐
│           DUNGEON EXPLORATION                          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  PARTY STATUS:                                         │
│    1. Ellyjobell: [████████··] 15/20 HP               │
│    2. Vistr: [██████████] 30/30 HP                    │
│    3. Patrin: [████······] 8/20 HP                    │
│    4. Trym: [██████████] 25/25 HP                     │
│    5. Immeral: [████████··] 18/22 HP                  │
│    6. Laucian: [██████████] 28/28 HP                  │
│                                                        │
│  COMBAT LOG:                                           │
│    Ellyjobell attacks Orc!                            │
│    Orc takes 8 damage                                 │
│    Vistr casts Magic Missile                          │
│    ...                                                │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### APRÈS l'ajout
```
┌──────────────────────────────────────────────────────────────────────────┐
│                    DUNGEON EXPLORATION                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PARTY STATUS:              │  MONSTER STATUS:                          │
│    1. Ellyjobell: [████···]│    Orc: [██████··] 12/18                 │
│    2. Vistr: [██████████]  │    Goblin: [████····] 4/10               │
│    3. Patrin: [████······] │    Orc Shaman: [██████] 15/15            │
│    4. Trym: [██████████]   │    Wolf: [████████] 8/8                  │
│    5. Immeral: [████████··]│    Wolf: [██████··] 6/8                  │
│    6. Laucian: [██████████]│    Kobold: [████████] 5/5                │
│                             │                                           │
├─────────────────────────────┴───────────────────────────────────────────┤
│  COMBAT LOG:                                                             │
│    Ellyjobell attacks Orc!                                              │
│    Orc takes 8 damage                                                   │
│    Vistr casts Magic Missile                                            │
│    ...                                                                  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Caractéristiques de l'Implémentation

### 1. Division de l'Écran
- L'écran est divisé en **deux colonnes égales**
- **Colonne gauche** : PARTY STATUS (personnages du joueur)
- **Colonne droite** : MONSTER STATUS (ennemis en combat)

### 2. Hauteur Synchronisée
- La section MONSTER STATUS a la **même hauteur** que PARTY STATUS
- Le COMBAT LOG commence juste en dessous, évitant tout débordement

### 3. Colonnes Multiples pour les Monstres
Si le nombre de monstres dépasse la hauteur disponible, ils sont affichés sur **plusieurs colonnes** (max 2) :

```
MONSTER STATUS:
┌──────────────────┬──────────────────┐
│ Orc: [████]      │ Kobold: [████]   │
│ Goblin: [██]     │ Skeleton: [███]  │
│ Wolf: [███]      │ Zombie: [██]     │
│ Orc: [████]      │ Rat: [█]         │
└──────────────────┴──────────────────┘
```

### 4. Affichage Conditionnel
- La fenêtre MONSTER STATUS s'affiche **uniquement en combat**
- Vérifie l'existence de `self.dungeon_state['monsters']`
- Affiche les monstres vivants (`alive_monsters`) en priorité

### 5. Barres de Vie Colorées
Mêmes couleurs que PARTY STATUS :
- 🟢 **Vert** : HP > 66%
- 🟡 **Jaune** : 33% < HP ≤ 66%
- 🔴 **Rouge** : HP ≤ 33%

### 6. Format d'Affichage Compact
```
NomDuMonstre: [████████] HP_actuel/HP_max
```
- Nom tronqué à 15 caractères pour économiser l'espace
- Barre de vie de 8 caractères (vs 10 pour les personnages)

---

## Détails Techniques

### Calcul des Colonnes
```python
# Division de l'écran
party_col_start = 2
party_col_width = (cols - 4) // 2
monster_col_start = party_col_start + party_col_width + 2
monster_col_width = cols - monster_col_start - 2
```

### Gestion des Monstres par Colonne
```python
# Nombre de monstres par colonne
max_monster_rows = party_height - 1  # -1 pour le header
monsters_per_col = max(6, max_monster_rows)

# Division en colonnes (max 2)
num_cols = (len(monsters) + monsters_per_col - 1) // monsters_per_col
num_cols = min(num_cols, 2)
```

### Boucle d'Affichage
```python
for col_idx in range(num_cols):
    start_idx = col_idx * monsters_per_col
    end_idx = min(start_idx + monsters_per_col, len(monsters))
    col_monsters = monsters[start_idx:end_idx]
    
    for monster in col_monsters:
        # Affichage du monstre...
```

---

## Avantages

### ✅ Visibilité en Temps Réel
- Le joueur voit **instantanément** l'état de tous les ennemis
- Plus besoin de parcourir le COMBAT LOG pour savoir qui est encore vivant

### ✅ Prise de Décision Tactique
- Identifie rapidement les ennemis faibles (presque morts)
- Repère les ennemis dangereux (pleine santé)
- Aide à prioriser les cibles

### ✅ Immersion Améliorée
- Affichage symétrique : party vs monsters
- Barres de vie colorées pour un feedback visuel immédiat
- Design cohérent avec le reste de l'interface ncurses

### ✅ Gestion Optimale de l'Espace
- Pas de débordement sur le COMBAT LOG
- Colonnes multiples pour les grandes rencontres (jusqu'à 12 monstres visibles)
- S'adapte automatiquement à la taille de la fenêtre

---

## Exemples de Rencontres

### Petite Rencontre (1-3 monstres)
```
PARTY STATUS:        │  MONSTER STATUS:
  1. Hero: [████]    │    Goblin: [██]
  2. Mage: [████]    │    Wolf: [███]
  3. Rogue: [███]    │
```

### Rencontre Moyenne (4-6 monstres)
```
PARTY STATUS:        │  MONSTER STATUS:
  1. Hero: [████]    │    Orc: [████]
  2. Mage: [████]    │    Orc: [███]
  3. Rogue: [███]    │    Goblin: [██]
  4. Cleric: [████]  │    Wolf: [███]
  5. Fighter: [███]  │    Kobold: [█]
  6. Ranger: [████]  │    Rat: [█]
```

### Grande Rencontre (7-12 monstres - 2 colonnes)
```
PARTY STATUS:        │  MONSTER STATUS:
  1. Hero: [████]    │    Orc: [████]    Zombie: [██]
  2. Mage: [████]    │    Orc: [███]     Skeleton: [█]
  3. Rogue: [███]    │    Goblin: [██]   Kobold: [█]
  4. Cleric: [████]  │    Wolf: [███]    Rat: [█]
  5. Fighter: [███]  │    Wolf: [██]     Rat: [█]
  6. Ranger: [████]  │    Kobold: [█]    Spider: [█]
```

---

## Fichiers Modifiés

- `/Users/display/PycharmProjects/DnD-5th-Edition-API/main_ncurses.py`
  - Fonction `draw_dungeon_explore()` (lignes ~471-570)

---

## Compatibilité

- ✅ Compatible avec toutes les tailles de terminal (minimum 80x24)
- ✅ Fonctionne avec le système de combat existant
- ✅ S'adapte dynamiquement au nombre de monstres
- ✅ Ne modifie pas la logique de combat (uniquement l'affichage)

---

## Notes de Développement

### Pourquoi 2 Colonnes Maximum ?
- Au-delà de 2 colonnes, le texte devient illisible (noms tronqués)
- Avec 2 colonnes, on peut afficher jusqu'à **12 monstres** sans débordement
- Les rencontres avec plus de 12 ennemis sont rares en D&D 5e

### Pourquoi une Barre de 8 Caractères ?
- Économise de l'espace pour les colonnes multiples
- Reste lisible et proportionnelle
- Cohérente avec les standards d'affichage ncurses

### Gestion des Noms Longs
```python
monster_name = monster.name if hasattr(monster, 'name') else str(monster)
monster_info = f"{monster_name[:15]}: ..."  # Tronqué à 15 chars
```

---

## Test de la Fonctionnalité

### Scénario 1 : Exploration Sans Combat
```bash
python main_ncurses.py
# Sélectionner "Edge of Town" → "Explore Dungeon"
# Avant le combat, seul PARTY STATUS s'affiche
```

### Scénario 2 : Combat avec 3 Monstres
```bash
# Lancer un combat (appuyer sur Enter)
# MONSTER STATUS s'affiche avec 3 ennemis dans une colonne
```

### Scénario 3 : Combat avec 10 Monstres
```bash
# Lancer un combat de niveau élevé
# MONSTER STATUS s'affiche avec 2 colonnes de 5 monstres chacune
```

---

**Date d'Implémentation :** 1 janvier 2026

**Version :** main_ncurses.py v2 (migration dnd-5e-core)

