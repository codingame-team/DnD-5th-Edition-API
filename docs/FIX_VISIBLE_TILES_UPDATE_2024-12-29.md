# Fix: Tuiles nouvellement visibles ne s'affichent pas lors du déplacement

**Date**: 29 décembre 2024  
**Problème**: Les tuiles nouvellement visibles ne s'affichent pas au fur et à mesure du déplacement  
**Solution**: Recalculer `visible_tiles` à chaque déplacement  
**Statut**: ✅ RÉSOLU

## Problème

Après avoir corrigé le déplacement du personnage, un nouveau problème est apparu : 

**Symptôme** : Quand le personnage se déplace, les nouvelles tuiles qui entrent dans son champ de vision ne s'affichent pas. Seules les tuiles déjà vues lors de la première exploration restent visibles.

## Analyse du problème

### Fonctionnement attendu (Fog of War)

Un jeu avec "fog of war" doit gérer **deux ensembles de tuiles** :

1. **`explored_tiles`** - Tuiles déjà visitées/explorées (permanent, ne disparaît jamais)
   - Une fois qu'une tuile a été vue, elle reste dans cet ensemble
   - Utilisé pour afficher les tuiles en mode "déjà vu" (peut-être grisé)

2. **`visible_tiles`** - Tuiles **actuellement** dans le champ de vision (dynamique)
   - Recalculé à chaque déplacement
   - Seules ces tuiles sont affichées en couleur/détails complets

### Comportement incorrect

Dans le code, `visible_tiles` était utilisé comme **accumulation** au lieu d'être **recalculé** :

```python
# ❌ AVANT - Mauvais comportement
def update_visible_tiles(self, vision_range: int = 10):
    # self.level.visible_tiles = set()  ← COMMENTÉ!
    view_x, view_y, view_width, view_height = self.calculate_view_window()
    for x in range(view_x, view_x + view_width):
        for y in range(view_y, view_y + view_height):
            # ❌ Saute les tuiles déjà dans visible_tiles
            if (x, y) in self.level.visible_tiles or dist((x, y), self.pos) > vision_range:
                continue
            if in_view_range(*self.pos, x, y, obstacles=self.level.obstacles):
                self.level.visible_tiles.add((x, y))
```

**Problèmes** :
1. `visible_tiles` n'est **jamais réinitialisé** (ligne commentée)
2. La condition `if (x, y) in self.level.visible_tiles` **saute** les tuiles déjà ajoutées
3. Résultat : `visible_tiles` accumule toutes les tuiles vues, mais ne reflète pas le champ de vision actuel

### Conséquence

```
Déplacement 1:
  Position: (5, 5)
  visible_tiles: {(4,4), (4,5), (5,4), (5,5), (6,5), (6,6)} ✅

Déplacement 2:
  Position: (10, 10)
  visible_tiles: {(4,4), (4,5), ... (anciennes) + (nouvelles)}
  ❌ Les anciennes tuiles (4,4), etc. ne sont plus visibles!
  ❌ Mais elles restent dans visible_tiles
  ❌ Les nouvelles tuiles autour de (10,10) ne sont pas calculées correctement
```

## Solution

### Approche

**Recalculer complètement `visible_tiles` à chaque déplacement** :

```python
# ✅ APRÈS - Correct
def update_visible_tiles(self, vision_range: int = 10):
    """
    Update the set of currently visible tiles based on hero's position.
    This is recalculated each time the hero moves.
    """
    # ✅ Reset visible tiles - we recalculate what's currently visible
    self.level.visible_tiles = set()
    
    view_x, view_y, view_width, view_height = self.calculate_view_window()
    for x in range(view_x, view_x + view_width):
        for y in range(view_y, view_y + view_height):
            # ✅ Skip only if too far away (pas de vérification "déjà vu")
            if dist((x, y), self.pos) > vision_range:
                continue
            # Check if tile is in line of sight
            if in_view_range(*self.pos, x, y, obstacles=self.level.obstacles):
                self.level.visible_tiles.add((x, y))
```

### Changements apportés

1. **Décommenté** `self.level.visible_tiles = set()` pour réinitialiser à chaque appel
2. **Supprimé** la condition `(x, y) in self.level.visible_tiles` qui empêchait le recalcul
3. **Simplifié** la logique : on ajoute toutes les tuiles visibles depuis la position actuelle

### Flux de fonctionnement

```
Joueur se déplace
    ↓
move_char() appelée
    ↓
game.x, game.y mis à jour (via properties)
    ↓
game.level.explored_tiles.add(game.pos)  ← Marque comme exploré
    ↓
game.update_visible_tiles()  ← Recalcule visible_tiles
    ↓
visible_tiles = {} (réinitialisé)
    ↓
Boucle sur view_window
    ↓
Pour chaque tuile dans le champ de vision:
  - Vérifier distance
  - Vérifier ligne de vue
  - Ajouter à visible_tiles
    ↓
update_display() appelée dans la boucle principale
    ↓
draw_map() affiche les tuiles:
  - Si dans visible_tiles → afficher en couleur
  - Sinon → afficher en noir
```

## Différence explored_tiles vs visible_tiles

| Ensemble | Type | Comportement | Utilisation |
|----------|------|--------------|-------------|
| `explored_tiles` | Permanent | Accumule, ne se réinitialise jamais | Tuiles déjà visitées (historique) |
| `visible_tiles` | Dynamique | Recalculé à chaque déplacement | Tuiles actuellement visibles (FOV) |

### Exemple

```python
# Position (5, 5)
explored_tiles = {(4,4), (5,4), (5,5), (6,5)}
visible_tiles  = {(4,4), (5,4), (5,5), (6,5)}  # Même ensemble

# Déplacement vers (10, 10)
explored_tiles = {(4,4), (5,4), (5,5), (6,5), (9,9), (10,9), (10,10), (11,10)}  # ✅ Accumule
visible_tiles  = {(9,9), (10,9), (10,10), (11,10)}  # ✅ Recalculé (seulement autour de 10,10)
```

## Utilisation dans le rendu

### draw_map()

```python
for y in range(view_y, view_y + view_height):
    for x in range(view_x, view_x + view_width):
        if (x, y) in self.level.visible_tiles:
            # ✅ Afficher la tuile normalement (dans le FOV actuel)
            screen.blit(photo_wall, (tile_x, tile_y))
        else:
            # Afficher en noir (hors FOV ou jamais vu)
            screen.fill(BLACK, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
```

**Note** : On pourrait améliorer en vérifiant aussi `explored_tiles` pour afficher les tuiles déjà vues en grisé :

```python
if (x, y) in self.level.visible_tiles:
    # Dans le FOV actuel - couleur normale
    screen.blit(photo_wall, (tile_x, tile_y))
elif (x, y) in self.level.explored_tiles:
    # Déjà vu mais hors FOV - afficher grisé
    screen.blit(gray_version, (tile_x, tile_y))
else:
    # Jamais vu - noir
    screen.fill(BLACK, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
```

## Tests de validation

### Test 1: Déplacement simple
```
1. Démarrer à (5, 5)
2. visible_tiles contient les tuiles autour de (5, 5)
3. Se déplacer à (6, 5)
4. ✅ visible_tiles recalculé avec tuiles autour de (6, 5)
5. ✅ Nouvelles tuiles à droite deviennent visibles
6. ✅ Anciennes tuiles à gauche disparaissent de visible_tiles
```

### Test 2: Retour en arrière
```
1. Démarrer à (5, 5)
2. explored_tiles = {tuiles autour de 5,5}
3. Se déplacer à (10, 10)
4. explored_tiles = {tuiles 5,5 + tuiles 10,10}
5. Retour à (5, 5)
6. ✅ visible_tiles recalculé avec tuiles autour de (5, 5)
7. ✅ Les tuiles sont visibles à nouveau (car recalculées)
8. ✅ explored_tiles contient toujours les deux zones
```

## Bénéfices de la correction

1. ✅ **FOV dynamique** : Le champ de vision suit le personnage
2. ✅ **Nouvelles tuiles visibles** : Affichées au fur et à mesure de l'exploration
3. ✅ **Performance** : Pas d'accumulation infinie de tuiles
4. ✅ **Logique claire** : Séparation entre "vu" et "actuellement visible"

## Améliorations futures possibles

### 1. Affichage des tuiles explorées

```python
# Dans draw_map()
if (x, y) in self.level.visible_tiles:
    # Visible maintenant - couleur normale
    screen.blit(photo_wall, (tile_x, tile_y))
elif (x, y) in self.level.explored_tiles:
    # Déjà exploré mais hors de vue - grisé
    gray_surface = photo_wall.copy()
    gray_surface.set_alpha(128)  # 50% transparent
    screen.blit(gray_surface, (tile_x, tile_y))
else:
    # Jamais vu - noir
    screen.fill(BLACK, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
```

### 2. Vision range variable

```python
# Selon l'équipement, la lumière, etc.
if hero.has_torch:
    vision_range = 15
elif in_dark_zone:
    vision_range = 5
else:
    vision_range = 10

game.update_visible_tiles(vision_range=vision_range)
```

### 3. Cachette de monstres

```python
# Dans update_display()
for monster in game.level.monsters:
    if monster.pos in game.level.visible_tiles:
        # ✅ Monstre visible seulement s'il est dans le FOV actuel
        image: Surface = level_sprites[monster.id]
        monster.draw(screen, image, TILE_SIZE, *view_port_tuple)
```

## Fichiers modifiés

### dungeon_pygame.py

**Fonction `update_visible_tiles()`** :
- ✅ Décommenté `self.level.visible_tiles = set()`
- ✅ Supprimé condition `(x, y) in self.level.visible_tiles`
- ✅ Ajouté docstring expliquant le recalcul

**Lignes** : ~1042-1058

## Conclusion

✅ **Problème résolu**

Les tuiles nouvellement visibles s'affichent maintenant correctement au fur et à mesure du déplacement grâce au **recalcul complet** de `visible_tiles` à chaque mouvement.

Le système de fog of war fonctionne maintenant comme prévu :
- **`visible_tiles`** = Ce qui est actuellement visible (recalculé)
- **`explored_tiles`** = Ce qui a déjà été vu (permanent)

---

**Status** : ✅ FIXED  
**Impact** : Amélioration majeure de l'expérience de jeu  
**Performance** : Aucun impact négatif (recalcul léger)

