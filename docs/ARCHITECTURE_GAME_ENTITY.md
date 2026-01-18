# Architecture: Séparation Business Logic / Presentation Layer

## 🎯 Problème

Les classes métier de `dnd-5e-core` (Character, Monster, Weapon, Armor, Potion) contenaient des attributs de positionnement (`id`, `x`, `y`, `image_name`) qui sont spécifiques à l'implémentation pygame.

**Problème de design :**
- ❌ Les classes métier dépendent de la couche présentation
- ❌ Impossible d'utiliser dnd-5e-core sans ces attributs
- ❌ Violation du principe de séparation des responsabilités

## ✅ Solution : Pattern Composition avec GameEntity

### Architecture Recommandée

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│          (pygame, tkinter)              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │       GameEntity<T>              │  │
│  │  - x, y, old_x, old_y            │  │
│  │  - image_name, id                │  │
│  │  - move(), check_collision()     │  │
│  │                                  │  │
│  │  entity: T (Character/Monster)   │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│               │ Wraps                   │
│               ▼                         │
│  ┌──────────────────────────────────┐  │
│  │    Business Logic Layer          │  │
│  │        (dnd-5e-core)             │  │
│  │                                  │  │
│  │  Character, Monster              │  │
│  │  Weapon, Armor, Potion           │  │
│  │  - abilities, hit_points         │  │
│  │  - damage_dice, armor_class      │  │
│  │  - spells, actions               │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Avantages

#### 1. **Séparation des Responsabilités**
- **Business Logic** : dnd-5e-core contient uniquement les règles D&D
- **Presentation** : GameEntity gère le positionnement et le rendu

#### 2. **Réutilisabilité**
- dnd-5e-core peut être utilisé dans n'importe quel frontend
- Pas de dépendance à pygame

#### 3. **Testabilité**
- Tests des règles D&D sans mock de pygame
- Tests de rendering séparés

#### 4. **Flexibilité**
- Facile de changer de frontend (pygame → godot, unity, etc.)
- Peut utiliser les mêmes entités core dans plusieurs jeux

## 📝 Migration Guide

### Étape 1 : État Actuel (Legacy)

**Avant (avec attributs de positionnement dans les classes core) :**

```python
# populate_functions.py
def request_monster(index_name: str) -> Monster:
    data = load_json(...)
    return Monster(
        index=data['index'],
        name=data['name'],
        abilities=abilities,
        # ... autres attributs core ...
        
        # ❌ Attributs de positionnement (legacy)
        id=-1,
        x=-1,
        y=-1,
        image_name=None
    )

# dungeon_pygame.py
monster = request_monster('goblin')
monster.x = 10  # ❌ Modifie directement la classe métier
monster.y = 20
```

### Étape 2 : Migration vers GameEntity

**Après (avec GameEntity wrapper) :**

```python
# populate_functions.py
def request_monster(index_name: str) -> Monster:
    data = load_json(...)
    return Monster(
        index=data['index'],
        name=data['name'],
        abilities=abilities,
        # ... uniquement attributs core ...
    )
    # ✅ Pas d'attributs de positionnement

# dungeon_pygame.py
from game_entity import create_game_monster

# Créer l'entité métier
monster_data = request_monster('goblin')

# Wrapper pour pygame avec positionnement
game_monster = create_game_monster(
    monster_data, 
    x=10, 
    y=20, 
    image_name='goblin.png'
)

# Accès aux données métier
print(game_monster.entity.name)  # "Goblin"
print(game_monster.entity.hit_points)  # 7

# Positionnement
game_monster.move(dx=1, dy=0)
print(game_monster.pos)  # (11, 20)
```

## 🔧 API de GameEntity

### Création

```python
from game_entity import (
    create_game_character,
    create_game_monster,
    create_game_weapon,
    create_game_armor,
    create_game_potion
)

# Character
character = create_game_character(
    char_data,
    x=5,
    y=5,
    image_name="warrior.png"
)

# Monster
monster = create_game_monster(
    monster_data,
    x=10,
    y=15,
    image_name="goblin.png"
)
```

### Positionnement

```python
# Position actuelle
pos = game_entity.pos  # (x, y)

# Déplacement relatif
game_entity.move(dx=1, dy=0)  # Move right

# Position absolue
game_entity.set_position(x=20, y=30)

# Position précédente
old_pos = game_entity.old_pos
```

### Collision

```python
if game_entity1.check_collision(game_entity2):
    print("Collision detected!")
```

### Accès aux Données Métier

```python
# Accès direct à l'entité wrappée
core_entity = game_entity.entity

# Propriétés déléguées
name = game_entity.name  # Délégué à entity.name
is_alive = game_entity.is_alive  # Délégué à entity.is_alive
```

## 📊 État de Migration

### État Actuel (Hybrid Approach)

**Les classes core gardent temporairement les attributs de positionnement :**

- ✅ **Avantage** : Compatibilité ascendante avec code existant
- ⚠️ **Inconvénient** : Classes core encore couplées à la présentation

**Attributs marqués comme DEPRECATED :**

```python
@dataclass
class WeaponData:
    # Core D&D 5e attributes
    index: str
    name: str
    # ...
    
    # Legacy positioning attributes (DEPRECATED - use GameEntity instead)
    id: int = -1
    image_name: Optional[str] = None
    x: int = -1
    y: int = -1
```

### Migration Future (Clean Separation)

**Objectif à long terme :**

1. ❌ Retirer tous les attributs de positionnement des classes core
2. ✅ Utiliser uniquement GameEntity pour le positionnement
3. ✅ dnd-5e-core devient 100% indépendant du frontend

## 🎯 Plan de Migration Progressif

### Phase 1 : Hybride (Actuel) ✅
- Attributs de positionnement dans les classes core (avec defaults)
- GameEntity créé et documenté
- Code existant continue de fonctionner

### Phase 2 : Transition
- Migrer dungeon_pygame.py pour utiliser GameEntity
- Marquer les attributs core comme deprecated
- Ajouter warnings lors de l'utilisation des attributs deprecated

### Phase 3 : Clean
- Retirer les attributs de positionnement des classes core
- GameEntity devient obligatoire pour pygame
- dnd-5e-core 100% indépendant

## 💡 Exemples d'Utilisation

### Exemple 1 : Rendering dans pygame

```python
def render_entities(screen, game_entities):
    """Render all game entities"""
    for game_entity in game_entities:
        # Position from GameEntity
        x, y = game_entity.pos
        
        # Load image
        image = load_image(game_entity.image_name)
        
        # Render at position
        screen.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
```

### Exemple 2 : Combat System

```python
def attack(attacker: GameMonster, defender: GameCharacter):
    """Combat system using GameEntity wrappers"""
    # Business logic uses core entities
    damage = attacker.entity.calculate_damage()
    defender.entity.take_damage(damage)
    
    # Presentation uses GameEntity
    if not defender.is_alive:
        # Remove from game grid
        game_entities.remove(defender)
```

### Exemple 3 : Collision Detection

```python
def check_collisions(game_entities: List[GameEntity]):
    """Check collisions between all entities"""
    for i, entity1 in enumerate(game_entities):
        for entity2 in game_entities[i+1:]:
            if entity1.check_collision(entity2):
                handle_collision(entity1, entity2)
```

## 📚 Références

### Patterns de Design Utilisés

1. **Composition over Inheritance**
   - GameEntity CONTIENT une entité core au lieu d'hériter
   - Plus flexible et découplé

2. **Adapter Pattern**
   - GameEntity adapte les entités core pour pygame
   - Interface unifiée pour le positionnement

3. **Separation of Concerns**
   - Business logic (dnd-5e-core) séparé de la présentation (GameEntity)
   - Chaque couche a sa responsabilité

### Fichiers Concernés

**dnd-5e-core :**
- `dnd_5e_core/equipment/weapon.py` - WeaponData (avec attributs legacy)
- `dnd_5e_core/equipment/armor.py` - ArmorData (avec attributs legacy)
- `dnd_5e_core/entities/character.py` - Character (pas d'attributs de positionnement)
- `dnd_5e_core/entities/monster.py` - Monster (pas d'attributs de positionnement)

**DnD-5th-Edition-API :**
- `game_entity.py` - GameEntity wrapper (nouveau)
- `dungeon_pygame.py` - À migrer pour utiliser GameEntity
- `populate_functions.py` - Crée des entités core (legacy avec attributs)

## ✅ Conclusion

### État Actuel
- ✅ GameEntity créé et documenté
- ✅ Architecture propre définie
- ✅ Compatibilité ascendante préservée
- ⏳ Migration en cours

### Prochaines Étapes
1. Tester GameEntity dans dungeon_pygame.py
2. Migrer progressivement le code vers GameEntity
3. Retirer les attributs legacy quand migration complète

---

**Pattern :** Composition > Inheritance  
**Principe :** Separation of Concerns  
**Status :** ✅ Architecture définie, migration progressive

