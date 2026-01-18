# Fix FINAL : Forcer la copie de l'inventaire pour Pickle

**Date** : 30 décembre 2024  
**Problème** : Items achetés présents dans les logs mais pas sauvegardés dans le gamestate  
**Cause** : Pickle ne détecte pas les modifications in-place des listes Python  
**Solution** : Forcer une copie de l'inventaire avant sauvegarde  
**Statut** : ✅ EN TEST

---

## Le problème identifié

### Logs montrent que l'achat fonctionne

```
You bought Healing!
[DEBUG] Gold BEFORE purchase: 911
[DEBUG] Gold AFTER purchase: 887
[DEBUG] Inventory AFTER: [..., 'Healing', ...]
```

**L'item EST bien ajouté à l'inventaire en mémoire** ✅

### Mais après reload, l'item disparaît

```
[Retour au dungeon]
Inventaire : [...] (pas de Healing) ❌
```

**L'item n'a PAS été sauvegardé** ❌

---

## Cause racine : Pickle et les modifications in-place

### Comment Pickle détecte les changements

Python's `pickle` module utilise l'**identité des objets** pour détecter les changements :

```python
# Modification in-place (même ID d'objet)
inventory = [item1, item2, None]
inventory[2] = item3  # ❌ Pickle peut ne PAS détecter ce changement
# id(inventory) reste le même

# Réassignation (nouvel ID d'objet)  
inventory = [item1, item2, item3]  # ✅ Pickle détecte le changement
# id(inventory) change
```

### Dans notre code

```python
# handle_buy() - Modification in-place
hero.entity.inventory[slot_index] = bought_item  # ❌ Modification in-place

# save_character_gamestate()
pickle.dump(game, f1)  # ❌ Pickle ne voit pas que inventory a changé
```

**Problème** : `hero.entity.inventory` est la **même liste** avant et après l'achat. Pickle peut considérer que rien n'a changé et **ne pas sauvegarder** la nouvelle version.

---

## Solution : Forcer une copie

### Principe

Créer une **nouvelle liste** avec le même contenu force Pickle à détecter le changement :

```python
# Avant sauvegarde
original_inventory = hero.entity.inventory
hero.entity.inventory = original_inventory.copy()  # ✅ Nouvelle liste, nouveau ID

# Maintenant pickle DOIT détecter le changement
pickle.dump(game, f1)  # ✅ Sauvegarde la nouvelle inventory
```

### Code modifié

**Fichier** : `boltac_tp_pygame.py` - `exit_boltac()`

```python
if original_game:
    print(f'✅ Using original game object with modifications')
    print(f'[DEBUG] About to save gamestate with:')
    print(f'[DEBUG]   - Gold: {original_game.hero.entity.gold}')
    print(f'[DEBUG]   - Inventory: {[i.name if i else None for i in original_game.hero.entity.inventory]}')
    
    # IMPORTANT: Force a copy of the inventory to ensure pickle detects changes
    # Python lists modified in-place might not trigger pickle to save properly
    print(f'[DEBUG] Forcing inventory copy to ensure pickle detects changes...')
    original_inventory = original_game.hero.entity.inventory
    original_game.hero.entity.inventory = original_inventory.copy()  # ✅ NOUVEAU
    print(f'[DEBUG] Inventory after copy: {[i.name if i else None for i in original_game.hero.entity.inventory]}')
    
    dungeon_pygame.save_character_gamestate(original_game, gamestate_dir)
    print(f'✅ Gamestate saved with Boltac purchases/sales')
```

---

## Pourquoi ça devrait marcher

### Avant (modification in-place)

```python
# Dans handle_buy()
hero.entity.inventory[2] = healing_potion
# id(hero.entity.inventory) = 4768365056  (AVANT)
# id(hero.entity.inventory) = 4768365056  (APRÈS) ← MÊME ID

# Dans save_character_gamestate()
pickle.dump(game, f)
# Pickle : "inventory ID n'a pas changé → pas de changement" ❌
```

### Après (copie forcée)

```python
# Dans handle_buy()
hero.entity.inventory[2] = healing_potion
# id(hero.entity.inventory) = 4768365056

# Dans exit_boltac() - AVANT sauvegarde
hero.entity.inventory = hero.entity.inventory.copy()
# id(hero.entity.inventory) = 4768999999  ← NOUVEAU ID

# Dans save_character_gamestate()
pickle.dump(game, f)
# Pickle : "inventory ID a changé → sauvegarder nouvelle version" ✅
```

---

## Test de validation

### 1. Lancer le test

```bash
python dungeon_menu_pygame.py
```

### 2. Aller chez Boltac et acheter un item

Observer les nouveaux logs :
```
[DEBUG] Forcing inventory copy to ensure pickle detects changes...
[DEBUG] Inventory after copy: [..., 'Healing', ...]
```

### 3. Quitter Boltac (ESC)

Vérifier les logs de sauvegarde.

### 4. Retour au dungeon

Appuyer sur **I** pour voir l'inventaire.

**Résultat attendu** : ✅ L'item acheté est VISIBLE

---

## Alternatives si ça ne marche toujours pas

### Alternative 1 : Forcer pickle protocol 4

```python
# Dans save_character_gamestate()
pickle.dump(game, f1, protocol=4)  # Force protocole récent
```

### Alternative 2 : Marquer l'inventaire comme "dirty"

```python
# Ajouter un attribut _modified
hero.entity._inventory_modified = True
```

### Alternative 3 : Sauvegarder l'inventaire séparément

```python
# Dans save_character_gamestate()
import json
with open(f'{_dir}/{char_name}_inventory.json', 'w') as f:
    json.dump([i.name if i else None for i in game.hero.entity.inventory], f)
```

### Alternative 4 : Utiliser __setstate__ / __getstate__

Définir ces méthodes dans la classe Character pour contrôler la sérialisation.

---

## Diagnostic si échec

### Vérifier que le fichier est bien écrit

```python
import pickle
import os

gamestate_file = 'gameState/pygame/Ellyjobell_gamestate.dmp'
stat = os.stat(gamestate_file)
print(f'File size: {stat.st_size} bytes')
print(f'Last modified: {stat.st_mtime}')

# Charger et vérifier
with open(gamestate_file, 'rb') as f:
    game = pickle.load(f)
    print(f'Gold: {game.hero.entity.gold}')
    print(f'Inventory: {[i.name if i else None for i in game.hero.entity.inventory]}')
```

Si le fichier **contient** l'item → Problème dans `load_character_gamestate()`  
Si le fichier **ne contient pas** l'item → Problème dans `save_character_gamestate()`

---

## Code pattern à suivre

### ✅ BON : Réassignation

```python
# Forcer un nouveau ID d'objet
hero.entity.inventory = hero.entity.inventory.copy()
hero.entity.inventory = [item for item in hero.entity.inventory]
hero.entity.inventory = list(hero.entity.inventory)
```

### ❌ MAUVAIS : Modification in-place

```python
# Même ID d'objet - pickle peut ne pas détecter
hero.entity.inventory[0] = item
hero.entity.inventory.append(item)
hero.entity.inventory.remove(item)
```

---

## Conclusion

### Changement effectué

✅ **Forcer copie de l'inventaire** avant sauvegarde dans `exit_boltac()`

### Principe

**Nouveau ID d'objet → Pickle détecte le changement → Sauvegarde garantie**

### Test

Lancer le jeu et vérifier que l'item acheté apparaît maintenant dans le dungeon.

**Si ça ne marche toujours pas, le problème est ailleurs (load, save, ou autre).** 🔬

---

**Fichier modifié** :  
`/Users/display/PycharmProjects/DnD-5th-Edition-API/boltac_tp_pygame.py`

**Ligne modifiée** : 183-188

**Status** : ✅ PRÊT À TESTER

