# Migration Pygame vers dnd-5e-core - Session 2024-12-29

## Contexte

Migration des jeux pygame (dungeon_pygame.py, boltac_tp_pygame.py, monster_kills_pygame.py) pour utiliser le package dnd-5e-core au lieu de dao_classes.py.

**Objectif**: Séparer les classes métier du frontend pygame tout en maintenant la compatibilité avec les versions console.

## Problèmes rencontrés et solutions

### Problème 1: Classes métier avec attributs de positionnement

**Erreur initiale**:
```python
class Character:
    def __init__(self, id, x, y, image_name, ...):  # ❌ Couplage frontend
        self.x = x
        self.y = y
        self.image_name = image_name
```

**Solution - Composition via GameEntity**:
```python
# dnd-5e-core: Classes métier pures
class Character:
    def __init__(self, name, race, class_type, ...):  # ✅ Pur métier
        self.name = name
        self.race = race

# game_entity.py: Wrapper de positionnement
class GameCharacter(GameEntity[Character]):
    def __init__(self, entity: Character, x, y, image_name, char_id):
        super().__init__(entity, x, y, old_x=x, old_y=y, image_name=image_name, entity_id=char_id)
```

### Problème 2: Structure game.hero ambiguë

**Erreur**:
```
AttributeError: 'Character' object has no attribute 'pos'
```

**Cause**: Confusion entre `Character` pur et `GameCharacter` avec positionnement

**Solution - Conversion automatique dans Game.__init__**:
```python
class Game:
    def __init__(self, hero: Character | GameCharacter, start_level=1):
        # ...
        if isinstance(hero, Character):
            # Convert to GameCharacter
            from main import get_char_image
            image_name = get_char_image(hero.class_type)
            self.hero = create_game_character(hero, x=hero_x, y=hero_y, image_name=image_name, char_id=1)
        else:
            # Already GameCharacter
            self.hero = hero
            self.hero.x, self.hero.y = hero_x, hero_y
        
        # Game position tracking (MUST be before update_visible_tiles)
        self.x, self.y = self.hero.x, self.hero.y
        self.id = self.hero.id
```

### Problème 3: Monstres non wrappés

**Erreur**:
```
AttributeError: 'Monster' object has no attribute 'pos'
```

**Cause**: Monstres créés comme `Monster` purs dans `load_maze()` puis ajoutés à `self.monsters` sans wrapping

**Solution - Wrapping dans place_monsters**:
```python
# AVANT (incorrect)
def load_maze(self, level):
    monsters: List[Monster] = []
    for monster_name in monsters_in_room:
        monster = request_monster(monster_name)
        monsters.append(monster)  # Monster pur
    
    if monsters:
        self.monsters += monsters  # ❌ Pas de pos!
    
    room = Room(..., monsters=monsters)

# APRÈS (correct)
def load_maze(self, level):
    monsters: List[Monster] = []
    for monster_name in monsters_in_room:
        monster = request_monster(monster_name)
        monsters.append(monster)  # Monster pur OK ici
    
    # Note: wrapping fait par place_monsters()
    room = Room(..., monsters=monsters)

def place_monsters(self, room, room_positions):
    """Wrap monsters with GameMonster"""
    wrapped_monsters = []
    monster_id_offset = len(self.monsters)
    
    for i, monster_data in enumerate(room.monsters):
        if hasattr(monster_data, 'entity'):
            game_monster = monster_data  # Already wrapped
        else:
            monster_id = monster_id_offset + i + 1
            game_monster = create_dungeon_monster(monster_data, x=x, y=y, monster_id=monster_id)
        wrapped_monsters.append(game_monster)
    
    room.monsters = wrapped_monsters
    self.monsters.extend(wrapped_monsters)  # ✅ Tous wrappés!
```

### Problème 4: can_move() avec mauvais paramètres

**Erreur**:
```
TypeError: Game.can_move() got an unexpected keyword argument 'char'
```

**Solution**:
```python
# Signature correcte
def can_move(self, dir: tuple) -> bool:
    dx, dy = dir
    x, y = self.hero.x + dx, self.hero.y + dy  # Utilise toujours self.hero
    # ...

# Appels corrigés
elif game.can_move(dir=UP):  # ✅ Sans char=game.hero
    handle_combat(...)
```

### Problème 5: Compatibilité console vs pygame

**Problématique**: 
- Console: charge `Character` pur depuis `characters/*.dmp`
- Pygame: charge `Game` avec `GameCharacter` depuis `pygame/*_gamestate.dmp`

**Solution - Sauvegarde double**:
```python
def save_character_gamestate(game: Game, _dir: str):
    """
    Double sauvegarde pour compatibilité:
    1. Game complet (pygame) dans gameState/pygame/
    2. Character pur (console) dans gameState/characters/
    """
    char_name = game.hero.name
    
    # 1. Sauvegarder Game complet pour pygame
    gamestate_file = f'{_dir}/{char_name}_gamestate.dmp'
    with open(gamestate_file, 'wb') as f1:
        pickle.dump(game, f1)
    
    # 2. Sauvegarder Character pur pour console
    characters_dir = os.path.join(os.path.dirname(_dir), 'characters')
    if os.path.exists(characters_dir):
        char_entity = game.hero.entity  # Extraire Character pur
        save_character(char=char_entity, _dir=characters_dir)
```

### Problème 6: Migration des anciens saves

**Solution - Migration automatique au chargement**:
```python
def load_character_gamestate(char_name: str, _dir: str) -> Optional[Game]:
    """Load with automatic migration from old format"""
    gs_filename = f'{_dir}/{char_name}_gamestate.dmp'
    if not os.path.exists(gs_filename):
        return None
    
    game: Game = pickle.load(f1)
    
    # Migration: ensure game.hero is GameCharacter
    if not isinstance(game.hero, GameCharacter):
        print(f'  └─ Migrating old save: converting Character to GameCharacter')
        char = game.hero
        image_name = get_char_image(char.class_type)
        
        game.hero = create_game_character(
            char, x=game.x, y=game.y, image_name=image_name, char_id=game.id
        )
        
        # Update game position references
        game.x, game.y = game.hero.x, game.hero.y
        game.id = game.hero.id
        
        # Save migrated version
        save_character_gamestate(game, _dir)
    
    return game
```

## Changements de structure

### Avant (dao_classes.py)

```python
# dao_classes.py - Tout couplé
class Sprite:
    def __init__(self, id, x, y, old_x, old_y, image_name):
        self.id = id
        self.x = x
        # ...

class Character(Sprite):  # ❌ Héritage = couplage
    def __init__(self, id, x, y, image_name, name, race, ...):
        super().__init__(id, x, y, x, y, image_name)
        self.name = name
        # ...

class Monster(Sprite):  # ❌ Héritage = couplage
    # ...
```

### Après (dnd-5e-core + game_entity.py)

```python
# dnd-5e-core/dnd_5e_core/entities/character.py - Métier pur
class Character:
    def __init__(self, name, race, class_type, abilities, ...):
        self.name = name
        self.race = race
        # Pas de x, y, image_name

# game_entity.py - Frontend pygame
class GameEntity(Generic[T]):
    def __init__(self, entity: T, x, y, old_x, old_y, image_name, entity_id):
        self.entity = entity  # ✅ Composition
        self.x = x
        self.y = y
        # ...
    
    def __getattr__(self, name):
        # Délégation vers entity
        return getattr(self.entity, name)

class GameCharacter(GameEntity[Character]):
    pass

class GameMonster(GameEntity[Monster]):
    pass
```

## Fichiers modifiés

### 1. dungeon_pygame.py

**Imports**:
```python
# Avant
from dao_classes import Character, Monster, Weapon, Armor

# Après
from dnd_5e_core.entities import Character, Monster
from dnd_5e_core.equipment import Weapon, Armor
from game_entity import GameCharacter, GameMonster, create_game_character, create_dungeon_monster
```

**Game.__init__**:
- Ajout conversion Character → GameCharacter
- Initialisation self.x, self.y, self.id AVANT update_visible_tiles()
- Ajout propriété @property def pos(self)

**Level.place_monsters**:
- Wrapping Monster → GameMonster
- Positionnement x, y

**Nouvelles fonctions**:
- `save_character_gamestate()` - Sauvegarde double
- `load_character_gamestate()` - Chargement avec migration
- `run()` - Point d'entrée

### 2. game_entity.py

**Nouvelles classes**:
- `GameEntity[T]` - Classe générique de base
- `GameCharacter` - Wrapper pour Character
- `GameMonster` - Wrapper pour Monster  
- `GameItem` - Wrapper pour Equipment

**Fonctions factory**:
- `create_game_character()`
- `create_dungeon_monster()`
- `create_game_weapon()`
- `create_dungeon_item()`

### 3. dungeon_menu_pygame.py

**Correction**:
```python
# Avant
option = self.font.render(f"{game.entity.class_type}", ...)  # ❌

# Après
option = self.font.render(f"{game.hero.entity.class_type}", ...)  # ✅
```

## Validation

### Tests unitaires

```bash
# Test 1: Import
python -c "import dungeon_pygame; print('✅ OK')"

# Test 2: Fonctions existent
python -c "
import dungeon_pygame
assert hasattr(dungeon_pygame, 'run')
assert hasattr(dungeon_pygame, 'save_character_gamestate')
assert hasattr(dungeon_pygame, 'load_character_gamestate')
assert hasattr(dungeon_pygame, 'Game')
assert hasattr(dungeon_pygame, 'Level')
print('✅ Toutes les fonctions présentes')
"
```

### Tests d'intégration

```bash
# Lancer le menu pygame
python dungeon_menu_pygame.py

# Tester:
# 1. Charger un personnage
# 2. Entrer dans le donjon
# 3. Se déplacer
# 4. Combat
# 5. Sauvegarder et quitter
# 6. Recharger et vérifier état
```

## Bénéfices

1. **Séparation des responsabilités**:
   - dnd-5e-core: Logique métier pure
   - game_entity.py: Positionnement pygame
   - dungeon_pygame.py: Interface pygame

2. **Réutilisabilité**:
   - Classes métier utilisables dans n'importe quel frontend
   - Console, ncurses, pygame, Qt, web...

3. **Maintenabilité**:
   - Modifications métier sans impact frontend
   - Tests unitaires du métier sans pygame

4. **Compatibilité**:
   - Sauvegarde double (console + pygame)
   - Migration automatique anciens saves

## Prochaines étapes

1. ✅ Migration dungeon_pygame.py
2. ⏳ Migration boltac_tp_pygame.py
3. ⏳ Migration monster_kills_pygame.py
4. ⏳ Tests automatisés
5. ⏳ Documentation utilisateur

## Conclusion

**Migration réussie** ✅

Le jeu pygame utilise maintenant le package dnd-5e-core avec une séparation claire entre classes métier et wrappers de positionnement. La compatibilité avec les versions console est assurée par le système de sauvegarde double et la migration automatique.

La structure finale est plus maintenable, testable et réutilisable.

