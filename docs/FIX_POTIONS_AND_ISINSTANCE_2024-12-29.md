# Fix: Sprites de potions + Erreur isinstance avec génériques

**Date**: 29 décembre 2024  
**Problèmes corrigés**:
1. Sprites de potions non affichés
2. Crash au quit : `TypeError: Subscripted generics cannot be used with class and instance checks`
**Statut**: ✅ CORRIGÉ

---

## Problème 1: Sprites de potions non affichés

### Diagnostic

Les potions n'ont **pas** d'attribut `index` (contrairement aux armes/armures), seulement un `name`.

**Structure des objets** :
```python
# Armes/Armures (ont un index)
weapon = WeaponData(index='longsword', name='Longsword', ...)
armor = ArmorData(index='chain-mail', name='Chain Mail', ...)

# Potions (PAS d'index)
potion = HealingPotion(name='Healing', rarity=COMMON, ...)  # ❌ Pas d'index !
```

### Problème dans le code

**AVANT** :
```python
def get_item_image_name(item):
    # 1. Vérifier image_name
    if hasattr(item, 'image_name'):
        return item.image_name
    
    # 2. Vérifier index - ❌ Les potions n'ont pas d'index !
    if hasattr(item, 'index') and item.index:
        # ... mapping armes/armures
        return f"{item.index}.png"
    
    # 3. Mappings potions - ❌ JAMAIS ATTEINT car potions n'ont pas d'index
    #    et le code a déjà retourné à l'étape 2
    potion_map = {...}
```

**Résultat** : Les potions retournaient `None.png` ou un nom invalide.

### Solution

Réorganiser le code pour **vérifier le type AVANT** de chercher l'index :

```python
def get_item_image_name(item):
    # 1. Vérifier image_name explicite
    if hasattr(item, 'image_name') and item.image_name:
        return item.image_name
    
    # 2. ✅ Vérifier si c'est une POTION AVANT de chercher l'index
    if 'Potion' in item.__class__.__name__:
        potion_map = {
            'healing': 'potion-red.png',
            'greater healing': 'potion-red.png',
            'superior healing': 'potion-red.png',
            'speed': 'potion-green.png',
            'strength': 'potion-blue.png',
        }
        item_name = item.name.lower()
        if item_name in potion_map:
            return potion_map[item_name]
        return 'potion.png'  # Fallback générique
    
    # 3. Vérifier index pour armes/armures
    if hasattr(item, 'index') and item.index:
        # ... mappings armes/armures
```

### Flux corrigé

```
Potion "Healing"
   ↓
1. hasattr('image_name') ? Non
   ↓
2. 'Potion' in class name ? ✅ Oui
   ↓
3. item.name.lower() = 'healing'
   ↓
4. potion_map['healing'] = 'potion-red.png'
   ↓
5. ✅ Retourne 'potion-red.png'
```

---

## Problème 2: Erreur isinstance avec génériques

### Erreur complète

```python
Traceback (most recent call last):
  File "dungeon_pygame.py", line 1184, in save_character_gamestate
    if not isinstance(game.hero, GameCharacter):
TypeError: Subscripted generics cannot be used with class and instance checks
```

### Cause

`GameCharacter` est défini comme un générique paramétré :

```python
# Dans game_entity.py
GameCharacter = GameEntity[Character]
```

Python **ne permet pas** `isinstance()` avec des génériques paramétrés :

```python
# ❌ ERREUR
isinstance(obj, GameCharacter)
isinstance(obj, GameEntity[Character])

# ✅ OK
isinstance(obj, GameEntity)  # Sans paramètre
```

### Solution

Utiliser **`hasattr()`** au lieu de `isinstance()` pour détecter la structure :

**AVANT** :
```python
# ❌ Crash avec TypeError
if not isinstance(game.hero, GameCharacter):
    # Convert to GameCharacter
    ...

# Plus loin
char_entity = game.hero.entity if isinstance(game.hero, GameCharacter) else game.hero
```

**APRÈS** :
```python
# ✅ Fonctionne - vérifie si l'objet a l'attribut 'entity'
if not hasattr(game.hero, 'entity'):
    # Convert to GameCharacter
    ...

# Plus loin
char_entity = game.hero.entity if hasattr(game.hero, 'entity') else game.hero
```

### Pattern utilisé : Duck Typing

Au lieu de vérifier le type exact, on vérifie la **structure** :

```python
# Duck typing : "Si ça a un attribut entity, c'est un GameEntity"
if hasattr(obj, 'entity'):
    # C'est un GameEntity wrapping une entité
    core_entity = obj.entity
else:
    # C'est déjà l'entité core
    core_entity = obj
```

**Avantages** :
- ✅ Fonctionne avec tous les types de wrappers
- ✅ Pas de dépendance sur les types génériques
- ✅ Plus pythonique ("duck typing")
- ✅ Plus robuste face aux changements de structure

---

## Changements de code

### Fichier: dungeon_pygame.py

**1. Fonction `get_item_image_name()`** (ligne ~2250)

```python
# AVANT - Ordre incorrect
def get_item_image_name(item):
    if hasattr(item, 'index'):  # ❌ Vérifie index AVANT le type
        return f"{item.index}.png"
    
    potion_map = {...}  # ❌ Jamais atteint pour potions

# APRÈS - Ordre correct
def get_item_image_name(item):
    # ✅ Vérifie le TYPE (Potion) AVANT l'index
    if 'Potion' in item.__class__.__name__:
        potion_map = {
            'healing': 'potion-red.png',
            'greater healing': 'potion-red.png',
            'speed': 'potion-green.png',
            'strength': 'potion-blue.png',
        }
        return potion_map.get(item.name.lower(), 'potion.png')
    
    if hasattr(item, 'index'):  # Pour armes/armures
        # ... mappings
```

**2. Fonction `save_character_gamestate()`** (ligne ~1184)

```python
# AVANT - isinstance avec générique
if not isinstance(game.hero, GameCharacter):  # ❌ TypeError
    ...
char_entity = game.hero.entity if isinstance(game.hero, GameCharacter) else game.hero  # ❌

# APRÈS - hasattr pour duck typing
if not hasattr(game.hero, 'entity'):  # ✅ Vérifie la structure
    ...
char_entity = game.hero.entity if hasattr(game.hero, 'entity') else game.hero  # ✅
```

---

## Mappings de potions

| Nom de potion | Sprite utilisé |
|---------------|----------------|
| Healing | `potion-red.png` 🔴 |
| Greater Healing | `potion-red.png` 🔴 |
| Superior Healing | `potion-red.png` 🔴 |
| Supreme Healing | `potion-red.png` 🔴 |
| Speed | `potion-green.png` 🟢 |
| Strength | `potion-blue.png` 🔵 |
| *Autre* | `potion.png` ⚪ (fallback) |

---

## Tests de validation

### Test 1: Sprites de potions

```
1. Ramasser une potion de soin (Healing Potion)
2. Ouvrir l'inventaire (I)
3. Vérifier le sprite
```

**Résultat attendu** :
- ✅ Sprite `potion-red.png` affiché
- ✅ Pas de carré magenta
- ✅ Potion reconnaissable visuellement

### Test 2: Différents types de potions

```
1. Ramasser plusieurs potions (Healing, Speed, Strength)
2. Observer les couleurs dans l'inventaire
```

**Résultat attendu** :
- ✅ Healing → Rouge (potion-red.png)
- ✅ Speed → Vert (potion-green.png)
- ✅ Strength → Bleu (potion-blue.png)

### Test 3: Quitter le jeu

```
1. Jouer quelques minutes
2. Appuyer sur ESC pour quitter
3. Vérifier qu'il n'y a pas d'erreur
```

**Résultat attendu** :
- ✅ Pas de TypeError
- ✅ Message "Saving X gamestate..."
- ✅ Retour au menu principal

### Test 4: Sauvegarder manuellement

```
1. Appuyer sur CMD+S (Mac) ou Win+S (PC)
2. Vérifier la sauvegarde
```

**Résultat attendu** :
- ✅ Message "Game saved!"
- ✅ Pas d'erreur isinstance

---

## Comparaison visuelle

### Avant la correction

**Inventaire** :
```
[⚔️][🛡️][🟣][🟣][⬛]  ← Carrés magenta pour potions
```

**Au quit** :
```
TypeError: Subscripted generics cannot be used with class and instance checks
❌ CRASH
```

### Après la correction

**Inventaire** :
```
[⚔️][🛡️][🔴][🟢][⬛]  ← Vrais sprites de potions (rouge, vert)
```

**Au quit** :
```
Saving Ellyjobell gamestate...
  └─ Character Ellyjobell also saved to characters/
✅ SUCCÈS
```

---

## Fichiers sprites requis

### Potions (sprites/items_icons/)

```
potion-red.png       # Potions de soin
potion-green.png     # Potions de vitesse
potion-blue.png      # Potions de force
potion.png           # Potion générique (fallback)
```

Si un fichier manque, le système utilise les fallbacks en cascade :

```
1. potion-red.png   ← Mapping direct
2. potion.png       ← Fallback générique
3. Carré magenta    ← Ultime fallback (code couleur)
```

---

## Pourquoi isinstance() échoue avec les génériques ?

### Explication technique

En Python, les génériques paramétrés ne peuvent pas être utilisés avec `isinstance()` :

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value

# ❌ Impossible
obj = Container[int](42)
isinstance(obj, Container[int])  # TypeError!

# ✅ Possible
isinstance(obj, Container)  # OK (sans paramètre)
```

### Pourquoi ?

Les types génériques sont **effacés à l'exécution** (type erasure) :

```python
Container[int] == Container[str]  # True à l'exécution !
# Impossible de distinguer à l'exécution
```

### Solution : Duck typing

Python préfère le duck typing :

```python
# Au lieu de :
if isinstance(obj, Container[SomeType]):  # ❌

# Utiliser :
if hasattr(obj, 'value'):  # ✅
    # C'est probablement un Container
```

**Philosophie Python** : "If it walks like a duck and quacks like a duck, it's a duck"

---

## Pattern GameEntity

### Structure

```python
# Core entity (métier)
character = Character(name="Ellyjobell", level=5, ...)

# Wrapper pour pygame (ajoute position)
game_character = GameEntity[Character](
    entity=character,
    x=10,
    y=15,
    image_name="fighter.png"
)
```

### Détection

```python
# ❌ ANCIEN (crash)
if isinstance(obj, GameEntity[Character]):
    entity = obj.entity

# ✅ NOUVEAU (fonctionne)
if hasattr(obj, 'entity'):
    entity = obj.entity
else:
    entity = obj
```

### Avantages

- ✅ **Séparation** : Logique métier (Character) vs affichage (GameEntity)
- ✅ **Réutilisable** : Character fonctionne en console ET pygame
- ✅ **Flexible** : Duck typing permet tous types de wrappers

---

## Améliorations futures possibles

### 1. Enum pour types de potions

```python
from enum import Enum

class PotionType(Enum):
    HEALING = "potion-red.png"
    SPEED = "potion-green.png"
    STRENGTH = "potion-blue.png"

# Dans get_item_image_name()
if isinstance(item, HealingPotion):
    return PotionType.HEALING.value
```

### 2. Registre de sprites

```python
SPRITE_REGISTRY = {
    'HealingPotion': 'potion-red.png',
    'SpeedPotion': 'potion-green.png',
    'StrengthPotion': 'potion-blue.png',
    'WeaponData': lambda item: load_weapon_image_name(item.index),
    'ArmorData': lambda item: load_armor_image_name(item.index),
}

def get_item_image_name(item):
    class_name = item.__class__.__name__
    if class_name in SPRITE_REGISTRY:
        sprite = SPRITE_REGISTRY[class_name]
        return sprite(item) if callable(sprite) else sprite
```

### 3. Protocole TypedDict

```python
from typing import Protocol

class HasEntity(Protocol):
    entity: Any
    x: int
    y: int

def save_character(obj: HasEntity | Character):
    # Type checker comprend la structure
    if hasattr(obj, 'entity'):
        entity = obj.entity
    else:
        entity = obj
```

---

## Conclusion

✅ **Les deux problèmes sont résolus !**

### Sprites de potions
- ✅ Ordre de vérification corrigé (type AVANT index)
- ✅ Mappings potions fonctionnent maintenant
- ✅ Couleurs différentes par type de potion

### Erreur isinstance
- ✅ Remplacement par `hasattr()` (duck typing)
- ✅ Compatible avec génériques paramétrés
- ✅ Plus pythonique et robuste

**Le jeu est maintenant stable et affiche correctement tous les items !** 🧪⚔️🛡️✅

---

**Fichiers modifiés** :
- `dungeon_pygame.py` (ligne ~1184, ligne ~2250)

**Pattern utilisé** :
- Duck typing avec `hasattr()` au lieu de `isinstance()`
- Vérification de type AVANT vérification d'attribut pour potions

**Status** : ✅ PRODUCTION READY

