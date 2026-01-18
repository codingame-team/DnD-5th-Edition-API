# Migration vers dnd-5e-core ✅

## Vue d'ensemble

Le projet DnD-5th-Edition-API a été **adapté avec succès** pour utiliser le package `dnd-5e-core` pour le chargement des données D&D 5e.

**Statut** : ✅ Migration complète et fonctionnelle

## Modifications apportées

### 1. populate_functions.py ✅

Le fichier `populate_functions.py` a été mis à jour pour :

- **Importer depuis dnd-5e-core** : Les classes et types de données sont maintenant importés depuis le package `dnd-5e-core` au lieu de `dao_classes`
- **Utiliser les loaders de dnd-5e-core** : Les fonctions de chargement des données JSON utilisent maintenant les loaders de `dnd-5e-core.data`
- **Fallback automatique** : Si `dnd-5e-core` n'est pas disponible, le système bascule automatiquement sur le chargement local des fichiers JSON

#### Imports mis à jour

```python
# Ancien
from dao_classes import Monster, Weapon, Armor, ...

# Nouveau
from dnd_5e_core.entities import Monster
from dnd_5e_core.equipment import Weapon, Armor, ...
from dnd_5e_core.spells import Spell, SpellCaster
from dnd_5e_core.combat import Action, ActionType, Damage, ...
from dnd_5e_core.abilities import Abilities, AbilityType
from dnd_5e_core.mechanics import DamageDice
```

#### Fonction helper `_load_json_data()`

Une nouvelle fonction helper a été ajoutée pour centraliser le chargement des données :

```python
def _load_json_data(category: str, index_name: str) -> dict:
    """
    Helper function to load JSON data from dnd-5e-core or local files.
    
    Priorité :
    1. Essaie d'utiliser les loaders de dnd-5e-core (core_load_monster, core_load_spell, etc.)
    2. Si échec, bascule sur le chargement direct des fichiers JSON locaux
    """
```

#### Fonctions mises à jour ✅

Toutes les fonctions `request_*` ont été mises à jour pour utiliser `_load_json_data()` :

- ✅ `request_damage_type()` - Types de dégâts
- ✅ `request_condition()` - Conditions
- ✅ `request_monster()` - Monstres
- ✅ `request_spell()` - Sorts
- ✅ `request_armor()` - Armures
- ✅ `request_weapon()` - Armes
- ✅ `request_weapon_property()` - Propriétés d'armes
- ✅ `request_trait()` - Traits raciaux
- ✅ `request_race()` - Races
- ✅ `request_subrace()` - Sous-races
- ✅ `request_language()` - Langues
- ✅ `request_proficiency()` - Maîtrises
- ✅ `request_equipment_category()` - Catégories d'équipement
- ✅ `request_equipment()` - Équipements
- ✅ `request_class()` - Classes

### 2. populate_rpg_functions.py ✅

Le fichier `populate_rpg_functions.py` a également été mis à jour pour importer les classes de potions depuis `dnd-5e-core.equipment`.

## Configuration

### Chemins des données

Le système configure automatiquement les répertoires de données pour `dnd-5e-core` :

```python
_base_path = os.path.dirname(__file__)
set_data_directory(os.path.join(_base_path, 'data'))
set_collections_directory(os.path.join(_base_path, 'collections'))
```

Cela permet à `dnd-5e-core` d'utiliser les fichiers de données locaux du projet DnD-5th-Edition-API.

## Tests et validation ✅

### Test d'import
```bash
python3 -c "import populate_functions; print(populate_functions.USE_DND_5E_CORE)"
# Résultat : True
```

### Test des collections
```bash
python3 -c "
import populate_functions
monsters = populate_functions.populate('monsters', 'results')
print(f'Loaded {len(monsters)} monsters')
"
# Résultat : Loaded 332 monsters
```

### Tests des fonctions request_*

| Fonction | Test | Résultat |
|----------|------|----------|
| `populate('monsters')` | 332 items | ✅ |
| `populate('spells')` | 319 items | ✅ |
| `populate('classes')` | 12 items | ✅ |
| `populate('races')` | 9 items | ✅ |
| `populate('equipment')` | 237 items | ✅ |
| `request_damage_type('slashing')` | Slashing | ✅ |
| `request_condition('blinded')` | Blinded | ✅ |
| `request_spell('fireball')` | Fireball | ✅ |
| `request_race('elf')` | Elf | ✅ |
| `request_class('fighter')` | Fighter | ✅ |
| `request_monster('aboleth')` | Aboleth (CR 10) | ✅ |

## Avantages

1. **Code partagé** ✅ : Les classes de données sont maintenant partagées entre tous les projets D&D 5e
2. **Maintenance simplifiée** ✅ : Les corrections et améliorations dans `dnd-5e-core` bénéficient à tous les projets
3. **Compatibilité** ✅ : Le système reste compatible avec les fichiers de données existants
4. **Fallback** ✅ : En cas de problème avec `dnd-5e-core`, le système bascule automatiquement sur le mode local
5. **Séparation des responsabilités** ✅ : La logique du jeu est séparée du positionnement 2D (Sprite)

## Note importante : Séparation Logique/UI

Les classes dans `dnd-5e-core` (Monster, Weapon, Armor) contiennent **uniquement la logique du jeu** et ne gèrent pas le positionnement 2D.

### Ancien système
```python
class Monster(Sprite):  # Hérite de Sprite
    id: int
    x: int
    y: int
    image_name: str
    # ... + logique du jeu
```

### Nouveau système
```python
# dnd-5e-core : Logique pure
@dataclass
class Monster:
    index: str
    name: str
    armor_class: int
    # ... logique du jeu uniquement

# UI layer (dungeon_pygame.py) : Wrapper pour le positionnement
class DungeonMonster(Sprite):
    def __init__(self, monster: Monster, x: int, y: int):
        self.monster = monster  # Contient la logique
        self.x = x
        self.y = y
        # ... gestion du positionnement 2D
```

## Prochaines étapes recommandées

Pour les projets qui utilisent le positionnement 2D (dungeon_pygame.py) :

1. ✅ Adapter `populate_functions.py` (FAIT)
2. ⏳ Créer des classes wrapper dans dungeon_pygame.py :
   - `DungeonMonster(Sprite)` qui contient un `Monster`
   - `DungeonWeapon(Sprite)` qui contient un `Weapon`
   - `DungeonArmor(Sprite)` qui contient un `Armor`
3. ⏳ Mettre à jour les autres fichiers du projet pour utiliser ces wrappers

## Fichiers migrés

- ✅ `populate_functions.py` - Fonctions de chargement de données
- ✅ `populate_rpg_functions.py` - Fonctions RPG auxiliaires
- ✅ `main.py` - Déjà migré précédemment

## Notes techniques

- Le flag `USE_DND_5E_CORE` indique si le package est disponible et utilisé
- Les fichiers de données locaux (`data/` et `collections/`) sont toujours nécessaires
- La migration est transparente pour le code qui utilise `populate_functions.py`
- Le système gère automatiquement le fallback vers le chargement local si dnd-5e-core n'est pas disponible

## Date de migration

Migration effectuée le : 24 décembre 2024

