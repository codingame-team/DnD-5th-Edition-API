# Debug: Fog of War - Nouvelles tuiles restent invisibles

**Date**: 29 décembre 2024  
**Problème**: Les nouvelles tuiles visibles restent dans le fog of war  
**Approche**: Debug détaillé pour identifier la cause  
**Statut**: 🔍 EN DEBUG

## Debug ajouté

### 1. Dans `update_visible_tiles()`

```python
def update_visible_tiles(self, vision_range: int = 10):
    # Reset visible tiles
    self.level.visible_tiles = set()
    
    view_x, view_y, view_width, view_height = self.calculate_view_window()
    print(f"[DEBUG] Hero pos: {self.pos}, view window: ({view_x}, {view_y}, {view_width}, {view_height})")
    
    tiles_checked = 0
    tiles_in_range = 0
    tiles_visible = 0
    
    for x in range(view_x, view_x + view_width):
        for y in range(view_y, view_y + view_height):
            tiles_checked += 1
            distance = dist((x, y), self.pos)
            if distance > vision_range:
                continue
            tiles_in_range += 1
            
            if in_view_range(*self.pos, x, y, obstacles=self.level.obstacles):
                self.level.visible_tiles.add((x, y))
                tiles_visible += 1
    
    print(f"[DEBUG] Tiles checked: {tiles_checked}, in range: {tiles_in_range}, visible: {tiles_visible}")
    print(f"[DEBUG] visible_tiles size: {len(self.level.visible_tiles)}")
    if len(self.level.visible_tiles) > 0:
        sample = list(self.level.visible_tiles)[:5]
        print(f"[DEBUG] Sample visible tiles: {sample}")
```

**Ce qui est tracé** :
- Position du héros
- Fenêtre de vue (view window)
- Nombre de tuiles vérifiées
- Nombre de tuiles dans le rayon de vision
- Nombre de tuiles réellement visibles (ligne de vue dégagée)
- Taille de l'ensemble `visible_tiles`
- Échantillon des premières tuiles visibles

### 2. Dans `draw_map()`

```python
def draw_map(self, path, screen):
    # ...load sprites...
    
    # Debug counters
    visible_count = 0
    explored_count = 0
    unknown_count = 0
    
    for y in range(view_y, view_y + view_height):
        for x in range(view_x, view_x + view_width):
            if (x, y) in self.level.visible_tiles:
                visible_count += 1
                # Draw visible tile...
            elif (x, y) in self.level.explored_tiles:
                explored_count += 1
                # Draw explored tile...
            else:
                unknown_count += 1
                # Draw black...
    
    # Debug only once per second
    if not hasattr(self, '_last_draw_debug') or time.time() - self._last_draw_debug > 1.0:
        print(f"[DEBUG draw_map] Rendered - visible: {visible_count}, explored: {explored_count}, unknown: {unknown_count}")
        self._last_draw_debug = time.time()
```

**Ce qui est tracé** :
- Nombre de tuiles rendues comme visibles
- Nombre de tuiles rendues comme explorées
- Nombre de tuiles rendues comme inconnues
- Limité à 1 fois par seconde pour éviter le spam

### 3. Dans `move_char()`

```python
if isinstance(char, Character):
    game.level.explored_tiles.add(game.pos)
    print(f"[DEBUG move_char] Character moved to {game.pos}, calling update_visible_tiles()")
    game.update_visible_tiles()
    print(f"[DEBUG move_char] After update, visible_tiles has {len(game.level.visible_tiles)} tiles")
```

**Ce qui est tracé** :
- Position après déplacement
- Confirmation de l'appel à `update_visible_tiles()`
- Taille de `visible_tiles` après mise à jour

## Comment tester

### Lancer le jeu avec debug

```bash
cd /Users/display/PycharmProjects/DnD-5th-Edition-API
/Users/display/PycharmProjects/DnD-5th-Edition-API/.venv/bin/python dungeon_menu_pygame.py
```

### Observer la console

Au démarrage du niveau :
```
[DEBUG] Hero pos: (5, 5), view window: (0, 0, 20, 15)
[DEBUG] Tiles checked: 300, in range: 314, visible: 150
[DEBUG] visible_tiles size: 150
[DEBUG] Sample visible tiles: [(4, 4), (4, 5), (5, 4), (5, 5), (6, 5)]
[DEBUG draw_map] Rendered - visible: 150, explored: 0, unknown: 150
```

Après un déplacement :
```
[DEBUG move_char] Character moved to (6, 5), calling update_visible_tiles()
[DEBUG] Hero pos: (6, 5), view window: (0, 0, 20, 15)
[DEBUG] Tiles checked: 300, in range: 314, visible: 160
[DEBUG] visible_tiles size: 160
[DEBUG] Sample visible tiles: [(5, 4), (5, 5), (6, 4), (6, 5), (7, 5)]
[DEBUG move_char] After update, visible_tiles has 160 tiles
[DEBUG draw_map] Rendered - visible: 160, explored: 150, unknown: 140
```

## Scénarios de diagnostic

### Scénario 1: visible_tiles est bien rempli mais pas affiché

**Symptômes** :
```
[DEBUG] visible_tiles size: 150
[DEBUG draw_map] Rendered - visible: 0, explored: 0, unknown: 300
```

**Cause probable** : Le set `visible_tiles` est sur un objet différent de celui utilisé par `draw_map()`

**Solution** : Vérifier que `game.level.visible_tiles` est le même objet partout

### Scénario 2: visible_tiles est vide

**Symptômes** :
```
[DEBUG] Tiles checked: 300, in range: 314, visible: 0
[DEBUG] visible_tiles size: 0
```

**Cause probable** : La fonction `in_view_range()` retourne toujours False

**Solution** : Vérifier l'implémentation de `in_view_range()` et les obstacles

### Scénario 3: update_visible_tiles() n'est pas appelé

**Symptômes** :
```
# Pas de message "[DEBUG move_char] Character moved to..."
```

**Cause probable** : `move_char()` ne détecte pas que `char` est un `Character`

**Solution** : Vérifier `isinstance(char, Character)` et le type de `game.hero`

### Scénario 4: view_window est incorrect

**Symptômes** :
```
[DEBUG] Hero pos: (50, 50), view window: (0, 0, 20, 15)
# La fenêtre ne suit pas le héros
```

**Cause probable** : `calculate_view_window()` utilise des coordonnées incorrectes

**Solution** : Vérifier que `calculate_view_window()` utilise `self.hero.x` et `self.hero.y`

## Hypothèses à tester

### Hypothèse 1: Problème de référence Level

Il pourrait y avoir **plusieurs instances** de `Level` :
- Une dans `game.level` où `update_visible_tiles()` écrit
- Une autre quelque part où `draw_map()` lit

**Test** :
```python
# Dans update_visible_tiles(), ajouter :
print(f"[DEBUG] Level instance ID: {id(self.level)}")
print(f"[DEBUG] visible_tiles instance ID: {id(self.level.visible_tiles)}")

# Dans draw_map(), ajouter :
print(f"[DEBUG draw_map] Level instance ID: {id(self.level)}")
print(f"[DEBUG draw_map] visible_tiles instance ID: {id(self.level.visible_tiles)}")
```

Si les IDs sont différents → **Problème trouvé !**

### Hypothèse 2: visible_tiles est réinitialisé entre update et draw

`visible_tiles` est peut-être réinitialisé quelque part entre l'appel à `update_visible_tiles()` et le rendu.

**Test** :
```python
# Chercher dans le code :
grep -n "visible_tiles = set()" dungeon_pygame.py
```

Si plusieurs endroits → **Un réinitialise après l'update !**

### Hypothèse 3: Problème de timing

`draw_map()` pourrait être appelé **avant** `update_visible_tiles()` dans la boucle de jeu.

**Test** : Vérifier l'ordre dans `main_game_loop()` :
```python
# Ordre correct :
1. handle_events()  # Peut appeler move_char() → update_visible_tiles()
2. update_display() # Appelle draw_map()

# Ordre incorrect :
1. update_display() # ❌ Utilise ancien visible_tiles
2. handle_events()  # Met à jour visible_tiles
```

### Hypothèse 4: in_view_range() trop strict

La fonction `in_view_range()` pourrait être trop restrictive et bloquer toutes les tuiles.

**Test** :
```python
# Dans update_visible_tiles(), temporairement :
# if in_view_range(*self.pos, x, y, obstacles=self.level.obstacles):
if True:  # Test : accepter TOUTES les tuiles dans le rayon
    self.level.visible_tiles.add((x, y))
```

Si ça fonctionne → **Problème dans in_view_range() !**

## Données attendues

### Démarrage normal

```
Position: (10, 10)
Vision range: 10
View window: (5, 5, 20, 15)
Tiles in range: ~314 (π * 10²)
Tiles visible: 100-200 (selon obstacles)
```

### Après déplacement d'une case

```
Old position: (10, 10)
New position: (11, 10)
Tiles in range: ~314 (même)
Tiles visible: 100-200 (quelques nouvelles, quelques perdues)
Delta explored: +5 à +20 nouvelles tuiles
```

## Prochaines étapes

1. **Lancer le jeu** avec le debug activé
2. **Observer la console** au démarrage et après déplacement
3. **Identifier le scénario** correspondant aux symptômes
4. **Appliquer la solution** selon le diagnostic

## Commandes utiles

### Vérifier le niveau de debug

```bash
# Compter les lignes de debug dans le code
grep -c "\[DEBUG\]" dungeon_pygame.py
# Devrait retourner > 10
```

### Filtrer uniquement les messages debug

```bash
# Lancer et filtrer les logs
python dungeon_menu_pygame.py 2>&1 | grep "\[DEBUG\]"
```

### Désactiver le debug

Une fois le problème trouvé, commenter les lignes `print(f"[DEBUG]...")`

## Résultat attendu

Après identification et correction, on devrait voir :

```
[DEBUG move_char] Character moved to (11, 10), calling update_visible_tiles()
[DEBUG] Hero pos: (11, 10), view window: (6, 5, 20, 15)
[DEBUG] Tiles checked: 300, in range: 314, visible: 175
[DEBUG] visible_tiles size: 175
[DEBUG move_char] After update, visible_tiles has 175 tiles
[DEBUG draw_map] Rendered - visible: 175, explored: 150, unknown: 125
```

Et visuellement : **Les nouvelles tuiles apparaissent !** ✅

---

**Status** : Debug actif, en attente de logs de test
**Action requise** : Lancer le jeu et observer les logs console

