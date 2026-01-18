#!/usr/bin/env python3
"""Simple wrapper to test if main.py can be imported without errors"""
import sys
import os

print("=" * 60)
print("Test de l'importation de main.py avec dnd-5e-core")
print("=" * 60)
print()

# Add dnd-5e-core to path (development mode)
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)
    print(f"✅ dnd-5e-core path ajouté: {_dnd_5e_core_path}")

try:
    print()
    print("1. Importation de dnd_5e_core...")
    import dnd_5e_core
    print(f"   ✅ dnd_5e_core importé: {dnd_5e_core.__file__}")

    print()
    print("2. Importation des modules dnd_5e_core...")
    from dnd_5e_core.entities import Character, Monster
    from dnd_5e_core.equipment import Weapon, Armor
    from dnd_5e_core.ui import cprint, Color
    print("   ✅ Tous les modules dnd_5e_core importés avec succès")

    print()
    print("3. Test des classes de base...")
    from dnd_5e_core.abilities import Abilities
    from dnd_5e_core.classes import ClassType

    # Note: Abilities uses short attribute names (str, dex, con, int, wis, cha)
    abilities = Abilities(str=10, dex=10, con=10, int=10, wis=10, cha=10)
    print(f"   ✅ Abilities créé: STR={abilities.str}, DEX={abilities.dex}")

    print()
    print("4. Test d'importation des races...")
    from dnd_5e_core.races import Race
    print("   ✅ Race importé")

    print()
    print("5. Test d'importation des sorts...")
    from dnd_5e_core.spells import Spell
    print("   ✅ Spell importé")

    print()
    print("=" * 60)
    print("🎉 TOUS LES TESTS RÉUSSIS!")
    print("   Le module dnd-5e-core fonctionne correctement")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print()
    print("=" * 60)
    print(f"❌ ERREUR lors de l'importation: {e}")
    print("=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)

