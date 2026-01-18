# Migration de Character.attack() - Séparation UI/Business Logic

**Date :** 26 décembre 2025  
**Phase :** 21  
**Objectif :** Migrer la méthode `attack()` de `dao_classes.py` vers `dnd-5e-core` sans les appels UI

---

## ❌ Problème Initial

Le code dans `main.py` utilisait la méthode `Character.attack()` qui n'existait pas dans `dnd-5e-core` car elle n'avait pas été migrée depuis `dao_classes.py`.

```python
# Erreur dans main.py (ligne 1913)
monster.hit_points -= attacker.attack(monster=monster, in_melee=(attacker in alive_chars[:3]))
# AttributeError: 'Character' object has no attribute 'attack'
```

---

## ✅ Solution Appliquée

### 1. Localisation de l'implémentation originale

**Fichier :** `dao_classes.py` (ligne 1321)

**Méthode originale :**
```python
def attack(self, monster: Monster, in_melee: bool = True, cast: bool = True) -> int:
    """Attack a monster"""
    # ... logique métier ...
    cprint(f"{color.RED}{self.name}{color.END} {attack_type} ...")  # ❌ UI couplée
    # ... plus de logique ...
    return damage_roll
```

**Problèmes :**
- ❌ Appels `cprint()` intégrés (couplage UI/business logic)
- ❌ Dépendance à `dao_classes` (ancien code)
- ❌ Violation du principe de séparation des responsabilités

### 2. Migration vers dnd-5e-core

**Fichier :** `dnd-5e-core/dnd_5e_core/entities/character.py`

**Nouvelle implémentation :**
```python
def attack(self, monster: Optional['Monster'] = None, character: Optional['Character'] = None,
           in_melee: bool = True, cast: bool = True, actions: Optional[List] = None) -> int:
    """
    Attack a monster or character.
    
    Pure business logic - no UI output.
    The caller is responsible for displaying attack messages using dnd_5e_core.ui.
    
    Args:
        monster: Target monster
        character: Target character (for PvP)
        in_melee: Whether in melee range
        cast: Whether to use spells if available
        actions: Available actions (unused, for compatibility)
        
    Returns:
        int: Total damage dealt
    """
    # ... toute la logique métier SANS cprint() ...
    
    if damage_roll:
        # UI layer should display attack message:
        # attack_type = (self.weapon.damage_type.index.replace("ing", "es") 
        #                if self.weapon else "punches")
        # cprint(f"{color.RED}{self.name}{color.END} {attack_type} 
        #         {color.GREEN}{target.name}{color.END} for {damage_roll} hit points!")
        
        # ... logique métier continue ...
    else:
        pass  # UI layer should display: f"{self.name} misses {target.name}!"
        
    return damage_roll
```

**Améliorations :**
- ✅ Tous les `cprint()` retirés
- ✅ Commentaires indiquant où la couche UI doit afficher
- ✅ Logique métier 100% préservée
- ✅ Support de `character` en plus de `monster` (PvP)
- ✅ Documentation claire

### 3. Migration de saving_throw()

**Également migrée** car utilisée par le système de combat :

```python
def saving_throw(self, dc_type: str, dc_value: int) -> bool:
    """
    Perform a saving throw against a spell or effect.
    
    Pure business logic - no UI output.
    
    Args:
        dc_type: Ability type for ST (e.g., 'dex', 'con', 'wis')
        dc_value: Difficulty class to beat
        
    Returns:
        bool: True if saving throw succeeds
    """
    # ... calculs SANS cprint() ...
    return saving_throw_result
```

---

## 📊 Logique Métier Migrée

### Fonctionnalités Préservées

1. **Sorts (Spellcasting)**
   - ✅ Détection des sorts lancables (cantrips + slots)
   - ✅ Sélection du meilleur sort disponible
   - ✅ Gestion des emplacements de sorts
   - ✅ Appel à `cast_attack()` pour les dégâts

2. **Attaques d'armes**
   - ✅ Calcul du jet d'attaque (1d20 + STR + prof_bonus)
   - ✅ Comparaison avec l'AC de la cible
   - ✅ Calcul des dégâts avec `damage_dice.roll()`
   - ✅ Support des attaques multiples (`multi_attacks`)

3. **Conditions spéciales**
   - ✅ Gestion de l'état "restrained" (dégâts à soi-même)
   - ✅ Vérification des HP du personnage
   - ✅ Accumulation des dégâts sur plusieurs attaques

4. **Saving Throws**
   - ✅ Calcul du modificateur d'habileté
   - ✅ Bonus de maîtrise
   - ✅ Support de l'avantage (advantage)

### Messages UI Supprimés

**Avant (dao_classes.py) :**
```python
cprint(f"{color.RED}{self.name}{color.END} {attack_type} {color.GREEN}{monster.name}{color.END} for {damage_roll} hit points!")
cprint(f"{self.name} inflicts himself {damage_roll} hit points!")
cprint(f"{self.name} *** IS DEAD ***!")
cprint(f"{self.name} misses {monster.name}!")
```

**Après (dnd-5e-core) :**
```python
# Commentaires seulement, pas d'affichage
# UI layer should display: f"{self.name} {attack_type} {target.name} for {damage_roll} hit points!"
# UI layer should display: f"{self.name} inflicts himself {damage_roll} hit points!"
# UI layer should display: f"{self.name} *** IS DEAD ***!"
# UI layer should display: f"{self.name} misses {target.name}!"
```

---

## 🎯 Utilisation dans main.py

### Avec UI (dnd_5e_core.ui)

```python
from dnd_5e_core.ui import cprint, color

# Attaque
damage = attacker.attack(monster=monster, in_melee=True)

# Affichage UI
if damage > 0:
    attack_type = (attacker.weapon.damage_type.index.replace("ing", "es") 
                   if attacker.weapon else "punches")
    cprint(f"{color.RED}{attacker.name}{color.END} {attack_type} "
           f"{color.GREEN}{monster.name}{color.END} for {damage} hit points!")
else:
    cprint(f"{attacker.name} misses {monster.name}!")

# Appliquer les dégâts
monster.hit_points -= damage
```

### Avantages de cette Approche

1. **Séparation des responsabilités**
   - Logique métier dans `dnd-5e-core`
   - Affichage dans `main.py` via `dnd_5e_core.ui`

2. **Testabilité**
   - Tests unitaires sans mock de `cprint()`
   - Validation de la logique métier isolée

3. **Réutilisabilité**
   - `attack()` utilisable dans n'importe quelle interface
   - Console, ncurses, pygame, PyQt, etc.

4. **Maintenabilité**
   - Changements d'UI sans toucher au core
   - Logique métier centralisée

---

## ✅ Tests de Validation

### Test 1 : Méthode existe
```python
from dnd_5e_core.entities import Character

assert hasattr(Character, 'attack'), "attack() method exists"
assert hasattr(Character, 'saving_throw'), "saving_throw() method exists"
```

### Test 2 : Signature correcte
```python
import inspect

sig = inspect.signature(Character.attack)
params = list(sig.parameters.keys())

assert 'monster' in params
assert 'character' in params
assert 'in_melee' in params
assert 'cast' in params
```

### Test 3 : Pas de dépendance UI
```python
import ast
import inspect

source = inspect.getsource(Character.attack)
tree = ast.parse(source)

# Vérifier qu'il n'y a pas d'appels à cprint
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            assert node.func.id != 'cprint', "No cprint calls in attack()"
```

---

## 📝 Fichiers Modifiés

### dnd-5e-core
- ✅ `entities/character.py`
  - Ajout de `attack()` (89 lignes)
  - Ajout de `saving_throw()` (31 lignes)
  - **Total : 120 lignes de logique métier ajoutées**

### Documentation
- ✅ `HISTORIQUE_COMPLET_SESSION.md` - Phase 21 ajoutée
- ✅ `MIGRATION_CHARACTER_ATTACK.md` - Ce document

---

## 🎯 Principe Appliqué

**Separation of Concerns (SoC)**

```
┌─────────────────────────────────┐
│   Presentation Layer            │
│   (main.py, main_ncurses.py)   │
│                                 │
│   Uses: dnd_5e_core.ui         │
│   - cprint()                    │
│   - color                       │
│   - Color                       │
└────────────┬────────────────────┘
             │ Calls
             ▼
┌─────────────────────────────────┐
│   Business Logic Layer          │
│   (dnd-5e-core)                │
│                                 │
│   Character.attack()            │
│   - Calculs de dégâts          │
│   - Jets d'attaque             │
│   - Gestion des conditions     │
│   - NO UI                       │
└─────────────────────────────────┘
```

---

## ✅ MIGRATION RÉUSSIE

**Résultat :**
- ✅ Méthode `attack()` migrée sans couplage UI
- ✅ Méthode `saving_throw()` migrée
- ✅ 100% de la logique métier préservée
- ✅ 0% de code UI dans dnd-5e-core
- ✅ Principe SoC respecté
- ✅ main.py peut utiliser `dnd_5e_core.ui` pour l'affichage

**Architecture propre et maintenable !** 🎉

---

**Date :** 26 décembre 2025  
**Status :** ✅ COMPLÈTE  
**Impact :** Séparation UI/Business Logic réussie  
**Next Steps :** Adapter main.py pour utiliser `dnd_5e_core.ui` pour les messages de combat

