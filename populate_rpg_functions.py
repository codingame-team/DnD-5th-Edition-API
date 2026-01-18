from __future__ import annotations

import json
import os
from random import randint, choice
from typing import Optional, List
import sys

# Note: pygame is NOT imported here because this module is used by both
# console and pygame versions. Import pygame only in pygame-specific code.

# ============================================
# MIGRATION: Add dnd-5e-core to path (development mode)
# ============================================
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
from dnd_5e_core.equipment import HealingPotion, PotionRarity, SpeedPotion, StrengthPotion, Potion

# NOTE: dao_rpg_classes_tk is DEPRECATED and imports pygame which breaks console build
# Use populate_functions.request_monster() instead which uses dnd_5e_core.entities.Monster
# from dao_rpg_classes_tk import Monster

# Import GameEntity for pygame positioning
try:
    from game_entity import create_game_weapon, create_game_armor, create_game_potion
    GAME_ENTITY_AVAILABLE = True
except ImportError:
    GAME_ENTITY_AVAILABLE = False

path = os.path.dirname(__file__)

armors = ['padded-armor', 'leather-armor', 'studded-leather-armor', 'hide-armor', 'chain-shirt', 'scale-mail',
          'breastplate', 'half-plate-armor', 'ring-mail', 'chain-mail', 'splint-armor', 'plate-armor', 'shield']

weapons = ['club', 'dagger', 'greatclub', 'handaxe', 'javelin', 'light-hammer', 'mace', 'quarterstaff', 'sickle',
           'spear', 'crossbow-light', 'dart', 'shortbow', 'sling', 'battleaxe', 'flail', 'glaive', 'greataxe',
           'greatsword', 'halberd', 'lance', 'longsword', 'maul', 'morningstar', 'pike', 'rapier', 'scimitar',
           'shortsword', 'trident', 'war-pick', 'warhammer', 'whip', 'blowgun', 'crossbow-hand', 'crossbow-heavy', 'longbow']


def load_weapon_image_name(index_name: str) -> Optional[str]:
    weapons = {'club': 'Club01',
               'dagger': 'Dagger',
               'greatclub': 'Club02',
               'handaxe': 'Axe01',
               'javelin': 'SpearAwlPike',
               'light-hammer': 'Hammer01',
               'mace': 'Mace',
               'quarterstaff': 'Quarterstaff',
               'sickle': '',
               'spear': 'Spear',
               'dart': 'Dart',
               'shortbow': 'BowShort',
               'sling': 'Sling',
               'battleaxe': 'AxeBattle',
               'flail': 'Flail01',
               'glaive': 'AxeGlaive',
               'greataxe': 'AxeGreat',
               'greatsword': 'SwordBroad',
               'halberd': 'AxeHalberd',
               'lance': 'Lance',
               'longsword': 'SwordLong',
               'maul': 'Hammer05',
               'morningstar': 'ThrowingStar',
               'pike': 'Pike',
               'rapier': 'SwordRapier',
               'scimitar': 'SwordScimitar',
               'shortsword': 'SwordShort',
               'trident': 'Trident',
               'war-pick': 'Pick2',
               'warhammer': 'HammerWar',
               'whip': 'Whip',
               'blowgun': 'BlowGun',
               'crossbow-light': 'CrossBowLight',
               'crossbow-hand': 'CrossBowLight',
               'crossbow-heavy': 'CrossBowHeavy',
               'longbow': 'BowLong'}
    image_name: str = weapons.get(index_name)
    return image_name + '.PNG' if image_name else 'None.PNG'


# https://www.aidedd.org/en/rules/equipment/armor/
# https://opengameart.org/content/armor-icons-by-equipment-slot
def load_armor_image_name(index_name: str) -> Optional[str]:
    armors = {
        'padded-armor': 'ArmorLeatherSoft',
        'leather-armor': 'ArmorLeatherSoft',
        'studded-leather-armor': 'ArmorLeatherSoftStudded',
        'hide-armor': 'ArmorLeatherHard',
        'chain-shirt': 'ArmorChainMail',
        'scale-mail': 'ArmorLeatherScaleMail',
        'breastplate': 'ArmorMetalScaleMail',
        'half-plate-armor': 'ArmorPlatemailPartial',
        'ring-mail': 'ArmorLeatherHardStudded',
        'chain-mail': 'ArmorChainMailAugmented',
        'splint-mail': 'ArmorMetalBrigandine',
        'splint-armor': 'ArmorMetalLamellar',
        'plate-armor': 'ArmorPlatemailFull',
        'shield': 'ShieldWoodenRound',
    }
    image_name: str = armors.get(index_name)
    return image_name + '.PNG' if image_name else 'None.PNG'



#
# def get_available_potions() -> List[Potion]:
#     potions: List[Potion] = []
#     image_name: str = load_potion_image_name('Healing')
#     potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Healing', rarity=PotionRarity.COMMON, hit_dice='2d4', bonus=2, cost=50)
#     potions.append(potion)
#     image_name: str = load_potion_image_name('Greater healing')
#     potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Greater healing', rarity=PotionRarity.UNCOMMON, hit_dice='4d4', bonus=4, cost=150)
#     potions.append(potion)
#     image_name: str = load_potion_image_name('Superior healing')
#     potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Superior healing', rarity=PotionRarity.RARE, hit_dice='8d4', bonus=8, cost=450)
#     potions.append(potion)
#     image_name: str = load_potion_image_name('Supreme healing')
#     potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Supreme healing', rarity=PotionRarity.VERY_RARE, hit_dice='10d4', bonus=20,
#                            cost=1350)
#     potions.append(potion)
#     image_name: str = load_potion_image_name('Speed')
#     potion = SpeedPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Speed', rarity=PotionRarity.VERY_RARE, duration=60)
#     potions.append(potion)
#     return potions


# def load_potions_collections_old() -> List[HealingPotion | SpeedPotion]:
#     potions: List[HealingPotion] = []
#     for _ in range(PotionRarity.COMMON.value):
#         image_name: str = load_potion_image_name('Healing')
#         potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Healing', rarity=PotionRarity.COMMON, hit_dice='2d4', bonus=2, cost=50)
#         potions.append(potion)
#     for _ in range(PotionRarity.COMMON.value + 1, PotionRarity.UNCOMMON.value + 1):
#         image_name: str = load_potion_image_name('Greater healing')
#         potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Greater healing', rarity=PotionRarity.UNCOMMON, hit_dice='4d4', bonus=4,
#                                cost=150)
#         potions.append(potion)
#     for _ in range(PotionRarity.UNCOMMON.value + 1, PotionRarity.RARE.value + 1):
#         image_name: str = load_potion_image_name('Superior healing')
#         potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Superior healing', rarity=PotionRarity.RARE, hit_dice='8d4', bonus=8, cost=450)
#         potions.append(potion)
#     for i in range(PotionRarity.RARE.value + 1, PotionRarity.VERY_RARE.value + 1):
#         if i % 2:
#             image_name: str = load_potion_image_name('Supreme healing')
#             potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Supreme healing', rarity=PotionRarity.VERY_RARE, hit_dice='10d4', bonus=20,
#                                    cost=1350)
#         else:
#             image_name: str = load_potion_image_name('Speed')
#             potion = SpeedPotion(id=-1, image_name=image_name, x=-1, y=-1, old_x=-1, old_y=-1, name='Speed', rarity=PotionRarity.VERY_RARE, duration=60)
#         potions.append(potion)
#     return potions



def get_random_potion(potions: List[Potion]) -> Potion:
    # Generate a random number between 1 and 100
    roll = randint(1, 100)

    # Determine the rarity based on the roll
    if roll <= PotionRarity.COMMON.value:
        rarity = PotionRarity.COMMON
    elif roll <= PotionRarity.UNCOMMON.value:
        rarity = PotionRarity.UNCOMMON
    elif roll <= PotionRarity.RARE.value:
        rarity = PotionRarity.RARE
    elif roll <= PotionRarity.VERY_RARE.value:
        rarity = PotionRarity.VERY_RARE
    else:
        rarity = PotionRarity.LEGENDARY

    # Filter potions by the selected rarity
    matching_potions = [p for p in potions if p.rarity == rarity]

    # If no potions of the selected rarity, fall back to all potions
    if not matching_potions:
        matching_potions = potions

    # Return a random potion from the matching potions
    return choice(matching_potions)

def load_potion_image_name(name: str) -> Optional[str]:
    potions = {
        'Healing': 'PotionShortRed',
        'Greater healing': 'PotionRed',
        'Superior healing': 'PotionTallRed',
        'Supreme healing': 'PotionTallRed2',
        'Speed': 'PotionShortBlue',
        'Hill Giant Strength': 'PotionTallBrown',
        'Frost Giant Strength': 'PotionTallSilver',
        'Stone Giant Strength': 'PotionTallGrey',
        'Fire Giant Strength': 'PotionTallYellow',
        'Cloud Giant Strength': 'PotionTallWhite',
        'Storm Giant Strength': 'PotionTallRuby'
    }
    image_name: str = potions.get(name)
    return image_name + '.PNG' if image_name else 'None.PNG'


def load_potions_collections() -> List[Potion]:
    """
    Load all available potions (core entities without positioning).
    For pygame positioning, wrap with GameEntity.
    """
    potions: List[Potion] = []

    # Healing Potions
    potion = HealingPotion(
        name='Healing',
        rarity=PotionRarity.COMMON,
        hit_dice='2d4',
        bonus=2,
        min_cost=10,
        max_cost=50
    )
    potions.append(potion)

    potion = HealingPotion(
        name='Greater healing',
        rarity=PotionRarity.UNCOMMON,
        hit_dice='4d4',
        bonus=4,
        min_cost=101,
        max_cost=500
    )
    potions.append(potion)

    potion = HealingPotion(
        name='Superior healing',
        rarity=PotionRarity.RARE,
        hit_dice='8d4',
        bonus=8,
        min_cost=501,
        max_cost=5000,
        min_level=5
    )
    potions.append(potion)

    potion = HealingPotion(
        name='Supreme healing',
        rarity=PotionRarity.VERY_RARE,
        hit_dice='10d4',
        bonus=20,
        min_cost=5001,
        max_cost=50000,
        min_level=11
    )
    potions.append(potion)

    # Speed Potion
    potion = SpeedPotion(
        name='Speed',
        rarity=PotionRarity.VERY_RARE,
        duration=60,
        min_cost=5001,
        max_cost=50000,
        min_level=11
    )
    potions.append(potion)

    # Strength Potions (Giant Strength series)
    potion = StrengthPotion(
        name='Hill Giant Strength',
        rarity=PotionRarity.UNCOMMON,
        value=21,
        duration=3600,
        min_cost=101,
        max_cost=500
    )
    potions.append(potion)

    potion = StrengthPotion(
        name='Frost Giant Strength',
        rarity=PotionRarity.RARE,
        value=23,
        duration=3600,
        min_cost=501,
        max_cost=5000,
        min_level=5
    )
    potions.append(potion)

    potion = StrengthPotion(
        name='Stone Giant Strength',
        rarity=PotionRarity.RARE,
        value=23,
        duration=3600,
        min_cost=501,
        max_cost=5000,
        min_level=5
    )
    potions.append(potion)

    potion = StrengthPotion(
        name='Fire Giant Strength',
        rarity=PotionRarity.RARE,
        value=25,
        duration=3600,
        min_cost=501,
        max_cost=5000,
        min_level=5
    )
    potions.append(potion)

    potion = StrengthPotion(
        name='Cloud Giant Strength',
        rarity=PotionRarity.VERY_RARE,
        value=27,
        duration=3600,
        min_cost=5001,
        max_cost=50000,
        min_level=11
    )
    potions.append(potion)

    potion = StrengthPotion(
        name='Storm Giant Strength',
        rarity=PotionRarity.LEGENDARY,
        value=29,
        duration=3600,
        min_cost=50001,
        max_cost=500000,
        min_level=11
    )
    potions.append(potion)

    return potions


# ============================================
# DEPRECATED: This function is obsolete and has been replaced
# Use populate_functions.request_monster() instead which uses dnd_5e_core.entities.Monster
# This function used dao_rpg_classes_tk.Monster which imports pygame, breaking console builds
# ============================================
# def request_monster(index_name: str) -> Optional[Monster]:
#     ... (commented out - see git history if needed)


# ============================================
# GameEntity Helper Functions for pygame
# ============================================

def create_game_weapon_with_image(weapon, image_name=None):
    """
    Create a GameEntity wrapper for a weapon with image.
    Falls back to core weapon if GameEntity not available (console mode).

    Args:
        weapon: Core Weapon entity
        image_name: Optional image name (loaded from load_weapon_image_name if None)

    Returns:
        GameEntity[Weapon] if available, otherwise core Weapon
    """
    if not GAME_ENTITY_AVAILABLE:
        return weapon

    if image_name is None:
        image_name = load_weapon_image_name(weapon.index)

    return create_game_weapon(weapon, x=-1, y=-1, image_name=image_name)


def create_game_armor_with_image(armor, image_name=None):
    """
    Create a GameEntity wrapper for armor with image.
    Falls back to core armor if GameEntity not available (console mode).

    Args:
        armor: Core Armor entity
        image_name: Optional image name (loaded from load_armor_image_name if None)

    Returns:
        GameEntity[Armor] if available, otherwise core Armor
    """
    if not GAME_ENTITY_AVAILABLE:
        return armor

    if image_name is None:
        image_name = load_armor_image_name(armor.index)

    return create_game_armor(armor, x=-1, y=-1, image_name=image_name)

def create_game_potion_with_image(potion, image_name=None):
    """
    Create a GameEntity wrapper for a potion with image.
    Falls back to core potion if GameEntity not available (console mode).

    Args:
        potion: Core Potion entity
        image_name: Optional image name (loaded from load_potion_image_name if None)

    Returns:
        GameEntity[Potion] if available, otherwise core Potion
    """
    if not GAME_ENTITY_AVAILABLE:
        return potion

    if image_name is None:
        image_name = load_potion_image_name(potion.name)

    return create_game_potion(potion, x=-1, y=-1, image_name=image_name)
