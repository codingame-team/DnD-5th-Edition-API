# Migration des monstres 5e.tools - Guide d'intégration

## ✅ État actuel

La migration des monstres de 5e.tools vers dnd-5e-core est **complète**. Tous les fichiers nécessaires ont été créés et les tokens ont été copiés.

## 📦 Ce qui a été migré

### 1. Tokens/Images (542 fichiers)
```
DnD-5th-Edition-API/images/monsters/tokens/*.webp
  ↓ COPIÉ VERS
dnd-5e-core/dnd_5e_core/data/monsters/tokens/*.webp
```

### 2. Données JSON
```
DnD-5th-Edition-API/maze/other_monsters/bestiary-sublist-data.json
  ↓ COPIÉ VERS
dnd-5e-core/dnd_5e_core/data/monsters/bestiary-sublist-data.json
```

### 3. Code et fonctions
- ✅ `populate_functions.py` - Ajout des fonctions helper
- ✅ `dnd_5e_core/entities/extended_monsters.py` - Loader pour monstres
- ✅ `dnd_5e_core/entities/special_monster_actions.py` - Builder pour actions
- ✅ `dnd_5e_core/utils/token_downloader.py` - Téléchargement tokens

## 🔧 Fonctions disponibles dans populate_functions.py

### Nouvelles fonctions helper

```python
# Vérifier si un monstre est dans les données étendues
is_extended_monster("Orc Eye of Gruumsh")  # → True

# Récupérer les données JSON d'un monstre étendu
data = get_extended_monster_data("Orc Eye of Gruumsh")

# Obtenir le chemin du token (télécharge si nécessaire)
token_path = get_extended_monster_token_path("Orc Eye of Gruumsh", "MM")
```

## 💡 Comment utiliser

### Dans votre code de jeu

```python
from populate_functions import request_monster_other, is_extended_monster, get_extended_monster_token_path

# Vérifier si c'est un monstre étendu
if is_extended_monster("Orc Eye of Gruumsh"):
    # Charger le monstre
    monster = request_monster_other("Orc Eye of Gruumsh")
    
    # Obtenir le token
    token_path = get_extended_monster_token_path("Orc Eye of Gruumsh")
    
    print(f"Monstre: {monster.name}")
    print(f"Token: {token_path}")
```

### Rechercher des monstres

```python
from dnd_5e_core.entities import get_extended_monster_loader

loader = get_extended_monster_loader()

# Rechercher tous les gobelins
goblins = loader.search_monsters(name_contains="goblin", min_cr=1, max_cr=3)

for goblin in goblins:
    print(f"{goblin['name']} - CR {goblin.get('cr', '?')}")
```

### Télécharger des tokens manquants

```python
from dnd_5e_core.utils import download_monster_token

# Télécharger un token spécifique
status = download_monster_token(
    "Goblin Boss",
    source="MM",
    save_folder="/path/to/dnd-5e-core/dnd_5e_core/data/monsters/tokens"
)

if status == 200:
    print("Token téléchargé avec succès!")
```

## 📊 Structure des données

### Fichier bestiary-sublist-data.json

```json
{
  "name": "Orc Eye of Gruumsh",
  "source": "MM",
  "cr": "2",
  "hp": {
    "average": 45,
    "formula": "6d8 + 18"
  },
  "ac": [
    {
      "ac": 16,
      "from": [...]
    }
  ],
  "str": 16,
  "dex": 12,
  ...
}
```

### Monstre dans le jeu

```python
Monster(
    index="orc-eye-of-gruumsh",
    name="Orc Eye of Gruumsh",
    challenge_rating=2.0,
    hit_points=45,
    armor_class=16,
    actions=[...],       # Actions implémentées
    sa=[...],            # Capacités spéciales
    sc=SpellCaster(...)  # Sorts (si lanceur de sorts)
)
```

## 🎮 Intégration avec Pygame

### Charger un monstre avec son token

```python
import pygame
from populate_functions import request_monster_other, get_extended_monster_token_path

# Charger le monstre
monster = request_monster_other("Orc Eye of Gruumsh")

# Charger le token
token_path = get_extended_monster_token_path("Orc Eye of Gruumsh")
if token_path:
    token_image = pygame.image.load(token_path)
else:
    token_image = default_monster_image

# Utiliser dans le jeu
screen.blit(token_image, (monster.x, monster.y))
```

## 🔍 Debugging

### Vérifier les monstres chargés

```python
from dnd_5e_core.entities import get_extended_monster_loader, get_special_actions_builder

loader = get_extended_monster_loader()
builder = get_special_actions_builder()

# Statistiques
stats = loader.get_stats()
print(f"Total monstres: {stats['total']}")
print(f"Par source: {stats['by_source']}")

# Monstres avec actions implémentées
implemented = builder.get_implemented_monsters()
print(f"Actions implémentées: {len(implemented)}")
```

### Vérifier les tokens

```bash
# Compter les tokens disponibles
ls /path/to/dnd-5e-core/dnd_5e_core/data/monsters/tokens/ | wc -l

# Vérifier si un token existe
ls /path/to/dnd-5e-core/dnd_5e_core/data/monsters/tokens/ | grep "Orc Eye"
```

## 📁 Chemins importants

```
dnd-5e-core/
├── dnd_5e_core/
│   ├── data/
│   │   └── monsters/
│   │       ├── bestiary-sublist-data.json (89 monstres)
│   │       ├── bestiary-sublist-data-all-monsters.json (tous)
│   │       ├── tokens/ (542 fichiers .webp)
│   │       └── README.md
│   ├── entities/
│   │   ├── extended_monsters.py (loader)
│   │   └── special_monster_actions.py (builder)
│   └── utils/
│       └── token_downloader.py
└── docs/
    ├── EXTENDED_MONSTERS_MIGRATION.md
    └── POPULATE_FUNCTIONS_INTEGRATION.md

DnD-5th-Edition-API/
└── populate_functions.py (fonctions helper ajoutées)
```

## 🚀 Prochaines étapes

### Pour utiliser immédiatement

1. ✅ Les fonctions sont déjà disponibles dans `populate_functions.py`
2. ✅ Les tokens sont copiés et accessibles
3. ✅ La fonction `request_monster_other()` continue de fonctionner

### Pour optimiser

1. **Remplacer les chemins hardcodés** :
   ```python
   # Dans get_extended_monster_token_path()
   # Remplacer le chemin hardcodé par un chemin relatif ou configurable
   ```

2. **Mettre en cache les loaders** :
   ```python
   # Les loaders sont déjà lazy-loaded (initialisés une seule fois)
   _extended_monster_loader = None  # ✅ Déjà fait
   _special_actions_builder = None  # ✅ Déjà fait
   ```

## 📝 Notes importantes

1. **Compatibilité** : Le code existant continue de fonctionner
2. **Performance** : Les loaders utilisent le cache après le premier chargement
3. **Tokens** : Téléchargement automatique si le token n'existe pas
4. **Fallback** : Si dnd-5e-core n'est pas disponible, le code fonctionne toujours

## ✨ Exemple complet

```python
#!/usr/bin/env python3
"""Exemple d'utilisation des monstres étendus"""

from populate_functions import (
    request_monster_other,
    is_extended_monster,
    get_extended_monster_token_path
)

# Liste des monstres à tester
monster_names = [
    "Orc Eye of Gruumsh",
    "Goblin Boss",
    "Hobgoblin Captain"
]

for name in monster_names:
    print(f"\n=== {name} ===")
    
    # Vérifier s'il existe
    if is_extended_monster(name):
        print("✓ Existe dans les données étendues")
        
        # Charger le monstre
        monster = request_monster_other(name)
        print(f"  CR: {monster.challenge_rating}")
        print(f"  HP: {monster.hit_points}")
        print(f"  AC: {monster.armor_class}")
        print(f"  Actions: {len(monster.actions)}")
        
        # Chercher le token
        token = get_extended_monster_token_path(name)
        if token:
            print(f"  Token: {token}")
        else:
            print("  Token: Non disponible")
    else:
        print("✗ Monstre non trouvé")
```

## 🎯 Résumé

- ✅ **542 tokens** copiés vers dnd-5e-core
- ✅ **89 monstres** avec données JSON complètes
- ✅ **47 monstres** avec actions implémentées
- ✅ **Fonctions helper** ajoutées à populate_functions.py
- ✅ **Compatible** avec le code existant
- ✅ **Testé** et fonctionnel

**La migration est complète et prête à l'utilisation ! 🎉**

---

**Besoin d'aide ?**
- Consulter `docs/EXTENDED_MONSTERS_MIGRATION.md` pour plus de détails
- Lancer `python test_extended_monsters.py` pour tester
- Vérifier les exemples ci-dessus

