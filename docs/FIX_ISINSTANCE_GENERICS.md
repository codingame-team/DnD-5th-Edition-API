# Correction: isinstance() avec Generic types

**Date**: 29 décembre 2024  
**Problème**: `TypeError: Subscripted generics cannot be used with class and instance checks`

## Problème rencontré

### Erreur
```python
def exit_boltac(hero: GameCharacter):
    char_entity = hero.entity if isinstance(hero, GameCharacter) else hero
    # TypeError: Subscripted generics cannot be used with class and instance checks
```

### Traceback complet
```
File "/Users/display/PycharmProjects/DnD-5th-Edition-API/boltac_tp_pygame.py", line 164, in exit_boltac
    char_entity = hero.entity if isinstance(hero, GameCharacter) else hero
                                 ~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/typing.py", line 1375, in __instancecheck__
    return self.__subclasscheck__(type(obj))
TypeError: Subscripted generics cannot be used with class and instance checks
```

## Explication

### Pourquoi cette erreur ?

En Python, les **types génériques paramétrés** (avec `[]`) ne peuvent pas être utilisés avec `isinstance()` ou `issubclass()`.

```python
# ❌ INCORRECT - Ne fonctionne pas
from typing import Generic, TypeVar

T = TypeVar('T')

class GameEntity(Generic[T]):
    def __init__(self, entity: T):
        self.entity = entity

class GameCharacter(GameEntity[Character]):
    pass

# Ceci échoue avec TypeError
if isinstance(obj, GameCharacter):  # ❌ GameCharacter est un générique paramétré
    ...

# Ceci échoue aussi
if isinstance(obj, GameEntity[Character]):  # ❌ Générique avec paramètre
    ...
```

### Pourquoi ?

Les génériques en Python sont principalement des **annotations de type** pour les type checkers (mypy, pyright). À l'exécution, Python ne peut pas vérifier le paramètre de type d'un générique.

```python
# Les deux sont identiques à l'exécution
GameEntity[Character]
GameEntity[Monster]
# → Même classe, paramètre ignoré
```

## Solution

### Option 1: Utiliser hasattr() ✅ (Recommandé)

**Principe**: Vérifier la présence d'un attribut caractéristique au lieu du type

```python
# ✅ CORRECT - Utilise hasattr
def exit_boltac(hero):
    # Vérifie si hero a un attribut 'entity' (caractéristique de GameEntity)
    char_entity = hero.entity if hasattr(hero, 'entity') else hero
    save_character(char=char_entity, _dir=characters_dir)
```

**Avantages**:
- ✅ Fonctionne avec tous les types génériques
- ✅ Plus flexible (duck typing)
- ✅ Pas d'import nécessaire
- ✅ Plus pythonique

### Option 2: Utiliser la classe de base non-paramétrée

```python
# ✅ CORRECT - Utilise la classe de base
from game_entity import GameEntity

def exit_boltac(hero):
    # Vérifie si hero est une instance de GameEntity (classe de base)
    char_entity = hero.entity if isinstance(hero, GameEntity) else hero
    save_character(char=char_entity, _dir=characters_dir)
```

**Note**: Fonctionne car `GameEntity` sans `[]` est vérifiable

### Option 3: Vérifier le type à l'exécution

```python
# ✅ CORRECT - Vérifie le nom de la classe
def exit_boltac(hero):
    is_game_entity = type(hero).__name__ == 'GameCharacter'
    char_entity = hero.entity if is_game_entity else hero
    save_character(char=char_entity, _dir=characters_dir)
```

**Désavantage**: Fragile (dépend du nom de classe)

## Solution appliquée

### Code final (boltac_tp_pygame.py)

```python
def exit_boltac(hero):
    """Save character when exiting Boltac's shop"""
    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'

    # Extract Character entity and save
    # Check if hero is a GameEntity wrapper (has 'entity' attribute)
    char_entity = hero.entity if hasattr(hero, 'entity') else hero
    save_character(char=char_entity, _dir=characters_dir)
    print(f'Character {char_entity.name} saved successfully')
```

**Changements**:
- ❌ Supprimé type hint `hero: GameCharacter`
- ❌ Supprimé `isinstance(hero, GameCharacter)`
- ✅ Ajouté `hasattr(hero, 'entity')`
- ✅ Supprimé import inutilisé `from game_entity import GameCharacter`

## Autres occurrences dans le projet

### Recherche dans le code

```bash
# Rechercher tous les isinstance avec génériques
grep -r "isinstance.*GameCharacter" *.py
# Résultat: Aucun autre cas trouvé

grep -r "isinstance.*GameEntity" *.py
# Résultat: Aucun autre cas trouvé
```

✅ **Aucune autre occurrence du problème dans le projet**

## Bonnes pratiques pour les génériques

### ❌ À éviter

```python
# Ne fonctionne pas
isinstance(obj, GameCharacter)
isinstance(obj, GameEntity[Character])
isinstance(obj, List[str])
isinstance(obj, Dict[str, int])

# Type hints inutiles avec isinstance
def func(x: GameCharacter):
    if isinstance(x, GameCharacter):  # ❌ Redondant et ne fonctionne pas
        ...
```

### ✅ À utiliser

```python
# Duck typing avec hasattr
def func(x):
    if hasattr(x, 'entity'):
        return x.entity
    return x

# Classe de base non-paramétrée
from game_entity import GameEntity
def func(x):
    if isinstance(x, GameEntity):
        return x.entity
    return x

# Type hints pour les IDE (pas pour isinstance)
def func(x: GameCharacter):  # ✅ Bon pour l'IDE
    # Mais utiliser hasattr pour les vérifications
    if hasattr(x, 'entity'):
        ...
```

## Leçon apprise

**Les génériques Python sont des annotations de type, pas des types à l'exécution.**

Utiliser:
- `hasattr()` pour vérifier la structure
- `isinstance()` avec la classe de base non-paramétrée
- Duck typing au lieu de type checking strict

Ne pas utiliser:
- `isinstance()` avec `Generic[T]`, `List[T]`, `Dict[K,V]`, etc.
- Type checking strict basé sur les génériques

## Références

- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [Generic types at runtime](https://peps.python.org/pep-0560/)

## Résumé

✅ **Problème résolu** en remplaçant `isinstance(hero, GameCharacter)` par `hasattr(hero, 'entity')`

Cette approche est:
- Plus flexible
- Plus pythonique
- Compatible avec tous les wrappers GameEntity
- Ne dépend pas des imports

