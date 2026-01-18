# Diagnostic: "No Items Available" in Boltac's Shop - 17 Décembre 2024

## 🐛 Problème Rapporté

"No items available" s'affiche dans le menu Buy de Boltac's Trading Post.

## 🔍 Diagnostic Ajouté

J'ai ajouté des **messages de debug** pour identifier exactement pourquoi les items ne s'affichent pas.

### Messages au Démarrage

Lors du chargement du jeu, vous verrez maintenant :

```
Loading game data...
Loaded X monsters
Loaded Y weapons        ← NOUVEAU
Loaded Z armors         ← NOUVEAU
Loaded N characters from roster
```

**Si vous voyez :**
- `"WARNING: No weapons loaded!"` → Les armes n'ont pas été chargées
- `"WARNING: No armors loaded!"` → Les armures n'ont pas été chargées

### Messages dans le Menu Buy

Si "No items available" s'affiche, vous verrez maintenant des messages `[DEBUG]` expliquant pourquoi :

```
No items available
[DEBUG] No weapons in database
[DEBUG] Character has no prof_armors attribute
[DEBUG] Character has 0 prof_armors
```

## 🔧 Causes Possibles

### 1. Base de Données Vide

**Symptôme :**
```
[DEBUG] No weapons in database
```

**Cause :** `load_dungeon_collections()` a échoué ou retourné des listes vides.

**Solution :** Vérifier que les fichiers de données sont présents et que les imports fonctionnent.

### 2. Attributs Manquants sur le Personnage

**Symptôme :**
```
[DEBUG] Character has no prof_armors attribute
[DEBUG] Character has no prof_weapons attribute
```

**Cause :** Le personnage n'a pas été créé avec les bons attributs.

**Solution :** 
- Recréer le personnage via Training Grounds
- Ou charger depuis la base de données avec tous les attributs

### 3. Liste de Maîtrises Vide

**Symptôme :**
```
[DEBUG] Character has 0 prof_armors
```

**Cause :** Le personnage n'a aucune armure maîtrisée (possible pour un Wizard par exemple).

**Solution :** C'est normal pour certaines classes. Le personnage devrait quand même voir les armes.

### 4. Erreur de Tri

**Symptôme :**
```
[DEBUG] Error sorting weapons: ...
[DEBUG] Error sorting armors: ...
```

**Cause :** Les objets Weapon/Armor n'ont pas d'attribut `cost.value`.

**Solution :** Vérifier l'intégrité des données chargées.

## ✅ Améliorations Appliquées

### 1. Messages de Debug au Chargement

**Fichier :** `main_ncurses.py` lignes ~282-293

```python
# Debug: Log data loaded
if self.weapons:
    self.push_message(f"Loaded {len(self.weapons)} weapons")
else:
    self.push_message("WARNING: No weapons loaded!")

if self.armors:
    self.push_message(f"Loaded {len(self.armors)} armors")
else:
    self.push_message("WARNING: No armors loaded!")
```

### 2. Debug dans draw_buy_items()

**Fichier :** `main_ncurses.py` lignes ~762-818

```python
items = []
debug_msgs = []

# Check weapons availability
if not self.weapons:
    debug_msgs.append("No weapons in database")

# Check character attributes
if not hasattr(character, 'prof_armors'):
    debug_msgs.append("Character has no prof_armors attribute")
if not hasattr(character, 'prof_weapons'):
    debug_msgs.append("Character has no prof_weapons attribute")

# Build items list with error handling
try:
    weapons_sorted = sorted(self.weapons, key=lambda i: ...)
    items.extend(weapons_sorted)
    debug_msgs.append(f"Added {len(weapons_sorted)} weapons")
except Exception as e:
    debug_msgs.append(f"Error sorting weapons: {str(e)[:30]}")

# ... same for armors

# Display debug messages if no items
if not items:
    for msg in debug_msgs[:5]:
        self.stdscr.addstr(y, x, f"[DEBUG] {msg}")
```

### 3. Gestion d'Erreurs Améliorée

- Try/catch autour du tri des armes
- Try/catch autour du tri des armures
- Affichage des erreurs à l'écran

## 🧪 Comment Diagnostiquer

### Étape 1 : Vérifier le Chargement

```bash
python run_ncurses.py
```

Au démarrage, observez les messages :
- ✅ `"Loaded X weapons"` → Armes OK
- ✅ `"Loaded Y armors"` → Armures OK
- ❌ `"WARNING: No weapons loaded!"` → PROBLÈME

### Étape 2 : Tester le Menu Buy

```bash
→ Boltac's Trading Post
→ Sélectionner personnage
→ Buy
```

Si "No items available" :
- Lire les messages `[DEBUG]`
- Identifier la cause exacte

### Étape 3 : Vérifier les Personnages

Si `"Character has no prof_armors attribute"` :

```bash
→ Training Grounds
→ Character Status
→ Sélectionner le personnage
```

Vérifier que le personnage a bien tous ses attributs.

## 🔍 Scénarios de Diagnostic

### Scénario A : Aucune Arme Chargée

**Symptômes :**
```
WARNING: No weapons loaded!
[DEBUG] No weapons in database
```

**Diagnostic :**
- IMPORTS_AVAILABLE = False → Les imports ont échoué
- load_dungeon_collections() a retourné des listes vides

**Actions :**
1. Vérifier les dépendances (pygame, numpy)
2. Vérifier les fichiers de données
3. Regarder les erreurs au lancement

### Scénario B : Personnage Sans Attributs

**Symptômes :**
```
Loaded 150 weapons
[DEBUG] Character has no prof_armors attribute
```

**Diagnostic :**
- Le personnage a été créé avec les stubs (IMPORTS_AVAILABLE = False)
- Le personnage vient d'une vieille sauvegarde

**Actions :**
1. Créer un nouveau personnage via Training Grounds
2. Ou corriger manuellement le fichier .dmp

### Scénario C : Classe Sans Armures

**Symptômes :**
```
Loaded 150 weapons
Loaded 50 armors
[DEBUG] Character has 0 prof_armors
[DEBUG] Added 150 weapons
```

**Diagnostic :**
- C'est normal pour certaines classes (Wizard, Sorcerer)
- Le personnage devrait quand même voir les armes

**Actions :**
- Aucune, c'est le comportement attendu
- Le menu devrait afficher les armes

### Scénario D : Erreur de Tri

**Symptômes :**
```
[DEBUG] Error sorting weapons: 'NoneType' has no attribute 'value'
```

**Diagnostic :**
- Les objets Weapon n'ont pas tous un attribut cost.value
- Données corrompues

**Actions :**
1. Vérifier l'intégrité de la base de données
2. Recharger les données

## 📊 Checklist de Diagnostic

Utilisez cette checklist pour diagnostiquer :

- [ ] Au démarrage : "Loaded X weapons" s'affiche ?
- [ ] Au démarrage : "Loaded Y armors" s'affiche ?
- [ ] Dans Buy menu : Quels messages `[DEBUG]` s'affichent ?
- [ ] Le personnage a-t-il été créé via Training Grounds ?
- [ ] Le personnage vient-il d'une vieille sauvegarde ?
- [ ] IMPORTS_AVAILABLE = True ou False ?

## 🎯 Solutions par Cause

| Cause | Solution |
|-------|----------|
| No weapons in database | Vérifier load_dungeon_collections() |
| No prof_armors attribute | Recréer personnage |
| Character has 0 prof_armors | Normal pour certaines classes |
| Error sorting weapons | Vérifier intégrité données |

## 📝 Prochaines Étapes

1. **Lancer le jeu** avec les nouveaux messages de debug
2. **Observer les messages** au démarrage
3. **Aller dans Buy menu** et noter les messages `[DEBUG]`
4. **Partager les messages** pour diagnostic précis

## 🔧 Si le Problème Persiste

Si après ces améliorations vous voyez toujours "No items available" :

1. Prendre note des messages `[DEBUG]` affichés
2. Vérifier les messages au démarrage
3. Partager ces informations pour un diagnostic plus poussé

Les messages de debug vous diront **exactement** pourquoi les items ne s'affichent pas !

---

**Date :** 17 décembre 2024  
**Version :** 0.4.4 - Debug Messages  
**Statut :** 🔍 Diagnostic Tools Added

🛠️ **Lancez le jeu pour voir les messages de diagnostic !**

