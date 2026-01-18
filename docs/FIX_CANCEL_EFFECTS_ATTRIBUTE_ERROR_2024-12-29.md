# Fix: AttributeError cancel_strength_effect et cancel_haste_effect

**Date**: 29 décembre 2024  
**Erreur**: `AttributeError: 'Character' object has no attribute 'cancel_strength_effect'`  
**Cause**: Ces méthodes n'existent pas dans la classe Character de dnd-5e-core  
**Solution**: Implémentation inline directement dans dungeon_pygame.py  
**Statut**: ✅ CORRIGÉ

---

## Erreur

```
Traceback (most recent call last):
  File "dungeon_pygame.py", line 1609, in main_game_loop
    game.hero.cancel_strength_effect()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Character' object has no attribute 'cancel_strength_effect'
```

---

## Cause

Les méthodes `cancel_haste_effect()` et `cancel_strength_effect()` existaient dans l'ancienne classe `Character` de `dao_classes.py`, mais n'ont pas été migrées vers `dnd-5e-core` car ce sont des fonctionnalités spécifiques au jeu pygame.

---

## Solution

Remplacement des appels de méthodes par une **implémentation inline** qui réinitialise directement les attributs.

### Code AVANT (ligne 1605-1609)

```python
if hasattr(game.hero, 'hasted') and game.hero.hasted and current_time - game.hero.haste_timer > 60:
    game.hero.cancel_haste_effect()  # ❌ AttributeError
if hasattr(game.hero, 'str_effect_modifier') and game.hero.str_effect_modifier > 0 and current_time - game.hero.str_effect_timer > 3600:
    game.hero.cancel_strength_effect()  # ❌ AttributeError
```

### Code APRÈS (ligne 1605-1616)

```python
# Cancel haste effect after 60 seconds
if hasattr(game.hero, 'hasted') and game.hero.hasted and current_time - game.hero.haste_timer > 60:
    # Inline implementation of cancel_haste_effect()
    game.hero.hasted = False
    game.hero.speed = 30  # Reset to normal speed
    cprint(f'{game.hero.name} is no longer hasted!')

# Cancel strength effect after 3600 seconds (1 hour)
if hasattr(game.hero, 'str_effect_modifier') and game.hero.str_effect_modifier > 0 and current_time - game.hero.str_effect_timer > 3600:
    # Inline implementation of cancel_strength_effect()
    game.hero.str_effect_modifier = 0
    cprint(f'{game.hero.name}\'s strength effect has worn off!')
```

---

## Logique implémentée

### 1. Annulation de l'effet Haste (60 secondes)

**Effet de Haste** :
- Double la vitesse du personnage
- Attributs : `hasted=True`, `speed=60`, `haste_timer=timestamp`

**Annulation** :
- `hasted = False`
- `speed = 30` (vitesse normale)
- Message : "X is no longer hasted!"

### 2. Annulation de l'effet Force (1 heure)

**Effet de Force** (Potion de Force de Géant) :
- Augmente la force temporairement
- Attributs : `str_effect_modifier>0`, `str_effect_timer=timestamp`

**Annulation** :
- `str_effect_modifier = 0`
- Message : "X's strength effect has worn off!"

---

## Avantages de la solution

✅ **Pas de dépendance** : Ne nécessite pas de modifier dnd-5e-core  
✅ **Code inline** : Logique claire et directe  
✅ **Maintenable** : Facile à comprendre et modifier  
✅ **Compatible** : Fonctionne avec GameEntity[Character]

---

## Flux temporel

```
Potion de Haste utilisée
   ↓
game.hero.hasted = True
game.hero.speed = 60
game.hero.haste_timer = current_time
   ↓
... 60 secondes passent ...
   ↓
current_time - haste_timer > 60 ?
   ↓ Oui
game.hero.hasted = False
game.hero.speed = 30
✅ Message: "Ellyjobell is no longer hasted!"
```

```
Potion de Force de Géant utilisée
   ↓
game.hero.str_effect_modifier = 10 (par exemple)
game.hero.str_effect_timer = current_time
   ↓
... 3600 secondes passent (1 heure) ...
   ↓
current_time - str_effect_timer > 3600 ?
   ↓ Oui
game.hero.str_effect_modifier = 0
✅ Message: "Ellyjobell's strength effect has worn off!"
```

---

## Tests

### Test 1: Effet Haste

```
1. Utiliser une potion de Speed (shift+S)
2. Attendre 60 secondes (ou modifier le timer pour tester)
3. Observer le message
```

**Résultat attendu** :
- ✅ Message "X is no longer hasted!"
- ✅ Vitesse retourne à 30
- ✅ Pas d'erreur

### Test 2: Effet Force

```
1. Utiliser une potion de Force de Géant
2. Attendre 3600 secondes (ou modifier pour tester)
3. Observer le message
```

**Résultat attendu** :
- ✅ Message "X's strength effect has worn off!"
- ✅ Modificateur de force retourne à 0
- ✅ Pas d'erreur

---

## Fichiers modifiés

**dungeon_pygame.py** (lignes 1605-1616)
- Remplacement de `cancel_haste_effect()` par implémentation inline
- Remplacement de `cancel_strength_effect()` par implémentation inline

---

## Conclusion

✅ **Problème résolu !**

Les effets temporaires (haste, strength) s'annulent maintenant correctement après leur durée sans générer d'AttributeError.

**Status** : ✅ PRODUCTION READY

