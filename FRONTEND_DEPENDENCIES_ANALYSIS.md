# Analyse des Dépendances - Frontends DnD-5th-Edition-API

**Date:** 6 janvier 2026

---

## 🎯 Objectif

Vérifier l'indépendance des frontends et factoriser les fonctions communes dans dnd-5e-core.

---

## 📊 Analyse des Imports

### 1. main_ncurses.py

```python
from main import (
    create_new_character,
    generate_random_character,
    display_character_sheet,
    menu_read_options,
    delete_character_prompt_ok,
    rename_character_prompt_ok,
    explore_dungeon,
    generate_encounter_levels,
    load_encounter_table,
    load_encounter_gold_table,
    load_xp_levels,
    generate_encounter
)
```

**Catégories:**
- **Gestion de personnages:** `create_new_character`, `generate_random_character`, `display_character_sheet`
- **UI/Prompts:** `menu_read_options`, `delete_character_prompt_ok`, `rename_character_prompt_ok`
- **Règles D&D 5e:** `generate_encounter_levels`, `load_encounter_table`, `generate_encounter`, `load_xp_levels`
- **Combat:** `explore_dungeon`

### 2. dungeon_pygame.py

```python
from main import (
    get_roster,
    save_character,
    load_xp_levels,
    load_character,
    get_char_image  # Import dynamique multiple fois
)
```

**Catégories:**
- **Persistence:** `get_roster`, `save_character`, `load_character`
- **Règles D&D 5e:** `load_xp_levels`
- **UI:** `get_char_image`

### 3. pyQTApp/wizardry.py

```python
from main import (
    load_party,
    save_character,
    save_party,
    load_character_collections,
    generate_random_character,
    display_character_sheet,
    get_roster
)
```

**Catégories:**
- **Persistence:** `load_party`, `save_party`, `save_character`, `get_roster`
- **Collections:** `load_character_collections`
- **Génération:** `generate_random_character`
- **Affichage:** `display_character_sheet`

---

## 🔍 Classification des Fonctions

### ✅ Fonctions à Migrer vers dnd-5e-core (Règles D&D 5e)

Ces fonctions implémentent les règles officielles de D&D 5e et devraient être dans le package:

1. **`load_xp_levels()`** - Table XP officielle D&D 5e
   - ✅ **DÉJÀ MIGRÉ** dans `dnd_5e_core.mechanics.experience.XP_LEVELS`

2. **`generate_encounter_levels()`** - Distribution de rencontres
   - ✅ **DÉJÀ MIGRÉ** dans `dnd_5e_core.mechanics.encounter_builder.generate_encounter_distribution()`

3. **`load_encounter_table()`** - Tables de rencontres
   - ✅ **DÉJÀ MIGRÉ** dans `dnd_5e_core.mechanics.encounter_builder.ENCOUNTER_TABLE`

4. **`generate_encounter()`** - Génération de rencontres
   - ✅ **DÉJÀ MIGRÉ** dans `dnd_5e_core.mechanics.encounter_builder.select_monsters_by_encounter_table()`

5. **`load_encounter_gold_table()`** - Récompenses
   - ⏳ **À MIGRER** - Règle D&D 5e pour les récompenses en or

6. **`load_character_collections()`** - Chargement des collections
   - ✅ **PARTIELLEMENT MIGRÉ** - Disponible via `dnd_5e_core.data`

7. **`generate_random_character()`** - Génération de personnages
   - ✅ **DÉJÀ MIGRÉ** dans `dnd_5e_core.data.loaders.simple_character_generator()`

### ⚠️ Fonctions Spécifiques au Projet (Garder dans main.py)

Ces fonctions sont spécifiques à l'application et ne font pas partie des règles D&D 5e:

1. **Persistence:**
   - `get_roster()` - Chargement des personnages sauvegardés
   - `save_character()` - Sauvegarde de personnages
   - `load_character()` - Chargement d'un personnage
   - `save_party()` - Sauvegarde du groupe
   - `load_party()` - Chargement du groupe

2. **UI/Affichage:**
   - `display_character_sheet()` - Affichage console
   - `menu_read_options()` - Gestion de menus
   - `delete_character_prompt_ok()` - Prompts de confirmation
   - `rename_character_prompt_ok()` - Prompts de confirmation
   - `get_char_image()` - Images pour pygame

3. **Logique Métier Spécifique:**
   - `create_new_character()` - Workflow complet de création
   - `explore_dungeon()` - Système de donjon spécifique

---

## 📝 Plan de Migration

### Phase 1: Migrer les Règles D&D 5e Manquantes

#### 1.1. Créer `gold_rewards.py` dans dnd-5e-core

```python
# dnd_5e_core/mechanics/gold_rewards.py

ENCOUNTER_GOLD_TABLE = {
    1: 50,
    2: 100,
    3: 150,
    4: 200,
    5: 250,
    # ... (à compléter depuis Encounter_Gold.csv)
}

def get_encounter_gold(encounter_level: int) -> int:
    """Get gold reward for encounter level"""
    return ENCOUNTER_GOLD_TABLE.get(encounter_level, 0)
```

#### 1.2. Améliorer `loaders.py`

Ajouter une version complète de `load_character_collections()` qui charge toutes les données:

```python
def load_character_collections():
    """Load all character creation data"""
    # Utiliser l'API D&D 5e ou les fichiers JSON
    races = load_all_races()
    subraces = load_all_subraces()
    classes = load_all_classes()
    spells = load_all_spells()
    # etc.
    return (races, subraces, classes, ...)
```

### Phase 2: Créer des Wrappers dans main.py

Pour maintenir la compatibilité, créer des wrappers dans main.py qui utilisent dnd-5e-core:

```python
# main.py

from dnd_5e_core.mechanics import (
    XP_LEVELS as load_xp_levels,
    generate_encounter_distribution as generate_encounter_levels,
    get_encounter_gold,
)
from dnd_5e_core.data import (
    simple_character_generator,
    load_monsters_database,
)

# Wrapper pour compatibilité
def generate_random_character(roster, races, subraces, classes, names, human_names, spells):
    """DEPRECATED: Use dnd_5e_core.data.simple_character_generator instead"""
    # Version simplifiée pour compatibilité
    return simple_character_generator(level=1)

# Marquer comme deprecated
import warnings
warnings.warn(
    "generate_random_character from main.py is deprecated. "
    "Use dnd_5e_core.data.simple_character_generator instead",
    DeprecationWarning,
    stacklevel=2
)
```

### Phase 3: Mettre à Jour les Frontends

#### Option A: Migration Complète (Recommandé)

Mettre à jour les frontends pour utiliser directement dnd-5e-core:

```python
# main_ncurses.py

# AVANT
from main import load_xp_levels, generate_encounter_levels

# APRÈS
from dnd_5e_core.mechanics import XP_LEVELS as load_xp_levels
from dnd_5e_core.mechanics.encounter_builder import generate_encounter_distribution as generate_encounter_levels
from main import (
    # Garder seulement les fonctions spécifiques au projet
    get_roster,
    save_character,
    display_character_sheet,
    menu_read_options,
    # etc.
)
```

#### Option B: Wrappers Transitoires

Garder les imports de main.py mais utiliser les wrappers qui pointent vers dnd-5e-core.

---

## 🎯 Recommandations

### Priorité 1: Fonctions de Règles D&D 5e

✅ **À FAIRE:**
1. Migrer `load_encounter_gold_table()` vers dnd-5e-core
2. Améliorer `load_character_collections()` dans dnd-5e-core
3. Créer wrappers deprecated dans main.py

### Priorité 2: Fonctions de Persistence

⚠️ **GARDER dans main.py:**
- Ce sont des fonctions spécifiques au projet
- Gèrent les fichiers .dmp et la structure du projet
- Ne font pas partie des règles D&D 5e

**Solution:** Créer un module `persistence.py` dans DnD-5th-Edition-API:

```python
# DnD-5th-Edition-API/persistence.py

def get_roster(characters_dir: str):
    """Load all saved characters"""
    # ... code existant

def save_character(char: Character, directory: str):
    """Save character to disk"""
    # ... code existant

def load_character(name: str, directory: str):
    """Load character from disk"""
    # ... code existant
```

Puis dans les frontends:
```python
from persistence import get_roster, save_character, load_character
```

### Priorité 3: Fonctions UI

⚠️ **GARDER dans main.py ou créer modules dédiés:**

```python
# DnD-5th-Edition-API/ui_helpers.py

def display_character_sheet(char):
    """Display character sheet in console"""
    # ... code existant

def menu_read_options(options):
    """Display menu and read choice"""
    # ... code existant
```

---

## 📊 Résumé

| Catégorie | Nombre | Action |
|-----------|--------|--------|
| Déjà migrées vers dnd-5e-core | 4 | ✅ Complet |
| À migrer vers dnd-5e-core | 2 | ⏳ À faire |
| Garder dans main.py (persistence) | 6 | ⚠️ Spécifique projet |
| Garder dans main.py (UI) | 5 | ⚠️ Spécifique projet |

---

## ✅ Actions Concrètes

### 1. Compléter dnd-5e-core

- [ ] Ajouter `dnd_5e_core/mechanics/gold_rewards.py`
- [ ] Améliorer `dnd_5e_core/data/loaders.py`
- [ ] Publier v0.1.7

### 2. Refactoriser DnD-5th-Edition-API

- [ ] Créer `persistence.py` pour les fonctions de sauvegarde
- [ ] Créer `ui_helpers.py` pour les fonctions d'affichage
- [ ] Créer wrappers deprecated dans main.py
- [ ] Mettre à jour les frontends pour utiliser les nouveaux modules

### 3. Documentation

- [ ] Documenter les fonctions deprecated
- [ ] Créer guide de migration pour les contributeurs
- [ ] Mettre à jour README avec la nouvelle structure

---

## 🎉 Avantages Attendus

### Pour dnd-5e-core
- ✅ Package plus complet
- ✅ Toutes les règles D&D 5e centralisées
- ✅ Utilisable pour d'autres projets

### Pour DnD-5th-Edition-API
- ✅ Code mieux organisé
- ✅ Séparation claire des responsabilités
- ✅ Modules réutilisables entre frontends
- ✅ Maintenance facilitée

### Pour les Contributeurs
- ✅ Comprendre facilement où ajouter du code
- ✅ Réutiliser les composants
- ✅ Tests plus faciles

---

**Date:** 6 janvier 2026  
**Status:** Analyse complète - Actions à entreprendre

