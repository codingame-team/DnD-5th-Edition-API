#!/usr/bin/env python3
"""
Migration Guide - dao_classes to dnd-5e-core
How to migrate existing games to use the new package
"""

# ============================================
# MIGRATION GUIDE
# ============================================

"""
ÉTAPE 1 : Ajouter dnd-5e-core au Python path
"""

import sys
sys.path.insert(0, '/')

"""
ÉTAPE 2 : Remplacer les imports dao_classes
"""

# ❌ ANCIEN (dao_classes.py)
# from dao_classes import (
#     Character, Monster, Weapon, Armor, Equipment,
#     Spell, SpellCaster, Action, SpecialAbility,
#     Race, SubRace, ClassType, Abilities,
#     HealingPotion, SpeedPotion, StrengthPotion,
#     Damage, Condition, DamageDice
# )

# ✅ NOUVEAU (dnd-5e-core)
from dnd_5e_core.entities import Character, Monster
from dnd_5e_core.equipment import (
    Weapon, Armor, Equipment, EquipmentCategory,
    HealingPotion, SpeedPotion, StrengthPotion, Cost
)
from dnd_5e_core.spells import Spell, SpellCaster
from dnd_5e_core.combat import Action, SpecialAbility, Damage, Condition
from dnd_5e_core.races import Race, SubRace, Trait, Language
from dnd_5e_core.classes import ClassType, Proficiency
from dnd_5e_core.abilities import Abilities, AbilityType
from dnd_5e_core.mechanics import DamageDice

"""
ÉTAPE 3 : Configurer le répertoire data
"""

from dnd_5e_core.data import set_data_directory

# Pointer vers les données JSON locales
set_data_directory('/data')

"""
ÉTAPE 4 : Garder populate_functions.py
"""

# populate_functions.py est TOUJOURS nécessaire car il :
# - Parse les JSON
# - Crée les objets complets
# - Gère les références croisées

from populate_functions import (
    populate,
    request_monster,
    request_spell,
    request_weapon,
    request_armor,
    request_race,
    request_class
)

"""
ÉTAPE 5 : Le reste du code reste IDENTIQUE
"""

# Toute la logique de jeu fonctionne exactement pareil !
# Les classes Monster, Character, etc. ont la même interface

# ============================================
# EXEMPLE COMPLET
# ============================================

def example_usage():
    """Exemple d'utilisation après migration"""

    # Charger un monstre (via populate_functions)
    goblin = request_monster("goblin")
    print(f"Monster: {goblin.name}")
    print(f"HP: {goblin.hit_points}")
    print(f"AC: {goblin.armor_class}")

    # Le reste du code fonctionne identique !
    # goblin.attack(player)
    # goblin.take_damage(10)
    # etc.

# ============================================
# TABLE DE CORRESPONDANCE
# ============================================

MIGRATION_MAP = {
    # dao_classes.py → dnd-5e-core

    # Entities
    "Monster": "dnd_5e_core.entities.Monster",
    "Character": "dnd_5e_core.entities.Character",
    "Sprite": "dnd_5e_core.entities.Sprite",

    # Equipment
    "Weapon": "dnd_5e_core.equipment.Weapon",
    "Armor": "dnd_5e_core.equipment.Armor",
    "Equipment": "dnd_5e_core.equipment.Equipment",
    "HealingPotion": "dnd_5e_core.equipment.HealingPotion",
    "SpeedPotion": "dnd_5e_core.equipment.SpeedPotion",
    "StrengthPotion": "dnd_5e_core.equipment.StrengthPotion",
    "Cost": "dnd_5e_core.equipment.Cost",

    # Spells
    "Spell": "dnd_5e_core.spells.Spell",
    "SpellCaster": "dnd_5e_core.spells.SpellCaster",

    # Combat
    "Action": "dnd_5e_core.combat.Action",
    "ActionType": "dnd_5e_core.combat.ActionType",
    "SpecialAbility": "dnd_5e_core.combat.SpecialAbility",
    "Damage": "dnd_5e_core.combat.Damage",
    "Condition": "dnd_5e_core.combat.Condition",

    # Races
    "Race": "dnd_5e_core.races.Race",
    "SubRace": "dnd_5e_core.races.SubRace",
    "Trait": "dnd_5e_core.races.Trait",
    "Language": "dnd_5e_core.races.Language",

    # Classes
    "ClassType": "dnd_5e_core.classes.ClassType",
    "Proficiency": "dnd_5e_core.classes.Proficiency",
    "ProfType": "dnd_5e_core.classes.ProfType",

    # Abilities
    "Abilities": "dnd_5e_core.abilities.Abilities",
    "AbilityType": "dnd_5e_core.abilities.AbilityType",

    # Mechanics
    "DamageDice": "dnd_5e_core.mechanics.DamageDice",
}

# ============================================
# SCRIPT DE MIGRATION AUTOMATIQUE
# ============================================

def migrate_file(input_file: str, output_file: str):
    """
    Migre un fichier Python de dao_classes vers dnd-5e-core

    Args:
        input_file: Fichier source (ex: main.py)
        output_file: Fichier destination (ex: main_v2.py)
    """

    with open(input_file, 'r') as f:
        content = f.read()

    # Ajouter l'import du package
    header = """#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/display/PycharmProjects/dnd-5e-core')

"""

    # Remplacer les imports dao_classes
    import_replacements = {
        "from dao_classes import": "# MIGRATED: from dao_classes import",
    }

    for old, new in import_replacements.items():
        content = content.replace(old, new)

    # Ajouter les nouveaux imports
    new_imports = """
# Imports dnd-5e-core
from dnd_5e_core.entities import Character, Monster
from dnd_5e_core.equipment import Weapon, Armor, Equipment, HealingPotion, Cost
from dnd_5e_core.spells import Spell, SpellCaster
from dnd_5e_core.combat import Action, SpecialAbility, Damage, Condition
from dnd_5e_core.races import Race, SubRace
from dnd_5e_core.classes import ClassType, Proficiency
from dnd_5e_core.abilities import Abilities
from dnd_5e_core.mechanics import DamageDice
from dnd_5e_core.data import set_data_directory

# Configure data directory
set_data_directory('/Users/display/PycharmProjects/DnD-5th-Edition-API/data')

"""

    # Combiner
    migrated_content = header + new_imports + content

    # Écrire le fichier migré
    with open(output_file, 'w') as f:
        f.write(migrated_content)

    print(f"✅ Migrated: {input_file} → {output_file}")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRATION GUIDE - dao_classes to dnd-5e-core")
    print("=" * 60)
    print()
    print("Ce guide montre comment migrer les 4 jeux vers dnd-5e-core")
    print()
    print("Fichiers à migrer:")
    print("  1. main.py → main_v2.py")
    print("  2. main_ncurses.py → main_ncurses_v2.py")
    print("  3. dungeon_pygame.py → dungeon_pygame_v2.py")
    print("  4. pyQTApp/wizardry.py → pyQTApp/wizardry_v2.py")
    print()
    print("Les fichiers originaux sont CONSERVÉS !")
    print()
    print("Pour migrer automatiquement, décommenter ci-dessous:")
    print()

    # Décommenter pour migrer automatiquement
    # migrate_file("main.py", "main_v2.py")
    # migrate_file("main_ncurses.py", "main_ncurses_v2.py")
    # migrate_file("dungeon_pygame.py", "dungeon_pygame_v2.py")
    # migrate_file("pyQTApp/wizardry.py", "pyQTApp/wizardry_v2.py")

    print("✅ Guide de migration prêt !")

