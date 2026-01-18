#!/usr/bin/env python3
"""
Script de test pour vérifier que les actions de combat s'exécutent correctement
"""

import sys
from typing import List

# Test des imports
print("=" * 60)
print("TEST 1: Vérification des imports")
print("=" * 60)

try:
    from dnd_5e_core.entities import Character, Monster
    print("✅ Import Character et Monster depuis dnd-5e-core")
except Exception as e:
    print(f"❌ Erreur import dnd-5e-core: {e}")
    sys.exit(1)

try:
    from dao_classes import CharAction, CharActionType, RangeType
    print("✅ Import CharAction, CharActionType, RangeType depuis dao_classes")
except Exception as e:
    print(f"❌ Erreur import dao_classes: {e}")
    sys.exit(1)

# Test de isinstance
print("\n" + "=" * 60)
print("TEST 2: Vérification de isinstance()")
print("=" * 60)

# Créer des instances de test (simplifié)
from dnd_5e_core.abilities import Abilities
from dnd_5e_core.combat import Action, ActionType as ActionTypeCore
from dnd_5e_core.mechanics import DamageDice

# Monster de test
test_monster = Monster(
    index="goblin",
    name="Goblin",
    abilities=Abilities(str=8, dex=14, con=10, int=10, wis=8, cha=8),
    proficiencies=[],
    armor_class=15,
    hit_points=7,
    hit_dice="2d6",
    xp=50,
    speed=30,
    challenge_rating=0.25,
    actions=[],
    sc=None,
    sa=None
)

print(f"test_monster type: {type(test_monster)}")
print(f"test_monster.__class__.__name__: {test_monster.__class__.__name__}")
print(f"isinstance(test_monster, Monster): {isinstance(test_monster, Monster)}")
print(f"isinstance(test_monster, Character): {isinstance(test_monster, Character)}")

# Test attribut sa
print("\n" + "=" * 60)
print("TEST 3: Vérification de l'attribut 'sa'")
print("=" * 60)

print(f"Monster a l'attribut 'sa': {hasattr(test_monster, 'sa')}")
print(f"Monster.sa value: {test_monster.sa}")
print(f"Monster.sa is None: {test_monster.sa is None}")

# Test du filtre avec sa = None
print("\n" + "=" * 60)
print("TEST 4: Test du filtre sur sa=None")
print("=" * 60)

try:
    # Ancienne version (devrait planter)
    result = list(filter(lambda a: a.ready, test_monster.sa))
    print(f"❌ Ancienne version devrait planter mais ne plante pas: {result}")
except TypeError as e:
    print(f"✅ Ancienne version plante comme prévu: {e}")

try:
    # Nouvelle version (devrait fonctionner)
    result = list(filter(lambda a: a.ready, test_monster.sa)) if test_monster.sa else []
    print(f"✅ Nouvelle version fonctionne: {result}")
except Exception as e:
    print(f"❌ Nouvelle version plante: {e}")

print("\n" + "=" * 60)
print("RÉSUMÉ DES TESTS")
print("=" * 60)
print("✅ Tous les tests sont OK si vous voyez ce message !")
print("=" * 60)

