# Fix: Sprites de potions + Drop d'items au sol

**Date**: 29 décembre 2024  
**Problèmes corrigés**:
1. Utiliser les vrais mappings de sprites de potions depuis `populate_rpg_functions.py`
2. Erreur AttributeError lors du drop d'items au sol : `'WeaponData' object has no attribute 'pos'`
**Statut**: ✅ CORRIGÉ

---

## Problème 1: Utilisation des vrais mappings de potions

### Contexte

Les associations de sprites pour les potions sont définies dans `populate_rpg_functions.py` dans la fonction `load_potion_image_name()` :

```python
# populate_rpg_functions.py - lignes 188-202
def load_potion_image_name(name: str) -> Optional[str]:
    potions = {
        'Healing': 'PotionShortRed',
        'Greater healing': 'PotionRed',
        'Superior healing': 'PotionTallRed',
        'Supreme healing': 'PotionTallRed2',
        'Speed': 'PotionShortBlue',
        'Hill Giant Strength': 'PotionTallBrown',
        'Frost Giant Strength': 'PotionTallSilver',
        'Stone Giant Strength': 'PotionTallGrey',
        'Fire Giant Strength': 'PotionTallYellow',
        'Cloud Giant Strength': 'PotionTallWhite',
        'Storm Giant Strength': 'PotionTallRuby'
    }
    image_name: str = potions.get(name)
    return image_name + '.PNG' if image_name else 'None.PNG'
```

### Problème

Dans `dungeon_pygame.py`, la fonction `get_item_image_name()` utilisait un **mapping manuel** différent et incomplet :

```python
# ❌ AVANT - Mapping manuel dans dungeon_pygame.py
if 'Potion' in item.__class__.__name__:
    potion_map = {
        'healing': 'potion-red.png',
        'greater healing': 'potion-red.png',
        'superior healing': 'potion-red.png',
        'supreme healing': 'potion-red.png',
        'speed': 'potion-green.png',
        'strength': 'potion-blue.png',
        # ...
    }
```

**Problèmes** :
- ❌ Duplication du code (2 endroits pour gérer les potions)
- ❌ Noms de fichiers différents (`potion-red.png` vs `PotionRed.PNG`)
- ❌ Mapping incomplet (manque les potions de force géante)
- ❌ Maintenance difficile

### Solution

**Utiliser la fonction officielle** `load_potion_image_name()` depuis `populate_rpg_functions.py` :

#### 1. Import de la fonction

```python
# dungeon_pygame.py - ligne 59
from populate_rpg_functions import (
    load_potions_collections, 
    load_weapon_image_name, 
    load_armor_image_name,
    load_potion_image_name  # ✅ Ajout
)
```

#### 2. Utilisation dans get_item_image_name()

```python
# ✅ APRÈS - Utilisation de la fonction officielle
if 'Potion' in item.__class__.__name__:
    # Use the official load_potion_image_name function
    potion_image = load_potion_image_name(
        item.name if hasattr(item, 'name') else 'Healing'
    )
    if potion_image and potion_image != 'None.PNG':
        return potion_image
    
    # Fallback for unknown potions
    return 'potion.png'
```

### Avantages

✅ **Source unique de vérité** : Un seul endroit pour gérer les mappings  
✅ **Cohérence** : Mêmes noms de fichiers partout  
✅ **Complet** : Toutes les potions supportées (healing, strength, giant strength, etc.)  
✅ **Maintenabilité** : Changement dans un seul fichier  
✅ **Extensibilité** : Facile d'ajouter de nouvelles potions

---

## Problème 2: AttributeError lors du drop d'items

### Erreur complète

```
Traceback (most recent call last):
  File "dungeon_pygame.py", line 1073, in drop
    self.add_to_level(item, image, level_sprites)
  File "dungeon_pygame.py", line 994, in add_to_level
    print(f'{item.name} dropped to ({item.pos})!')
                                     ^^^^^^^^
AttributeError: 'WeaponData' object has no attribute 'pos'
```

### Contexte

Les objets métier (`WeaponData`, `ArmorData`, `Potion`) du package `dnd-5e-core` **n'ont pas d'attribut `pos`**. Ils ont seulement `x` et `y` comme attributs de positionnement, mais pas de propriété calculée `pos` qui retourne `(x, y)`.

**Structure des objets** :

```python
# ✅ Classes métier (dnd-5e-core)
class WeaponData:
    x: int  # Position X
    y: int  # Position Y
    # Pas d'attribut pos !

# ✅ Wrapper pygame (game_entity.py)
class GameEntity:
    x: int
    y: int
    @property
    def pos(self) -> tuple:
        return (self.x, self.y)
```

### Endroits affectés

Le code utilisait `item.pos` à 3 endroits :

1. **Ligne 1018** : `print(f'{item.name} dropped to ({item.pos})!')` dans `add_to_level()`
2. **Ligne 1401** : `if item.pos not in game.level.visible_tiles:` dans `update_display()`
3. **Ligne 1405** : `if item.pos == game.pos:` dans `update_display()`

### Solution

Remplacer `item.pos` par `(item.x, item.y)` ou créer une variable locale `item_pos` :

#### 1. Dans add_to_level() - ligne 1018

```python
# ❌ AVANT
print(f'{item.name} dropped to ({item.pos})!')

# ✅ APRÈS
print(f'{item.name} dropped to ({item.x}, {item.y})!')
```

#### 2. Dans update_display() - lignes 1401-1405

```python
# ❌ AVANT
for item in game.level.items:
    try:
        if item.pos not in game.level.visible_tiles:
            continue
        # ...
        if item.pos == game.pos:
            # ...

# ✅ APRÈS
for item in game.level.items:
    try:
        # Items don't have pos attribute, use (x, y) tuple
        item_pos = (item.x, item.y)
        if item_pos not in game.level.visible_tiles:
            continue
        # ...
        if item_pos == game.pos:
            # ...
```

### Pourquoi ce problème ?

Pendant la migration vers `dnd-5e-core` :
- ✅ **Personnages et monstres** : Wrappés dans `GameEntity` → ont `.pos`
- ❌ **Items au sol** : Restent des objets simples → n'ont PAS `.pos`

**Stratégie** :
- Items dans l'**inventaire** : Pas besoin de position
- Items au **sol** : Ont `x`, `y` mais pas de propriété `pos`
- Monsters/Hero : Wrappés dans `GameEntity` avec propriété `pos`

---

## Comparaison des mappings de potions

### Anciens mappings (dungeon_pygame.py)

```python
# ❌ Mappings manuels incomplets
{
    'healing': 'potion-red.png',
    'greater healing': 'potion-red.png',
    'superior healing': 'potion-red.png',
    'supreme healing': 'potion-red.png',
    'speed': 'potion-green.png',
    'strength': 'potion-blue.png',
}
```

### Nouveaux mappings (populate_rpg_functions.py)

```python
# ✅ Mappings officiels complets
{
    'Healing': 'PotionShortRed.PNG',
    'Greater healing': 'PotionRed.PNG',
    'Superior healing': 'PotionTallRed.PNG',
    'Supreme healing': 'PotionTallRed2.PNG',
    'Speed': 'PotionShortBlue.PNG',
    'Hill Giant Strength': 'PotionTallBrown.PNG',
    'Frost Giant Strength': 'PotionTallSilver.PNG',
    'Stone Giant Strength': 'PotionTallGrey.PNG',
    'Fire Giant Strength': 'PotionTallYellow.PNG',
    'Cloud Giant Strength': 'PotionTallWhite.PNG',
    'Storm Giant Strength': 'PotionTallRuby.PNG'
}
```

### Différences visuelles

| Potion | Ancien sprite | Nouveau sprite | Différence |
|--------|---------------|----------------|------------|
| Healing | `potion-red.png` | `PotionShortRed.PNG` | ✅ Petite bouteille rouge |
| Greater Healing | `potion-red.png` | `PotionRed.PNG` | ✅ Bouteille moyenne rouge |
| Superior Healing | `potion-red.png` | `PotionTallRed.PNG` | ✅ Grande bouteille rouge |
| Supreme Healing | `potion-red.png` | `PotionTallRed2.PNG` | ✅ Très grande bouteille rouge |
| Speed | `potion-green.png` | `PotionShortBlue.PNG` | ✅ Bouteille bleue (pas verte!) |
| Hill Giant Strength | ❌ N/A | `PotionTallBrown.PNG` | ✅ Nouvelle potion |

**Note** : Les nouveaux sprites ont des **tailles variées** selon la puissance de la potion !

---

## Tests de validation

### Test 1: Drop d'item au sol

```
1. Ouvrir l'inventaire (I)
2. Clic droit sur une arme ou armure
3. L'item devrait tomber au sol
```

**Résultat attendu** :
```
✅ Message : "Longsword dropped to (15, 20)!"
✅ Pas d'erreur AttributeError
✅ Item visible au sol sur la carte
```

### Test 2: Ramasser un item au sol

```
1. Se déplacer sur un item au sol
2. L'item devrait être ramassé automatiquement
```

**Résultat attendu** :
```
✅ Message : "Hero gained an item! (Longsword) #42"
✅ Item apparaît dans l'inventaire
✅ Item disparaît du sol
```

### Test 3: Sprites de potions variés

```
1. Ouvrir plusieurs coffres pour obtenir différentes potions
2. Ouvrir l'inventaire (I)
3. Observer les sprites
```

**Résultat attendu** :
```
✅ Healing → PotionShortRed.PNG (petite bouteille rouge)
✅ Greater Healing → PotionRed.PNG (bouteille moyenne rouge)
✅ Superior Healing → PotionTallRed.PNG (grande bouteille rouge)
✅ Speed → PotionShortBlue.PNG (petite bouteille bleue)
✅ Potions de force géante → Couleurs variées
```

---

## Changements de code

### Fichier: dungeon_pygame.py

**1. Import de load_potion_image_name** (ligne 59)

```python
# AVANT
from populate_rpg_functions import (
    load_potions_collections,
    load_weapon_image_name,
    load_armor_image_name
)

# APRÈS
from populate_rpg_functions import (
    load_potions_collections,
    load_weapon_image_name,
    load_armor_image_name,
    load_potion_image_name  # ✅ Ajout
)
```

**2. Fonction get_item_image_name()** (ligne ~2320)

```python
# AVANT - Mapping manuel
if 'Potion' in item.__class__.__name__:
    potion_map = {
        'healing': 'potion-red.png',
        # ...
    }
    if item_name in potion_map:
        return potion_map[item_name]

# APRÈS - Utilisation de la fonction officielle
if 'Potion' in item.__class__.__name__:
    potion_image = load_potion_image_name(
        item.name if hasattr(item, 'name') else 'Healing'
    )
    if potion_image and potion_image != 'None.PNG':
        return potion_image
    return 'potion.png'
```

**3. Fonction add_to_level()** (ligne 1018)

```python
# AVANT
print(f'{item.name} dropped to ({item.pos})!')  # ❌ AttributeError

# APRÈS
print(f'{item.name} dropped to ({item.x}, {item.y})!')  # ✅
```

**4. Fonction update_display()** (lignes 1401-1405)

```python
# AVANT
for item in game.level.items:
    if item.pos not in game.level.visible_tiles:  # ❌
        continue
    if item.pos == game.pos:  # ❌
        # ...

# APRÈS
for item in game.level.items:
    item_pos = (item.x, item.y)  # ✅ Créer tuple
    if item_pos not in game.level.visible_tiles:
        continue
    if item_pos == game.pos:
        # ...
```

---

## Architecture de la solution

### Flux de chargement des sprites de potions

```
Potion créée
   ↓
get_item_image_name(potion)
   ↓
Détecte 'Potion' in class name
   ↓
Appelle load_potion_image_name(potion.name)
   ↓
Retourne 'PotionRed.PNG' (par exemple)
   ↓
Essaie de charger sprites/items_icons/PotionRed.PNG
   ↓
Si échec → Fallback carré magenta
   ↓
✅ Sprite affiché
```

### Flux de drop d'item

```
User clic droit sur item dans inventaire
   ↓
game.drop(item, image, sprites, level_sprites)
   ↓
game.add_to_level(item, image, level_sprites)
   ↓
Trouve position libre près du héros
   ↓
item.x, item.y = position
item.id = nouvel_id
   ↓
level_sprites[item.id] = image
game.level.items.append(item)
   ↓
print(f'{item.name} dropped to ({item.x}, {item.y})!')  # ✅
   ↓
✅ Item au sol, visible sur la carte
```

---

## Bugs corrigés

| Bug | Description | Statut |
|-----|-------------|--------|
| #1 | Mapping manuel de potions dupliqué | ✅ CORRIGÉ |
| #2 | Noms de sprites incohérents | ✅ CORRIGÉ |
| #3 | Potions manquantes (giant strength) | ✅ CORRIGÉ |
| #4 | AttributeError lors du drop d'item | ✅ CORRIGÉ |
| #5 | item.pos non existant pour WeaponData/ArmorData | ✅ CORRIGÉ |

---

## Fichiers de sprites requis

### Potions (sprites/items_icons/)

```
PotionShortRed.PNG      # Healing
PotionRed.PNG           # Greater healing
PotionTallRed.PNG       # Superior healing
PotionTallRed2.PNG      # Supreme healing
PotionShortBlue.PNG     # Speed
PotionTallBrown.PNG     # Hill Giant Strength
PotionTallSilver.PNG    # Frost Giant Strength
PotionTallGrey.PNG      # Stone Giant Strength
PotionTallYellow.PNG    # Fire Giant Strength
PotionTallWhite.PNG     # Cloud Giant Strength
PotionTallRuby.PNG      # Storm Giant Strength
```

**Fallback** : Si les fichiers PNG n'existent pas, des carrés magenta sont créés automatiquement.

---

## Améliorations futures

### 1. Ajouter propriété pos aux classes métier

Dans `dnd-5e-core`, ajouter une propriété `pos` :

```python
# dnd_5e_core/equipment/weapon.py
class WeaponData:
    x: int = 0
    y: int = 0
    
    @property
    def pos(self) -> tuple:
        return (self.x, self.y)
```

**Avantage** : Uniformité du code, utilisation de `item.pos` partout

### 2. Centraliser tous les mappings de sprites

Créer un fichier unique `sprite_mappings.py` :

```python
WEAPON_SPRITES = {
    'longsword': 'SwordLong.PNG',
    # ...
}

ARMOR_SPRITES = {
    'chain-mail': 'ArmorChainMailAugmented.PNG',
    # ...
}

POTION_SPRITES = {
    'Healing': 'PotionShortRed.PNG',
    # ...
}
```

**Avantage** : Source unique pour tous les sprites

---

## Conclusion

✅ **Les deux problèmes sont résolus !**

### Sprites de potions
- ✅ Utilisation de `load_potion_image_name()` depuis `populate_rpg_functions.py`
- ✅ Mappings officiels complets avec toutes les potions
- ✅ Sprites variés selon le type et la puissance

### Drop d'items
- ✅ Remplacement de `item.pos` par `(item.x, item.y)`
- ✅ Plus d'erreur AttributeError
- ✅ Items peuvent être déposés et ramassés sans crash

**Le jeu est maintenant stable et cohérent pour la gestion des items !** 🎮✨

---

**Fichiers modifiés** : `dungeon_pygame.py`  
**Lignes modifiées** : 59 (import), ~2320 (get_item_image_name), 1018 (add_to_level), 1401-1405 (update_display)  
**Pattern utilisé** : Centralisation des mappings, Duck typing pour les positions  
**Status** : ✅ PRODUCTION READY

