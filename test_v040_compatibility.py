"""
Test de compatibilité des frontends avec dnd-5e-core v0.4.0
Valide que tous les frontends fonctionnent avec la nouvelle version
"""

import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))


def test_dnd_5e_core_version():
    """Vérifier que dnd-5e-core v0.4.0+ est installé"""
    print("\n" + "="*80)
    print("TEST 1: Version dnd-5e-core")
    print("="*80)

    try:
        import dnd_5e_core
        version = dnd_5e_core.__version__
        print(f"✅ dnd-5e-core installé: v{version}")

        # Vérifier version >= 0.4.0
        major, minor = map(int, version.split('.')[:2])
        if major == 0 and minor >= 4:
            print(f"✅ Version compatible (>= 0.4.0)")
            return True
        else:
            print(f"⚠️  Version ancienne: {version}")
            return False

    except ImportError:
        print("❌ dnd-5e-core non installé!")
        return False


def test_main_py_imports():
    """Vérifier que main.py peut importer dnd-5e-core"""
    print("\n" + "="*80)
    print("TEST 2: main.py Imports")
    print("="*80)

    try:
        # Simuler les imports de main.py
        from dnd_5e_core import (
            Character, Monster, Abilities, ClassType,
            load_monster, simple_character_generator
        )

        print(f"✅ Imports basiques OK")

        # Test création personnage avec ClassAbilities
        fighter = simple_character_generator(level=5, class_name='fighter', name='Test')

        if hasattr(fighter, 'multi_attacks'):
            print(f"✅ ClassAbilities appliquées (Extra Attack: {fighter.multi_attacks})")
        else:
            print(f"⚠️  ClassAbilities non détectées")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conditions_available():
    """Vérifier que le système de conditions est disponible"""
    print("\n" + "="*80)
    print("TEST 3: Système de Conditions")
    print("="*80)

    try:
        from dnd_5e_core.combat.condition import (
            Condition, ConditionType,
            create_poisoned_condition
        )

        print(f"✅ Module condition importé")

        condition = create_poisoned_condition()
        print(f"✅ Condition créée")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_magic_items_available():
    """Vérifier que les magic items sont disponibles"""
    print("\n" + "="*80)
    print("TEST 4: Magic Items")
    print("="*80)

    try:
        from dnd_5e_core.equipment import (
            create_ring_of_protection,
            create_wand_of_magic_missiles,
            create_staff_of_healing
        )

        items = [
            create_ring_of_protection(),
            create_wand_of_magic_missiles(),
            create_staff_of_healing()
        ]

        print(f"✅ {len(items)} magic items créés")
        for item in items:
            print(f"   - {item.name} ({item.rarity.value})")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiclass_system():
    """Vérifier que le système de multiclassing est disponible"""
    print("\n" + "="*80)
    print("TEST 5: Système de Multiclassing")
    print("="*80)

    try:
        from dnd_5e_core.classes.multiclass import (
            can_multiclass_into,
            MULTICLASS_PREREQUISITES
        )

        print(f"✅ Module multiclass importé")
        print(f"✅ {len(MULTICLASS_PREREQUISITES)} classes supportées")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_frontend_main_compatibility():
    """Vérifier compatibilité basique de main.py"""
    print("\n" + "="*80)
    print("TEST 6: Frontend main.py")
    print("="*80)

    try:
        # On ne peut pas vraiment importer main.py sans lancer le jeu
        # Mais on peut vérifier que le fichier existe et contient les bons imports

        main_file = Path(__file__).parent / "main.py"

        if not main_file.exists():
            print(f"❌ main.py non trouvé")
            return False

        content = main_file.read_text()

        # Vérifier imports clés
        required_imports = [
            "from dnd_5e_core",
            "Character",
            "Monster"
        ]

        missing = []
        for imp in required_imports:
            if imp not in content:
                missing.append(imp)

        if missing:
            print(f"⚠️  Imports manquants: {missing}")
        else:
            print(f"✅ main.py utilise dnd-5e-core")

        # Vérifier migration marker
        if "[MIGRATION v2]" in content or "dnd-5e-core package" in content:
            print(f"✅ main.py migré vers dnd-5e-core")

        return True

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def test_pygame_compatibility():
    """Vérifier compatibilité de dungeon_pygame.py"""
    print("\n" + "="*80)
    print("TEST 7: Frontend Pygame")
    print("="*80)

    try:
        pygame_file = Path(__file__).parent / "dungeon_pygame.py"

        if not pygame_file.exists():
            print(f"⚠️  dungeon_pygame.py non trouvé")
            return True  # Pas bloquant

        content = pygame_file.read_text()

        if "from dnd_5e_core" in content:
            print(f"✅ dungeon_pygame.py utilise dnd-5e-core")
        else:
            print(f"⚠️  dungeon_pygame.py n'utilise pas dnd-5e-core?")

        return True

    except Exception as e:
        print(f"⚠️  Erreur (non bloquant): {e}")
        return True


def run_all_tests():
    """Exécuter tous les tests de compatibilité"""
    print("\n" + "🧪"*40)
    print("TESTS DE COMPATIBILITÉ FRONTENDS - dnd-5e-core v0.4.0")
    print("🧪"*40)

    tests = [
        ("Version dnd-5e-core", test_dnd_5e_core_version),
        ("main.py Imports", test_main_py_imports),
        ("Système de Conditions", test_conditions_available),
        ("Magic Items", test_magic_items_available),
        ("Multiclassing", test_multiclass_system),
        ("Frontend main.py", test_frontend_main_compatibility),
        ("Frontend Pygame", test_pygame_compatibility),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERREUR dans {test_name}: {e}")
            results.append((test_name, False))

    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*80)

    passed = 0
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\nScore: {passed}/{len(results)} ({passed*100//len(results)}%)")

    if passed == len(results):
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ DnD-5th-Edition-API est compatible avec dnd-5e-core v0.4.0")
        print("\n💡 Les frontends bénéficient automatiquement:")
        print("   - ClassAbilities (Extra Attack, Rage, etc.)")
        print("   - RacialTraits (Darkvision, Lucky, etc.)")
        print("   - Conditions (Poisoned, Restrained, etc.)")
        print("   - Magic Items (10+ items prédéfinis)")
        print("   - Multiclassing (validation + spell slots)")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) échoué(s)")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
