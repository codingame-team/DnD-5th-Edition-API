from __future__ import annotations

import csv
import json
import math
import os
from copy import deepcopy
from logging import debug
from random import randint
from typing import List, Tuple, Optional
import re

from dao_classes import CategoryType, DamageDice, Monster, Armor, RangeType, SpecialAbility, SpellCaster, Weapon, Race, \
    SubRace, Proficiency, ClassType, Language, Equipment, WeaponProperty, WeaponRange, AbilityType, WeaponThrowRange, \
    Trait, EquipmentCategory, \
    Abilities, Action, Damage, ActionType, DamageType, Spell, ProfType, Condition, Inventory, AreaOfEffect
from populate_rpg_functions import load_armor_image_name, load_weapon_image_name
from tools.common import parse_challenge_rating

""" CSV loads """

path = os.path.dirname(__file__)


def populate_names(race: Race) -> dict():
    """
    :return: list of names (except humans and half-elf)
    """
    names_list = dict()
    with open(f"{path}/data/names/{race.index}.csv", newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        for gender, name in csv_data:
            if gender not in names_list:
                names_list[gender] = []
            else:
                names_list[gender].append(name)
    return names_list


def populate_human_names() -> dict():
    """
    :return: list of names (humans and half-elf)
    """
    names_list = dict()
    with open(f"{path}/data/names/human.csv", newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        for ethnic, sex, name in csv_data:
            if ethnic not in names_list:
                names_list[ethnic] = dict()
            else:
                if sex not in names_list[ethnic]:
                    names_list[ethnic][sex] = []
                else:
                    names_list[ethnic][sex].append(name)
    return names_list


def read_csvfile_old(filename: str):
    """
    :param filename: csv file in Tables directory
    :return: list of dictionaries
    """
    result = []
    with open(f'{path}/Tables/{filename}', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        headers = next(reader, None)
        csv_data = csv.DictReader(csv_file, delimiter=';')
        for row in csv_data:
            result.append({header: row(header) for header in headers})
    return result


def read_csvfile(filename: str):
    """
    :param filename: csv file in Tables directory
    :return: list of dictionaries
    """
    with open(f'{path}/Tables/{filename}', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader, None)
        return list(reader)


def height_weight_table() -> List:
    """
    :return: List of race height/weight modifier's parameters
    """
    """Race;Base Height;Height Modifier;Base Weight;Weight Modifier"""
    headers = ['Race', 'Base Height', 'Height Modifier',
               'Base Weight', 'Weight Modifier']
    hw_conv_table = []
    with open(f"{path}/Tables/Height and Weight-Height and Weight.csv", newline='') as csv_file:
        # csv_data = csv.reader(csv_file, delimiter=';')
        # next(csv_data, None)
        csv_data = csv.DictReader(csv_file, delimiter=';')
        for row in csv_data:
            hw_conv_table.append({header: row(header) for header in headers})
    return hw_conv_table


""" JSON loads """


def populate(collection_name: str, key_name: str, with_url=False, collection_path: str = None) -> List[str]:
    """
    :return: list of collection names
    """
    if not collection_path:
        collection_path = 'collections'
    try:
        with open(f"{path}/{collection_path}/{collection_name}.json", "r") as f:
            data = json.loads(f.read())
            # collection_count = int(data['count'])
            collection_json_list = data[key_name]
    except:
        print(f'f: {f.name} - key_name: {key_name} - data: {data}')
        exit(0)
    if with_url:
        data_list = [(json_data['index'], json_data['url'])
                     for json_data in collection_json_list]
    else:
        data_list = [json_data['index'] for json_data in collection_json_list]
    return data_list


def request_damage_type(index_name: str) -> DamageType:
    """
    Send a request to local database for a damage type's characteristic
    :param index_name: name of the damage type
    :return: DamageType object
    """
    with open(f"{path}/data/damage-types/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return DamageType(index=data['index'], name=data['name'], desc=data['desc'])


def request_condition(index_name: str) -> Condition:
    """
    Send a request to local database for a condition's characteristic
    :param index_name: name of the condition
    :return: Condition object
    """
    with open(f"{path}/data/conditions/{index_name}.json", "r") as f:
        data = json.loads(f.read())

    return Condition(index=data['index'], name=data['name'], desc=data['desc'])


def request_other_actions(index_name: str) -> List[Action]:
    actions: List[Action] = []
    with open(f"{path}/data/monsters/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        damages: List[Damage] = []
        if index_name == 'rug-of-smothering':
            effects: List[Condition] = []
            for index in ('restrained', 'blinded'):
                effect: Condition = request_condition(index)
                if effect.index == 'restrained':
                    effect.dc_type = AbilityType.STR
                    effect.dc_value = 13
                effects.append(effect)
            damage_type: DamageType = request_damage_type(index_name='bludgeoning')
            damages.append(Damage(type=damage_type, dd=DamageDice('2d6', 3)))
            action_dict: dict = data['actions'][0]
            action = Action(name=action_dict['name'], desc=action_dict['desc'], type=ActionType.MELEE,
                            attack_bonus=action_dict.get('attack_bonus'), damages=damages,
                            effects=effects)
            actions.append(action)
            return actions


def request_monster(index_name: str) -> Monster:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    # print(index_name)
    with open(f"{path}/data/monsters/{index_name}.json", "r") as f:
        data = json.loads(f.read())

    can_cast: bool = False
    can_attack: bool = False
    slots: List[int] = []
    spells: List[Spell] = []
    caster_level: int = None
    dc: int = None
    ability_modifier: int = 0
    spell_caster: SpellCaster = None
    special_abilities: List[SpecialAbility] = []
    if "special_abilities" in data:
        for special_ability in data['special_abilities']:
            action_name: str = special_ability['name']
            if special_ability['name'] == 'Spellcasting':
                ability: dict = special_ability['spellcasting']
                caster_level = ability['level']
                dc_type = ability['ability']['index']
                dc_value = ability['dc']
                ability_modifier = ability['modifier']
                slots = [s for s in ability['slots'].values()]
                for spell_dict in ability['spells']:
                    spell_index_name: str = spell_dict['url'].split('/')[3]
                    spell = request_spell(spell_index_name)
                    if spell is None:
                        continue
                    spells.append(spell)
            elif 'damage' in special_ability:
                damages: List[Damage] = []
                for damage in special_ability['damage']:
                    if "damage_type" in damage:
                        can_attack = True
                        damage_type: DamageType = request_damage_type(index_name=damage['damage_type']['index'])
                        if '+' in damage['damage_dice']:
                            damage_dice, bonus = damage['damage_dice'].split('+')
                            bonus = int(bonus)
                        elif '-' in damage['damage_dice']:
                            damage_dice, bonus = damage['damage_dice'].split('-')
                            bonus = -int(bonus)
                        else:
                            damage_dice, bonus = damage['damage_dice'], 0
                        damages.append(Damage(type=damage_type, dd=DamageDice(damage_dice, bonus)))
                # TODO: parse range in
                desc: str = special_ability['desc']
                area_of_effect: AreaOfEffect = AreaOfEffect(type='sphere', size=15)
                if 'dc' in special_ability:
                    dc_type = special_ability['dc']['dc_type']['index']
                    dc_value = special_ability['dc']['dc_value']
                    dc_success = special_ability['dc']['success_type']
                else:
                    dc_type = dc_success = dc_value = None
                if damages:
                    special_abilities.append(SpecialAbility(name=action_name,
                                                            desc=special_ability['desc'],
                                                            damages=damages,
                                                            dc_type=dc_type,
                                                            dc_value=dc_value,
                                                            dc_success=dc_success,
                                                            recharge_on_roll=None,
                                                            area_of_effect=area_of_effect))
        if spells:
            can_attack = True
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=slots,
                                                    learned_spells=spells,
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + ability_modifier,
                                                    ability_modifier=ability_modifier)

    actions: List[Action] = []

    if "actions" in data:
        # Melee attacks
        for action in data['actions']:
            # print(f"{data['name']} - action = {action}")
            if action['name'] != 'Multiattack' and "damage" in action:
                normal_range = long_range = 5
                is_melee_attack = re.search("Melee.*Attack", action['desc'])
                is_ranged_attack = re.search("Ranged.*Attack", action['desc'])
                if is_ranged_attack:
                    # desc = "Ranged Weapon Attack: +7 to hit, range 150/600 ft., one target. Hit: 7 (1d8 + 3) piercing damage plus 13 (3d8) poison damage, and the target must succeed on a DC 14 Constitution saving throw or be poisoned. The poison lasts until it is removed by the lesser restoration spell or similar magic."
                    range_pattern = r"range\s+(\d+)/(\d+)\s*ft\."
                    match = re.search(range_pattern, action['desc'])
                    if match:
                        normal_range = int(match.group(1))
                        long_range = int(match.group(2))
                damages: List[Damage] = []
                for damage in action['damage']:
                    # print(f'damage = {damage}')
                    if "damage_type" in damage:
                        damage_type: DamageType = request_damage_type(index_name=damage['damage_type']['index'])
                        damages.append(Damage(type=damage_type, dd=DamageDice(damage['damage_dice'])))
                if damages:
                    can_attack = True
                    action_type = ActionType.MIXED if is_melee_attack and is_ranged_attack else ActionType.MELEE if is_melee_attack else ActionType.RANGED
                    actions.append(Action(name=action['name'], desc=action['desc'], type=action_type, normal_range=normal_range, long_range=long_range,
                                          attack_bonus=action.get('attack_bonus'),
                                          multi_attack=None, damages=damages))
        # Multiattacks
        for action in data['actions']:
            if action['name'] == 'Multiattack':
                can_attack = True
                multi_attack: List[Action] = []
                # Todo: verify if there could be more than one choice...
                choose_count: int = action['options']['choose']
                for action_dict in action['options']['from'][0]:
                    multi_action: List[Action] = [a for a in actions if a.name == action_dict['name']]
                    try:
                        count: int = int(action_dict['count'])
                    except:
                        print(f"invalid count option for {index_name} : {action_dict['name']}")
                        continue
                    if not isinstance(count, int):
                        continue
                    # if multi_action[0].type == ActionType.MELEE:
                    if multi_action and multi_action[0].type in (ActionType.MELEE, ActionType.RANGED):
                        for _ in range(count):
                            multi_attack.append(multi_action[0])
                # action_type: str = ActionType.MELEE if 'Melee' in action['desc'] else ActionType.RANGED if 'Ranged' in action['desc']
                actions.append(
                    Action(name=action['name'], desc=action['desc'], type=ActionType.MELEE, attack_bonus=None,
                           multi_attack=multi_attack, damages=None))
        # Special abilities
        for action in data['actions']:
            if 'dc' in action:
                damages: List[Damage] = []
                for damage in action['damage']:
                    if "damage_type" in damage:
                        can_attack = True
                        damage_type: DamageType = request_damage_type(index_name=damage['damage_type']['index'])
                        if '+' in damage['damage_dice']:
                            damage_dice, bonus = damage['damage_dice'].split('+')
                            bonus = int(bonus)
                        elif '-' in damage['damage_dice']:
                            damage_dice, bonus = damage['damage_dice'].split('-')
                            bonus = -int(bonus)
                        else:
                            damage_dice, bonus = damage['damage_dice'], 0
                        damages.append(Damage(type=damage_type, dd=DamageDice(damage_dice, bonus)))
                # print(index_name)
                recharge_on_roll: int = None
                action_name: str = action['name']
                if "usage" in action:
                    if action['usage'].get('type') == 'recharge on roll':
                        recharge_on_roll = action['usage']['min_value']
                elif 'Recharge' in action_name:
                    pattern = r"Recharge (\d+)"
                    match = re.search(pattern, action_name)
                    if match:
                        action_name = action_name.split('(')[0].strip()
                        recharge_on_roll = int(match.group(1))

                area_of_effect: AreaOfEffect = AreaOfEffect(type='sphere', size=5)
                if damages:
                    special_abilities.append(SpecialAbility(name=action_name,
                                                            desc=action['desc'],
                                                            damages=damages,
                                                            dc_type=action['dc']['dc_type']['index'],
                                                            dc_value=action['dc']['dc_value'],
                                                            dc_success=action['dc']['success_type'],
                                                            recharge_on_roll=recharge_on_roll,
                                                            area_of_effect=area_of_effect))

    # TODO Check if there are other special abilities that we did not cover...
    if not actions:
        actions = request_other_actions(index_name)

    proficiencies: List[Proficiency] = []
    if 'proficiencies' in data:
        for prof in data['proficiencies']:
            proficiency: Proficiency = request_proficiency(
                index_name=prof['proficiency']['index'])
            proficiency.value = prof.get('value')
            proficiencies.append(proficiency)

    return Monster(id=-1,
                   image_name=f'monster_{index_name}.png',
                   x=-1, y=-1, old_x=-1, old_y=-1,
                   index=index_name,
                   name=data['name'],
                   abilities=Abilities(str=data['strength'], dex=data['dexterity'], con=data['constitution'],
                                       int=data['intelligence'], wis=data['wisdom'], cha=data['charisma']),
                   proficiencies=proficiencies,
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   challenge_rating=data['challenge_rating'],
                   actions=actions,
                   sc=spell_caster,
                   sa=special_abilities)  # if can_attack else None

def get_special_monster_actions(name: str) -> tuple[List[Action], List[SpecialAbility], SpellCaster]:
    actions: List[Action] = []
    special_abilities: List[SpecialAbility] = []
    spell_caster: SpellCaster = None
    print(name)
    if name == "Orc Eye of Gruumsh":
        damage_type: DamageType = request_damage_type(index_name='piercing')
        # Ranged attack
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3)),
                                 Damage(type=damage_type, dd=DamageDice(dice='1d8'))]
        action = Action(name='Spear', desc='', type=ActionType.RANGED, attack_bonus=5, damages=damages, normal_range=20, long_range=60)
        actions.append(action)
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=3))]
        action = Action(name='Spear', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
    elif name == "Ogre Bolt Launcher":
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d4', bonus=4))]
        action = Action(name='Fist', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
        # Ranged attack
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='3d10', bonus=1))]
        action = Action(name='Bolt Launcher', desc='', type=ActionType.RANGED, attack_bonus=3, damages=damages, normal_range=120, long_range=480)
        actions.append(action)
    elif name == "Ogre Battering Ram":
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d10', bonus=4))]
        action = Action(name='Bash', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
    elif name == "Hobgoblin Captain":
        # Multi Attack
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=2))]
        multi_attack_action = Action(name='Greatsword', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2, damages=None)
        actions.append(action)
        # Single Attacks
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Javelin', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        actions.append(action)
        # Ranged attack
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Javelin', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
    elif name == 'Piercer':
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice=f'{randint(1, 6)}d6', bonus=0))]
        action = Action(name='Drop', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        actions.append(action)
    elif name == "Illusionist":
        # Multiple attack
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d10', bonus=3))]
        multi_attack_action = Action(name='Arcane Burst', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=120, long_range=math.inf)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Ranged attack
        # TODO: modify request_spell function for non SRD monsters
        # range = '120 ft'
        # action = Action(name='Multiattack', desc='', type=ActionType.RANGED,
        #        attack_bonus=None,
        #        multi_attack=[multi_attack_action] * 2, damages=None)
        # actions.append(action)
        # Spell casting
        # The illusionist casts one of the following spells, using Intelligence as the spellcasting ability (spell save {@dc 13})
        # caster_level = special_ability['spellcasting']['level']
        # dc_type = 'int'
        # dc_value = 13
        # ability_modifier = special_ability['spellcasting']['modifier']
        # slots = [s for s in special_ability['spellcasting']['slots'].values()]
        # spells: List[Spell] = []
        # for spell_dict in special_ability['spellcasting']['spells']:
        #     spell_index_name: str = spell_dict['url'].split('/')[3]
        #     spell = request_spell(spell_index_name)
        #     if spell is None:
        #         continue
        #     spells.append(spell)
        #     spell_caster: SpellCaster = SpellCaster(level=caster_level,
        #                                             spell_slots=slots,
        #                                             learned_spells=spells,
        #                                             dc_type=dc_type,
        #                                             dc_value=dc_value + ability_modifier,
        #                                             ability_modifier=ability_modifier)
    elif name == "Goblin Boss":
        # Multi Attack
        # The goblin makes two attacks with its scimitar. The second attack has disadvantage.
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        multi_attack_action_1 = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        multi_attack_action_2 = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages, disadvantage=True)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        # Single Attacks
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Javelin', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        actions.append(action)
        # Ranged attack
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Javelin', desc='', type=ActionType.MIXED, attack_bonus=2, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
    elif name == "Xvart":
        # Single Attacks
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Shortsword', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        actions.append(action)
        # Ranged attack
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        action = Action(name='Sling', desc='', type=ActionType.RANGED, attack_bonus=4, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
    elif name == "Kobold Inventor":
        # Melee/Ranged Attacks
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        action = Action(name='Dagger', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=20, long_range=60)
        actions.append(action)
        # Ranged attack
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        action = Action(name='Sling', desc='', type=ActionType.RANGED,
               attack_bonus=4, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
        # TODO "Weapon Invention"
        # "The kobold uses one of the following options (choose one or roll a {@dice d8}); the kobold can use each one no more than once per day:"
    elif name == "Half-ogre":
        # Single Attacks
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=3))]
        action = Action(name='Battleaxe', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
        # Ranged attack
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        action = Action(name='Javelin', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
    elif name == "Water Weird":
        # TODO: implement condition restrain
        # Single Attacks
        # "If the target is Medium or smaller, it is {@condition grappled} (escape {@dc 13}) and pulled 5 feet toward the water weird. Until this grapple ends, the target is {@condition restrained}, the water weird tries to drown it, and the water weird can't constrict another target."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='3d6', bonus=3))]
        action = Action(name='Constrict', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=10, long_range=math.inf)
        actions.append(action)
    elif name == "Apprentice Wizard":
        # TODO: implement spell attacks
        # Multiple attack
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d10', bonus=3))]
        action = Action(name='Arcane Burst', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=120, long_range=math.inf)
        actions.append(action)
    elif name == "Orc War Chief":
        # Multiple attack
        # "The orc makes two attacks with its greataxe or its spear."
        # Great Axe * 2
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d12', bonus=4)),
                                 Damage(type=damage_type, dd=DamageDice(dice='1d8'))]
        multi_attack_action = Action(name='Greataxe', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Spear * 2
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=4))]
        multi_attack_action = Action(name='Spear', desc='', type=ActionType.MIXED, attack_bonus=6, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Deathlock":
        # TODO implement spell casting
        # Multiple attack
        # "The deathlock makes two Deathly Claw or Grave Bolt attacks."
        # Deathly Claw * 2
        damage_type: DamageType = request_damage_type(index_name='necrotic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=2))]
        multi_attack_action = Action(name='Deathly Claw', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Grave Bolt * 2
        damage_type: DamageType = request_damage_type(index_name='necrotic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d10', bonus=3))]
        multi_attack_action = Action(name='Grave Bolt', desc='', type=ActionType.RANGED, attack_bonus=5, damages=damages, normal_range=120, long_range=math.inf)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Allip":
        # Single attacks
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d6', bonus=3))]
        action = Action(name='Maddening Touch', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
        # Special attacks
        # N.B.: "Whispers of Compulsion" effective only with a party
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=3))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='sphere', size=30)
        # TODO: implement condition stunned
        sa: SpecialAbility = SpecialAbility(name='Howling Babble',
                                                desc='',
                                                damages=damages,
                                                dc_type='wis',
                                                dc_value=14,
                                                dc_success='half',
                                                recharge_on_roll=1,
                                                area_of_effect=area_of_effect)
        special_abilities.append(sa)
    elif name == 'Orog':
        # Melee/Ranged attacks
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=4))]
        action = Action(name='Javelin', desc='', type=ActionType.MIXED, attack_bonus=6, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
        # Multiple attack
        # "The orog makes two greataxe attacks."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d12', bonus=4))]
        multi_attack_action = Action(name='Greataxe', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == 'Warlock of the Great Old One':
        # Multiple attack
        # "The warlock makes two Dagger attacks."
        # Melee/Ranged Attacks
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        multi_attack_action = Action(name='Dagger', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Special attacks
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=0))]
        # TODO: implement condition frightened and area of effect
        # "The warlock opens a momentary extraplanar rift within 60 feet of it.
        # The rift is a scream-filled, 20-foot cube. Each creature in that area must make a {@dc 15} Wisdom saving throw.
        # On a failed save, a creature takes 9 ({@damage 2d8}) psychic damage and is {@condition frightened} of the warlock until the start of the warlock's next turn.
        # On a successful save, a creature takes half as much damage and isn't {@condition frightened}."
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cube', size=20)
        sa: SpecialAbility = SpecialAbility(name='Howling Void',
                                                desc='',
                                                damages=damages,
                                                dc_type='wis',
                                                dc_value=15,
                                                dc_success='half',
                                                recharge_on_roll=1,
                                                area_of_effect=area_of_effect)
        special_abilities.append(sa)
    elif name == "Star Spawn Grue":
        # Single Attacks
        # TODO ???
        # The target must succeed on a {@dc 10} Wisdom saving throw or attack rolls against it have advantage until the start of the grue's next turn."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d4', bonus=1))]
        action = Action(name='Confounding Bite', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        actions.append(action)
    elif name == "Star Spawn Mangler":
        # Multiple attack
        # "The mangler makes two Claw attacks."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=4))]
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        multi_attack_action = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Special attacks
        damage_type: DamageType = request_damage_type(index_name='psychic')
        # TODO implements multiple attacks in sa (and not multiple damages)
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8'))] * 6
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cube', size=5)
        sa: SpecialAbility = SpecialAbility(name='Flurry of Claws',
                                                desc='',
                                                damages=damages,
                                                dc_type='wis',
                                                dc_value=15,
                                                dc_success='half',
                                                recharge_on_roll=5,
                                                area_of_effect=area_of_effect)
        special_abilities.append(sa)
    elif name == "Adult Oblex":
        # Multiple attack
        # "The oblex makes two pseudopod attacks, and it uses Eat Memories."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=4))]
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        multi_attack_action = Action(name='Pseudopod', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Special attacks
        damage_type: DamageType = request_damage_type(index_name='psychic')
        # TODO implements memory drained effect
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d8', bonus=0))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cube', size=5)
        sa: SpecialAbility = SpecialAbility(name='Eat Memories',
                                                desc='',
                                                damages=damages,
                                                dc_type='wis',
                                                dc_value=15,
                                                dc_success='half',
                                                recharge_on_roll=1,
                                                area_of_effect=area_of_effect)
        special_abilities.append(sa)
    elif name == 'Vampiric Mist':
        # Special attacks
        damage_type: DamageType = request_damage_type(index_name='necrotic')
        # TODO implements life drain effect
        # "The mist touches one creature in its space.
        # The target must succeed on a {@dc 13} Constitution saving throw (Undead and Constructs automatically succeed),
        # or it takes 10 ({@damage 2d6 + 3}) necrotic damage, the mist regains 10 hit points,
        # and the target's hit point maximum is reduced by an amount equal to the necrotic damage taken.
        # This reduction lasts until the target finishes a long rest.
        # The target dies if its hit point maximum is reduced to 0."
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cube', size=5)
        sa: SpecialAbility = SpecialAbility(name='Life Drain',
                                                desc='',
                                                damages=damages,
                                                dc_type='wis',
                                                dc_value=13,
                                                dc_success='half',
                                                recharge_on_roll=1,
                                                area_of_effect=area_of_effect)
        special_abilities.append(sa)
    elif name == 'Spawn of Kyuss':
        # Multiple attack
        # "The spawn of Kyuss makes two Claw attacks, and it uses Burrowing Worm."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        damage_type: DamageType = request_damage_type(index_name='necrotic')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=0))]
        multi_attack_action = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Special attacks
        damage_type: DamageType = request_damage_type(index_name='necrotic')
        # TODO implements Burrowing Worm effect (curse effect)
        # "A worm launches from the spawn of Kyuss at one Humanoid that the spawn can see within 10 feet of it.
        # The worm latches onto the target's skin unless the target succeeds on a {@dc 11} Dexterity saving throw.
        # The worm is a Tiny Undead with AC 6, 1 hit point, a 2 (-4) in every ability score, and a speed of 1 foot.
        # While on the target's skin, the worm can be killed by normal means or scraped off using an action (the spawn can use Burrowing Worm to launch a scraped-off worm at a Humanoid it can see within 10 feet of the worm).
        # Otherwise, the worm burrows under the target's skin at the end of the target's next turn, dealing 1 piercing damage to it.
        # At the end of each of its turns thereafter, the target takes 7 ({@damage 2d6}) necrotic damage per worm infesting it (maximum of {@damage 10d6}), and if it drops to 0 hit points, it dies and then rises 10 minutes later as a spawn of Kyuss.
        # If a worm-infested target is targeted by an effect that cures disease or removes a curse, all the worms infesting it wither away."

        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        sa: SpecialAbility = SpecialAbility(name='Burrowing Worm',
                                                desc='',
                                                damages=damages,
                                                dc_type='dex',
                                                dc_value=11,
                                                dc_success='half',
                                                recharge_on_roll=1)
        special_abilities.append(sa)
    elif name == "Hobgoblin Warlord":
        # Multiple attack
        # "The hobgoblin makes three melee attacks. Alternatively, it can make two ranged attacks with its javelins."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d10', bonus=3))]
        multi_attack_action = Action(name='Longsword', desc='', type=ActionType.MELEE, attack_bonus=9, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        multi_attack_action = Action(name='Javelin', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages, normal_range=30, long_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # TODO
        # "Shield Bash" Melee attack & knock
        # "Leadership (Recharges after a Short or Long Rest)"
    elif name == "Duergar Mind Master":
        # Multiple attack
        # "The duergar makes two Mind-Poison Dagger attacks. It can replace one attack with a use of Mind Mastery."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        multi_attack_action = Action(name='Mind-Poison Dagger', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
        # TODO Mind Mastery (Condition Charmed)
        # TODO Invisibility {@recharge 4} (Concentration)
    elif name == "Duergar Screamer":
        # Multiple attack
        # "The screamer makes one Drill attack, and it uses Sonic Scream."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        multi_attack_action_1: Action = Action(name='Drill', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='thunder')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        area_of_effect = AreaOfEffect(type='cube', size=15)
        multi_attack_action_2: SpecialAbility = SpecialAbility(name='Burrowing Worm',
                                                desc='',
                                                damages=damages,
                                                dc_type='str',
                                                dc_value=11,
                                                dc_success='half',
                                                recharge_on_roll=1,
                                                area_of_effect=area_of_effect,
                                                effects=[Condition('prone', 'prone', '')])
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        # Reactions (to attack)
        reactions: dict[str, Action] = {"Engine of Pain": multi_attack_action_1}
    elif name == "Duergar Kavalrachni":
        # "The duergar makes two War Pick attacks."
        # TODO: implement poison effect
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=2))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d4'))]
        multi_attack_action = Action(name='War Pick', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d10'))]
        action = Action(name='Heavy Crossbow', desc='', type=ActionType.RANGED, attack_bonus=6, damages=damages, normal_range=100, long_range=400)
        actions.append(action)
    elif name == "Female Steeder":
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=3))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d8'))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
        # TODO Implement "Sticky Leg"
    elif name == "Succubus":
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        action = Action(name='Claw (Fiend Form Only)', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
        # TODO Implement "Charm", "Draining Kiss"
    elif name == "Incubus":
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        action = Action(name='Claw (Fiend Form Only)', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
        # TODO Implement "Charm", "Draining Kiss"
    return actions, special_abilities, spell_caster

def request_monster_other(name: str) -> Optional[Monster]:
    """
    Send a request to local database for a monster's characteristic
    :param monster_name: name of the monster
    :return: Monster object
    """
    with open(f"{path}/maze/other_monsters/bestiary-sublist-data.json", "r") as f:
        list_data = json.loads(f.read())
        monster_data = [monster for monster in list_data if monster['name'].lower() == name.lower() ]
        if not monster_data:
            return None
        data = monster_data[0]

        proficiencies: List[Proficiency] = []
        actions, special_abilities, spell_caster = get_special_monster_actions(name)
        ac: int = data['_fAc'][0]
        hit_dice: str = data['hp']['formula']
        dice, bonus = hit_dice.split(' + ') if '+' in hit_dice else [hit_dice, 0]
        hit_dice: DamageDice = DamageDice(dice=dice, bonus=int(bonus))
        # https://tomedunn.github.io/the-finished-book/monsters/calculating-monster-xp/
        # multi_attacks: List[Action] = [a for m in actions for a in m.multi_attack if m.multi_attack]
        single_attacks: List[Action] = [a for a in actions if not a.multi_attack]
        # print(name)
        multi_attacks: List[Action] = []
        # if any(a.multi_attack for a in actions):
        multi_attacks = [m for a in actions if a.multi_attack for m in a.multi_attack]
        attacks = single_attacks + multi_attacks + special_abilities
        damages: List[int] = [damage.dd.avg for a in attacks for damage in a.damages]
        # effective_attack_bonus
        # attack_bonus_list: List[int] = [a.attack_bonus for a in single_attacks if not a.multi_attack] + [m.attack_bonus for a in actions for m in a.multi_attack if a.multi_attack]
        try:
            ab: float = sum([a.attack_bonus for a in attacks if hasattr(a, 'attack_bonus')]) / len(attacks) if attacks else 0.0
        except ZeroDivisionError:
            print(f'Error: {name}')
        # average damage per round assuming all attacks hit
        dpr: float = sum(damages) / len(damages)
        xp: float = 5 * int(data['hp']['average']) * dpr * (ac + ab - 2) / (4 * 13)
        print(f'{name}: {xp} XP')
        return Monster(id=-1,
                       image_name=f'monster_enemy.png',
                       x=-1, y=-1, old_x=-1, old_y=-1,
                       index=name.lower().replace(' ', '-'),
                       name=data['name'],
                       abilities=Abilities(str=data['str'], dex=data['dex'], con=data['con'],
                                           int=data['int'], wis=data['wis'], cha=data['cha']),
                       proficiencies=proficiencies,
                       armor_class=ac,
                       hit_points=hit_dice.roll(),
                       hit_dice=data['hp']['formula'],
                       xp=int(xp),
                       challenge_rating=parse_challenge_rating(data['cr']),
                       actions=actions,
                       sc=spell_caster,
                       sa=special_abilities)  # if can_attack else None


def request_spell(index_name: str) -> Spell:
    """
    Send a request to local database for a spell's characteristic
    :param index_name: name of the monster
    :return: Spell object
    """
    with open(f"{path}/data/spells/{index_name}.json", "r") as f:
        data = json.loads(f.read())

    allowed_classes: List[str] = [c['index'] for c in data['classes']]

    if 'heal_at_slot_level' in data:
        pass

    damage_type: DamageType = None
    damage_at_slot_level: dict() = None
    damage_at_character_level: dict() = None
    if "damage" in data:
        # print(data['index'], data['damage'])
        damage_type = data['damage']['damage_type']['index'] if "damage_type" in data['damage'] else None
        damage_at_slot_level = data['damage'].get('damage_at_slot_level')
        damage_at_character_level = data['damage'].get(
            'damage_at_character_level')
        # print(f"{data['index']} - damage_at_character_level={damage_at_character_level}")
        # print(f"{data['index']} - damage_at_slot_level={damage_at_slot_level}")

        dc_type: str = None
        dc_success: str = None
        # print(data)
        if "dc" in data:
            dc_type = data['dc']['dc_type']['index']
            dc_success = data['dc']['dc_success']
            # print(f"{data['index']} - dc_type = {dc_type}")

        # range: int
        # attack_type: str  # ranged, touch
        # area_of_effet: AreaOfEffect
        # school: str

        # print(index_name)
        range = int(data['range'].split()[0]) if 'feet' in data['range'] else 5
        if 'area_of_effect' in data:
            area_of_effect = AreaOfEffect(type=data['area_of_effect']['type'], size=data['area_of_effect']['size'])
        else:
            area_of_effect = AreaOfEffect(type='sphere', size=range)
        # print(index_name, area_of_effect)
        school: str = data['school']['index']

        return Spell(index=data['index'],
                     name=data['name'],
                     desc=data['desc'],
                     level=data['level'],
                     allowed_classes=allowed_classes,
                     damage_type=damage_type,
                     damage_at_slot_level=damage_at_slot_level,
                     damage_at_character_level=damage_at_character_level,
                     dc_type=dc_type,
                     dc_success=dc_success,
                     range=range,
                     area_of_effect=area_of_effect,
                     school=school
                     )


def request_armor(index_name: str) -> Armor:
    """
    Send a request to local database for a armor's characteristic
    :param index_name: name of the armor
    :return: Armor object
    """
    with open(f"{path}/data/armors/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    if "armor_class" in data:
        image_name = load_armor_image_name(index_name)
        return Armor(id=-1,
                     image_name=image_name,
                     x=-1, y=-1, old_x=-1, old_y=-1,
                     index=data['index'],
                     name=data['name'],
                     armor_class=data['armor_class'],
                     str_minimum=data['str_minimum'],
                     category=request_equipment_category(
                         data['equipment_category']['index']),
                     stealth_disadvantage=data['stealth_disadvantage'],
                     cost=data['cost'],
                     weight=data['weight'],
                     desc=None,
                     equipped=False)
    return None


def request_weapon_property(index_name: str) -> WeaponProperty:
    """
    Send a request to local database for a weapon's property characteristic
    :param index_name: name of the weapon's property
    :return: WeaponProperty object
    """
    with open(f"{path}/data/weapon-properties/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return WeaponProperty(index=data['index'],
                          name=data['name'],
                          desc=data['desc'])


def request_weapon(index_name: str) -> Weapon:
    """
    Send a request to local database for a weapon's characteristic
    :param index_name: name of the weapon
    :return: Weapon object
    """
    with open(f"{path}/data/weapons/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    weapon_properties = None
    if 'properties' in data:
        weapon_properties: List[WeaponProperty] = [
            request_weapon_property(d['index']) for d in data['properties']]
    throw_range = None
    if 'throw_range' in data:
        throw_range = WeaponThrowRange(
            data['throw_range']['normal'], data['throw_range']['long'])
    if "damage" in data:
        damage_dice_two_handed: DamageDice = None
        if "two_handed_damage" in data:
            damage_dice_two_handed: DamageDice = DamageDice(data['two_handed_damage']['damage_dice'])
        return Weapon(id=-1,
                      image_name=load_weapon_image_name(index_name),
                      x=-1, y=-1, old_x=-1, old_y=-1,
                      index=data['index'],
                      name=data['name'],
                      category=request_equipment_category(data['equipment_category']['index']),
                      category_type=CategoryType(data['weapon_category']),
                      range_type=RangeType(data['weapon_range']),
                      damage_dice=DamageDice(data['damage']['damage_dice']),
                      damage_dice_two_handed=damage_dice_two_handed,
                      damage_type=request_damage_type(index_name=data['damage']['damage_type']['index']),
                      range=WeaponRange(normal=data['range']['normal'], long=data['range']['long']),
                      throw_range=throw_range,
                      is_magic=False,
                      cost=data['cost'],
                      weight=data['weight'],
                      properties=weapon_properties,
                      desc=None,
                      equipped=False)
    return None


def request_trait(index_name: str) -> Trait:
    """
    Send a request to local database for a trait's characteristic
    :param index_name: name of the trait
    :return: Trait object
    """
    with open(f"{path}/data/traits/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return Trait(index=data['index'],
                 name=data['name'],
                 desc=data['desc'])


def request_race(index_name: str) -> Race:
    """
    Send a request to local database for a race's characteristic
    :param index_name: name of the race
    :return: Race object
    """
    with open(f"{path}/data/races/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus'])
                                for ability_bonus in data['ability_bonuses']])
        starting_proficiencies: List[Proficiency] = [request_proficiency(
            d['index']) for d in data.get('starting_proficiencies')]
        starting_proficiency_options: List[Tuple[List[Proficiency], int]] = []
        if data.get('starting_proficiency_options'):
            dat = data.get('starting_proficiency_options')
            choose: int = dat['choose']
            proficiencies_choose: List[Proficiency] = [
                request_proficiency(d['index']) for d in dat['from']]
            starting_proficiency_options.append((choose, proficiencies_choose))
        languages: List[Language] = [lang['index']
                                     for lang in data['languages']]
        traits: List[Trait] = [request_trait(
            d['index']) for d in data['traits']]
        subraces: List[SubRace] = [request_subrace(
            d['index']) for d in data['subraces']]
        subraces: List[str] = [d['index'] for d in data['subraces']]
        return Race(index=data['index'],
                    name=data['name'],
                    speed=data['speed'],
                    ability_bonuses=ability_bonuses,
                    alignment=data['alignment'],
                    age=data['age'],
                    size=data['size'],
                    size_description=data['size_description'],
                    starting_proficiencies=starting_proficiencies,
                    starting_proficiency_options=starting_proficiency_options,
                    languages=languages,
                    language_desc=data['language_desc'],
                    traits=traits,
                    subraces=subraces)


def request_subrace(index_name: str) -> SubRace:
    """
    Send a request to local database for a subrace's characteristic
    :param index_name: name of the subrace
    :return: SubRace object
    """
    with open(f"{path}/data/subraces/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus'])
                                for ability_bonus in data['ability_bonuses']])
        starting_proficiencies: List[Proficiency] = [request_proficiency(
            d['index']) for d in data['starting_proficiencies']]
        racial_traits: List[Trait] = [request_trait(
            d['index']) for d in data['racial_traits']]
        return SubRace(index=data['index'],
                       name=data['name'],
                       desc=data['desc'],
                       ability_bonuses=ability_bonuses,
                       starting_proficiencies=starting_proficiencies,
                       racial_traits=racial_traits)


def request_language(index_name: str) -> Language:
    """
    Send a request to local database for a language's characteristic
    :param index_name: name of the language
    :return: Language object
    """
    with open(f"{path}/data/languages/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        return Language(index_name=data['index'],
                        name=data['name'],
                        desc=data['desc'],
                        type=data['type'],
                        typical_speakers=data['typical_speakers'],
                        script=data['script'])


def request_proficiency(index_name: str) -> Proficiency:
    """
    Send a request to local database for a proficiency's characteristic
    :param index_name: name of the proficiency
    :return: Proficiency object
    """
    with open(f"{path}/data/proficiencies/{index_name}.json", "r") as f:
        data = json.loads(f.read())

    classes: List[str] = []
    races: List[str] = []
    for _class in data['classes']:
        classes.append(_class['index'])
    for race in data['races']:
        races.append(race['index'])
    ref_url: str = data['reference']['url']
    category: str = ref_url.split('/')[2]
    index_name: str = ref_url.split('/')[3]
    ref: object = None
    match category:
        case 'equipment':
            ref: Equipment = request_equipment(index_name=index_name)
        case 'equipment-categories':
            ref: List[Equipment] = list_equipment_category(
                index_name=index_name)
        case 'ability-scores':
            ref: AbilityType = AbilityType(index_name)

    return Proficiency(index=data['index'],
                       name=data['name'],
                       type=ProfType(data['type']),
                       ref=ref,
                       classes=classes,
                       races=races)


def request_language(index_name: str) -> Language:
    """
    Send a request to local database for a language's characteristic
    :param index_name: name of the language
    :return: Language object
    """
    with open(f"{path}/data/languages/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        return Language(index=data['index'],
                        name=data['name'],
                        desc=data['desc'],
                        type=data['type'],
                        typical_speakers=data['typical_speakers'],
                        script=data['script'])


def request_equipment_category(index_name: str) -> EquipmentCategory:
    """
    Send a request to local database for an equipment category's characteristic
    :param index_name: name of the equipment category
    :return: EquipmentCategory object
    """
    with open(f"{path}/data/equipment-categories/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        return EquipmentCategory(index=data['index'],
                                 name=data['name'],
                                 url=data['url'])


def list_equipment_category(index_name: str) -> List[Equipment]:
    """
    Send a request to local database to list equipments inside an equipment category
    :param index_name: name of the equipment category
    :return: list of equipment's objects
    """
    with open(f"{path}/data/equipment-categories/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    equipments: List[Equipment] = []
    for equip in data.get('equipment'):
        equipment: Equipment = request_equipment(equip['index'])
        equipments.append(equipment)
    return equipments


def request_equipment(index_name: str) -> Optional[Equipment]:
    """
    Send a request to local database for an equipment's characteristic
    :param index_name: name of the equipment
    :return: Equipment object
    """
    try:
        with open(f"{path}/data/equipment/{index_name}.json", "r") as f:
            data = json.loads(f.read())
            equipment_category = data['equipment_category']['index']
            if equipment_category == 'weapon':
                return request_weapon(index_name)
            elif equipment_category == 'armor':
                return request_armor(index_name)
            else:
                return Equipment(id=-1,
                                 image_name='None.PNG',
                                 x=-1, y=-1, old_x=-1, old_y=-1,
                                 index=data['index'],
                                 name=data['name'],
                                 category=request_equipment_category(equipment_category),
                                 cost=data['cost'],
                                 weight=data.get('weight'),
                                 desc=data.get('desc'),
                                 equipped=False)
    except FileNotFoundError:
        # print(f'equipment {index_name} not existing in database!')
        return None


def get_spell_slots(class_name: str) -> Tuple[dict(), List[int], List[int]]:
    """
        Determine the spell slots and known spells by level
    :param class_name: class_type name
    :return: known spells and spell slots by level
    """
    csv_filename: str = f'{class_name}-{class_name}.csv'
    slots: List[str] = []
    spell_slots: dict() = dict()
    spells_known: List[int] = []
    cantrips_known: List[int] = []

    def str2int(x):
        return 0 if not x else int(x)

    # print(class_name)
    match class_name:
        case 'Wizard' | 'Druid' | 'Cleric' | 'Ranger':
            # Lvl;Proficiency Bonus;Features;Cantrips Known;1;2;3;4;5;6;7;8;9
            data = read_csvfile(csv_filename)
            # print(data)
            for line in data:
                char_level, prof_bonus, features, ct_known, *slots = line
                spell_slots[int(char_level)] = list(map(str2int, slots))
                cantrips_known.append(str2int(ct_known))
                spells_known.append(100)
                # TODO
            # print(f'{class_name} - spell slots : {spell_slots} - - spell known : {spells_known}')
        case 'Paladin':
            data = read_csvfile(csv_filename)
            for line in data:
                char_level, prof_bonus, features, *slots = line
                spell_slots[int(char_level)] = list(map(str2int, slots))
                spells_known.append(10 * int(char_level))
                # TODO
        case 'Sorcerer':
            """
                Lvl;Proficiency Bonus;Sorcery Points;Features;Cantrips Known;Spells Known;1;2;3;4;5;6;7;8;9
                1;2;;Spellcasting, Sorcerous Origin;4;2;2;;;;;;;;
                2;2;2;Font of Magic;4;3;3;;;;;;;;
            """
            data = read_csvfile(csv_filename)
            for line in data:
                char_level, prof_bonus, sorcery_points, features, ct_known, sp_known, *slots = line
                # print(f'{class_name} - level #{char_level} slots: {slots}')
                spell_slots[int(char_level)] = list(map(str2int, slots))
                cantrips_known.append(str2int(ct_known))
                spells_known.append(str2int(sp_known))
            # exit_message(spell_slots)
        case 'Bard':
            data = read_csvfile(csv_filename)
            for line in data:
                char_level, prof_bonus, features, ct_known, sp_known, *slots = line
                spell_slots[int(char_level)] = list(map(str2int, slots))
                cantrips_known.append(str2int(ct_known))
                spells_known.append(str2int(sp_known))
        case 'Warlock':
            data = read_csvfile(csv_filename)
            for line in data:
                # Lvl;Proficiency Bonus;Features;Cantrips Known;Spells Known;Spell Slots;Slot Level;Invocations Known
                char_level, prof_bonus, features, ct_known, sp_known, spell_slots_count, slot_level, inv_known = line
                spell_slots[int(char_level)] = [int(spell_slots_count)] * \
                                               int(slot_level) + [0] * (5 - int(slot_level))
                cantrips_known.append(str2int(ct_known))
                spells_known.append(str2int(sp_known))
    return spell_slots, spells_known, cantrips_known


def request_class(index_name: str, known_proficiencies: List[Proficiency] = None,
                  abilities: List[AbilityType] = None) -> ClassType:
    """
    Send a request to local database for a class's characteristic
    :param index_name: name of the class
    :return: ClassType object
    """
    with open(f"{path}/data/classes/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        proficiencies: List[Proficiency] = [request_proficiency(
            d['index']) for d in data['proficiencies']]
        proficiency_choices: List[Tuple[List[Proficiency], int]] = []
        for dat in data['proficiency_choices']:
            choose: int = dat['choose']
            proficiencies_choose: List[Proficiency] = [
                request_proficiency(d['index']) for d in dat['from']]
            proficiency_choices.append((choose, proficiencies_choose))

        starting_equipment: List[Inventory] = []
        for equip_dict in data['starting_equipment']:
            quantity: int = equip_dict['quantity']
            equipment: Equipment = request_equipment(
                equip_dict['equipment']['index'])
            starting_equipment.append(
                Inventory(quantity=quantity, equipment=equipment))

        starting_equipment_options: List[List[Inventory]] = []
        for st_eq_option in data['starting_equipment_options']:
            choose: int = st_eq_option['choose']
            equipments_choose: List[Inventory] = []
            for eq_choice in st_eq_option['from']:
                if known_proficiencies:
                    known_proficiencies: List[str] = [p.index for p in known_proficiencies]
                    prereq = True
                    for p_dict in eq_choice['prerequisites']:
                        if p_dict['proficiency']['index'] not in known_proficiencies:
                            prereq = False
                    if not prereq:
                        continue
                if 'equipment' in eq_choice:
                    equipment: Inventory = Inventory(
                        quantity=eq_choice['quantity'], equipment=request_equipment(eq_choice['equipment']['index']))
                    equipments_choose.append(equipment)
                elif 'equipment_option' in eq_choice:
                    quantity: int = eq_choice['quantity'] if 'quantity' in eq_choice else 1
                    equipment_category: EquipmentCategory = request_equipment_category(
                        eq_choice['equipment_option']['from']['equipment_category']['index'])
                    equipments_choose.append(
                        Inventory(quantity=quantity, equipment=equipment_category))
                elif 'equipment_category' in eq_choice:
                    quantity: int = eq_choice['quantity'] if 'quantity' in eq_choice else 1
                    equipment_category: EquipmentCategory = request_equipment_category(
                        eq_choice['equipment_category']['index'])
                    equipments_choose.append(
                        Inventory(quantity=quantity, equipment=equipment_category))
                else:
                    equipments: List[Inventory] = []
                    for item_no, equip_dict in eq_choice.items():
                        # print(f'item_no: {item_no}, equip_dict: {equip_dict}')
                        if 'equipment' in equip_dict:
                            quantity: int = equip_dict['quantity'] if 'quantity' in equip_dict else 1
                            equipment: Equipment = request_equipment(
                                equip_dict['equipment']['index'])
                            equipments.append(
                                Inventory(quantity=quantity, equipment=equipment))
                    equipments_choose.append(equipments)
            if equipments_choose:
                # starting_equipment_options.append((choose, equipments_choose))
                starting_equipment_options.append(equipments_choose)

        saving_throws: List[AbilityType] = [AbilityType(
            d['index']) for d in data['saving_throws']]

        can_cast: bool = 'spells' in data
        spell_slots, spells_known, cantrips_known = {}, [], []
        if can_cast:
            spell_slots, spells_known, cantrips_known = get_spell_slots(
                class_name=data['name'])

        spellcasting_level: int = None
        spellcasting_ability: str = None
        if 'spellcasting' in data:
            spellcasting_level: int = int(data['spellcasting']['level'])
            spellcasting_ability: str = data['spellcasting']['spellcasting_ability']['index']

        return ClassType(index=data['index'],
                         name=data['name'],
                         hit_die=data['hit_die'],
                         proficiency_choices=proficiency_choices,
                         proficiencies=proficiencies,
                         saving_throws=saving_throws,
                         starting_equipment=starting_equipment,
                         starting_equipment_options=starting_equipment_options,
                         class_levels=data['class_levels'],
                         multi_classing=data['multi_classing'],
                         subclasses=data['subclasses'],
                         spellcasting_level=spellcasting_level,
                         spellcasting_ability=spellcasting_ability,
                         can_cast='spells' in data,
                         spell_slots=deepcopy(spell_slots),
                         spells_known=spells_known,
                         cantrips_known=cantrips_known)
