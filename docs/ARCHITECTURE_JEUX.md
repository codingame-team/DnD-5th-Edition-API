# 🎮 Architecture des Jeux - DnD-5th-Edition-API

**Date:** 23 décembre 2025  
**Statut:** ✅ **DOCUMENTATION CLARIFIÉE**

---

## 🎯 Structure Actuelle des Jeux

### Jeux Utilisant dnd-5e-core

#### 1. **main.py** - Version Console Principale
- **Description:** Version console complète avec toutes les règles D&D 5e
- **Dépendances:** ✅ Utilise `dnd_5e_core`
- **Fonctionnalités:**
  - Création de personnages complète
  - Système de combat complet
  - Gestion de groupe (party)
  - Castle (Tavern, Inn, Temple, Training, Trading Post)
  - Exploration de donjons
- **Fichier:** `main.py`

#### 2. **main_ncurses.py** - Version Ncurses
- **Description:** Déclinaison ncurses de main.py
- **Dépendances:** ✅ Utilise `dnd_5e_core`
- **Interface:** Ncurses (terminal textuel)
- **Fonctionnalités:** Identiques à main.py mais avec interface ncurses
- **Variantes:**
  - `main_ncurses.py` - Version de base
  - `main_ncurses_v2.py` - Version migrée simple
  - `main_ncurses_v2_FULL.py` - Version complète (2783 lignes)

#### 3. **Suite Pygame** - Jeu Complet avec Interface Graphique
Ensemble de scripts formant un jeu pygame complet :

##### a) **dungeon_pygame.py**
- Exploration de donjons avec vue 2D
- Système de combat graphique
- Gestion des sorts et actions
- **Dépendances:** ✅ Utilise `dnd_5e_core`

##### b) **dungeon_menu_pygame.py**
- Menu principal du jeu pygame
- Sélection de personnages
- Navigation vers dungeon ou trading post
- **Dépendances:** ✅ Utilise `dnd_5e_core`
- **Import confirmé:**
  ```python
  from dnd_5e_core.entities import Character
  from dnd_5e_core.ui import cprint, Color, color
  ```

##### c) **boltac_tp_pygame.py**
- Trading Post (magasin de Boltac)
- Achat/vente d'équipement
- Gestion de l'inventaire graphique
- **Dépendances:** ✅ Utilise `dnd_5e_core`
- **Fichier actuel visible:** Oui, avec imports dnd-5e-core

##### d) **monster_kills_pygame.py**
- Statistiques de monstres tués
- Interface graphique pour visualiser les kills
- **Dépendances:** ✅ Utilise `dnd_5e_core`

**Note:** Ces 4 fichiers forment un **jeu pygame unifié** avec menu, exploration, combat, shop et stats.

### Jeux Indépendants (Sans dnd-5e-core)

#### 4. **dungeon_tk.py** - Version Tkinter
- **Description:** Jeu avec interface Tkinter
- **Dépendances:** ❌ **N'utilise PAS dnd-5e-core**
- **Règles:** Règles D&D simplifiées et personnalisées
- **Raison:** Conçu comme un jeu autonome avec mécanique simplifiée
- **Fonctionnalités:**
  - Arena basique
  - Règles D&D simplifiées
  - Un seul personnage
  - Exploration multi-niveaux
  - Collecte de trésors

---

## 📊 Résumé des Dépendances

| Jeu | Utilise dnd-5e-core | Interface | Complexité |
|-----|---------------------|-----------|------------|
| **main.py** | ✅ Oui | Console | Complète |
| **main_ncurses.py** | ✅ Oui | Ncurses | Complète |
| **dungeon_pygame.py** | ✅ Oui | Pygame | Complète |
| **dungeon_menu_pygame.py** | ✅ Oui | Pygame | Menu |
| **boltac_tp_pygame.py** | ✅ Oui | Pygame | Shop |
| **monster_kills_pygame.py** | ✅ Oui | Pygame | Stats |
| **dungeon_tk.py** | ❌ Non | Tkinter | Simplifiée |

### Total
- **Jeux avec dnd-5e-core:** 6 fichiers (formant 3 jeux distincts)
- **Jeux sans dnd-5e-core:** 1 fichier

---

## 🎮 Organisation des Jeux

### Groupe 1: Console/Ncurses
```
main.py ────────┐
                ├─── Même logique, interfaces différentes
main_ncurses.py ┘
```

### Groupe 2: Suite Pygame
```
dungeon_menu_pygame.py (Menu principal)
    ├─── dungeon_pygame.py (Exploration/Combat)
    ├─── boltac_tp_pygame.py (Trading Post)
    └─── monster_kills_pygame.py (Statistiques)
```

### Groupe 3: Tkinter (Standalone)
```
dungeon_tk.py (Jeu autonome, règles simplifiées)
```

---

## 📁 Structure de Migration

### Fichiers Migrés vers dnd-5e-core

Tous les fichiers marqués ✅ utilisent les imports suivants :

```python
from dnd_5e_core.entities import Character, Monster, Sprite
from dnd_5e_core.equipment import Weapon, Armor, HealingPotion, Equipment, Potion
from dnd_5e_core.spells import Spell, SpellCaster
from dnd_5e_core.combat import Action, ActionType, SpecialAbility, Damage
from dnd_5e_core.races import Race, SubRace, Trait, Language
from dnd_5e_core.classes import ClassType, Proficiency, Feature, Level
from dnd_5e_core.abilities import Abilities, AbilityType
from dnd_5e_core.mechanics import DamageDice
from dnd_5e_core.ui import cprint, Color, color
```

### Fichiers Non Migrés

**dungeon_tk.py** utilise ses propres classes simplifiées :
- Pas de dépendance externe complexe
- Logique de jeu autonome
- Règles D&D personnalisées et allégées

---

## 🔧 Utilisation de populate_functions.py

### Avant Migration Collections (Décembre 2024)
```python
from populate_functions import populate

# Charge depuis collections locales
monsters = populate('monsters', 'results')
```

### Après Migration Collections (Décembre 2025)
```python
from populate_functions import populate

# Charge depuis dnd-5e-core/collections (avec fallback)
monsters = populate('monsters', 'results')
```

**Impact:** Tous les jeux bénéficient automatiquement de la migration collections sans modification de code !

---

## 📝 Documentation de Migration

### Emplacement
Toute la documentation de migration se trouve dans :

```
DnD-5th-Edition-API/docs/archive/
├── migration/
│   ├── MIGRATION_COMPLETE_ALL.md
│   ├── MIGRATION_FINAL_COMPLETE.md
│   ├── DATA_MIGRATION_COMPLETE.md
│   └── COLLECTIONS_MIGRATION_SUMMARY.md
├── fixes/
│   ├── FIX_COMBAT_MESSAGE_SHIFT.md
│   ├── FIX_NO_ITEMS_COMPLETE.md
│   └── ... (10 fichiers)
└── implementations/
    ├── NCURSES_CONVERSION_COMPLETE.md
    ├── CHARACTER_INVENTORY_MANAGEMENT.md
    └── ... (8 fichiers)
```

### Documents Récents (Décembre 2025)
- **dnd-5e-core/docs/COLLECTIONS_MIGRATION.md** - Migration collections
- **dnd-5e-core/docs/COLLECTIONS_COMPLETE.md** - Résumé migration
- **dnd-5e-core/docs/PROJETS_ADAPTATION.md** - Adaptation projets
- **dnd-5e-core/docs/CONTEXTE_PROJETS.md** - Contexte complet

---

## ✅ État Actuel (Décembre 2025)

### Migrations Terminées
- [x] Code vers dnd-5e-core (Décembre 2024)
- [x] Données JSON vers dnd-5e-core (Décembre 2024)
- [x] Collections vers dnd-5e-core (Décembre 2025)
- [x] populate_functions.py adapté (Décembre 2025)

### Jeux Fonctionnels
- [x] main.py avec dnd-5e-core
- [x] main_ncurses.py avec dnd-5e-core
- [x] Suite pygame avec dnd-5e-core
- [x] dungeon_tk.py (autonome, sans dnd-5e-core)

### Tests
- [x] Collections : 7/7 tests passés
- [x] populate() : 332 monstres, 319 sorts chargés
- [ ] Tests complets de tous les jeux (à faire)

---

## 🚀 Prochaines Actions

### Court Terme
1. Tester chaque jeu individuellement :
   - [ ] main.py
   - [ ] main_ncurses.py
   - [ ] dungeon_menu_pygame.py (suite complète)
   - [ ] dungeon_tk.py (vérifier qu'il reste autonome)

2. Vérifier les fallbacks :
   - [ ] Collections locales fonctionnent si dnd-5e-core absent
   - [ ] Comportement graceful en cas d'erreur

### Moyen Terme
- [ ] Documentation des règles simplifiées de dungeon_tk.py
- [ ] Tests unitaires pour chaque jeu
- [ ] Guide de lancement pour chaque interface

---

## 🎯 Clarifications Importantes

### Pourquoi dungeon_tk.py N'utilise Pas dnd-5e-core ?

**Réponse:** Par design architectural
- Conçu comme un **jeu léger et autonome**
- Utilise des **règles D&D simplifiées personnalisées**
- Pas besoin de la complexité complète de D&D 5e
- Plus facile à maintenir et distribuer indépendamment

### La Suite Pygame Est-elle Un Seul Jeu ?

**Réponse:** Oui
- **dungeon_menu_pygame.py** = Menu principal
- **dungeon_pygame.py** = Module exploration/combat
- **boltac_tp_pygame.py** = Module trading post
- **monster_kills_pygame.py** = Module statistiques

Ces 4 fichiers forment un **jeu pygame complet** avec navigation entre les différents modules.

---

## 📖 Références

- **HISTORIQUE_DEVELOPPEMENT.md** - Historique complet des migrations
- **CHANGELOG.md** - Changements par version
- **dnd-5e-core/README.md** - Documentation du package core
- **docs/archive/** - Documentation de migration archivée

---

**Date de documentation:** 23 décembre 2025  
**Statut:** ✅ **ARCHITECTURE CLARIFIÉE ET DOCUMENTÉE**

