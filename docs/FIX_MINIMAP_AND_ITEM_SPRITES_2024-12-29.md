# Fix: Mini-map sans fog of war + Sprites d'items corrigés

**Date**: 29 décembre 2024  
**Problèmes corrigés**:
1. Mini-map affiche maintenant toutes les tuiles explorées (pas de fog of war)
2. Chargement amélioré des sprites d'items (armes, armures, potions)
**Statut**: ✅ CORRIGÉ

---

## Problème 1: Mini-map avec fog of war

### Situation avant

La mini-map utilisait `visible_tiles` ce qui créait un fog of war sur la mini-map aussi, rendant difficile la navigation dans les zones déjà explorées.

```python
# ❌ AVANT - Fog of war sur la mini-map
for y in range(self.map_height):
    for x in range(self.map_width):
        if (x, y) not in self.level.visible_tiles:  # ❌ Seulement ce qui est actuellement visible
            color = BLACK
```

### Solution appliquée

La mini-map affiche maintenant **toutes les tuiles explorées** avec deux niveaux de luminosité :

```python
# ✅ APRÈS - Toutes les tuiles explorées sont visibles
for y in range(self.map_height):
    for x in range(self.map_width):
        if (x, y) not in self.level.explored_tiles:  # ✅ Tout ce qui a été exploré
            color = BLACK  # Jamais exploré
        else:
            # Déterminer la couleur selon le type de tuile
            if tile == '#':
                base_color = (128, 128, 128)  # Mur
            elif tile in ('<', '>'):
                base_color = (0, 0, 255)  # Escaliers
            # ...
            
            # Luminosité différente selon si actuellement visible ou non
            if (x, y) in self.level.visible_tiles:
                color = base_color  # Pleine luminosité
            else:
                # 50% luminosité pour exploré mais hors FOV
                color = tuple(int(c * 0.5) for c in base_color)
```

### Résultat

**Mini-map** :
- ✅ Affiche **toutes les zones explorées**
- ✅ Zone actuellement visible : luminosité normale
- ✅ Zone déjà explorée mais hors FOV : luminosité réduite (50%)
- ✅ Zone jamais explorée : noir total

**Carte principale** :
- ✅ **Conserve le fog of war dynamique** (plus immersif)
- ✅ Seulement les tuiles actuellement visibles sont affichées
- ✅ Les tuiles explorées mais hors FOV sont assombries

---

## Problème 2: Sprites d'items manquants

### Diagnostic

Les items du package `dnd-5e-core` (WeaponData, ArmorData, Potion) n'ont pas d'attribut `image_name`, ce qui causait :
- ❌ Beaucoup d'items sans sprite (carrés de couleur)
- ❌ Potions non reconnues
- ❌ Armes/armures avec noms mal formatés

### Solution: Fonction de mapping

Ajout d'une fonction `get_item_image_name()` qui mappe les noms d'items vers les fichiers sprites :

```python
def get_item_image_name(item) -> str:
    """
    Generate image filename for an item.
    Maps item names/types to actual sprite filenames.
    """
    # 1. Vérifier attribut image_name explicite
    if hasattr(item, 'image_name') and item.image_name:
        return item.image_name
    
    # 2. Vérifier attribut index (slug)
    if hasattr(item, 'index') and item.index:
        return f"{item.index}.png"
    
    # 3. Mappings spécifiques pour potions
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
    
    # 4. Fallback: générer slug du nom
    item_slug = item_name.replace(' ', '-').replace("'", '').replace(',', '')
    return f"{item_slug}.png"
```

### Chargement avec fallbacks multiples

Le chargement des sprites essaye maintenant **plusieurs variantes** :

```python
# Try 1: Nom original
try:
    s[item.id] = pygame.image.load(f"{item_sprites_dir}/{item_image_name}").convert_alpha()
    loaded = True
except FileNotFoundError:
    pass

# Try 2: Sans extension .png (au cas où doublée)
if not loaded:
    try:
        base_name = item_image_name.replace('.png', '')
        s[item.id] = pygame.image.load(f"{item_sprites_dir}/{base_name}.png").convert_alpha()
        loaded = True
    except FileNotFoundError:
        pass

# Try 3: Underscores au lieu de tirets
if not loaded:
    try:
        alt_name = item_image_name.replace('-', '_')
        s[item.id] = pygame.image.load(f"{item_sprites_dir}/{alt_name}").convert_alpha()
        loaded = True
    except FileNotFoundError:
        pass

# Try 4: Potion générique si c'est une potion
if not loaded and 'Potion' in item.__class__.__name__:
    try:
        s[item.id] = pygame.image.load(f"{item_sprites_dir}/potion.png").convert_alpha()
        loaded = True
    except FileNotFoundError:
        pass

# Fallback final: Carré de couleur
if not loaded:
    fallback_surface = pygame.Surface((ICON_SIZE, ICON_SIZE))
    if 'Weapon' in item.__class__.__name__:
        fallback_surface.fill((192, 192, 192))  # Argent pour armes
    elif 'Armor' in item.__class__.__name__:
        fallback_surface.fill((139, 69, 19))  # Marron pour armures
    elif 'Potion' in item.__class__.__name__:
        fallback_surface.fill((255, 0, 255))  # Magenta pour potions
    s[item.id] = fallback_surface
```

### Mappings de potions

| Nom de potion | Fichier sprite |
|---------------|----------------|
| Healing | `potion-red.png` |
| Greater Healing | `potion-red.png` |
| Superior Healing | `potion-red.png` |
| Speed | `potion-green.png` |
| Strength | `potion-blue.png` |

### Exemples de conversion

| Item | Slug généré | Variantes essayées |
|------|-------------|-------------------|
| Longsword | `longsword.png` | longsword.png, longsword, long_sword.png |
| Chain Mail | `chain-mail.png` | chain-mail.png, chain_mail.png |
| Healing | `potion-red.png` | Mapping direct |
| Dagger +1 | `dagger-1.png` | dagger-1.png, dagger_1.png |

---

## Comparaison visuelle

### Mini-map

**AVANT** :
```
⬛⬛⬛⬛⬛⬛⬛⬛  ← Zones explorées mais hors FOV = noir
⬛⬛🟦🟦🟦⬛⬛⬛  ← Seulement le FOV actuel visible
⬛⬛🟦🔴🟦⬛⬛⬛  ← 🔴 = Joueur
⬛⬛🟦🟦🟦⬛⬛⬛
⬛⬛⬛⬛⬛⬛⬛⬛
```

**APRÈS** :
```
⬛⬛⬛⬛⬛⬛⬛⬛  ← Jamais exploré = noir
🔵🔵🟦🟦🟦🔵🔵🔵  ← 🔵 = Exploré (sombre), 🟦 = Visible (clair)
🔵🔵🟦🔴🟦🔵🔵🔵  ← 🔴 = Joueur
🔵🔵🟦🟦🟦🔵🔵🔵  ← Toutes les zones explorées visibles
⬛⬛🔵🔵🔵⬛⬛⬛
```

### Inventaire

**AVANT** :
```
[🔴][🔵][⬜][⬜][⬜]  ← Beaucoup de carrés de couleur
[🟤][🟤][⬛][⬛][⬛]  ← Pas d'images reconnaissables
```

**APRÈS** :
```
[🗡️][🛡️][🧪][🧪][⬜]  ← Sprites d'armes/armures/potions
[⚔️][🎯][🧪][⬛][⬛]  ← Plus d'images réelles
```

---

## Bénéfices

### Navigation améliorée

✅ **La mini-map sert maintenant de vraie carte**
- Voir toutes les zones déjà explorées
- Planifier les déplacements
- Repérer les zones non explorées

✅ **Distinction visuelle claire**
- Zone actuelle : luminosité normale
- Zone explorée : luminosité réduite
- Zone inconnue : noir

### Immersion conservée

✅ **La carte principale garde le fog of war**
- Experience de jeu immersive
- Découverte progressive
- Tension dans l'exploration

✅ **Deux modes complémentaires**
- Mini-map : vision tactique/stratégique
- Carte : vision immersive/locale

### Inventaire utilisable

✅ **Plus de sprites d'items affichés**
- Potions reconnaissables par couleur
- Armes et armures avec leurs icônes
- Fallbacks multiples pour couvrir tous les cas

✅ **Moins de carrés de couleur**
- Meilleure identification visuelle
- Interface plus professionnelle

---

## Tests de validation

### Test 1: Mini-map

```
1. Démarrer le jeu
2. Explorer plusieurs salles
3. Revenir à la première salle
4. Regarder la mini-map
```

**Résultat attendu** :
- ✅ Toutes les salles explorées sont visibles sur la mini-map
- ✅ La salle actuelle est plus lumineuse
- ✅ Les autres salles sont plus sombres mais visibles

### Test 2: Fog of war principal

```
1. Dans une grande salle
2. Se déplacer dans un coin
3. Observer la carte principale
```

**Résultat attendu** :
- ✅ Seul le FOV actuel est visible clairement
- ✅ Le reste est noir ou assombri
- ✅ Le fog of war fonctionne dynamiquement

### Test 3: Sprites d'items

```
1. Ramasser plusieurs items (armes, armures, potions)
2. Ouvrir l'inventaire (I)
3. Observer les icônes
```

**Résultat attendu** :
- ✅ Les potions affichent potion-red.png, potion-green.png, etc.
- ✅ Les armes affichent leurs sprites (ou fallback argent)
- ✅ Les armures affichent leurs sprites (ou fallback marron)

---

## Changements de code

### Fichier: dungeon_pygame.py

**1. Fonction `draw_mini_map()`** (ligne ~645) :
```python
# AVANT
if (x, y) not in self.level.visible_tiles:
    color = BLACK

# APRÈS
if (x, y) not in self.level.explored_tiles:  # ✅ explored au lieu de visible
    color = BLACK
else:
    # Calculer couleur de base
    if (x, y) in self.level.visible_tiles:
        color = base_color  # Pleine luminosité
    else:
        color = tuple(int(c * 0.5) for c in base_color)  # 50% luminosité
```

**2. Nouvelle fonction `get_item_image_name()`** (ligne ~2236) :
```python
def get_item_image_name(item) -> str:
    """Map item names to sprite filenames"""
    # Mappings potions
    potion_map = {
        'healing': 'potion-red.png',
        'speed': 'potion-green.png',
        ...
    }
    # Fallback to slug generation
    return f"{item_slug}.png"
```

**3. Fonction `create_sprites()`** (ligne ~2270) :
```python
# AVANT
if hasattr(item, 'image_name'):
    item_image_name = item.image_name
else:
    item_image_name = f"{item_slug}.png"

# APRÈS
item_image_name = get_item_image_name(item)  # ✅ Fonction helper

# Try multiple fallbacks
# Try 1: Original name
# Try 2: Without .png
# Try 3: With underscores
# Try 4: Generic potion
# Fallback: Colored square
```

---

## Fichiers de sprites requis

### Potions (sprites/items_icons/)

- `potion-red.png` - Potions de soin
- `potion-green.png` - Potions de vitesse
- `potion-blue.png` - Potions de force
- `potion.png` - Potion générique (fallback)

### Armes et armures

Les noms sont générés à partir du nom de l'item :
- `longsword.png` ou `long-sword.png` ou `long_sword.png`
- `chain-mail.png` ou `chain_mail.png`
- Etc.

Si le fichier n'existe pas, un carré de couleur est affiché :
- Argent pour armes
- Marron pour armures

---

## Améliorations futures possibles

### 1. Légende sur la mini-map

```python
# Ajouter une légende
legend_items = [
    ("Mur", (128, 128, 128)),
    ("Sol", (64, 64, 64)),
    ("Escaliers", (0, 0, 255)),
    ("Fontaine", (0, 255, 0)),
]
# Dessiner la légende en bas de la mini-map
```

### 2. Configuration du fog of war

```python
# Dans un menu d'options
fog_of_war_options = {
    "main_map": True,   # Fog of war sur carte principale
    "mini_map": False,  # Pas de fog of war sur mini-map
}
```

### 3. Zoom sur la mini-map

```python
# Permettre de zoomer sur une zone spécifique
if click_on_minimap:
    zoom_to_position(clicked_x, clicked_y)
```

### 4. Sprites d'items personnalisés

Créer un fichier de configuration JSON :

```json
{
  "items": {
    "longsword": "sword_long.png",
    "healing_potion": "potion_hp_red.png",
    "chain_mail": "armor_chain.png"
  }
}
```

---

## Conclusion

✅ **Les deux problèmes sont résolus** :

1. **Mini-map** : Affiche toutes les zones explorées pour meilleure navigation
2. **Sprites d'items** : Chargement amélioré avec fallbacks multiples

Le jeu offre maintenant :
- 📍 **Navigation facilitée** avec la mini-map complète
- 🎮 **Immersion conservée** avec le fog of war sur la carte principale  
- 🎨 **Interface améliorée** avec plus de sprites d'items visibles

---

**Fichiers modifiés** : `dungeon_pygame.py`  
**Lignes modifiées** :
- ~645-695 (draw_mini_map)
- ~2236-2265 (get_item_image_name)
- ~2270-2340 (create_sprites avec fallbacks)

**Status** : ✅ PRODUCTION READY

