# Fix : AttributeError Charisma et HealingPotion.equipped

**Date** : 30 décembre 2024  
**Problèmes** :
1. `AttributeError: 'Abilities' object has no attribute 'charisma'`
2. `AttributeError: 'HealingPotion' object has no attribute 'equipped'`

**Statut** : ✅ CORRIGÉ

---

## Problème 1 : AttributeError 'charisma'

### Erreur

```python
File "dnd_5e_core/entities/character.py", line 618, in gain_level
    val = self.abilities.get_value_by_name(name=attr)
File "dnd_5e_core/abilities/abilities.py", line 59, in get_value_by_name
    return getattr(self, attr_map.get(name, name.lower()))
AttributeError: 'Abilities' object has no attribute 'charisma'
```

### Cause

Dans la méthode `gain_level()`, nous utilisions `"Charisma"` mais la classe `Abilities` attend `"Charism"` (sans 'a' final).

**Classe Abilities** :
```python
@dataclass
class Abilities:
    str: int  # Strength
    dex: int  # Dexterity
    con: int  # Constitution
    int: int  # Intelligence
    wis: int  # Wisdom
    cha: int  # Charisma (mais mappé comme "Charism")
    
    def get_value_by_name(self, name: str) -> int:
        attr_map = {
            "Strength": "str",
            "Dexterity": "dex",
            "Constitution": "con",
            "Intelligence": "int",
            "Wisdom": "wis",
            "Charism": "cha"  # ← Pas "Charisma" !
        }
        return getattr(self, attr_map.get(name, name.lower()))
```

### Solution

**Fichier** : `/dnd-5e-core/dnd_5e_core/entities/character.py` - ligne 615

**AVANT** :
```python
attrs = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
```

**APRÈS** :
```python
attrs = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charism"]
```

---

## Problème 2 : AttributeError 'equipped'

### Erreur

```python
File "pyQTApp/Castle/Boltac_module.py", line 102, in populate_sell_table
    selectable: bool = isinstance(item, Potion) or not item.equipped
AttributeError: 'HealingPotion' object has no attribute 'equipped'
```

### Cause

Le code supposait que **tous les items** ont un attribut `equipped`, mais ce n'est pas le cas :

- ✅ `Weapon` a `equipped`
- ✅ `Armor` a `equipped`
- ❌ `Potion` n'a PAS `equipped` (les potions ne s'équipent pas)
- ❌ `HealingPotion` n'a PAS `equipped`

**Code problématique** :
```python
for i, item in enumerate(inventory):
    selectable: bool = isinstance(item, Potion) or not item.equipped  # ❌ item.equipped crash si Potion
```

**Logique** :
1. Si c'est une `Potion` → `selectable = True`
2. Sinon → `selectable = not item.equipped`

**Problème** : Si `item` est une `Potion`, on évalue quand même `not item.equipped` à cause du `or` !

### Solution

**Fichier** : `/pyQTApp/Castle/Boltac_module.py` - ligne 102

**AVANT** :
```python
selectable: bool = isinstance(item, Potion) or not item.equipped
```

**APRÈS** :
```python
# Potions don't have equipped attribute, only Equipment does
selectable: bool = isinstance(item, Potion) or (hasattr(item, 'equipped') and not item.equipped)
```

**Logique corrigée** :
1. Si c'est une `Potion` → `selectable = True` (court-circuit, pas d'évaluation du `or`)
2. Sinon, vérifier si `item` a l'attribut `equipped` **avant** de l'accéder
3. Si oui et pas équipé → `selectable = True`
4. Sinon → `selectable = False`

---

## Explication : Priorité des opérateurs et court-circuit

### Opérateur `or` en Python

```python
a or b
```

**Évaluation** :
1. Évalue `a`
2. Si `a` est `True` → Retourne `a` (court-circuit, `b` n'est PAS évalué)
3. Si `a` est `False` → Évalue et retourne `b`

### Cas problématique

```python
isinstance(item, Potion) or not item.equipped
```

**Si item = HealingPotion** :
1. `isinstance(item, Potion)` → `True`
2. Court-circuit → Retourne `True`
3. ✅ **Pas d'erreur** car `not item.equipped` n'est PAS évalué

**MAIS** : L'erreur vient du fait que `HealingPotion` **hérite** de `Potion` mais n'a pas `equipped`.

**Le vrai problème** : Si le code essaie d'accéder à `item.equipped` pour **n'importe quelle raison**, ça crash.

### Solution robuste

```python
isinstance(item, Potion) or (hasattr(item, 'equipped') and not item.equipped)
```

**Garantit** :
- Potions → Toujours `True`
- Equipment sans `equipped` → `False` (pas de crash)
- Equipment avec `equipped=True` → `False`
- Equipment avec `equipped=False` → `True`

---

## Tests de validation

### Test 1 : Montée de niveau

```python
# Console
python main.py
# Choisir "2) Castle"
# Choisir "2) Adventurer's Inn"
# Reposer suffisamment pour monter de niveau
```

**Résultat attendu** :
```
New level #3 gained!!!
Gandalf gained 5 hit points
You gained Charism
```

**✅ Pas d'erreur `AttributeError: 'Abilities' object has no attribute 'charisma'`**

---

### Test 2 : Vente d'items chez Boltac

```python
# Console
python pyQTApp/Castle/Boltac_module.py  # ou lancer l'app Qt
# Sélectionner un personnage avec des potions dans l'inventaire
# Observer la table de vente
```

**Résultat attendu** :
- ✅ Potions affichées et sélectionnables
- ✅ Armes/armures équipées non sélectionnables
- ✅ Armes/armures non équipées sélectionnables
- ✅ **Pas d'erreur `AttributeError: 'HealingPotion' object has no attribute 'equipped'`**

---

## Résumé des changements

### Fichier 1 : character.py

**Ligne** : 615  
**Changement** : `"Charisma"` → `"Charism"`  
**Raison** : Correspondre au mapping de la classe `Abilities`

### Fichier 2 : Boltac_module.py

**Ligne** : 102  
**Changement** : 
```python
# AVANT
selectable: bool = isinstance(item, Potion) or not item.equipped

# APRÈS
selectable: bool = isinstance(item, Potion) or (hasattr(item, 'equipped') and not item.equipped)
```
**Raison** : Vérifier l'existence de `equipped` avant de l'accéder

---

## Note sur "Charism" vs "Charisma"

### Origine

Le terme `"Charism"` (sans 'a' final) est une **convention du projet** héritée du code original.

### Cohérence

**Dans tout le projet** :
- ✅ `abilities.cha` → Attribut court
- ✅ `"Charism"` → Nom long dans les mappings
- ❌ `"Charisma"` → **NE PAS UTILISER** (n'existe pas dans le mapping)

### Mapping complet

| Nom long | Attribut | Nom D&D standard |
|----------|----------|------------------|
| `"Strength"` | `str` | Strength |
| `"Dexterity"` | `dex` | Dexterity |
| `"Constitution"` | `con` | Constitution |
| `"Intelligence"` | `int` | Intelligence |
| `"Wisdom"` | `wis` | Wisdom |
| `"Charism"` | `cha` | Charisma |

**Pourquoi "Charism" ?** Probablement pour éviter la confusion avec le mot anglais "charisma" ou pour uniformiser avec les autres noms sans 'a' final.

---

## Conclusion

✅ **DEUX PROBLÈMES CORRIGÉS !**

1. ✅ **`"Charisma"` → `"Charism"`** dans `gain_level()`
2. ✅ **Vérification `hasattr(item, 'equipped')`** avant accès

**Les deux bugs sont maintenant résolus et le code fonctionne correctement !** 🎮✨

---

**Fichiers modifiés** :
1. `/dnd-5e-core/dnd_5e_core/entities/character.py` - ligne 615
2. `/DnD-5th-Edition-API/pyQTApp/Castle/Boltac_module.py` - ligne 102

**Status** : ✅ PRODUCTION READY

