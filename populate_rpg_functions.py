import json
import os
from typing import Optional, List

import pygame
from pygame import Surface

from dao_classes import HealingPotion, PotionRarity
from dao_rpg_classes import Monster

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
               'crossbow-light': 'CrossbowLight',
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


def load_potion_image_name(name: str) -> Optional[str]:
    potions = {
        'Healing': 'PotionShortRed',
        'Greater healing': 'PotionRed',
        'Superior healing': 'PotionTallRed',
        'Supreme healing': 'PotionTallRed2',

    }
    image_name: str = potions.get(name)
    return image_name + '.PNG' if image_name else 'None.PNG'


def load_potions_collections() -> List[HealingPotion]:
    healing_potions: List[HealingPotion] = []
    for _ in range(PotionRarity.COMMON.value):
        image_name: str = load_potion_image_name('Healing')
        potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, name='Healing', rarity=PotionRarity.COMMON, hit_dice='2d4', bonus=2)
        healing_potions.append(potion)
    for _ in range(PotionRarity.COMMON.value + 1, PotionRarity.UNCOMMON.value + 1):
        image_name: str = load_potion_image_name('Greater healing')
        potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, name='Greater healing', rarity=PotionRarity.UNCOMMON, hit_dice='4d4', bonus=4)
        healing_potions.append(potion)
    for _ in range(PotionRarity.UNCOMMON.value + 1, PotionRarity.RARE.value + 1):
        image_name: str = load_potion_image_name('Superior healing')
        potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, name='Superior healing', rarity=PotionRarity.RARE, hit_dice='8d4', bonus=8)
        healing_potions.append(potion)
    for _ in range(PotionRarity.RARE.value + 1, PotionRarity.VERY_RARE.value + 1):
        image_name: str = load_potion_image_name('Supreme healing')
        potion = HealingPotion(id=-1, image_name=image_name, x=-1, y=-1, name='Supreme healing', rarity=PotionRarity.VERY_RARE, hit_dice='10d4', bonus=20)
        healing_potions.append(potion)
    return healing_potions


def request_monster(index_name: str) -> Optional[Monster]:
    try:
        with open(f"{path}/data/monsters/{index_name}.json", "r") as f:
            data = json.loads(f.read())
        attack_bonus: int = 0
        match index_name:
            case 'ankheg':
                damage_dice = '2d6+3'
                speed = data['speed']['walk']
            case 'baboon':
                damage_dice = '1d4-1'
                speed = data['speed']['walk']
            case 'bat':
                damage_dice = '1'
                speed = data['speed']['fly']
            case 'blob':
                return None
            case 'crab':
                damage_dice = '1'
                speed = data['speed']['walk']
            case 'ghost':
                damage_dice = '4d6+3'
                speed = data['speed']['fly']
                attack_bonus = 5
            case 'goblin':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
                attack_bonus = 4
            case 'harpy':
                damage_dice = '2d4+1'
                speed = data['speed']['fly']
                attack_bonus = 3
            case 'lizard':
                damage_dice = '1'
                speed = data['speed']['walk']
            case 'mimic':
                damage_dice = '1d8+3'
                speed = data['speed']['walk']
                attack_bonus = 3
            case 'owl':
                damage_dice = '1d6+2'
                speed = data['speed']['fly']
                attack_bonus = 3
            case 'eagle':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
            case 'goblin':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
            case 'rat':
                damage_dice = '1'
                speed = data['speed']['walk']
            case 'rat_scull':
                return None
            case 'skeleton':
                damage_dice = '1d6+2'
                speed = data['speed']['walk']
                attack_bonus = 4
            case 'snake':
                return None
            case 'spider':
                damage_dice = '1'
                speed = data['speed']['walk']
                attack_bonus = 4
            case 'tentacle':
                return None
            case 'wasp':
                return None
            case 'wolf':
                damage_dice = '2d4+2'
                speed = data['speed']['walk']
                attack_bonus = 4
        return Monster(x=-1,
                       y=-1,
                       img=pygame.image.load(f"{path}/sprites/rpgcharacterspack/monster_{index_name}.png"),
                       name=index_name,
                       hit_dice=data['hit_dice'],
                       damage_dice=damage_dice,
                       attack_bonus=attack_bonus,
                       ac=data['armor_class'],
                       speed=int(speed.split()[0]),
                       xp=data['xp'],
                       cr=data['challenge_rating'])
    except FileNotFoundError:
        return None
