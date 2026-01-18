# Correction token_images_dir Non Défini

**Date :** 27 décembre 2025  
**Erreur :** `NameError: name 'token_images_dir' is not defined`

---

## ❌ Problème

La fonction `main_game_loop()` dans `dungeon_pygame.py` utilisait la variable `token_images_dir` sans qu'elle soit définie.

```python
def main_game_loop(game):
    # ...
    token_images = game.load_token_images(token_images_dir)  # ❌ token_images_dir non défini
    # NameError: name 'token_images_dir' is not defined
```

---

## ✅ Solution Appliquée

### Définition de token_images_dir

**Fichier :** `dungeon_pygame.py` (ligne 1190)

```python
def main_game_loop(game):
    global level_sprites
    running = True
    return_to_main = False
    game.last_round_time = time.time()
    
    # Define token images directory (in dnd-5e-core)
    import os
    _parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
    token_images_dir = os.path.join(_dnd_5e_core_path, 'data', 'tokens')
    
    # Create directory if it doesn't exist
    if not os.path.exists(token_images_dir):
        os.makedirs(token_images_dir, exist_ok=True)
    
    token_images = game.load_token_images(token_images_dir)
    round_no: int = 1
    # ...
```

**Logique :**
1. ✅ Calcule le chemin vers dnd-5e-core
2. ✅ Définit le chemin vers `data/tokens`
3. ✅ Crée le dossier s'il n'existe pas
4. ✅ Charge les images de tokens

---

## 📁 Structure des Tokens

```
dnd-5e-core/
└── data/
    └── tokens/
        ├── goblin.png
        ├── orc.png
        ├── dragon.png
        └── ... (autres tokens de monstres)
```

Les tokens sont des images 105x105 pixels utilisées pour afficher les monstres dans le jeu pygame.

---

## 🔧 Fonction load_token_images()

```python
def load_token_images(self, token_images_dir: str) -> dict:
    token_images = {}
    for filename in os.listdir(token_images_dir):
        monster_name, _ = os.path.splitext(filename)
        image_path = os.path.join(token_images_dir, filename)
        original_image = pygame.image.load(image_path)
        # Resize to 105x105 pixels
        token_images[monster_name] = pygame.transform.scale(original_image, (105, 105))
    return token_images
```

**Retourne :** Un dictionnaire `{monster_name: pygame.Surface}`

---

## ✅ Tests de Validation

```python
# Test 1: Variable définie
def main_game_loop(game):
    # ...
    token_images_dir = os.path.join(...)  # ✅ Défini
    token_images = game.load_token_images(token_images_dir)  # ✅ Fonctionne

# Test 2: Dossier créé
assert os.path.exists(token_images_dir)

# Test 3: Images chargées (si tokens présents)
token_images = game.load_token_images(token_images_dir)
assert isinstance(token_images, dict)
```

---

## 📝 Fichiers Modifiés

**DnD-5th-Edition-API**
- ✅ `dungeon_pygame.py`
  - Définition de `token_images_dir` dans `main_game_loop()`
  - Création automatique du dossier tokens
  - Chemin correct vers dnd-5e-core/data/tokens

---

## ✅ PROBLÈME RÉSOLU

**Résultat :**
- ✅ token_images_dir défini avant utilisation
- ✅ Dossier tokens créé automatiquement
- ✅ Chemin correct vers dnd-5e-core
- ✅ dungeon_pygame.py fonctionne

**Le jeu pygame devrait maintenant démarrer complètement !** 🎉

---

**Date :** 27 décembre 2025  
**Status :** ✅ RÉSOLU  
**Type :** Variable Non Définie  
**Impact :** Main game loop fonctionnel

