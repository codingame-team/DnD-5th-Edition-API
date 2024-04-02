import json
import os
from typing import Optional, List

import pygame
from pygame import Surface

from dao_classes import Potion, PotionRarity
from dao_rpg_classes import Monster

path = os.path.dirname(__file__)

armors = ['padded-armor', 'leather-armor', 'studded-leather-armor', 'hide-armor', 'chain-shirt', 'scale-mail',
           'breastplate', 'half-plate-armor', 'ring-mail', 'chain-mail', 'splint-armor', 'plate-armor', 'shield']

weapons = ['club', 'dagger', 'greatclub', 'handaxe', 'javelin', 'light-hammer', 'mace', 'quarterstaff', 'sickle',
           'spear', 'crossbow-light', 'dart', 'shortbow', 'sling', 'battleaxe', 'flail', 'glaive', 'greataxe',
           'greatsword', 'halberd', 'lance', 'longsword', 'maul', 'morningstar', 'pike', 'rapier', 'scimitar',
           'shortsword', 'trident', 'war-pick', 'warhammer', 'whip', 'blowgun', 'crossbow-hand', 'crossbow-heavy', 'longbow']

def load_weapon_image(index_name: str) -> Surface:
    weapons = {'club': 'Club01', 'dagger': 'Dagger', 'greatclub': 'Club02', 'handaxe': 'Axe01', 'javelin': '', 'light-hammer': 'Hammer01', 'mace': 'Mace', 'quarterstaff': 'Quarterstaff', 'sickle': '',
               'spear': 'Spear', 'crossbow-light': 'CrossbowLight', 'dart': 'Dart', 'shortbow': 'BowShort', 'sling': 'Sling', 'battleaxe': 'AxeBattle', 'flail': 'Flail01', 'glaive': 'AxeGlaive', 'greataxe': 'AxeGreat',
               'greatsword': 'SwordBroad', 'halberd': '', 'lance': '', 'longsword': 'SwordLong', 'maul': '', 'morningstar': 'ThrowingStar', 'pike': 'Pike', 'rapier': 'SwordRapier', 'scimitar': 'SwordScimitar',
               'shortsword': 'SwordShort', 'trident': 'Trident', 'war-pick': 'Pick2', 'warhammer': 'HammerWar', 'whip': 'Whip', 'blowgun': '', 'crossbow-hand': 'CrossBowLight', 'crossbow-heavy': 'CrossBowHeavy', 'longbow': 'BowLong'}
    image_name: str = weapons.get(index_name)
    image_filename: str = f"{path}/sprites/Items/{image_name}.PNG" if image_name else f"{path}/sprites/None.PNG"
    return pygame.image.load(image_filename)

# https://www.aidedd.org/en/rules/equipment/armor/
# https://opengameart.org/content/armor-icons-by-equipment-slot
def load_armor_image(index_name: str) -> Surface:
    match index_name:
        case 'padded-armor':
            image_name = 'ArmorLeatherSoft' # Not found
        case 'leather-armor':
            image_name = 'ArmorLeatherSoft'
        case 'studded-leather-armor':
            image_name = 'ArmorLeatherSoftStudded'
        case 'hide-armor':
            image_name = None
        case 'chain-shirt':
            image_name = 'ArmorChainMail' # not exactly
        case 'scale-mail':
            image_name = 'ArmorLeatherScaleMail'
        case 'breastplate':
            image_name = 'ArmorMetalScaleMail'
        case 'half-plate-armor':
            image_name = 'ArmorPlatemailPartial'
        case 'ring-mail':
            image_name = 'ArmorLeatherHardStudded'
        case 'chain-mail':
            image_name = 'ArmorChainMailAugmented'
        case 'splint-mail':
            image_name = 'ArmorMetalBrigandine'
        case 'plate-armor':
            image_name = 'ArmorPlatemailFull'
        case 'shield':
            image_name = 'ShieldWoodenRound'
        case _:
            image_name = None
    image_filename: str = f"{path}/sprites/Items/{image_name}.PNG" if image_name else f"{path}/sprites/None.PNG"
    return pygame.image.load(image_filename)

def load_potion_image(name: str) -> Surface:
    match name:
        case 'Healing':
            image_name = 'PotionShortRed'
        case 'Greater healing':
            image_name = 'PotionRed'
        case 'Superior healing':
            image_name = 'PotionTallRed'
        case 'Supreme healing':
            image_name = 'PotionTallRed2'
        case _:
            image_name = None
    image_filename: str = f"{path}/sprites/Items/{image_name}.PNG" if image_name else f"{path}/sprites/None.PNG"
    return pygame.image.load(image_filename)

def load_potions_collections() -> List[Potion]:
    potions: List[Potion] = []
    for _ in range(PotionRarity.COMMON.value):
        potion = Potion(name='Healing', rarity=PotionRarity.COMMON, hit_dice='2d4', bonus=2)
        potions.append(potion)
    for _ in range(PotionRarity.COMMON.value + 1, PotionRarity.UNCOMMON.value + 1):
        potion = Potion(name='Greater healing', rarity=PotionRarity.UNCOMMON, hit_dice='4d4', bonus=4)
        potions.append(potion)
    for _ in range(PotionRarity.UNCOMMON.value + 1, PotionRarity.RARE.value + 1):
        potion = Potion(name='Superior healing', rarity=PotionRarity.RARE, hit_dice='8d4', bonus=8)
        potions.append(potion)
    for _ in range(PotionRarity.RARE.value + 1, PotionRarity.VERY_RARE.value + 1):
        potion = Potion(name='Supreme healing', rarity=PotionRarity.VERY_RARE, hit_dice='10d4', bonus=20)
        potions.append(potion)
    return potions

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
