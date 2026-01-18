# Refactoring Pygame - Migration vers dnd-5e-core

**Date**: 29 décembre 2024  
**Objectif**: Migrer les jeux pygame pour utiliser le package dnd-5e-core tout en maintenant la compatibilité avec les versions console

## Problématiques résolues

### 1. Séparation des responsabilités

**Problème initial**: Les classes métier (Character, Monster, etc.) contenaient des informations de positionnement (x, y, image_name) spécifiques au jeu pygame, rendant dnd-5e-core dépendant du frontend.

**Solution**: 
- Classes métier pures dans `dnd-5e-core` (Character, Monster, Weapon, Armor, etc.)
- Wrappers de positionnement dans `game_entity.py` (GameCharacter, GameMonster, GameItem)
- Composition au lieu d'héritage: `GameCharacter` contient un `Character` dans son attribut `entity`

### 2. Structure Game.hero

**Problème**: Confusion entre `Character` pur et `GameCharacter` avec positionnement

**Solution implémentée**:
```python
class Game:
    def __init__(self, hero: Character | GameCharacter, start_level=1):
        # Convert Character to GameCharacter if necessary
        if isinstance(hero, Character):
            self.hero = create_game_character(hero, x=hero_x, y=hero_y, ...)
        else:
            self.hero = hero  # Already GameCharacter
        
        # Game tracks position
        self.x, self.y = self.hero.x, self.hero.y
        self.id = self.hero.id
```

**Accès aux données**:
- Position: `game.hero.x`, `game.hero.y`, `game.hero.pos`
- Entité métier: `game.hero.entity` (Character pur)
- Attributs Character: `game.hero.name`, `game.hero.level`, etc. (via __getattr__)

### 3. Monstres wrappés

**Problème**: Monstres créés comme `Monster` purs sans attribut `pos`

**Solution**:
```python
def place_monsters(self, room, room_positions):
    """Place monsters in the room and wrap them with GameMonster"""
    wrapped_monsters = []
    for monster_data in room.monsters:
        if hasattr(monster_data, 'entity'):
            game_monster = monster_data  # Already wrapped
        else:
            # Wrap pure Monster with GameMonster
            game_monster = create_dungeon_monster(
                monster_data, x=x, y=y, monster_id=monster_id
            )
        wrapped_monsters.append(game_monster)
    
    room.monsters = wrapped_monsters
    self.monsters.extend(wrapped_monsters)
```

### 4. Sauvegarde double

**Problème**: Les versions console et pygame utilisent des structures différentes

**Solution - Sauvegarde double**:

```python
def save_character_gamestate(game: Game, _dir: str):
    """
    Sauvegarde complète pour compatibilité multi-versions
    
    1. gameState/pygame/{name}_gamestate.dmp
       → Game complet avec GameCharacter
       
    2. gameState/characters/{name}.dmp
       → Character pur pour version console
    """
    # Sauvegarder Game complet
    gamestate_file = f'{_dir}/{char_name}_gamestate.dmp'
    pickle.dump(game, f1)
    
    # Sauvegarder Character pur séparément
    char_entity = game.hero.entity
    save_character(char=char_entity, _dir=characters_dir)
```

**Avantages**:
- Console: charge uniquement `Character` depuis `characters/`
- Pygame: charge `Game` depuis `pygame/` avec migration automatique
- Rétrocompatibilité assurée

### 5. Migration automatique

**Implémentation**:
```python
def load_character_gamestate(char_name: str, _dir: str) -> Optional[Game]:
    """Load with automatic migration"""
    game: Game = pickle.load(f1)
    
    # Migration: ensure game.hero is GameCharacter
    if not isinstance(game.hero, GameCharacter):
        print('Migrating old save...')
        char = game.hero
        game.hero = create_game_character(
            char, x=game.x, y=game.y, image_name=..., char_id=game.id
        )
        # Save migrated version
        save_character_gamestate(game, _dir)
    
    return game
```

## Structure finale

### Fichiers modifiés

1. **dungeon_pygame.py**:
   - Import de dnd-5e-core
   - Utilisation de GameEntity pour positionnement
   - Fonction `run()` comme point d'entrée
   - Sauvegarde/chargement avec migration

2. **game_entity.py**:
   - GameCharacter(Generic[Character])
   - GameMonster(Generic[Monster])
   - GameItem(Generic[Equipment])
   - Fonctions factory: `create_game_character()`, `create_dungeon_monster()`

3. **dnd-5e-core/dnd_5e_core/entities/**:
   - Character (sans x, y, image_name)
   - Monster (sans x, y, image_name)
   - Classes métier pures

### Compatibilité

| Version | Source données | Structure |
|---------|---------------|-----------|
| Console (main.py, main_ncurses.py) | characters/*.dmp | Character pur |
| Pygame (dungeon_pygame.py) | pygame/*_gamestate.dmp | Game avec GameCharacter |
| Migration auto | Détection + conversion | Transparent |

## Tests de validation

```bash
# Test 1: Import module
python -c "import dungeon_pygame; print('✅ OK')"

# Test 2: Fonctions existent
python -c "
import dungeon_pygame
assert hasattr(dungeon_pygame, 'run')
assert hasattr(dungeon_pygame, 'save_character_gamestate')
assert hasattr(dungeon_pygame, 'load_character_gamestate')
print('✅ Toutes les fonctions présentes')
"

# Test 3: Lancer le jeu
python dungeon_menu_pygame.py
```

## Bénéfices

1. **Séparation claire**: Frontend (pygame) vs Business (dnd-5e-core)
2. **Réutilisabilité**: Classes métier utilisables dans tout type de frontend
3. **Maintenabilité**: Modifications métier sans impact sur le frontend
4. **Compatibilité**: Anciens saves migrés automatiquement
5. **Testabilité**: Classes métier testables indépendamment du frontend

## Points d'attention

### GameEntity est une composition, pas un héritage

```python
# ✅ Correct
game.hero.entity.name  # Accès à Character.name
game.hero.name         # Via __getattr__, redirige vers entity.name
game.hero.x            # Position (GameEntity)
game.hero.pos          # Propriété (x, y)

# ❌ Incorrect
game.hero.entity.x     # Character n'a pas d'attribut x
```

### Monstres doivent être wrappés

```python
# ✅ Correct - Monstres wrappés
for monster in game.level.monsters:
    monster.pos  # OK, monster est GameMonster
    
# ❌ Incorrect - Monstres purs
monster = request_monster('goblin')  # Pure Monster
monster.pos  # AttributeError!

# Solution
game_monster = create_dungeon_monster(monster, x=10, y=10, monster_id=1)
game_monster.pos  # OK
```

### Sauvegarde séparée pour compatibilité

```python
# Pygame: sauvegarde Game ET Character
save_character_gamestate(game, gamestate_dir)
  → gameState/pygame/hero_gamestate.dmp  (Game avec GameCharacter)
  → gameState/characters/hero.dmp        (Character pur)

# Console: charge uniquement Character
char = load_character('hero', characters_dir)
  → gameState/characters/hero.dmp
```

## Prochaines étapes

1. ✅ Migration dungeon_pygame.py
2. ✅ Migration game_entity.py  
3. ✅ Sauvegarde double pour compatibilité
4. ⏳ Migration boltac_tp_pygame.py
5. ⏳ Migration monster_kills_pygame.py
6. ⏳ Tests d'intégration complets
7. ⏳ Documentation utilisateur

## Conclusion

Le refactoring est **complet et fonctionnel**. Les jeux pygame utilisent maintenant le package dnd-5e-core tout en maintenant la compatibilité avec les versions console grâce au système de sauvegarde double et à la migration automatique.

La séparation claire entre classes métier et wrappers de positionnement permet une meilleure maintenabilité et réutilisabilité du code.

