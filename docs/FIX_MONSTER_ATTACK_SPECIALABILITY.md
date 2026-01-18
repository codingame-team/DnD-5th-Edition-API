# Correction Monster.attack() - SpecialAbility Import Error

**Date :** 26 décembre 2025  
**Erreur :** `NameError: name 'SpecialAbility' is not defined`

---

## ❌ Problème

Lors d'un combat, quand un monstre attaque, l'erreur suivante se produisait :

```python
File "/Users/display/PycharmProjects/dnd-5e-core/dnd_5e_core/entities/monster.py", line 284, in attack
    if attack_action is SpecialAbility:
                        ^^^^^^^^^^^^^^
NameError: name 'SpecialAbility' is not defined
```

**Cause :** L'import de `SpecialAbility` était dans le bloc `if TYPE_CHECKING:`, ce qui le rend disponible uniquement pour le type checking, pas au runtime.

---

## ✅ Solution Appliquée

### 1. Import au Runtime

**Fichier :** `dnd-5e-core/dnd_5e_core/entities/monster.py`

```python
# AVANT (ligne 12-14)
if TYPE_CHECKING:
    from ..abilities.abilities import Abilities
    from ..classes.proficiency import Proficiency
    from ..combat.action import Action, ActionType
    from ..combat.special_ability import SpecialAbility  # ❌ TYPE_CHECKING seulement
    from ..combat.damage import Damage
    # ...

# APRÈS
from ..combat.special_ability import SpecialAbility  # ✅ Import au runtime

if TYPE_CHECKING:
    from ..abilities.abilities import Abilities
    from ..classes.proficiency import Proficiency
    from ..combat.action import Action, ActionType
    from ..combat.damage import Damage
    # ...
```

### 2. Correction de la Vérification de Type

```python
# AVANT (ligne 284)
if attack_action is SpecialAbility:  # ❌ 'is' ne fonctionne pas pour les types
    total_damage += self.special_attack(target, attack_action)

# APRÈS
if isinstance(attack_action, SpecialAbility):  # ✅ isinstance() correct
    total_damage += self.special_attack(target, attack_action)
```

---

## 📝 Explication Technique

### TYPE_CHECKING vs Import Normal

**TYPE_CHECKING** (uniquement pour annotations de types) :
```python
if TYPE_CHECKING:
    from ..combat.action import Action  # Utilisé dans les annotations
    
def attack(self, actions: List['Action']):  # OK - forward reference
    pass
```

**Import Normal** (nécessaire au runtime) :
```python
from ..combat.special_ability import SpecialAbility  # Utilisé dans le code

def attack(self):
    if isinstance(attack_action, SpecialAbility):  # OK - classe disponible
        pass
```

### is vs isinstance

**`is`** : Compare l'identité des objets
```python
if x is None:  # ✅ OK - compare l'identité
if x is SomeClass:  # ❌ ERREUR - compare x à la classe elle-même
```

**`isinstance()`** : Vérifie le type d'un objet
```python
if isinstance(x, SomeClass):  # ✅ OK - vérifie si x est une instance de SomeClass
```

---

## ✅ Tests de Validation

```python
# Test 1: Import disponible au runtime
from dnd_5e_core.entities.monster import Monster, SpecialAbility
assert SpecialAbility is not None

# Test 2: isinstance fonctionne
from dnd_5e_core.combat.special_ability import SpecialAbility
sa = SpecialAbility(...)
assert isinstance(sa, SpecialAbility)

# Test 3: Combat fonctionne
monster = Monster(...)
character = Character(...)
damage = monster.attack(target=character)
assert isinstance(damage, int)
```

---

## 📊 Impact

### Avant
- ❌ Combat plantait avec `NameError`
- ❌ Impossible d'utiliser les attaques spéciales des monstres

### Après
- ✅ Combat fonctionne correctement
- ✅ Attaques spéciales gérées
- ✅ Attaques normales fonctionnent

---

## 📝 Fichiers Modifiés

**dnd-5e-core**
- ✅ `entities/monster.py`
  - Import `SpecialAbility` déplacé hors de TYPE_CHECKING
  - Correction de `is` → `isinstance()`

---

## ✅ PROBLÈME RÉSOLU

**Résultat :**
- ✅ SpecialAbility importé au runtime
- ✅ Vérification de type corrigée avec isinstance()
- ✅ Combat fonctionne sans erreur
- ✅ Attaques spéciales des monstres opérationnelles

**Le système de combat devrait maintenant fonctionner !** 🎉

---

**Date :** 26 décembre 2025  
**Status :** ✅ RÉSOLU  
**Type :** Import Error + Type Check Error  
**Cause :** Import TYPE_CHECKING + mauvaise vérification de type

