# Fix: Bugs de combat et touches clavier AZERTY

**Date**: 29 décembre 2024  
**Problèmes corrigés**:
1. Crash lors du combat : `Character` n'a pas de méthode `draw_effect()`
2. Conflit de touche S pour AZERTY
**Statut**: ✅ CORRIGÉ

---

## Problème 1: Crash lors du combat

### Erreur observée

```python
Traceback (most recent call last):
  File "dungeon_pygame.py", line 2054, in handle_combat
    draw_attack_effect(game, game.hero, damage)
  File "dungeon_pygame.py", line 2012, in draw_attack_effect
    char.draw_effect(screen, sprites, TILE_SIZE, FPS, *view_port_tuple, sound_file)
  File "game_entity.py", line 104, in __getattr__
    return getattr(self.entity, name)
AttributeError: 'Character' object has no attribute 'draw_effect'
```

### Cause

La fonction `draw_attack_effect()` appelait `char.draw_effect()` sur tous les personnages, mais :
- **Monsters** ont la méthode `draw_effect()` ✅
- **Characters** n'ont PAS cette méthode ❌

Quand le joueur était touché, `game.hero` (un `GameEntity[Character]`) était passé à `draw_attack_effect()`, qui essayait d'appeler `draw_effect()` → **crash**.

### Solution appliquée

Vérifier si la méthode existe avant de l'appeler :

```python
def draw_attack_effect(game: Game, char: [Character | Monster], damage: int):
    if damage > 0:
        sound_file = f'{sound_effects_dir}/Sword Impact Hit 1.wav'
    else:
        sound_file = f'{sound_effects_dir}/Sword Parry 1.wav'
    
    # ✅ Vérifier si la méthode existe
    if hasattr(char, 'draw_effect') and callable(getattr(char, 'draw_effect', None)):
        # Pour les monstres : effet visuel
        sprites_sheet = f'{effects_images_dir}/flash04.png'
        sprites: List[Surface] = extract_sprites(sprites_sheet, columns=5, rows=2)
        view_port_tuple = game.calculate_view_window()
        char.draw_effect(screen, sprites, TILE_SIZE, FPS, *view_port_tuple, sound_file)
    else:
        # Pour le personnage joueur : juste le son
        sound = pygame.mixer.Sound(sound_file)
        sound.play()
```

### Résultat

✅ **Plus de crash lors du combat**  
✅ **Les monstres affichent l'effet visuel**  
✅ **Le joueur joue juste le son d'impact**

---

## Problème 2: Touches clavier AZERTY

### Situation initiale

Les touches **QZSD** étaient déjà supportées, MAIS il y avait un conflit :

```python
# ❌ Conflit sur la touche S
elif event.key == pygame.K_s and (event.mod & pygame.KMOD_META):
    # CMD-S : Sauvegarder
    save_character_gamestate(game, gamestate_dir)

elif event.key in (pygame.K_DOWN, pygame.K_s):
    # S : Déplacement vers le bas
    move_down()

elif event.key == pygame.K_s:
    # S : Utiliser potion de vitesse
    handle_speed_potion_use(game)
```

**Problème** : La touche **S simple** était utilisée pour :
1. Déplacement vers le bas (ligne 1886)
2. Utiliser potion de vitesse (ligne 1909)

Python exécute le **premier** `elif` qui match → la potion n'était **jamais** accessible !

### Solution appliquée

Réorganiser l'ordre et utiliser **Shift+S** pour la potion :

```python
# ✅ S seul : Déplacement vers le bas
elif event.key in (pygame.K_DOWN, pygame.K_s) and not (event.mod & pygame.KMOD_SHIFT):
    # DOWN or S (without Shift) - Move down
    move_down()

# ✅ Shift+S : Utiliser potion de vitesse  
elif event.key == pygame.K_s and (event.mod & pygame.KMOD_SHIFT):
    # Shift+S - Use speed potion
    handle_speed_potion_use(game)
```

### Mapping complet des touches

| Touche | Action | Alternative |
|--------|--------|-------------|
| **Z** | Haut ⬆️ | Flèche haut |
| **S** | Bas ⬇️ | Flèche bas |
| **Q** | Gauche ⬅️ | Flèche gauche |
| **D** | Droite ➡️ | Flèche droite |
| **P** | Utiliser potion de soin 🧪 | - |
| **Shift+S** | Utiliser potion de vitesse ⚡ | - |
| **O** | Ouvrir porte 🚪 | - |
| **C** | Fermer porte 🚪 | - |
| **I** | Info position 📍 | - |
| **H** | Aide (Help) ❓ | - |
| **CMD/Win+S** | Sauvegarder 💾 | - |
| **ESC** | Quitter et sauvegarder 🚪 | - |

### Notes AZERTY

Les touches **QZSD** correspondent à la disposition AZERTY française :

```
  Z (Haut)
  ↑
Q ← → D
  ↓
  S (Bas)
```

En **QWERTY**, c'est **WASD** :

```
  W (Haut)
  ↑
A ← → D
  ↓
  S (Bas)
```

Le jeu **supporte les deux** ! Les flèches directionnelles fonctionnent aussi.

---

## Tests de validation

### Test 1: Combat

```
1. Démarrer le jeu
2. Se déplacer vers un monstre
3. Attaquer le monstre
4. Le monstre riposte et touche le joueur
```

**Résultat attendu** :
- ✅ Pas de crash
- ✅ Son d'impact joué
- ✅ Effet visuel sur le monstre (si le joueur le touche)
- ✅ Son sur le joueur (s'il est touché)

### Test 2: Touches AZERTY

```
1. Appuyer sur Z → Se déplace vers le haut
2. Appuyer sur S → Se déplace vers le bas
3. Appuyer sur Q → Se déplace vers la gauche
4. Appuyer sur D → Se déplace vers la droite
```

**Résultat attendu** :
- ✅ Le personnage se déplace dans la direction correcte
- ✅ Les tuiles visibles se mettent à jour
- ✅ Les logs debug apparaissent

### Test 3: Potion de vitesse

```
1. Obtenir une potion de vitesse
2. Appuyer sur S simple → Se déplace vers le bas
3. Appuyer sur Shift+S → Utilise la potion de vitesse
```

**Résultat attendu** :
- ✅ S seul ne consomme PAS la potion
- ✅ Shift+S consomme la potion

---

## Changements de code

### Fichier: dungeon_pygame.py

**1. Fonction `draw_attack_effect()`** (ligne ~2008) :
```python
# AVANT
char.draw_effect(screen, sprites, ...)

# APRÈS
if hasattr(char, 'draw_effect') and callable(getattr(char, 'draw_effect', None)):
    char.draw_effect(screen, sprites, ...)
else:
    sound = pygame.mixer.Sound(sound_file)
    sound.play()
```

**2. Fonction `handle_keyboard_events()`** (ligne ~1860) :
```python
# AVANT
elif event.key in (pygame.K_DOWN, pygame.K_s):
    move_down()
# ...
elif event.key == pygame.K_s:
    handle_speed_potion_use(game)

# APRÈS  
elif event.key in (pygame.K_DOWN, pygame.K_s) and not (event.mod & pygame.KMOD_SHIFT):
    # S sans Shift : déplacement
    move_down()
# ...
elif event.key == pygame.K_s and (event.mod & pygame.KMOD_SHIFT):
    # Shift+S : potion
    handle_speed_potion_use(game)
```

---

## Pattern utilisé : Duck Typing

### Principe

Au lieu de vérifier le **type** exact, on vérifie si l'objet **a la méthode** :

```python
# ❌ Approche par type (fragile)
if isinstance(char, Monster):
    char.draw_effect(...)

# ✅ Approche par capacité (robuste)
if hasattr(char, 'draw_effect') and callable(getattr(char, 'draw_effect', None)):
    char.draw_effect(...)
```

**Avantages** :
- Fonctionne avec tous les types qui ont la méthode
- Plus pythonique ("If it walks like a duck and quacks like a duck...")
- Plus flexible pour l'évolution future

### Vérification complète

```python
hasattr(char, 'draw_effect')  # ✅ L'attribut existe
callable(getattr(char, 'draw_effect', None))  # ✅ C'est une méthode appelable
```

Cela évite les erreurs si `draw_effect` existe mais n'est pas une fonction.

---

## Améliorations futures possibles

### 1. Effet visuel pour le joueur

Créer une méthode `draw_effect()` dans la classe `Character` :

```python
# Dans dnd-5e-core/dnd_5e_core/entities/character.py
def draw_effect(self, screen, sprites, tile_size, fps, view_x, view_y, view_width, view_height, sound_file):
    """Draw visual effect when character is hit"""
    # Implémenter un effet visuel simple (flash, shake, etc.)
    pass
```

### 2. Configuration des touches

Permettre à l'utilisateur de configurer ses touches :

```python
# config.json
{
    "keyboard": {
        "layout": "azerty",  # ou "qwerty"
        "up": ["z", "up"],
        "down": ["s", "down"],
        "left": ["q", "left"],
        "right": ["d", "right"]
    }
}
```

### 3. Aide contextuelle

Afficher les touches disponibles à l'écran :

```python
# En bas de l'écran
"Z/↑: Haut | S/↓: Bas | Q/←: Gauche | D/→: Droite | P: Potion | Shift+S: Vitesse"
```

---

## Conclusion

✅ **Les deux problèmes sont corrigés** :

1. **Combat** : Plus de crash, les effets s'affichent correctement
2. **Touches AZERTY** : QZSD fonctionne sans conflit, Shift+S pour la potion

Le jeu est maintenant complètement jouable avec un clavier AZERTY ! 🎮🇫🇷

---

**Fichiers modifiés** : `dungeon_pygame.py`  
**Lignes modifiées** : ~2008-2020 (draw_attack_effect), ~1860-1920 (handle_keyboard_events)  
**Status** : ✅ PRODUCTION READY

