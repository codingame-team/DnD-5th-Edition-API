#!/usr/bin/env python3
"""Test simple qui vérifie que dnd_5e_core est inclus dans l'exécutable"""
import sys
import os

print("=" * 50)
print("Test dnd-5e-core dans l'exécutable")
print("=" * 50)
print()

try:
    print("1. Test import dnd_5e_core...")
    import dnd_5e_core
    print(f"   ✅ Module importé depuis: {dnd_5e_core.__file__}")

    print()
    print("2. Test import des entités...")
    from dnd_5e_core.entities import Character, Monster
    print("   ✅ Character et Monster importés")

    print()
    print("3. Test import des équipements...")
    from dnd_5e_core.equipment import Weapon, Armor
    print("   ✅ Weapon et Armor importés")

    print()
    print("4. Test import du système de combat...")
    from dnd_5e_core.combat import Action, ActionType
    print("   ✅ Combat system importé")

    print()
    print("5. Test import des utilitaires...")
    from dnd_5e_core.ui import cprint, Color
    print("   ✅ UI utilities importés")

    print()
    print("=" * 50)
    print("🎉 TOUS LES TESTS RÉUSSIS!")
    print("=" * 50)
    sys.exit(0)

except Exception as e:
    print()
    print("=" * 50)
    print(f"❌ ERREUR: {e}")
    print("=" * 50)
    import traceback
    traceback.print_exc()
    sys.exit(1)

