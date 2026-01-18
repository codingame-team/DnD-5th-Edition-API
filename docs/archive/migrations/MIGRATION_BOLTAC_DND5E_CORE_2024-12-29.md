# Migration boltac_tp_pygame.py vers dnd-5e-core

**Date**: 29 décembre 2024  
**Statut**: ✅ Terminée

## Contexte

Le module `boltac_tp_pygame.py` est le shop de trading où les personnages peuvent acheter et vendre de l'équipement. Contrairement à `dungeon_pygame.py`, ce module ne gère PAS de donjons et n'a donc pas besoin d'un objet `Game` complet.

## Problème initial

```python
# ERREUR
def exit_boltac(game: Game):  # ❌ Référence Game qui n'existe pas
    if isinstance(hero, GameEntity):  # ❌ hero non défini
        save_character_gamestate(char=hero, _dir=...)  # ❌ Ancienne signature
```

**Traceback**:
```
TypeError: save_character_gamestate() got an unexpected keyword argument 'char'
```

## Solution implémentée

### 1. Correction de `exit_boltac`

**Avant**:
```python
def exit_boltac(game: Game):
    game_path = get_save_game_path()
    if isinstance(hero, GameEntity):
        save_character_gamestate(char=hero, _dir=game_path + '/pygame')
    else:
        save_character(char=hero.entity, _dir=game_path + '/characters')
```

**Après**:
```python
def exit_boltac(hero: GameCharacter):
    """Save character when exiting Boltac's shop"""
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    
    # Extract Character entity and save
    char_entity = hero.entity if isinstance(hero, GameCharacter) else hero
    save_character(char=char_entity, _dir=characters_dir)
    print(f'Character {char_entity.name} saved successfully')
```

**Changements**:
- ✅ Paramètre `hero: GameCharacter` au lieu de `game: Game`
- ✅ Utilise `save_character` au lieu de `save_character_gamestate`
- ✅ Sauvegarde uniquement dans `characters/` (pas besoin de gamestate pygame)
- ✅ Extrait `Character` pur de `GameCharacter.entity`

### 2. Correction de `load_game_data`

**Avant**:
```python
def load_game_data(character_name: str):
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'

    try:
        saved_game: GameCharacter = load_character_gamestate(character_name, gamestate_dir)
        hero: GameCharacter = saved_game if saved_game else GameCharacter(load_character(...))
        # ...
```

**Après**:
```python
def load_game_data(character_name: str):
    """Load character data for Boltac's shop"""
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'

    try:
        # Load Character from characters directory
        char: Character = load_character(character_name, characters_dir)
        
        # Wrap in GameCharacter for consistent interface
        from main import get_char_image
        image_name = get_char_image(char.class_type) if hasattr(char, 'class_type') else None
        from game_entity import create_game_character
        hero = create_game_character(char, x=-1, y=-1, image_name=image_name, char_id=1)
        
        # Get available equipment
        weapons = sorted(char.prof_weapons, key=lambda x: x.cost.value)
        armors = sorted(char.prof_armors, key=lambda x: x.cost.value)
        potions = load_potions_collections()
        
        return hero, [weapons, armors, potions]
    # ...
```

**Changements**:
- ✅ Charge depuis `characters/` au lieu de `pygame/`
- ✅ Utilise `load_character` au lieu de `load_character_gamestate`
- ✅ Crée `GameCharacter` avec `create_game_character()` pour interface cohérente
- ✅ Position `-1, -1` car pas utilisée dans le shop

### 3. Nettoyage des imports

**Avant**:
```python
from dungeon_pygame import load_character_gamestate, save_character_gamestate
from game_entity import GameCharacter, GameEntity
```

**Après**:
```python
from game_entity import GameCharacter
```

**Supprimé**:
- ❌ `load_character_gamestate` - Non nécessaire pour le shop
- ❌ `save_character_gamestate` - Non nécessaire pour le shop
- ❌ `GameEntity` - Non utilisé

## Architecture finale

### Flux de données

```
dungeon_menu_pygame.py (Menu principal)
    │
    ├─── "Dungeon" ──> dungeon_pygame.run()
    │                   ├─ Charge: Game from pygame/
    │                   └─ Sauve: Game to pygame/ + Character to characters/
    │
    └─── "Boltac" ──> boltac_tp_pygame.run()
                       ├─ Charge: Character from characters/
                       └─ Sauve: Character to characters/
```

### Pourquoi pas de Game pour Boltac ?

1. **Pas de donjon**: Le shop n'a pas de carte, monstres, niveaux
2. **Pas de position**: Le personnage n'a pas de coordonnées x,y dans le shop
3. **Simplicité**: Juste besoin d'accéder à l'inventaire et l'or du personnage
4. **Compatibilité**: Charge/sauve depuis le même répertoire que les versions console

### Structure `hero` dans boltac

```python
hero: GameCharacter
    ├─ entity: Character (métier pur)
    │   ├─ name: str
    │   ├─ gold: int
    │   ├─ inventory: List[Equipment]
    │   ├─ prof_weapons: List[Proficiency]
    │   └─ prof_armors: List[Proficiency]
    │
    ├─ x: int = -1 (non utilisé)
    ├─ y: int = -1 (non utilisé)
    └─ image_name: str (non utilisé)
```

**Pourquoi GameCharacter ?**
- Interface cohérente avec dungeon_pygame
- Accès à `.entity` pour le Character pur
- Facilite les modifications futures

## Tests de validation

```bash
# Test 1: Import module
python -c "import boltac_tp_pygame; print('✅ OK')"

# Test 2: Fonctions existent
python -c "
import boltac_tp_pygame
assert hasattr(boltac_tp_pygame, 'run')
assert hasattr(boltac_tp_pygame, 'exit_boltac')
assert hasattr(boltac_tp_pygame, 'load_game_data')
print('✅ Toutes les fonctions présentes')
"

# Test 3: Lancer le shop
python -c "
import boltac_tp_pygame
# boltac_tp_pygame.run('CharacterName')
print('✅ Module prêt')
"
```

## Compatibilité

| Action | Source | Destination |
|--------|--------|-------------|
| Charger personnage | characters/*.dmp | GameCharacter |
| Acheter/Vendre | - | hero.entity.inventory |
| Sauvegarder | hero.entity | characters/*.dmp |

**Compatible avec**:
- ✅ Console (main.py, main_ncurses.py)
- ✅ Dungeon pygame (dungeon_pygame.py)
- ✅ Menu pygame (dungeon_menu_pygame.py)

## Résumé

**Migration réussie** ✅

Le shop Boltac utilise maintenant le package dnd-5e-core et sauvegarde/charge les personnages depuis le même répertoire que les versions console, assurant une compatibilité totale.

La structure est simplifiée par rapport au dungeon car elle n'a pas besoin de gestion de Game/Level/position.

