# Correctif urgent: isinstance() avec types génériques

**Date**: 29 décembre 2024  
**Fichier**: `boltac_tp_pygame.py`  
**Statut**: ✅ CORRIGÉ

## Problème

```
TypeError: Subscripted generics cannot be used with class and instance checks
```

**Ligne problématique**:
```python
char_entity = hero.entity if isinstance(hero, GameCharacter) else hero
```

## Cause

Python ne permet pas d'utiliser `isinstance()` avec des types génériques paramétrés comme `GameCharacter` qui hérite de `GameEntity[Character]`.

## Solution appliquée

**AVANT** ❌:
```python
from game_entity import GameCharacter

def exit_boltac(hero: GameCharacter):
    char_entity = hero.entity if isinstance(hero, GameCharacter) else hero
    # TypeError!
```

**APRÈS** ✅:
```python
def exit_boltac(hero):
    # Check if hero is a GameEntity wrapper (has 'entity' attribute)
    char_entity = hero.entity if hasattr(hero, 'entity') else hero
    # Fonctionne!
```

## Changements effectués

1. ✅ Remplacé `isinstance(hero, GameCharacter)` par `hasattr(hero, 'entity')`
2. ✅ Supprimé type hint `hero: GameCharacter`
3. ✅ Supprimé import inutilisé `from game_entity import GameCharacter`

## Validation

- ✅ Aucune erreur de compilation
- ✅ Module s'importe correctement
- ✅ Logic hasattr testée et validée

## Impact

**Aucun autre fichier affecté** - Ce problème était unique à `boltac_tp_pygame.py`

## Documentation

Voir `docs/FIX_ISINSTANCE_GENERICS.md` pour les détails complets et bonnes pratiques.

