# 🚧 PLAN DE MIGRATION : Séparation Business Logic / Presentation

## ✅ État Actuel (Phase 1 - Complété)

### Fichiers Nettoyés dans dnd-5e-core
- ✅ `equipment/weapon.py` - Attributs de positionnement retirés
- ✅ `equipment/armor.py` - Attributs de positionnement retirés

### Fichiers Modifiés dans DnD-5th-Edition-API
- ✅ `populate_functions.py` - request_armor() et request_weapon() nettoyés
- ✅ `populate_rpg_functions.py` - Fonctions helper GameEntity ajoutées
- ✅ `game_entity.py` - Créé avec pattern Composition

## ⏳ TODO : Fichiers Restants à Migrer

### 1. Classes Potion dans dnd-5e-core

**Problème :** Les classes Potion utilisent encore des paramètres non-métier

**Fichier :** `dnd-5e-core/dnd_5e_core/equipment/potion.py`

**Classes concernées :**
- `HealingPotion` - Utilise id, image_name, x, y, old_x, old_y
- `SpeedPotion` - Utilise id, image_name, x, y, old_x, old_y  
- `StrengthPotion` - Utilise id, image_name, x, y, old_x, old_y

**Action requise :**
```python
# AVANT
class HealingPotion(Potion):
    def __init__(self, id, image_name, x, y, old_x, old_y, name, rarity, ...):
        # ...

# APRÈS
class HealingPotion(Potion):
    def __init__(self, name, rarity, hit_dice, bonus, min_cost, max_cost, min_level=1):
        # Retirer tous les paramètres de positionnement
```

### 2. populate_rpg_functions.py - load_potions_collections()

**Problème :** Crée des potions avec paramètres de positionnement

**Fichier :** `populate_rpg_functions.py` (lignes 205-238)

**Action requise :**
```python
# AVANT
potion = HealingPotion(
    id=-1, image_name=fn('Healing'), 
    x=-1, y=-1, old_x=-1, old_y=-1,
    name='Healing', rarity=PotionRarity.COMMON,
    hit_dice='2d4', bonus=2, 
    min_cost=10, max_cost=50
)

# APRÈS
potion = HealingPotion(
    name='Healing',
    rarity=PotionRarity.COMMON,
    hit_dice='2d4',
    bonus=2,
    min_cost=10,
    max_cost=50
)
# Wrapper GameEntity si nécessaire pour pygame
```

### 3. Jeux à Migrer

#### A. dungeon_pygame.py ⭐ PRIORITAIRE

**Utilisation actuelle :**
- Accès direct à `monster.x`, `monster.y`
- Probablement aussi `weapon.x`, `armor.x`, `potion.x` ?

**Migration requise :**
```python
# AVANT
monster = request_monster('goblin')
monster.x = 10
monster.y = 20
screen.blit(image, (monster.x * TILE, monster.y * TILE))

# APRÈS
from game_entity import create_game_monster
monster_data = request_monster('goblin')
game_monster = create_game_monster(monster_data, x=10, y=20, image_name='goblin.png')
screen.blit(image, (game_monster.x * TILE, game_monster.y * TILE))
# Accès métier via game_monster.entity
```

**Lignes concernées :**
- Ligne 1058 : `monster.x` - Rendu des monstres
- Ligne 1171 : `monster.x, monster.y = cell` - Placement des monstres
- Chercher tous les usages de `.x` et `.y` sur les entités

#### B. main_ncurses.py

**Utilisation :** Probablement pas de positionnement (interface texte)

**Action :** Vérifier et adapter si nécessaire

#### C. wizardry.py (PyQt)

**Utilisation :** Interface PyQt, probablement pas de positionnement 2D

**Action :** Vérifier et adapter si nécessaire

#### D. boltac_pygame.py

**Utilisation :** Boutique pygame, peut utiliser positionnement

**Action :** Vérifier et migrer vers GameEntity si nécessaire

#### E. dungeon_menu_pygame.py

**Utilisation :** Menu pygame

**Action :** Vérifier et migrer vers GameEntity si nécessaire

## 📋 Ordre de Migration Recommandé

### Phase 2 : Nettoyage Potions

1. ✅ **Nettoyer classes Potion dans dnd-5e-core**
   - Retirer id, image_name, x, y, old_x, old_y
   - Garder uniquement logique métier

2. ✅ **Adapter populate_rpg_functions.py**
   - Créer potions sans paramètres de positionnement
   - Ajouter helper create_game_potion_with_image()

### Phase 3 : Migration dungeon_pygame.py

3. ✅ **Identifier tous les usages de positionnement**
   ```bash
   grep -n "\.x\|\.y\|\.old_x\|\.old_y\|\.image_name" dungeon_pygame.py
   ```

4. ✅ **Créer wrappers GameEntity pour les entités**
   - Monsters → GameMonster
   - Potions → GamePotion  
   - Weapons → GameWeapon (si utilisés dans donjon)
   - Armors → GameArmor (si utilisés dans donjon)

5. ✅ **Adapter le code de rendu**
   - Remplacer `entity.x` par `game_entity.x`
   - Accès métier via `game_entity.entity`

### Phase 4 : Migration Autres Jeux

6. ✅ **main_ncurses.py** - Vérifier/Adapter
7. ✅ **wizardry.py** - Vérifier/Adapter
8. ✅ **boltac_pygame.py** - Migrer vers GameEntity
9. ✅ **dungeon_menu_pygame.py** - Migrer vers GameEntity

### Phase 5 : Tests & Validation

10. ✅ **Rebuild et test de chaque jeu**
11. ✅ **Validation que les exécutables fonctionnent**
12. ✅ **Documentation finale**

## 🔧 Scripts Helper pour la Migration

### Script 1 : Trouver les Usages de Positionnement

```bash
#!/bin/bash
# find_positioning_usage.sh

echo "=== Recherche des usages de positionnement ==="
echo ""

for file in dungeon_pygame.py boltac_pygame.py dungeon_menu_pygame.py main_ncurses.py wizardry.py; do
    if [ -f "$file" ]; then
        echo "📄 $file:"
        grep -n "\.x\b\|\.y\b\|\.old_x\|\.old_y\|\.image_name" "$file" | head -20
        echo ""
    fi
done
```

### Script 2 : Compter les Modifications Nécessaires

```bash
#!/bin/bash
# count_changes.sh

echo "=== Comptage des modifications nécessaires ==="
echo ""

for file in dungeon_pygame.py boltac_pygame.py dungeon_menu_pygame.py; do
    if [ -f "$file" ]; then
        count=$(grep -c "\.x\b\|\.y\b" "$file" || true)
        echo "$file: ~$count lignes à vérifier"
    fi
done
```

## ⚠️ Défis Identifiés

### 1. Potions avec Anciens Paramètres

**Problème :** load_potions_collections() crée 11 potions différentes avec anciens paramètres

**Impact :** Cassera le code si on change simplement les signatures

**Solution :**
- Option A : Changer signatures Potion ET update load_potions_collections() en même temps
- Option B : Garder anciens paramètres optionnels temporairement (avec warnings)
- ✅ **Recommandé : Option A** (changement propre en une fois)

### 2. GameEntity Générique vs Spécifique

**Question :** GameEntity[T] ou classes séparées GameMonster, GamePotion ?

**Recommandation actuelle :** Garder GameEntity[T] générique
- Plus flexible
- Moins de code
- Type aliases pour la lisibilité : `GameMonster = GameEntity[Monster]`

### 3. Compatibilité Ascendante

**Question :** Comment migrer progressivement sans tout casser ?

**Approche :**
1. ✅ Phase 1 : GameEntity créé, attributs marqués DEPRECATED
2. ✅ Phase 2 : Migration d'un jeu (dungeon_pygame.py)
3. ⏳ Phase 3 : Migration des autres jeux
4. ⏳ Phase 4 : Retrait complet des attributs deprecated

## 📊 Estimation du Travail

### Déjà Fait (Phase 1)
- ✅ Architecture GameEntity définie
- ✅ Weapon et Armor nettoyés dans dnd-5e-core
- ✅ populate_functions.py nettoyé
- ✅ Helper functions créées

### Reste à Faire

| Tâche | Complexité | Temps Estimé |
|-------|-----------|--------------|
| Nettoyer classes Potion | Moyen | 30 min |
| Adapter load_potions_collections() | Facile | 15 min |
| Migrer dungeon_pygame.py | Élevé | 2-3 heures |
| Vérifier main_ncurses.py | Facile | 15 min |
| Vérifier wizardry.py | Facile | 15 min |
| Migrer boltac_pygame.py | Moyen | 1 heure |
| Migrer dungeon_menu_pygame.py | Moyen | 1 heure |
| Tests complets | Moyen | 1 heure |
| **TOTAL** | | **6-8 heures** |

## 🎯 Prochaine Étape Immédiate

**Recommandation : Commencer par dungeon_pygame.py**

Raisons :
1. C'est le jeu principal qui utilise le positionnement
2. Une fois migré, servira d'exemple pour les autres
3. Permettra de valider que GameEntity fonctionne bien

**Commandes pour démarrer :**

```bash
cd /Users/display/PycharmProjects/DnD-5th-Edition-API

# 1. Identifier tous les usages
grep -n "monster\.x\|monster\.y" dungeon_pygame.py

# 2. Identifier structure du code
grep -n "class.*:" dungeon_pygame.py
grep -n "def.*monster" dungeon_pygame.py

# 3. Créer une branche de migration
git checkout -b feature/migrate-to-game-entity
```

## 📚 Documentation Nécessaire

### Après Migration Complète

1. **Guide de Migration** - Pour futurs jeux
2. **API Reference** - GameEntity documentation complète
3. **Examples** - Snippets avant/après
4. **Architecture Diagram** - Schéma de séparation

---

**Status Actuel :** Phase 1 Complète ✅  
**Prochaine Phase :** Migration dungeon_pygame.py  
**Temps Estimé Restant :** 6-8 heures  
**Complexité :** Moyenne à Élevée

