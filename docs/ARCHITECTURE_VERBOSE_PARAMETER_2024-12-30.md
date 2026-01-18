# Architecture : Méthode gain_level() avec paramètre verbose

**Date** : 30 décembre 2024  
**Objectif** : Unifier la gestion des messages dans les méthodes métier du package `dnd_5e_core`  
**Statut** : ✅ IMPLÉMENTÉ

---

## Vue d'ensemble

### Principe : Messages stockés, affichage optionnel

**Architecture** :
```python
def business_method(self, ..., verbose: bool = False) -> tuple:
    """
    Args:
        verbose: If True, print messages. If False, only return them.
    
    Returns:
        tuple: (messages: str, result_data)
    """
    display_msg: List[str] = []
    
    # Business logic
    display_msg.append("Action performed")
    
    # Format messages
    messages = '\n'.join(display_msg)
    
    # Optional print
    if verbose:
        print(messages)
    
    return messages, result_data
```

**Avantages** :
- ✅ **Séparation métier/UI** : La logique métier ne dépend pas de l'affichage
- ✅ **Flexibilité** : Chaque frontend choisit comment afficher les messages
- ✅ **Testabilité** : Les tests peuvent vérifier les messages sans capturer stdout
- ✅ **Compatibilité** : Fonctionne pour console, pygame, web, etc.

---

## Méthode gain_level() - Implémentation complète

### Signature

**Fichier** : `/dnd-5e-core/dnd_5e_core/entities/character.py`

```python
def gain_level(self, tome_spells: List = None, verbose: bool = False) -> tuple:
    """
    Gain a level with optional ability changes and spell learning.

    Args:
        tome_spells: List of Spell objects available to learn from (for spellcasters)
        verbose: If True, print messages to console. If False, only return messages.

    Returns:
        tuple: (messages: str, new_spells: List[Spell])
            - messages: Newline-separated string of level-up events
            - new_spells: List of newly learned spells (empty if not a spellcaster)
    """
```

### Logique métier complète

#### 1. Augmentation du niveau et HP

```python
display_msg: List[str] = []
new_spells = []

# Increase level
self.level += 1

# Calculate HP gain
level_up_hit_die = {12: 7, 10: 6, 8: 5, 6: 4}
hp_gained = randint(1, level_up_hit_die[self.class_type.hit_die]) + self.ability_modifiers.con
hp_gained = max(1, hp_gained)
self.max_hit_points += hp_gained
self.hit_points += hp_gained

display_msg.append(f"New level #{self.level} gained!!!")
display_msg.append(f"{self.name} gained {hp_gained} hit points")
```

#### 2. Changements de caractéristiques (vieillissement)

**Inspiré de Wizardry** : Avec l'âge, possibilité de perdre ou gagner des caractéristiques.

```python
# Handle ability score changes due to aging (PROCEDURE GAINLOST from Wizardry)
attrs = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
for attr in attrs:
    val = self.abilities.get_value_by_name(name=attr)
    if randint(0, 3) % 4:  # 75% chance
        if randint(0, 129) < self.age // 52:  # Age check (age in weeks)
            # Lose ability due to age
            if val == 18 and randint(0, 5) != 4:
                continue
            val -= 1
            if attr == "Constitution" and val == 2:
                display_msg.append("** YOU HAVE DIED OF OLD AGE **")
                self.status = "LOST"
                self.hit_points = 0
            else:
                display_msg.append(f"You lost {attr}")
        elif val < 18:
            # Gain ability
            val += 1
            display_msg.append(f"You gained {attr}")
    self.abilities.set_value_by_name(name=attr, value=val)
```

**Mécanique** :
- 75% de chance de test par caractéristique
- Si vieux : risque de perdre (peut mourir de vieillesse si CON = 2)
- Si jeune : chance de gagner (jusqu'à 18)

#### 3. Apprentissage des sorts (spellcasters)

```python
if self.class_type.can_cast and tome_spells:
    # Spell slots disponibles au nouveau niveau
    available_spell_levels = [
        i + 1 for i, slot in enumerate(self.class_type.spell_slots[self.level]) if slot > 0
    ]
    
    # Calcul du nombre de sorts à apprendre
    if self.level > 1:
        new_spells_known_count = (
            self.class_type.spells_known[self.level - 1] - 
            self.class_type.spells_known[self.level - 2]
        )
        new_cantrip_count = 0
        if self.class_type.cantrips_known:
            new_cantrip_count = (
                self.class_type.cantrips_known[self.level - 1] - 
                self.class_type.cantrips_known[self.level - 2]
            )
    else:
        new_spells_known_count = self.class_type.spells_known[0]
        new_cantrip_count = self.class_type.cantrips_known[0] if self.class_type.cantrips_known else 0
    
    # Filtrer les sorts apprenables
    learnable_spells = [
        s for s in tome_spells 
        if s.level <= max(available_spell_levels) 
        and s not in self.sc.learned_spells 
        and hasattr(s, 'damage_type') and s.damage_type
    ]
    
    # Mettre à jour les spell slots
    self.sc.spell_slots = deepcopy(self.class_type.spell_slots[self.level])
    
    # Trier par niveau (plus haut en premier)
    learnable_spells.sort(key=lambda s: s.level, reverse=True)
    
    # Apprendre les sorts
    new_spells_count = 0
    while learnable_spells and (new_spells_known_count > 0 or new_cantrip_count > 0):
        learned_spell = learnable_spells.pop()
        
        if learned_spell.level == 0 and new_cantrip_count > 0:
            new_cantrip_count -= 1
            self.sc.learned_spells.append(learned_spell)
            new_spells.append(learned_spell)
            new_spells_count += 1
            display_msg.append(f"Learned cantrip: {learned_spell.name}")
        elif learned_spell.level > 0 and new_spells_known_count > 0:
            new_spells_known_count -= 1
            self.sc.learned_spells.append(learned_spell)
            new_spells.append(learned_spell)
            new_spells_count += 1
            display_msg.append(f"Learned spell: {learned_spell.name} (level {learned_spell.level})")
    
    if new_spells_count:
        display_msg.append(f"You learned {new_spells_count} new spell(s)!!!")
```

#### 4. Formatage et retour

```python
# Format messages
messages = '\n'.join(display_msg)

# Print if verbose
if verbose:
    print(messages)

return messages, new_spells
```

---

## Utilisation selon les frontends

### 1. Pygame (dungeon_pygame.py) - Affichage direct

**Contexte** : Jeu graphique temps réel, messages affichés immédiatement.

```python
def handle_fountains(game):
    # ...
    if char.level < len(game.xp_levels) and char.xp >= game.xp_levels[char.level]:
        # Get available spells
        tome_spells = None
        if char.class_type.can_cast:
            spell_names = populate(collection_name='spells', key_name='results')
            all_spells = [request_spell(name) for name in spell_names]
            tome_spells = [s for s in all_spells if s and char.class_type.index in s.allowed_classes]
        
        # Gain level - verbose=True prints directly
        messages, new_spells = char.gain_level(tome_spells=tome_spells, verbose=True)
        
        # Add spell sprites
        if new_spells:
            for spell in new_spells:
                image = pygame.image.load(f"{spell_sprites_dir}/{spell.school}.png")
                spell.id = max(sprites) + 1 if sprites else 1
                sprites[spell.id] = pygame.transform.scale(image, (ICON_SIZE, ICON_SIZE))
```

**Avantages** :
- ✅ **Simple** : Un seul appel avec `verbose=True`
- ✅ **Immédiat** : Messages affichés dans la console pygame
- ✅ **Focus frontend** : Gère seulement les sprites

### 2. Console (main.py) - Affichage personnalisé

**Contexte** : Jeu console tour par tour, messages groupés et formatés.

```python
def castle(party: List[Character], roster: List[Character], xp_levels: List[int]):
    display_msg: List[str] = []
    
    # ... autres messages (healing, etc.) ...
    
    # Level gain
    if char.level < len(xp_levels) and char.xp >= xp_levels[char.level]:
        if char.class_type.can_cast:
            spell_names = populate(collection_name="spells", key_name="results")
            all_spells = [request_spell(name) for name in spell_names]
            class_tome_spells = [s for s in all_spells if s and char.class_type.index in s.allowed_classes]
            display_message, new_spells = char.gain_level(tome_spells=class_tome_spells, verbose=False)
        else:
            display_message, new_spells = char.gain_level(verbose=False)
        
        # Ajouter aux messages globaux
        display_msg.append(display_message)
    
    # ... autres messages (birthday, etc.) ...
    
    # Affichage groupé final
    return "\n".join(display_msg)
```

**Avantages** :
- ✅ **Contrôle total** : Messages groupés avec d'autres actions
- ✅ **Formatage personnalisé** : Peut ajouter des séparateurs, couleurs, etc.
- ✅ **Contexte** : Messages dans le contexte de l'action globale

### 3. ncurses (main_ncurses.py) - Affichage fenêtré

**Contexte** : Interface textuelle avec fenêtres, messages formatés avec couleurs.

```python
def display_castle_actions(char: Character, tome_spells: List[Spell] = None):
    window = curses.newwin(20, 60, 5, 10)
    
    # Gain level
    messages, new_spells = char.gain_level(tome_spells=tome_spells, verbose=False)
    
    # Affichage formaté avec couleurs
    lines = messages.split('\n')
    y = 1
    for line in lines:
        if "New level" in line:
            window.addstr(y, 2, line, curses.color_pair(COLOR_GREEN) | curses.A_BOLD)
        elif "You lost" in line or "DIED" in line:
            window.addstr(y, 2, line, curses.color_pair(COLOR_RED) | curses.A_BOLD)
        elif "Learned spell" in line:
            window.addstr(y, 2, line, curses.color_pair(COLOR_CYAN))
        else:
            window.addstr(y, 2, line)
        y += 1
    
    window.refresh()
```

**Avantages** :
- ✅ **Formatage avancé** : Couleurs, style selon le type de message
- ✅ **Fenêtrage** : Messages dans des zones dédiées
- ✅ **Interactivité** : Peut paginer les longs messages

### 4. Web/API (futur) - JSON response

**Contexte** : API REST, messages en JSON.

```python
@app.route('/character/<id>/levelup', methods=['POST'])
def level_up(id):
    char = get_character(id)
    tome_spells = get_available_spells(char)
    
    # Gain level - verbose=False pour récupérer les messages
    messages, new_spells = char.gain_level(tome_spells=tome_spells, verbose=False)
    
    # Return JSON
    return jsonify({
        'success': True,
        'new_level': char.level,
        'messages': messages.split('\n'),
        'new_spells': [s.name for s in new_spells],
        'character': serialize_character(char)
    })
```

**Avantages** :
- ✅ **Structuré** : Messages en array JSON
- ✅ **Complet** : Toutes les données de la montée de niveau
- ✅ **Client-agnostic** : Le client choisit comment afficher

---

## Autres méthodes à migrer avec ce pattern

### 1. Character.attack()

**Actuel** : Affiche directement avec `cprint()`

**Proposé** :
```python
def attack(self, monster, in_melee: bool = True, verbose: bool = False) -> tuple:
    """
    Returns:
        tuple: (messages: str, damage: int)
    """
    display_msg = []
    
    # Attack logic
    if hit:
        display_msg.append(f"{self.name} hits {monster.name} for {damage} damage!")
    else:
        display_msg.append(f"{self.name} misses {monster.name}!")
    
    messages = '\n'.join(display_msg)
    if verbose:
        print(messages)
    
    return messages, damage
```

### 2. Monster.attack()

```python
def attack(self, target, actions, distance, verbose: bool = False) -> tuple:
    """
    Returns:
        tuple: (messages: str, damage: int)
    """
    display_msg = []
    
    # Attack logic
    display_msg.append(f"{self.name} attacks {target.name}!")
    
    messages = '\n'.join(display_msg)
    if verbose:
        print(messages)
    
    return messages, damage
```

### 3. Character.drink()

```python
def drink(self, potion, verbose: bool = False) -> tuple:
    """
    Returns:
        tuple: (messages: str, hp_restored: int)
    """
    display_msg = []
    
    # Drink logic
    display_msg.append(f"{self.name} drinks {potion.name}")
    display_msg.append(f"Restored {hp_restored} HP!")
    
    messages = '\n'.join(display_msg)
    if verbose:
        print(messages)
    
    return messages, hp_restored
```

### 4. Character.victory()

```python
def victory(self, monster, solo_mode: bool = True, verbose: bool = False) -> tuple:
    """
    Returns:
        tuple: (messages: str, xp_gained: int, gold_gained: int)
    """
    display_msg = []
    
    # Victory logic
    display_msg.append(f"{self.name} defeated {monster.name}!")
    display_msg.append(f"Gained {xp_gained} XP and {gold_gained} gold")
    
    messages = '\n'.join(display_msg)
    if verbose:
        print(messages)
    
    return messages, xp_gained, gold_gained
```

---

## Pattern général

### Template pour toute méthode métier

```python
def business_action(self, ..., verbose: bool = False) -> tuple:
    """
    Perform a business action.
    
    Args:
        ...: Business parameters
        verbose: If True, print messages. If False, return them silently.
    
    Returns:
        tuple: (messages: str, result_data...)
            - messages: Newline-separated string of action events
            - result_data: Action-specific results (damage, items, etc.)
    """
    # 1. Initialize message container
    display_msg: List[str] = []
    
    # 2. Business logic with message collection
    # ... perform action ...
    display_msg.append("Action performed")
    display_msg.append(f"Result: {result}")
    
    # 3. Format messages
    messages = '\n'.join(display_msg)
    
    # 4. Optional print
    if verbose:
        print(messages)
    
    # 5. Return messages + results
    return messages, result_data
```

### Règles de conception

1. **Toujours retourner les messages** : Même si verbose=True
2. **Messages dans une List[str]** : Un élément = une ligne
3. **Join avec '\n'** : Formatage standard
4. **verbose=False par défaut** : Pour ne pas forcer l'affichage
5. **Tuple de retour** : (messages, ...data)

---

## Migration progressive

### Phase 1 : Méthodes critiques ✅ FAIT

- ✅ `Character.gain_level()` - Montée de niveau

### Phase 2 : Méthodes de combat

- [ ] `Character.attack()` - Attaque du personnage
- [ ] `Monster.attack()` - Attaque du monstre
- [ ] `Character.victory()` - Victoire sur un monstre

### Phase 3 : Méthodes d'items

- [ ] `Character.drink()` - Boire une potion
- [ ] `Character.equip()` - Équiper un item
- [ ] `Character.use_item()` - Utiliser un item

### Phase 4 : Méthodes de sorts

- [ ] `Character.cast_spell()` - Lancer un sort
- [ ] `Spell.apply_effect()` - Appliquer l'effet d'un sort

---

## Tests unitaires

### Exemple de test pour gain_level()

```python
def test_gain_level_verbose_false():
    """Test that gain_level with verbose=False doesn't print"""
    char = create_test_character(level=1, xp=300)
    
    # Capture stdout
    import io, sys
    captured = io.StringIO()
    sys.stdout = captured
    
    # Call with verbose=False
    messages, new_spells = char.gain_level(verbose=False)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    # Check nothing was printed
    assert captured.getvalue() == ""
    
    # Check messages were returned
    assert "New level #2 gained!!!" in messages
    assert "gained" in messages.lower()

def test_gain_level_verbose_true():
    """Test that gain_level with verbose=True prints messages"""
    char = create_test_character(level=1, xp=300)
    
    # Capture stdout
    import io, sys
    captured = io.StringIO()
    sys.stdout = captured
    
    # Call with verbose=True
    messages, new_spells = char.gain_level(verbose=True)
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    
    # Check messages were printed
    output = captured.getvalue()
    assert "New level #2 gained!!!" in output
    
    # Check messages were also returned
    assert messages == output.strip()

def test_gain_level_spellcaster():
    """Test spell learning during level gain"""
    wizard = create_test_wizard(level=1, xp=300)
    tome_spells = [magic_missile, shield, mage_armor]
    
    messages, new_spells = wizard.gain_level(tome_spells=tome_spells, verbose=False)
    
    # Check spells were learned
    assert len(new_spells) == 2  # Wizard learns 2 spells at level 2
    assert all(s in wizard.sc.learned_spells for s in new_spells)
    
    # Check messages mention spells
    assert "Learned spell:" in messages
```

---

## Avantages de cette architecture

### 1. Séparation des responsabilités

```
┌─────────────────────────────────────────┐
│ Package métier (dnd_5e_core)            │
├─────────────────────────────────────────┤
│ • Logique de jeu pure                   │
│ • Stocke les messages                   │
│ • Retourne (messages, data)             │
│ • Pas de dépendance UI                  │
└─────────────────────────────────────────┘
                ↓ (messages, data)
┌─────────────────────────────────────────┐
│ Frontend (pygame/console/web)           │
├─────────────────────────────────────────┤
│ • Décide comment afficher               │
│ • Formatage personnalisé                │
│ • Contexte d'affichage                  │
│ • Interactivité                         │
└─────────────────────────────────────────┘
```

### 2. Testabilité

- ✅ **Tests faciles** : Vérifier les messages sans stdout
- ✅ **Isolation** : Tester logique métier indépendamment
- ✅ **Assertions** : `assert "message" in messages`

### 3. Flexibilité

- ✅ **Multi-frontend** : Console, pygame, web, mobile
- ✅ **Internationalisation** : Messages peuvent être traduits
- ✅ **Logs** : Messages peuvent être loggés
- ✅ **UI personnalisée** : Chaque frontend choisit son style

### 4. Compatibilité ascendante

```python
# Ancien code (dao_classes.py)
display_msg, new_spells = char.gain_level(tome_spells=spells)
print(display_msg)

# Nouveau code (dnd_5e_core) - Compatible
display_msg, new_spells = char.gain_level(tome_spells=spells, verbose=False)
print(display_msg)

# Nouveau code - Simplifié pour pygame
display_msg, new_spells = char.gain_level(tome_spells=spells, verbose=True)
# Déjà affiché, pas besoin de print
```

---

## Conclusion

✅ **ARCHITECTURE UNIFIÉE IMPLÉMENTÉE !**

### Changements effectués

1. ✅ **Méthode gain_level() complète** : Migrée de dao_classes.py
2. ✅ **Paramètre verbose** : Contrôle de l'affichage
3. ✅ **Retour tuple** : (messages, data) pour flexibilité
4. ✅ **Messages stockés** : List[str] → '\n'.join()
5. ✅ **Compatibilité** : Fonctionne pour tous les frontends

### Prochaines étapes

1. Migrer les autres méthodes (attack, victory, drink, etc.)
2. Ajouter des tests unitaires pour chaque méthode
3. Documenter les patterns dans le README de dnd_5e_core

**Le package dnd_5e_core est maintenant frontend-agnostic !** 🎮✨📦

---

**Fichiers modifiés** :
- `/dnd-5e-core/dnd_5e_core/entities/character.py` - Méthode gain_level() complète
- `/DnD-5th-Edition-API/dungeon_pygame.py` - handle_fountains() simplifié

**Status** : ✅ PRODUCTION READY

