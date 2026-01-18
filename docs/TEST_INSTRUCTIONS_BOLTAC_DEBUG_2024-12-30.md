# Instructions de test - Debug Boltac Inventory Sync

**Date** : 30 décembre 2024  
**Objectif** : Vérifier avec des logs détaillés pourquoi l'inventaire n'est pas synchronisé

---

## Instructions de test

### 1. Lancer le jeu

```bash
cd /Users/display/PycharmProjects/DnD-5th-Edition-API
python dungeon_menu_pygame.py
```

### 2. Sélectionner un personnage qui a déjà exploré le donjon

Par exemple : **Laucian**, **Ellyjobell**, ou tout personnage avec un gamestate existant.

### 3. Aller chez Boltac

1. Clic sur le radio button **"Shop to Boltac"**
2. Clic sur le nom du personnage

**Observer la console** - Devrait afficher :
```
✅ Loading [NomPersonnage] from active gamestate (dungeon adventure)
[DEBUG LOAD] saved_game object id: 140xxxxx
[DEBUG LOAD] hero object id: 140xxxxx
[DEBUG LOAD] hero.entity object id: 140xxxxx
[DEBUG LOAD] char.gold: XXX
[DEBUG LOAD] char.inventory: [...]
```

**Noter** : Les IDs des objets (saved_game, hero, hero.entity)

### 4. Acheter un item

1. Sélectionner catégorie (Weapons/Armors/Potions)
2. Cliquer sur un item dans la liste
3. Cliquer sur **BUY**

**Observer la console** - Devrait afficher :
```
You bought [ItemName]!
[DEBUG] Gold BEFORE purchase: XXX
[DEBUG] Gold AFTER purchase: YYY
[DEBUG] Adding [ItemName] to inventory slot Z
[DEBUG] Inventory BEFORE: [...]
[DEBUG] Inventory AFTER: [..., ItemName, ...]
[DEBUG] hero object id: 140xxxxx
[DEBUG] hero.entity object id: 140xxxxx
[DEBUG] hero.entity.inventory object id: 140xxxxx
```

**VÉRIFIER** :
- ✅ L'item apparaît bien dans "Inventory AFTER"
- ✅ Les IDs d'objets sont les MÊMES que dans load_game_data

### 5. Quitter Boltac

Appuyer sur **ESC** ou cliquer sur **Exit**

**Observer la console** - Devrait afficher :
```
[DEBUG EXIT_BOLTAC] Starting exit for [NomPersonnage]
[DEBUG] hero object id: 140xxxxx
[DEBUG] hero.entity object id: 140xxxxx
[DEBUG] char_entity.gold: YYY
[DEBUG] char_entity.inventory: [..., ItemName, ...]
[DEBUG] original_game provided: True/False
[DEBUG] original_game.hero object id: 140xxxxx
[DEBUG] original_game.hero is hero: True/False  <-- CRUCIAL
[DEBUG] original_game.hero.entity.gold: YYY
[DEBUG] original_game.hero.entity.inventory: [..., ItemName, ...]
✅ Character saved to characters directory
Saving gamestate for [NomPersonnage]...
✅ Using original game object with modifications
[DEBUG] About to save gamestate with:
[DEBUG]   - Gold: YYY
[DEBUG]   - Inventory: [..., ItemName, ...]
✅ Gamestate saved with Boltac purchases/sales
```

**POINTS CRITIQUES À VÉRIFIER** :

#### A. `original_game provided: True`
- ✅ **True** : Bon, le gamestate a été passé
- ❌ **False** : PROBLÈME - Le gamestate n'a pas été passé

#### B. `original_game.hero is hero: True`
- ✅ **True** : Bon, c'est le MÊME objet
- ❌ **False** : PROBLÈME - Ce sont des objets DIFFÉRENTS

#### C. Les IDs d'objets
- ✅ **Tous identiques** : load → buy → exit utilisent le même objet
- ❌ **Différents** : PROBLÈME - Des copies ont été faites

#### D. L'inventaire dans "About to save"
- ✅ **Contient ItemName** : L'item est présent avant sauvegarde
- ❌ **Ne contient pas ItemName** : PROBLÈME - L'item a été perdu

### 6. Retour au menu et reload

Après la sortie de Boltac, le menu devrait recharger le gamestate.

**Observer la console** :
```
🔄 Reloading gamestate for [NomPersonnage]...
✅ Gamestate reloaded for [NomPersonnage]
```

### 7. Retourner dans le dongeon

1. Clic sur radio button **"Explore Dungeon"**
2. Clic sur le nom du personnage
3. Appuyer sur **I** pour ouvrir l'inventaire

**VÉRIFICATION FINALE** :
- ✅ L'item acheté est visible dans l'inventaire
- ✅ Le gold est correct (diminué du prix)

---

## Scénarios de diagnostic

### Scénario 1 : original_game is None

**Symptôme** :
```
[DEBUG] original_game provided: False
⚠️  No original game - loading gamestate to update
```

**Cause** : Le gamestate n'est pas passé correctement dans la chaîne `load_game_data → run → main_game_loop → exit_boltac`

**Solution** : Vérifier que `load_game_data` retourne bien 3 valeurs et que `run()` les propage.

### Scénario 2 : original_game.hero is NOT hero

**Symptôme** :
```
[DEBUG] original_game.hero is hero: False
[DEBUG] original_game.hero object id: 140111111
[DEBUG] hero object id: 140222222  <-- DIFFÉRENT
```

**Cause** : Une copie de l'objet hero a été faite quelque part

**Diagnostic** :
1. Comparer les IDs dans `load_game_data` vs `exit_boltac`
2. Si différents → Une copie a été faite dans `main_game_loop` ou `handle_buy`

**Solution** : Vérifier qu'aucune copie n'est faite (pas de `copy()`, `deepcopy()`, ou assignation)

### Scénario 3 : Inventory correct dans exit_boltac, mais perdu après

**Symptôme** :
```
[DEBUG] About to save gamestate with:
[DEBUG]   - Inventory: [..., ItemName, ...]  <-- Item présent
✅ Gamestate saved

[Retour au dungeon]
Inventory : [...]  <-- Item ABSENT
```

**Cause** : Problème dans `save_character_gamestate()` ou `load_character_gamestate()`

**Diagnostic** :
1. Vérifier que le fichier `.pkl` est bien sauvegardé
2. Vérifier que le menu recharge bien le bon fichier

### Scénario 4 : IDs d'objets changent entre load et exit

**Symptôme** :
```
[DEBUG LOAD] hero.entity.inventory object id: 140111111
[DEBUG EXIT] hero.entity.inventory object id: 140222222  <-- DIFFÉRENT
```

**Cause** : L'inventaire a été réassigné (ex: `hero.entity.inventory = [...]`)

**Solution** : Utiliser seulement des modifications in-place (ex: `hero.entity.inventory[0] = item`)

---

## Collecte des logs

### Copier tous les logs

Après le test complet, copier **TOUTE** la sortie console depuis :
- `✅ Loading [NomPersonnage] from active gamestate`
- Jusqu'à la fin de l'exploration du dungeon

### Points d'attention dans les logs

1. **IDs d'objets** : Doivent rester constants
2. **`original_game.hero is hero`** : Doit être `True`
3. **Inventory dans exit_boltac** : Doit contenir l'item acheté
4. **Gold** : Doit être cohérent partout

---

## Exemple de logs CORRECTS

```
✅ Loading Laucian from active gamestate (dungeon adventure)
[DEBUG LOAD] saved_game object id: 4567890123
[DEBUG LOAD] hero object id: 4567890456
[DEBUG LOAD] hero.entity object id: 4567890789
[DEBUG LOAD] char.gold: 150
[DEBUG LOAD] char.inventory: [Longsword, Shield, None, ...]

[User achète Battleaxe]

You bought Battleaxe!
[DEBUG] Gold BEFORE purchase: 150
[DEBUG] Gold AFTER purchase: 120
[DEBUG] Adding Battleaxe to inventory slot 2
[DEBUG] Inventory BEFORE: [Longsword, Shield, None, ...]
[DEBUG] Inventory AFTER: [Longsword, Shield, Battleaxe, ...]
[DEBUG] hero object id: 4567890456  ✅ MÊME ID
[DEBUG] hero.entity object id: 4567890789  ✅ MÊME ID
[DEBUG] hero.entity.inventory object id: 4567891234

[User quitte]

[DEBUG EXIT_BOLTAC] Starting exit for Laucian
[DEBUG] hero object id: 4567890456  ✅ MÊME ID
[DEBUG] hero.entity object id: 4567890789  ✅ MÊME ID
[DEBUG] char_entity.gold: 120
[DEBUG] char_entity.inventory: [Longsword, Shield, Battleaxe, ...]
[DEBUG] original_game provided: True  ✅
[DEBUG] original_game.hero object id: 4567890456  ✅ MÊME ID
[DEBUG] original_game.hero is hero: True  ✅ CRUCIAL
[DEBUG] original_game.hero.entity.gold: 120
[DEBUG] original_game.hero.entity.inventory: [Longsword, Shield, Battleaxe, ...]
✅ Character Laucian saved to characters directory
Saving gamestate for Laucian...
✅ Using original game object with modifications
[DEBUG] About to save gamestate with:
[DEBUG]   - Gold: 120
[DEBUG]   - Inventory: [Longsword, Shield, Battleaxe, ...]  ✅
✅ Gamestate saved with Boltac purchases/sales
```

**Tous les IDs sont identiques** → Le même objet est utilisé partout → Les modifications sont préservées ✅

---

## Prochaines étapes selon les résultats

### Si `original_game is hero: True` et item présent dans logs MAIS absent dans jeu

→ Problème dans `save_character_gamestate()` ou `load_character_gamestate()`

### Si `original_game is hero: False`

→ Problème dans le passage de paramètres entre fonctions

### Si IDs changent

→ Copie non intentionnelle quelque part

---

**Lancez le test et envoyez-moi TOUS les logs de la console !**

