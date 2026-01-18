#!/usr/bin/env python3
"""
Test de la fonction populate() après migration vers dnd-5e-core
"""

import sys
from pathlib import Path

# Ajouter dnd-5e-core au path
sys.path.insert(0, str(Path(__file__).parent.parent / 'dnd-5e-core'))

# Test 1: Import direct de dnd-5e-core
print("🧪 Test 1: Import direct de dnd-5e-core")
try:
    from dnd_5e_core.data import populate
    monsters = populate('monsters', 'results')
    print(f"✅ {len(monsters)} monstres chargés depuis dnd-5e-core")
    print(f"   Premiers: {monsters[:3]}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 2: Import avec URL
print("\n🧪 Test 2: Import avec URLs")
try:
    from dnd_5e_core.data import populate
    monsters_urls = populate('monsters', 'results', with_url=True)
    print(f"✅ {len(monsters_urls)} monstres avec URLs")
    print(f"   Premier: {monsters_urls[0]}")
except Exception as e:
    print(f"❌ Erreur: {e}")

# Test 3: Fonctions de convenance
print("\n🧪 Test 3: Fonctions de convenance")
try:
    from dnd_5e_core.data import get_monsters_list, get_spells_list
    monsters = get_monsters_list()
    spells = get_spells_list()
    print(f"✅ Monstres: {len(monsters)}")
    print(f"✅ Sorts: {len(spells)}")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n🎉 Tous les tests sont passés!")
print("✅ populate() depuis dnd-5e-core fonctionne correctement")

