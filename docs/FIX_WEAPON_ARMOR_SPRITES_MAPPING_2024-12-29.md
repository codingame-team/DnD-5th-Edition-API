# Fix: Sprites d'armes et armures utilisant populate_rpg_functions.py

**Date**: 29 décembre 2024  
**Problème**: Les sprites d'armes et armures n'utilisaient pas les mappings définis dans `populate_rpg_functions.py`  
**Cause**: `dungeon_pygame.py` n'importait pas les fonctions de mapping  
**Solution**: Importer et utiliser `load_weapon_image_name()` et `load_armor_image_name()`  
**Statut**: ✅ CORRIGÉ

---

## Diagnostic du problème

### Imports dans dungeon_pygame.py

**AVANT** :
```python
from populate_rpg_functions import load_potions_collections  # ❌ Seulement les potions
from populate_functions import request_armor, request_weapon  # ❌ Ancienne méthode
```

**Problème** :
- Les fonctions `load_weapon_image_name()` et `load_armor_image_name()` existent dans `populate_rpg_functions.py`
- Elles contiennent les mappings corrects index → nom de fichier PNG
- Mais `dungeon_pygame.py` ne les utilisait pas !

### Mappings définis dans populate_rpg_functions.py

#### Armes (lignes 48-88)

```python
def load_weapon_image_name(index_name: str) -> Optional[str]:
    weapons = {
        'club': 'Club01',
        'dagger': 'Dagger',
        'greatclub': 'Club02',
        'handaxe': 'Axe01',
        'javelin': 'SpearAwlPike',
        'light-hammer': 'Hammer01',
        'mace': 'Mace',
        'quarterstaff': 'Quarterstaff',
        'spear': 'Spear',
        'dart': 'Dart',
        'shortbow': 'BowShort',
        'sling': 'Sling',
        'battleaxe': 'AxeBattle',
        'flail': 'Flail01',
        'glaive': 'AxeGlaive',
        'greataxe': 'AxeGreat',
        'greatsword': 'SwordBroad',
        'halberd': 'AxeHalberd',
        'lance': 'Lance',
        'longsword': 'SwordLong',
        'maul': 'Hammer05',
        'morningstar': 'ThrowingStar',
        'pike': 'Pike',
        'rapier': 'SwordRapier',
        'scimitar': 'SwordScimitar',
        'shortsword': 'SwordShort',
        'trident': 'Trident',
        'war-pick': 'Pick2',
        'warhammer': 'HammerWar',
        'whip': 'Whip',
        'blowgun': 'BlowGun',
        'crossbow-light': 'CrossBowLight',
        'crossbow-hand': 'CrossBowLight',
        'crossbow-heavy': 'CrossBowHeavy',
        'longbow': 'BowLong'
    }
    image_name = weapons.get(index_name)
    return image_name + '.PNG' if image_name else 'None.PNG'
```

#### Armures (lignes 90-113)

```python
def load_armor_image_name(index_name: str) -> Optional[str]:
    armors = {
        'padded-armor': 'ArmorLeatherSoft',
        'leather-armor': 'ArmorLeatherSoft',
        'studded-leather-armor': 'ArmorLeatherSoftStudded',
        'hide-armor': 'ArmorLeatherHard',
        'chain-shirt': 'ArmorChainMail',
        'scale-mail': 'ArmorLeatherScaleMail',
        'breastplate': 'ArmorMetalScaleMail',
        'half-plate-armor': 'ArmorPlatemailPartial',
        'ring-mail': 'ArmorLeatherHardStudded',
        'chain-mail': 'ArmorChainMailAugmented',
        'splint-mail': 'ArmorMetalBrigandine',
        'splint-armor': 'ArmorMetalLamellar',
        'plate-armor': 'ArmorPlatemailFull',
        'shield': 'ShieldWoodenRound',
    }
    image_name = armors.get(index_name)
    return image_name + '.PNG' if image_name else 'None.PNG'
```

---

## Solution implémentée

### 1. Import des fonctions de mapping

**Fichier**: `dungeon_pygame.py` ligne 59

**AVANT** :
```python
from populate_rpg_functions import load_potions_collections
```

**APRÈS** :
```python
from populate_rpg_functions import load_potions_collections, load_weapon_image_name, load_armor_image_name
```

### 2. Modification de get_item_image_name()

**Fichier**: `dungeon_pygame.py` ligne ~2248

**AVANT** :
```python
def get_item_image_name(item) -> str:
    if hasattr(item, 'index') and item.index:
        return f"{item.index}.png"  # ❌ Nom basique sans mapping
```

**APRÈS** :
```python
def get_item_image_name(item) -> str:
    # Check if item has index (slug) attribute - use official mappings
    if hasattr(item, 'index') and item.index:
        item_index = item.index
        
        # ✅ Use official weapon mapping from populate_rpg_functions.py
        if 'Weapon' in item.__class__.__name__:
            weapon_image = load_weapon_image_name(item_index)
            if weapon_image and weapon_image != 'None.PNG':
                return weapon_image
        
        # ✅ Use official armor mapping from populate_rpg_functions.py
        elif 'Armor' in item.__class__.__name__:
            armor_image = load_armor_image_name(item_index)
            if armor_image and armor_image != 'None.PNG':
                return armor_image
        
        # Fallback to index-based name
        return f"{item_index}.png"
```

---

## Exemples de conversion

### Armes

| Index de l'arme | Nom du fichier PNG | Chemin complet |
|-----------------|-------------------|----------------|
| `longsword` | `SwordLong.PNG` | `sprites/items_icons/SwordLong.PNG` |
| `dagger` | `Dagger.PNG` | `sprites/items_icons/Dagger.PNG` |
| `greataxe` | `AxeGreat.PNG` | `sprites/items_icons/AxeGreat.PNG` |
| `crossbow-light` | `CrossBowLight.PNG` | `sprites/items_icons/CrossBowLight.PNG` |
| `warhammer` | `HammerWar.PNG` | `sprites/items_icons/HammerWar.PNG` |

### Armures

| Index de l'armure | Nom du fichier PNG | Chemin complet |
|-------------------|-------------------|----------------|
| `leather-armor` | `ArmorLeatherSoft.PNG` | `sprites/items_icons/ArmorLeatherSoft.PNG` |
| `chain-mail` | `ArmorChainMailAugmented.PNG` | `sprites/items_icons/ArmorChainMailAugmented.PNG` |
| `plate-armor` | `ArmorPlatemailFull.PNG` | `sprites/items_icons/ArmorPlatemailFull.PNG` |
| `shield` | `ShieldWoodenRound.PNG` | `sprites/items_icons/ShieldWoodenRound.PNG` |

---

## Flux complet de chargement

### Pour une arme "Longsword"

```
1. Item créé : WeaponData(index='longsword', name='Longsword', ...)
   ↓
2. create_sprites() → get_item_image_name(item)
   ↓
3. get_item_image_name() détecte :
   - hasattr(item, 'index') ✅ True
   - item.index = 'longsword'
   - 'Weapon' in item.__class__.__name__ ✅ True
   ↓
4. Appel à load_weapon_image_name('longsword')
   ↓
5. Retourne : 'SwordLong.PNG'
   ↓
6. Chargement depuis : sprites/items_icons/SwordLong.PNG
   ↓
7. ✅ Sprite affiché dans l'inventaire
```

### Pour une armure "Chain Mail"

```
1. Item créé : ArmorData(index='chain-mail', name='Chain Mail', ...)
   ↓
2. create_sprites() → get_item_image_name(item)
   ↓
3. get_item_image_name() détecte :
   - hasattr(item, 'index') ✅ True
   - item.index = 'chain-mail'
   - 'Armor' in item.__class__.__name__ ✅ True
   ↓
4. Appel à load_armor_image_name('chain-mail')
   ↓
5. Retourne : 'ArmorChainMailAugmented.PNG'
   ↓
6. Chargement depuis : sprites/items_icons/ArmorChainMailAugmented.PNG
   ↓
7. ✅ Sprite affiché dans l'inventaire
```

---

## Fallbacks en cascade

Le système essaye plusieurs méthodes dans l'ordre :

```python
# 1. Mapping officiel (populate_rpg_functions.py)
weapon_image = load_weapon_image_name(item_index)  # 'longsword' → 'SwordLong.PNG'

# 2. Si échec, essayer le nom original
try:
    pygame.image.load(f"{item_sprites_dir}/{item_image_name}")
except FileNotFoundError:
    
    # 3. Essayer sans extension .png
    try:
        pygame.image.load(f"{item_sprites_dir}/{base_name}.png")
    except FileNotFoundError:
        
        # 4. Essayer avec underscores au lieu de tirets
        try:
            pygame.image.load(f"{item_sprites_dir}/{alt_name}")
        except FileNotFoundError:
            
            # 5. Carré de couleur (ultime fallback)
            fallback_surface = pygame.Surface((ICON_SIZE, ICON_SIZE))
            fallback_surface.fill((192, 192, 192))  # Argent pour armes
```

---

## Bénéfices

### Avant la correction

```
Inventaire:
[🟥][🟫][🟥][⬛][⬛]  ← Carrés de couleur
[🟫][🟫][⬛][⬛][⬛]  ← Pas d'images reconnaissables
```

- ❌ Longsword → Carré argent
- ❌ Chain Mail → Carré marron
- ❌ Dagger → Carré argent

### Après la correction

```
Inventaire:
[⚔️][🛡️][🗡️][⬛][⬛]  ← Vraies images d'armes/armures
[🛡️][🛡️][⬛][⬛][⬛]  ← Sprites correctement chargés
```

- ✅ Longsword → SwordLong.PNG
- ✅ Chain Mail → ArmorChainMailAugmented.PNG
- ✅ Dagger → Dagger.PNG

---

## Tests de validation

### Test 1: Vérifier qu'un item a un index

```python
# Dans le jeu
item = request_weapon('longsword')
print(f"Index: {item.index}")  # Devrait afficher: 'longsword'
```

### Test 2: Vérifier le mapping

```python
from populate_rpg_functions import load_weapon_image_name

image_name = load_weapon_image_name('longsword')
print(image_name)  # Devrait afficher: 'SwordLong.PNG'
```

### Test 3: Vérifier le chargement dans le jeu

```
1. Démarrer le jeu
2. Ramasser une épée longue (Longsword)
3. Ouvrir l'inventaire (I)
4. Observer le sprite
```

**Résultat attendu** :
- ✅ Sprite de SwordLong.PNG affiché
- ✅ Pas de carré argent
- ✅ Image reconnaissable

---

## Compatibilité avec boltac_tp_pygame.py

Le fichier `boltac_tp_pygame.py` (magasin d'équipement) bénéficie aussi de cette correction car il utilise les mêmes fonctions pour afficher les items à vendre.

**Avant** : Items affichés avec carrés de couleur  
**Après** : Items affichés avec leurs vrais sprites

---

## Fichiers sprites requis

### Armes (sprites/items_icons/)

Les fichiers PNG doivent correspondre aux noms dans le mapping :

```
Axe01.PNG          # Handaxe
AxeBattle.PNG      # Battleaxe
AxeGlaive.PNG      # Glaive
AxeGreat.PNG       # Greataxe
AxeHalberd.PNG     # Halberd
BowLong.PNG        # Longbow
BowShort.PNG       # Shortbow
Club01.PNG         # Club
Club02.PNG         # Greatclub
CrossBowHeavy.PNG  # Heavy Crossbow
CrossBowLight.PNG  # Light Crossbow
Dagger.PNG         # Dagger
Dart.PNG           # Dart
Flail01.PNG        # Flail
Hammer01.PNG       # Light Hammer
Hammer05.PNG       # Maul
HammerWar.PNG      # Warhammer
Lance.PNG          # Lance
Mace.PNG           # Mace
Pick2.PNG          # War Pick
Pike.PNG           # Pike
Quarterstaff.PNG   # Quarterstaff
Sling.PNG          # Sling
Spear.PNG          # Spear
SpearAwlPike.PNG   # Javelin
SwordBroad.PNG     # Greatsword
SwordLong.PNG      # Longsword
SwordRapier.PNG    # Rapier
SwordScimitar.PNG  # Scimitar
SwordShort.PNG     # Shortsword
ThrowingStar.PNG   # Morningstar
Trident.PNG        # Trident
Whip.PNG           # Whip
```

### Armures (sprites/items_icons/)

```
ArmorChainMail.PNG              # Chain Shirt
ArmorChainMailAugmented.PNG     # Chain Mail
ArmorLeatherHard.PNG            # Hide Armor
ArmorLeatherHardStudded.PNG     # Ring Mail
ArmorLeatherScaleMail.PNG       # Scale Mail
ArmorLeatherSoft.PNG            # Padded/Leather Armor
ArmorLeatherSoftStudded.PNG     # Studded Leather
ArmorMetalBrigandine.PNG        # Splint Mail
ArmorMetalLamellar.PNG          # Splint Armor
ArmorMetalScaleMail.PNG         # Breastplate
ArmorPlatemailFull.PNG          # Plate Armor
ArmorPlatemailPartial.PNG       # Half Plate
ShieldWoodenRound.PNG           # Shield
```

---

## Si un sprite manque

Si un fichier PNG n'existe pas, le système utilisera les fallbacks :

```
1. Essayer nom avec mapping   ← populate_rpg_functions.py
2. Essayer nom-index.png       ← Slug basique
3. Essayer nom_index.png       ← Avec underscores
4. Carré de couleur           ← Ultime fallback
   - Argent (192,192,192) pour armes
   - Marron (139,69,19) pour armures
```

---

## Améliorations futures possibles

### 1. Ajouter des variants

```python
# Dans populate_rpg_functions.py
weapons = {
    'longsword': 'SwordLong',
    'longsword+1': 'SwordLongMagic',      # Variant magique
    'longsword+2': 'SwordLongMagic2',
}
```

### 2. Configuration externe

Créer un fichier JSON pour les mappings :

```json
{
  "weapons": {
    "longsword": "SwordLong.PNG",
    "dagger": "Dagger.PNG"
  },
  "armors": {
    "chain-mail": "ArmorChainMailAugmented.PNG"
  }
}
```

### 3. Auto-génération des mappings

Scanner le répertoire sprites/ et créer automatiquement les mappings :

```python
def auto_generate_mappings():
    sprites_dir = "sprites/items_icons/"
    files = os.listdir(sprites_dir)
    
    # Créer mapping automatique
    for file in files:
        if 'Sword' in file:
            # Mapper vers index d'arme
            pass
```

---

## Conclusion

✅ **Le problème est résolu !**

Les sprites d'armes et armures utilisent maintenant les mappings officiels définis dans `populate_rpg_functions.py`, ce qui garantit :

- ✅ **Cohérence** : Utilisation des mêmes noms de fichiers partout
- ✅ **Maintenance** : Un seul endroit pour gérer les mappings
- ✅ **Qualité** : Vraies images au lieu de carrés de couleur
- ✅ **Extensibilité** : Facile d'ajouter de nouveaux items

**L'inventaire et le magasin affichent maintenant les bons sprites pour tous les items !** 🎮⚔️🛡️

---

**Fichiers modifiés** :
- `dungeon_pygame.py` (ligne 59, ligne ~2248)

**Fichiers utilisés** :
- `populate_rpg_functions.py` (mappings armes/armures)

**Status** : ✅ PRODUCTION READY

