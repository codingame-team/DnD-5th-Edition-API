# Debug : Attaques toujours pas exécutées dans Combat_module.py

**Date** : 31 décembre 2024  
**Problème** : Les attaques ne sont toujours pas exécutées dans wizardry.py  
**Statut** : 🔍 DEBUG AJOUTÉ

---

## 🔍 Hypothèses

### 1. Exception silencieuse
- Une erreur se produit dans la boucle de combat
- L'erreur est ignorée silencieusement
- La boucle continue sans exécuter les actions

### 2. Boucle vide
- La queue d'attaquants est vide
- `while queue:` ne s'exécute jamais
- Aucun message n'est affiché

### 3. Conditions incorrectes
- `if attacker.hit_points > 0:` est toujours False
- Ou `isinstance(attacker, Monster/Character)` échoue
- Le corps de la condition n'est jamais exécuté

---

## 🔧 Debug ajouté

### 1. Try/Except dans la boucle while

**Ligne 156** :
```python
while queue:
    try:
        attacker = queue.pop()
        debug(f"Processing attacker: {attacker.name} (HP: {attacker.hit_points})")
        # ... rest of combat logic ...
    except Exception as e:
        debug(f"ERROR in combat loop: {type(e).__name__}: {str(e)}")
        import traceback
        debug(traceback.format_exc())
        self.cprint(f"ERROR: {type(e).__name__}: {str(e)}")
```

**But** : Catcher toutes les exceptions et les afficher dans la console ET l'interface Qt.

---

### 2. Debug supplémentaires

**Ligne 160** :
```python
debug(f"  → Attacker is alive, checking type...")
```

**Ligne 162** :
```python
debug(f"  → {attacker.name} is a Monster")
```

**Ligne 258** :
```python
debug(f"  → {attacker.name} is a Character")
debug(f"  → Character action: {action.type}")
```

---

## 📊 Messages attendus dans la console

### Scénario normal (combat fonctionne)

```
actions [Attack -  - Harpy, Spell - Magic Missile - Sahuagin]
=== ROUND 1 ===
Queue size: 8, Alive monsters: 2, Alive chars: 6
Starting combat loop with 8 attackers in queue
Processing attacker: Gandalf (HP: 13)
  → Attacker is alive, checking type...
  → Gandalf is a Character
  → Character action: CharActionType.MELEE_ATTACK
Gandalf slashes Harpy for 12 hit points!
Processing attacker: Harpy (HP: 7)
  → Attacker is alive, checking type...
  → Harpy is a Monster
Harpy slashes Gandalf for 5 hit points!
...
Combat loop finished. Round 1 complete
```

---

### Scénario avec exception

```
actions [Attack -  - Harpy, Spell - Magic Missile - Sahuagin]
=== ROUND 1 ===
Queue size: 8, Alive monsters: 2, Alive chars: 6
Starting combat loop with 8 attackers in queue
Processing attacker: Gandalf (HP: 13)
  → Attacker is alive, checking type...
  → Gandalf is a Character
  → Character action: CharActionType.MELEE_ATTACK
ERROR in combat loop: AttributeError: 'NoneType' object has no attribute 'name'
Traceback (most recent call last):
  File "Combat_module.py", line 270, in combat
    monster: Monster = min(monsters, key=lambda m: m.hit_points)
AttributeError: 'NoneType' object has no attribute 'name'
```

**Interface Qt** :
```
ERROR: AttributeError: 'NoneType' object has no attribute 'name'
```

---

### Scénario avec boucle vide

```
actions [Attack -  - Harpy, Spell - Magic Missile - Sahuagin]
=== ROUND 1 ===
Queue size: 0, Alive monsters: 2, Alive chars: 6
Starting combat loop with 0 attackers in queue
Combat loop finished. Round 1 complete
```

**Problème** : Queue vide dès le début

---

### Scénario avec HP à 0

```
actions [Attack -  - Harpy, Spell - Magic Missile - Sahuagin]
=== ROUND 1 ===
Queue size: 8, Alive monsters: 2, Alive chars: 6
Starting combat loop with 8 attackers in queue
Processing attacker: Gandalf (HP: 0)
Processing attacker: Harpy (HP: 0)
...
Combat loop finished. Round 1 complete
```

**Problème** : Tous les attaquants ont HP = 0

---

## 🧪 Procédure de test

### Étape 1 : Lancer wizardry.py

```bash
python pyQTApp/wizardry.py 2>&1 | tee combat_debug.log
```

### Étape 2 : Aller à Edge of Town

1. Cliquer sur "Edge of Town"
2. Sélectionner une action pour chaque personnage
3. Cliquer sur "Combat"

### Étape 3 : Observer la console

Regarder dans `stderr` ou `combat_debug.log` pour voir les messages de debug.

### Étape 4 : Observer l'interface Qt

Regarder dans le panneau "Events" pour voir si des messages d'erreur s'affichent.

---

## 🔍 Problèmes possibles identifiés

### 1. abilities.dex n'existe pas

**Code** :
```python
attack_queue = [(c, randint(1, c.abilities.dex)) for c in self.party] + 
               [(m, randint(1, m.abilities.dex)) for m in self.monsters]
```

**Problème potentiel** : Si `abilities` n'a pas d'attribut `dex`, cela lève une exception.

**Solution** :
```python
# Option 1: Vérifier l'attribut
attack_queue = [(c, randint(1, getattr(c.abilities, 'dex', 10))) for c in self.party] + 
               [(m, randint(1, getattr(m.abilities, 'dex', 10))) for m in self.monsters]

# Option 2: Try/except
def get_initiative(entity):
    try:
        return randint(1, entity.abilities.dex)
    except AttributeError:
        return randint(1, 10)

attack_queue = [(c, get_initiative(c)) for c in self.party] + 
               [(m, get_initiative(m)) for m in self.monsters]
```

---

### 2. Queue inversée

**Code** :
```python
attack_queue.sort(key=lambda x: x[1], reverse=True)
attackers = [c for c, init_roll in attack_queue]
queue = [c for c in attackers if c.hit_points > 0]
while queue:
    attacker = queue.pop()  # Pop LAST element
```

**Problème** : `pop()` prend le dernier élément (plus basse initiative) au lieu du premier (plus haute initiative).

**Solution** :
```python
# Option 1: Pop from front
attacker = queue.pop(0)

# Option 2: Don't reverse sort
attack_queue.sort(key=lambda x: x[1])  # Remove reverse=True
attacker = queue.pop()  # Now pop() gets highest initiative
```

---

### 3. Break prématuré

**Code** :
```python
melee_chars: List[Character] = [c for i, c in enumerate(alive_chars) if i < 3]
ranged_chars: List[Character] = [c for i, c in enumerate(alive_chars) if i >= 3]
if not melee_chars + ranged_chars:
    break
```

**Problème** : Si `alive_chars` est vide, sort de la boucle même s'il reste des monstres à traiter.

**Solution** :
```python
if not alive_chars:
    break  # More explicit check
```

---

## 📝 Prochaines étapes

### Si exception trouvée
1. Lire le traceback complet
2. Identifier la ligne exacte qui cause l'erreur
3. Corriger le bug
4. Tester à nouveau

### Si boucle vide
1. Vérifier pourquoi `queue` est vide
2. Vérifier `attack_queue` avant le tri
3. Vérifier `self.party` et `self.monsters`
4. Vérifier les HP des entités

### Si HP à 0
1. Vérifier `load_monsters()` et `hp_roll()`
2. Vérifier `load_party()`
3. S'assurer que les entités ont des HP > 0 au départ

### Si aucun message
1. Vérifier que `debug()` fonctionne
2. Vérifier que stderr est redirigé correctement
3. Vérifier que PyQt affiche bien les messages

---

## 🎯 Objectif

Identifier **EXACTEMENT** où le code échoue :
- ✅ Exception catchée et affichée
- ✅ Debug détaillé à chaque étape
- ✅ Messages visibles dans console ET interface

**Lancez maintenant wizardry.py et regardez les messages de debug !**

---

**Fichier modifié** :
- `/pyQTApp/EdgeOfTown/Combat_module.py`

**Lignes modifiées** :
- 156-158 : Try block
- 160, 162, 258-259 : Debug supplémentaires
- 303-308 : Except block avec traceback

**Status** : 🔍 DEBUG EN PLACE - Testez et observez les messages !

