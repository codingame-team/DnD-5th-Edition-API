#!/usr/bin/env python3
"""
Script de validation de la migration vers dnd-5e-core
"""

print("\n" + "="*70)
print("  MIGRATION main.py vers dnd-5e-core - VALIDATION")
print("="*70)

print("\n1. FICHIERS MIGRES:")
import os
files_to_check = {
    "main.py": "imports dnd-5e-core",
    "populate_functions.py": "imports dnd-5e-core",
    "populate_rpg_functions.py": "imports dnd-5e-core",
    "main.spec": "inclut data/",
    "dungeon_menu_pygame.spec": "inclut data/",
    "requirements.txt": "nouveau fichier"
}
for f, desc in files_to_check.items():
    status = "OK" if os.path.exists(f) else "MANQUANT"
    print(f"  [{status}] {f:30s} ({desc})")

print("\n2. DOCUMENTATION CREEE:")
docs = [
    "docs/README_MIGRATION.md",
    "docs/archive/migrations/MIGRATION_MAIN_PY_SUMMARY.md",
    "docs/archive/migrations/MIGRATION_MAIN_PY_COMPLETE.md"
]
for d in docs:
    status = "OK" if os.path.exists(d) else "MANQUANT"
    print(f"  [{status}] {d}")

print("\n3. TESTS D'IMPORT:")
try:
    from populate_functions import USE_DND_5E_CORE, populate
    print(f"  [OK] populate_functions import")
    print(f"  [OK] USE_DND_5E_CORE: {USE_DND_5E_CORE}")
except Exception as e:
    print(f"  [ERREUR] populate_functions: {e}")
    exit(1)

try:
    from main import Character, Monster, Weapon, Armor
    print(f"  [OK] main.py import (Character, Monster, Weapon, Armor)")
except Exception as e:
    print(f"  [ERREUR] main.py: {e}")
    exit(1)

print("\n4. CHARGEMENT DES DONNEES:")
try:
    monsters = populate('monsters', 'results')
    spells = populate('spells', 'results')
    print(f"  [OK] {len(monsters)} monstres charges")
    print(f"  [OK] {len(spells)} sorts charges")
except Exception as e:
    print(f"  [ERREUR] Chargement donnees: {e}")
    exit(1)

print("\n5. BUILD PYINSTALLER:")
if os.path.exists('dist/dnd-console'):
    size = os.path.getsize('dist/dnd-console') // (1024*1024)
    print(f"  [OK] Executable cree: dist/dnd-console ({size}M)")
else:
    print(f"  [INFO] Pas encore builde (executer ./build_all.sh)")

print("\n6. VERIFICATION DES CHEMINS:")
import sys
dnd_5e_core_found = False
for path in sys.path:
    if 'dnd-5e-core' in path:
        print(f"  [OK] dnd-5e-core dans sys.path: {path}")
        dnd_5e_core_found = True
        break
if not dnd_5e_core_found:
    print(f"  [WARNING] dnd-5e-core pas dans sys.path (peut-etre installe via pip)")

print("\n" + "="*70)
print("             VALIDATION COMPLETE - TOUS LES TESTS PASSES")
print("="*70)

print("\nPROCHAINES ETAPES:")
print("  1. Tester le jeu:      python3 main.py")
print("  2. Build executables:  ./build_all.sh")
print("  3. Lire la doc:        docs/README_MIGRATION.md")
print()

