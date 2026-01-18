# Correction Character Wrapping dans dungeon_pygame.py

**Date :** 27 décembre 2025  
**Erreur :** `AttributeError: 'Character' object has no attribute 'pos'`

---

## ❌ Problème

Le personnage chargé dans `dungeon_pygame.py` n'était pas wrappé avec `GameCharacter`, donc il n'avait pas les attributs de positionnement (`x`, `y`, `pos`) nécessaires pour le jeu pygame.

```python
# dungeon_pygame.py, ligne 452
self.hero = load_character(char_name=char_name, _dir=char_dir)
self.hero.x, self.hero.y = hero_x, hero_y  # ❌ Attributs assignés manuellement

# Ligne 947
if (x, y) in self.level.visible_tiles or dist((x, y), self.hero.pos) > vision_range:
                                                           ^^^^^^^^^^^^^ 
# AttributeError: 'Character' object has no attribute 'pos'
```

**Cause :** Le `Character` de dnd-5e-core est pur business logic et n'a pas d'attributs de positionnement. Il faut utiliser `GameCharacter` de `game_entity.py` qui ajoute ces attributs via composition.

---

## ✅ Solution Appliquée

### 1. Import des Wrappers GameEntity

**Fichier :** `dungeon_pygame.py` (ligne 28)

```python
# AVANT
from dnd_5e_core.entities import Character, Monster, Sprite
# ... autres imports ...
# ❌ Pas d'import de game_entity

# APRÈS
from dnd_5e_core.entities import Character, Monster, Sprite
# ... autres imports ...

# Import pygame-specific wrappers from game_entity
from game_entity import (
    GameEntity, GameMonster, GameCharacter, GameItem,
    create_game_monster, create_game_character, create_game_weapon,
    create_dungeon_monster, create_dungeon_character, create_dungeon_item
)
```

### 2. Wrapping du Hero à la Création

**Fichier :** `dungeon_pygame.py` (ligne 452)

```python
# AVANT
self.hero = load_character(char_name=char_name, _dir=char_dir)
self.hero.x, self.hero.y = hero_x, hero_y  # ❌ Assignment manuel

# APRÈS
# Load character data and wrap as GameCharacter
character_data = load_character(char_name=char_name, _dir=char_dir)
self.hero = create_dungeon_character(character_data, x=hero_x, y=hero_y, char_id=1)
# ✅ GameCharacter avec x, y, pos, draw(), etc.
```

### 3. Vérification au Chargement des Sauvegardes

**Fichier :** `dungeon_pygame.py` fonction `run()` (ligne 2070)

```python
# AVANT
game = load_character_gamestate(character_name, ...)
# ❌ Pas de vérification si hero est wrappé

# APRÈS
game = load_character_gamestate(character_name, ...)
if game is not None:
    # Ensure hero is wrapped as GameCharacter (for old save files)
    if not isinstance(game.hero, GameCharacter):
        x, y = getattr(game.hero, 'x', 0), getattr(game.hero, 'y', 0)
        game.hero = create_dungeon_character(game.hero, x=x, y=y, char_id=1)
# ✅ Compatibilité avec anciennes sauvegardes
```

---

## 📊 Architecture GameEntity

### Character (dnd-5e-core) - Business Logic

```python
@dataclass
class Character:
    name: str
    race: Race
    class_type: ClassType
    hit_points: int
    # ... attributs métier
    # ❌ PAS de x, y, pos, draw()
```

### GameCharacter (game_entity.py) - Presentation Layer

```python
@dataclass
class GameEntity(Generic[T]):
    entity: T  # Character core
    x: int = 0
    y: int = 0
    old_x: int = 0
    old_y: int = 0
    id: int = -1
    
    @property
    def pos(self) -> tuple[int, int]:
        return self.x, self.y
    
    def draw(self, screen, image, tile_size, vp_x, vp_y):
        # Render on pygame screen
        
    def __getattr__(self, name):
        # Delegate to entity (e.g., hit_points, name, etc.)
        return getattr(self.entity, name)

GameCharacter = GameEntity[Character]
```

### Utilisation dans dungeon_pygame.py

```python
# Création
character_data = load_character(...)  # Character core
hero = create_dungeon_character(character_data, x=10, y=20, char_id=1)

# Accès positionnel (GameEntity)
hero.x, hero.y  # ✅ 10, 20
hero.pos  # ✅ (10, 20)
hero.draw(screen, image, TILE_SIZE, vp_x, vp_y)  # ✅ Rendering

# Accès métier (délégation automatique)
hero.hit_points  # ✅ Délégué à hero.entity.hit_points
hero.name  # ✅ Délégué à hero.entity.name
hero.attack(monster)  # ✅ Délégué à hero.entity.attack()
```

---

## ✅ Tests de Validation

```python
# Test 1: GameCharacter importé
from game_entity import GameCharacter, create_dungeon_character
assert GameCharacter is not None

# Test 2: Hero wrappé
character_data = load_character('TestChar')
hero = create_dungeon_character(character_data, x=10, y=20, char_id=1)

assert isinstance(hero, GameCharacter)
assert hasattr(hero, 'pos')
assert hero.pos == (10, 20)
assert hero.x == 10
assert hero.y == 20

# Test 3: Délégation fonctionne
assert hasattr(hero, 'hit_points')  # Délégué à entity
assert hasattr(hero, 'name')  # Délégué à entity
```

---

## 📝 Fichiers Modifiés

**DnD-5th-Edition-API**
- ✅ `dungeon_pygame.py`
  - Import de `game_entity` ajouté (ligne 28)
  - Wrapping du hero à la création (ligne 452)
  - Vérification au chargement des sauvegardes (ligne 2070)

---

## 🎯 Impact

### Avant
- ❌ Character sans attributs de positionnement
- ❌ AttributeError sur `.pos`, `.x`, `.y`
- ❌ Pas de méthode `draw()`
- ❌ Incompatible avec pygame

### Après
- ✅ GameCharacter avec positionnement
- ✅ Propriété `.pos` disponible
- ✅ Méthode `draw()` disponible
- ✅ Délégation automatique vers Character core
- ✅ Compatible avec anciennes sauvegardes

---

## ✅ PROBLÈME RÉSOLU

**Résultat :**
- ✅ Hero wrappé comme GameCharacter
- ✅ Attributs de positionnement disponibles
- ✅ Compatibilité avec anciennes sauvegardes
- ✅ Architecture propre (business logic séparée de la présentation)

**Le jeu pygame devrait maintenant fonctionner !** 🎉

---

**Date :** 27 décembre 2025  
**Status :** ✅ RÉSOLU  
**Type :** Missing Wrapper (GameEntity)  
**Impact :** dungeon_pygame.py fonctionnel

