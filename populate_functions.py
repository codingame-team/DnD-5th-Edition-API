from __future__ import annotations

import csv
import json
import os
from copy import deepcopy
from random import randint
from typing import List, Tuple, Optional
import re
import sys

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
from dnd_5e_core.entities import Character, Monster, Sprite
from dnd_5e_core.equipment import (
    Weapon, Armor, Equipment, Cost, EquipmentCategory, Inventory,
    WeaponProperty, WeaponRange, WeaponThrowRange, CategoryType, RangeType, DamageType
)
from dnd_5e_core.spells import Spell, SpellCaster
from dnd_5e_core.combat import Action, ActionType, SpecialAbility, Damage, Condition, AreaOfEffect
from dnd_5e_core.races import Race, SubRace, Trait, Language
from dnd_5e_core.classes import ClassType, Proficiency, ProfType
from dnd_5e_core.abilities import Abilities, AbilityType
from dnd_5e_core.mechanics import DamageDice

from populate_rpg_functions import load_armor_image_name, load_weapon_image_name
from tools.common import parse_challenge_rating, resource_path

# Import dnd-5e-core for data loading
try:
    from dnd_5e_core.data import (
        populate as core_populate,
        set_data_directory,
        load_monster as core_load_monster,
        load_spell as core_load_spell,
        load_weapon as core_load_weapon,
        load_armor as core_load_armor,
        load_race as core_load_race,
        load_class as core_load_class,
        load_equipment as core_load_equipment
    )
    from dnd_5e_core.data.collections import set_collections_directory
    # Import for extended monsters from 5e.tools
    from dnd_5e_core.entities import get_extended_monster_loader, get_special_actions_builder
    from dnd_5e_core.utils import download_monster_token

    # Configure dnd-5e-core to use the local data directories
    _base_path = os.path.dirname(__file__)
    set_data_directory(os.path.join(_base_path, 'data'))
    set_collections_directory(os.path.join(_base_path, 'collections'))

    USE_DND_5E_CORE = True
except ImportError as e:
    print(f"Warning: dnd-5e-core not available ({e}), using local data loading")
    USE_DND_5E_CORE = False

""" CSV loads """

path = os.path.dirname(__file__)


def populate_names(race: Race) -> dict():
    """
    :return: list of names (except humans and half-elf)
    """
    names_list = dict()
    with open(resource_path(f"data/names/{race.index}.csv"), newline='') as csv_file:
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
    with open(resource_path("data/names/human.csv"), newline='') as csv_file:
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
    with open(resource_path(f'Tables/{filename}'), newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        headers = next(reader, None)
        csv_data = csv.DictReader(csv_file, delimiter=';')
        for row in csv_data:
            result.append({header: row(header) for header in headers})
    return result

# ============================================
# EXTENDED MONSTERS FROM 5E.TOOLS
# ============================================

# Initialize loaders for extended monsters (lazy loading)
_extended_monster_loader = None
_special_actions_builder = None


def get_extended_loader():
    """Get the extended monster loader instance (lazy initialization)"""
    global _extended_monster_loader
    if _extended_monster_loader is None and USE_DND_5E_CORE:
        _extended_monster_loader = get_extended_monster_loader()
    return _extended_monster_loader


def get_actions_builder():
    """Get the special actions builder instance (lazy initialization)"""
    global _special_actions_builder
    if _special_actions_builder is None and USE_DND_5E_CORE:
        _special_actions_builder = get_special_actions_builder()
    return _special_actions_builder


def is_extended_monster(name: str) -> bool:
    """Check if a monster is available in the extended 5e.tools data"""
    loader = get_extended_loader()
    if loader is None:
        return False
    data = loader.get_monster_by_name(name)
    return data is not None


def get_extended_monster_data(name: str) -> Optional[dict]:
    """Get the JSON data for an extended monster from 5e.tools"""
    loader = get_extended_loader()
    if loader is None:
        return None
    return loader.get_monster_by_name(name)


def get_extended_monster_token_path(name: str, source: str = None) -> Optional[str]:
    """
    Get the path to a monster token image.
    If the token doesn't exist, attempts to download it.

    :param name: Monster name
    :param source: Source book code (e.g., "MM", "MPMM")
    :return: Path to the token image or None
    """
    if not USE_DND_5E_CORE:
        return None

    # Get source from extended data if not provided
    if source is None:
        data = get_extended_monster_data(name)
        if data:
            source = data.get('source', 'MM')
        else:
            source = 'MM'

    # Check if token exists in dnd-5e-core
    from pathlib import Path
    token_folder = Path('/Users/display/PycharmProjects/dnd-5e-core/dnd_5e_core/data/monsters/tokens')
    safe_name = name.replace('/', '_')
    token_path = token_folder / f"{safe_name}.webp"

    if token_path.exists():
        return str(token_path)

    # Try to download the token
    try:
        status = download_monster_token(name, source=source, save_folder=str(token_folder))
        if status == 200 and token_path.exists():
            return str(token_path)
    except Exception as e:
        print(f"[WARNING] Could not download token for {name}: {e}")

    return None


# ============================================
# END EXTENDED MONSTERS SECTION
# ============================================


def read_csvfile(filename: str):
    """
    :param filename: csv file in Tables directory
    :return: list of dictionaries
    """
    with open(resource_path(f'Tables/{filename}'), newline='') as csv_file:
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
    with open(resource_path("Tables/Height and Weight-Height and Weight.csv"), newline='') as csv_file:
        # csv_data = csv.reader(csv_file, delimiter=';')
        # next(csv_data, None)
        csv_data = csv.DictReader(csv_file, delimiter=';')
        for row in csv_data:
            hw_conv_table.append({header: row(header) for header in headers})
    return hw_conv_table


""" JSON loads """


def _load_json_data(category: str, index_name: str) -> dict:
    """
    Helper function to load JSON data from dnd-5e-core or local files.

    :param category: Category of data (e.g., 'monsters', 'spells', 'weapons')
    :param index_name: Index/slug of the item
    :return: Dictionary with JSON data
    """
    if USE_DND_5E_CORE:
        try:
            # Try loading via dnd-5e-core loaders
            if category == 'monsters':
                return core_load_monster(index_name)
            elif category == 'spells':
                return core_load_spell(index_name)
            elif category == 'weapons':
                return core_load_weapon(index_name)
            elif category in ('armor', 'armors'):
                return core_load_armor(index_name)
            elif category == 'races':
                return core_load_race(index_name)
            elif category == 'classes':
                return core_load_class(index_name)
            elif category == 'equipment':
                return core_load_equipment(index_name)
        except Exception as e:
            # If core loader fails, fall back to local file
            if os.getenv('DEBUG'):
                print(f"Warning: dnd-5e-core load failed for {category}/{index_name} ({e}), using local file")

    # Fallback: Load from local data directory
    file_path = resource_path(f"data/{category}/{index_name}.json")
    with open(file_path, "r") as f:
        return json.loads(f.read())


def populate(collection_name: str, key_name: str, with_url=False, collection_path: str = None) -> List[str]:
    """
    Load collection data from dnd-5e-core (preferred) or local collections directory (fallback).

    :param collection_name: Name of the collection file (without .json)
    :param key_name: Key to extract from JSON (usually 'results')
    :param with_url: If True, return tuples of (index, url)
    :param collection_path: Optional custom path to collections directory
    :return: List of collection names or (name, url) tuples
    """
    # Use dnd-5e-core if available (preferred method)
    if USE_DND_5E_CORE:
        try:
            return core_populate(collection_name, key_name, with_url, collection_path)
        except Exception as e:
            # If dnd-5e-core fails, log and fallback
            print(f"Warning: dnd-5e-core populate failed ({e}), using local fallback")

    # Fallback: Use local collections directory
    if not collection_path:
        collection_path = 'collections'
    try:
        with open(resource_path(f"{collection_path}/{collection_name}.json"), "r") as f:
            data = json.loads(f.read())
            collection_json_list = data[key_name]
    except Exception as e:
        print(f'Error loading collection {collection_name}: {e}')
        if 'f' in locals():
            print(f'File: {f.name} - key_name: {key_name}')
        sys.exit(1)  # Use sys.exit instead of exit, and exit with error code 1

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
    data = _load_json_data('damage-types', index_name)
    return DamageType(index=data['index'], name=data['name'], desc=data['desc'])


def request_condition(index_name: str) -> Condition:
    """
    Send a request to local database for a condition's characteristic
    :param index_name: name of the condition
    :return: Condition object
    """
    data = _load_json_data('conditions', index_name)
    return Condition(index=data['index'], name=data['name'], desc=data['desc'])


def request_other_actions(index_name: str) -> List[Action]:
    actions: List[Action] = []
    data = _load_json_data('monsters', index_name)
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

def extract_recharge_on_roll_from(action) -> Optional[int]:
    action_name: str = action['name']
    if "usage" in action:
        if action['usage'].get('type') == 'recharge on roll':
            return action['usage']['min_value']
    elif 'Recharge' in action_name:
        pattern = r"Recharge (\d+)"
        match = re.search(pattern, action_name)
        if match:
            action_name = action_name.split('(')[0].strip()
            return int(match.group(1))

def extract_special_ability_from(action: str, recharge_on_roll: int) -> Optional[SpecialAbility]:
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
    area_of_effect: AreaOfEffect = AreaOfEffect(type='sphere', size=5)
    if damages:
        return SpecialAbility(name=action['name'],
                                desc=action.get('desc'),
                                damages=damages,
                                dc_type=action['dc']['dc_type']['index'],
                                dc_value=action['dc']['dc_value'],
                                dc_success=action['dc']['success_type'],
                                recharge_on_roll=recharge_on_roll,
                                area_of_effect=area_of_effect)


def request_monster(index_name: str) -> Optional[Monster]:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object or None if not found
    """
    # print(index_name)
    data = _load_json_data('monsters', index_name)

    # Check if monster data was loaded
    if data is None:
        return None

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
            if action['name'] != 'Multiattack':
                if "damage" in action:
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
                        else:
                            normal_range = 5
                            long_range = None
                    damages: List[Damage] = []
                    for damage in action['damage']:
                        # print(f'damage = {damage}')
                        if "choose" in damage and damage['type'] == 'damage':
                            actions_count = int(damage['choose'])
                            damages_list = damage['from']
                            for damage_dict in damages_list:
                                damage_type: DamageType = request_damage_type(index_name=damage_dict['damage_type']['index'])
                                damage_choice = Damage(type=damage_type, dd=DamageDice(damage_dict['damage_dice']))
                                action_type = ActionType.MIXED if is_melee_attack and is_ranged_attack else ActionType.MELEE if is_melee_attack else ActionType.RANGED
                                actions.append(Action(name=action['name'], desc=action['desc'], type=action_type, normal_range=normal_range, long_range=long_range,
                                                      attack_bonus=action.get('attack_bonus'), multi_attack=None, damages=[damage_choice]))
                        elif "damage_type" in damage:
                            damage_type: DamageType = request_damage_type(index_name=damage['damage_type']['index'])
                            damages.append(Damage(type=damage_type, dd=DamageDice(damage['damage_dice'])))

                if damages:
                    can_attack = True
                    action_type = ActionType.MIXED if is_melee_attack and is_ranged_attack else ActionType.MELEE if is_melee_attack else ActionType.RANGED
                    actions.append(Action(name=action['name'], desc=action['desc'], type=action_type, normal_range=normal_range, long_range=long_range,
                                          attack_bonus=action.get('attack_bonus'), multi_attack=None, damages=damages))
        # Multiattacks
        for action in data['actions']:
            if action['name'] == 'Multiattack':
                can_attack = True
                multi_attack: List[Action] = []
                # Todo: verify if there could be more than one choice...
                VALID_TYPES = {ActionType.MELEE, ActionType.RANGED}
                choose_count: int = action['options']['choose']
                for action_dict in action['options']['from'][0]:
                    try:
                        count = int(action_dict['count'])
                        action_match = next((a for a in actions if a.name == action_dict['name']), None)
                        if action_match and action_match.type in VALID_TYPES:
                            multi_attack.extend([action_match] * count)
                    except (ValueError, KeyError):
                        print(f"invalid count option for {index_name} : {action_dict['name']}")
                # action_type: str = ActionType.MELEE if 'Melee' in action['desc'] else ActionType.RANGED if 'Ranged' in action['desc']
                actions.append(Action(name=action['name'], desc=action['desc'], type=ActionType.MELEE, attack_bonus=None, multi_attack=multi_attack, damages=None))
        # Special abilities
        for action in data['actions']:
            if 'dc' in action:
                recharge_on_roll: Optional[int] = extract_recharge_on_roll_from(action)
                if 'damage' in action:
                    sa: Optional[SpecialAbility] = extract_special_ability_from(action, recharge_on_roll)
                    if sa: special_abilities.append(sa)
            elif 'attack_options' in action:
                recharge_on_roll: Optional[int] = extract_recharge_on_roll_from(action)
                options: str = action['attack_options']
                if options.get('type') == 'attack':
                    choose_count: int = int(options.get('choose'))
                    if choose_count == 1:
                        for a in options.get('from'):
                            if 'dc' in a:
                                if 'damage' in a:
                                    sa: Optional[SpecialAbility] = extract_special_ability_from(a, recharge_on_roll)
                                    if sa: special_abilities.append(sa)
                    else:
                        # TODO: check if there are multi-attack defined in some monster json
                        continue


    # TODO Check if there are other special abilities that we did not cover...
    if not actions:
        actions = request_other_actions(index_name)

    proficiencies: List[Proficiency] = []
    if 'proficiencies' in data:
        for prof in data['proficiencies']:
            proficiency: Proficiency = request_proficiency(index_name=prof['proficiency']['index'])
            proficiency.value = prof.get('value')
            proficiencies.append(proficiency)

    # print(index_name)
    speed: str = data['speed']['fly'] if 'fly' in data['speed'] else data['speed']['walk'] if 'walk' in data['speed'] else '30'

    return Monster(
                   index=index_name,
                   name=data['name'],
                   abilities=Abilities(str=data['strength'], dex=data['dexterity'], con=data['constitution'],
                                       int=data['intelligence'], wis=data['wisdom'], cha=data['charisma']),
                   proficiencies=proficiencies,
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   speed=int(speed.split()[0]),
                   challenge_rating=data['challenge_rating'],
                   actions=actions,
                   sc=spell_caster,
                   sa=special_abilities)

def get_special_monster_actions(name: str) -> tuple[List[Action], List[SpecialAbility], SpellCaster]:
    actions: List[Action] = []
    special_abilities: List[SpecialAbility] = []
    spell_caster: SpellCaster = None
    # print(name)
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
        # Spellcasting
        caster_level = 3
        dc_type = 'wis'
        dc_value = 11
        spells = ['guidance', 'resistance', 'thaumaturgy']
        spells += ['bless', 'command']
        spells += ['augury', 'spiritual-weapon']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[4, 2, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 1,
                                                    ability_modifier=1)
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
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
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
        multi_attack_action = Action(name='Arcane Burst', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Ranged attack
        # range = '120 ft'
        # action = Action(name='Multiattack', desc='', type=ActionType.RANGED,
        #        attack_bonus=None,
        #        multi_attack=[multi_attack_action] * 2, damages=None)
        # actions.append(action)
        # Spellcasting
        caster_level = 2
        dc_type = 'int'
        dc_value = 13
        spells = ['dancing-lights', 'mage-hand', 'minor-illusion']
        spells += ['disguise-self', 'invisibility', 'mage-armor', 'major-image', 'phantasmal-force', 'phantom-steed']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 1, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 5,
                                                    ability_modifier=5)
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
        action = Action(name='Constrict', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=10)
        actions.append(action)
    elif name == "Apprentice Wizard":
        # Multiple attack
        damage_type: DamageType = request_damage_type(index_name='psychic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d10', bonus=3))]
        action = Action(name='Arcane Burst', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=120)
        actions.append(action)
        # Spellcasting
        caster_level = 1
        dc_type = 'int'
        dc_value = 12
        spells = ['mage-hand', 'prestidigitation']
        spells += ['burning hands', 'disguise-self', 'mage-armor']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 4,
                                                    ability_modifier=5)
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
        multi_attack_action = Action(name='Grave Bolt', desc='', type=ActionType.RANGED, attack_bonus=5, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Spellcasting
        caster_level = 1
        dc_type = 'cha'
        dc_value = 11
        spells = ['detect-magic', 'disguise-self', 'mage-armor', 'mage-hand']
        spells += ['dispel-magic', 'hunger-of-Hadar', 'invisibility', 'spider-climb']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 4,
                                                    ability_modifier=4)
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
        # Spellcasting
        caster_level = 1
        dc_type = 'cha'
        dc_value = 15
        spells = ['detect-magic', 'guidance', 'levitate',  'mage-armor', 'mage-hand', 'minor-illusion', 'prestidigitation']
        spells += ['arcane-gate', 'detect-thoughts', 'true-seeing']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 4,
                                                    ability_modifier=4)
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
        # Spellcasting
        caster_level = 12
        dc_type = 'int'
        dc_value = 15
        spells = ['identify', 'ray-of-sickness']
        spells += ['hold-person', 'locate-object']
        spells += ['bestow-curse', 'counterspell', 'lightning-bolt']
        spells += ['phantasmal-killer', 'polymorph']
        spells += ['contact-other-plane', 'scrying']
        spells += ['eyebite']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[4, 3, 3, 3, 2, 1],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 7,
                                                    ability_modifier=7)
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
        area_of_effect = AreaOfEffect(type='cube', size=10)
        sa: SpecialAbility = SpecialAbility(name='Burrowing Worm',
                                                desc='',
                                                damages=damages,
                                                dc_type='dex',
                                                dc_value=11,
                                                dc_success='half',
                                                area_of_effect=area_of_effect,
                                                recharge_on_roll=1)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action, multi_attack_action, sa])
        actions.append(action)
        # special_abilities.append(sa)
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
    elif name == "Sea Hag":
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        action = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
        # TODO Death glare
        # "The hag targets one {@condition frightened} creature she can see within 30 feet of her.
        # If the target can see the hag, it must succeed on a {@dc 11} Wisdom saving throw against this magic or drop to 0 hit points."
        # area_of_effect = AreaOfEffect(type='cube', size=30)
        # action: SpecialAbility = SpecialAbility(name='Death glare',
        #                                         desc='',
        #                                         damages=[],
        #                                         dc_type='wis',
        #                                         dc_value=11,
        #                                         dc_success='none',
        #                                         recharge_on_roll=1,
        #                                         area_of_effect=area_of_effect,
        #                                         effects=[Condition('frightened')])
        # actions.append(action)
    elif name == "Kuo-toa Archpriest":
        # Spellcasting
        # "The kuo-toa is a 10th-level spellcaster. Its spellcasting ability is Wisdom (spell save {@dc 14}, {@hit 6} to hit with spell attacks). The kuo-toa has the following cleric spells prepared:"
        # Multi-attack
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        damage_type =  request_damage_type(index_name='lightning')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='4d6'))]
        multi_attack_action_1 = Action(name='Scepter', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        multi_attack_action_2 = Action(name='Unarmed Strike', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        # Spellcasting
        caster_level = 10
        dc_type = 'wis'
        dc_value = 14
        spells = ['guidance', 'sacred-flame', 'thaumaturgy']
        spells += ['detect-magic', 'sanctuary', 'shield-of-faith']
        spells += ['hold-person', 'spiritual-weapon']
        spells += ['spirit-guardians', 'tongues']
        spells += ['control-water', 'divination']
        spells += ['mass-cure-wounds', 'scrying']
        spells += ['phantasmal-killer', 'polymorph']
        spells += ['contact-other-plane', 'scrying']
        spells += ['eyebite']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[4, 3, 3, 3, 2],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 7,
                                                    ability_modifier=7)
    elif name == "Kuo-toa":
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=1))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=1))]
        action = Action(name='Spear', desc='', type=ActionType.MIXED, attack_bonus=3, damages=damages, normal_range=20, long_range=60)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=1))]
        action = Action(name='Spear', desc='', type=ActionType.MIXED, attack_bonus=3, damages=damages, normal_range=20, long_range=60)
        actions.append(action)
        # TODO "Net" (condition restrained)
        # "{@atk rw} {@hit 3} to hit, range 5/15 ft., one Large or smaller creature.
        # {@h}The target is {@condition restrained}.
        # A creature can use its action to make a {@dc 10} Strength check to free itself or another creature in a net, ending the effect on a success.
        # Dealing 5 slashing damage to the net (AC 10) frees the target without harming it and destroys the net."
        # TODO Reaction "Sticky Shield"
        # "When a creature misses the kuo-toa with a melee weapon attack, the kuo-toa uses its sticky shield to catch the weapon.
        # The attacker must succeed on a {@dc 11} Strength saving throw, or the weapon becomes stuck to the kuo-toa's shield.
        # If the weapon's wielder can't or won't let go of the weapon, the wielder is {@condition grappled} while the weapon is stuck. While stuck, the weapon can't be used.
        # A creature can pull the weapon free by taking an action to make a {@dc 11} Strength check and succeeding."
    elif name == "Kuo-toa Whip":
        # Spellcasting
        # "The kuo-toa is a 2nd-level spellcaster. Its spellcasting ability is Wisdom (spell save {@dc 12}, {@hit 4} to hit with spell attacks). The kuo-toa has the following cleric spells prepared:"
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        # TODO "Pincer Staff" Condition Grappled
        # "{@atk mw} {@hit 4} to hit, reach 10 ft., one target. {@h}5 ({@damage 1d6 + 2}) piercing damage.
        # If the target is a Medium or smaller creature, it is {@condition grappled} (escape {@dc 14}).
        # Until this grapple ends, the kuo-toa can't use its pincer staff on another target."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        multi_attack_action_2 = Action(name='Pincer Staff', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=10)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        # Spellcasting
        caster_level = 2
        dc_type = 'wis'
        dc_value = 11
        spells = ['sacred-flame', 'thaumaturgy']
        spells += ['bane', 'shield-of-faith']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[3, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 5,
                                                    ability_modifier=5)
    elif name == "Sahuagin Baron":
        # Multiattack
        # "The sahuagin makes three attacks: one with his bite and two with his claws or trident."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d4', bonus=4))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=4))]
        multi_attack_action_2 = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        # "{@atk mw,rw} {@hit 7} to hit, reach 5 ft. or range 20/60 ft., one target.
        # {@h}11 ({@damage 2d6 + 4}) piercing damage, or 13 ({@damage 2d8 + 4}) piercing damage if used with two hands to make a melee attack."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=4))]
        multi_attack_action_3 = Action(name='Trident', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=4))]
        multi_attack_action_4 = Action(name='Trident', desc='', type=ActionType.RANGED, attack_bonus=7, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_3, multi_attack_action_3])
        actions.append(action)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_4, multi_attack_action_4])
        actions.append(action)
    elif name == "Sahuagin Priestess":
        # Spellcasting
        # "The sahuagin is a 6th-level spellcaster. Her spellcasting ability is Wisdom (spell save {@dc 12}, {@hit 4} to hit with spell attacks). She has the following cleric spells prepared:"
        # Multiattack
        # "The sahuagin makes two melee attacks: one with her bite and one with her claws."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=1))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=1))]
        multi_attack_action_2 = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        # Spellcasting
        caster_level = 6
        dc_type = 'wis'
        dc_value = 12
        spells = ['guidance', 'thaumaturgy']
        spells += ['bless', 'detect-magic', 'guiding-bolt']
        spells += ['hold-person', 'spiritual-weapon']
        spells += ['mass-healing-word', 'tongues']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[4, 3, 3, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 5,
                                                    ability_modifier=5)
    elif name == "Sea Spawn":
        # Multiattack
        # "The sea spawn makes two Unarmed Strike attacks and one Piscine Anatomy attack."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        multi_attack_action_0 = Action(name='Unarmed Strike', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        # "Piscine Anatomy"
        # "The sea spawn uses one of the following options (choose one or roll a {@dice d6}):"
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        # TODO Condition Poisoned
        # "{@atk mw} {@hit 4} to hit, reach 5 ft., one creature.
        # {@h}3 ({@damage 1d6}) poison damage, and the target must succeed on a {@dc 12} Constitution saving throw or be {@condition poisoned} for 1 minute.
        # The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6'))]
        multi_attack_action_2 = Action(name='Poison Quills', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        multi_attack_action_3 = Action(name='Tentacle', desc='', type=ActionType.RANGED, attack_bonus=4, damages=damages, normal_range=10)
        for multi_action in (multi_attack_action_1, multi_attack_action_2, multi_attack_action_3):
            action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_0, multi_action])
            actions.append(action)
    elif name == "Yuan-ti Pureblood":
        # Multiattack
        # "The yuan-ti makes two melee attacks."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=1))]
        multi_attack_action = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Ranged attack
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=1))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        action = Action(name='Shortbow', desc='', type=ActionType.RANGED, attack_bonus=3, damages=damages, normal_range=80, long_range=320)
        actions.append(action)
        # Spellcasting
        caster_level = 3
        dc_type = 'cha'
        dc_value = 12
        spells = ['animal-friendship']
        spells += ['poison-spray', 'suggestion']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 0, 99, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 3,
                                                    ability_modifier=3)
    elif name == "Firenewt Warlock of Imix":
        # Multiattack
        # "The firenewt makes three Morningstar or Fire Ray attacks."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=1))]
        multi_attack_action = Action(name='Morningstar', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='fire')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        multi_attack_action = Action(name='Fire Ray', desc='', type=ActionType.RANGED, attack_bonus=4, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
        # Spellcasting
        caster_level = 0
        dc_type = 'cha'
        dc_value = 12
        spells = ['guidance', 'light', 'mage-armor', 'mage-hand', 'prestidigitation']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=0)
    elif name == "Firenewt Warrior":
        # Multiattack
        # "The firenewt makes two Scimitar attacks."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=1))]
        multi_attack_action = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Special attack
        # "Spit Fire (Recharges after a Short or Long Rest)"
        damage_type: DamageType = request_damage_type(index_name='fire')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8'))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='sphere', size=10)
        sa: SpecialAbility = SpecialAbility(name='Spit Fire',
                                                desc='',
                                                damages=damages,
                                                dc_type='dex',
                                                dc_value=11,
                                                dc_success='half',
                                                recharge_on_roll=7,
                                                area_of_effect=area_of_effect)
        special_abilities.append(sa)
    elif name == "Yuan-ti Malison":
        # Multiattack
        # "The yuan-ti makes two ranged attacks or two melee attacks, but can use its bite only once."
        # Melee attacks
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        multi_attack_action_2 = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_2] * 2)
        actions.append(action)
        # Ranged attack
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=2))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        multi_attack_action = Action(name='Longbow', desc='', type=ActionType.RANGED, attack_bonus=4, damages=damages, normal_range=150, long_range=600)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Spellcasting
        caster_level = 3
        dc_type = 'cha'
        dc_value = 13
        spells = ['animal-friendship', 'suggestion']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 0, 99, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=0)
    elif name == "Yuan-ti Broodguard":
        # Multiattack
        # "The broodguard makes one Bite attack and two Claw attacks."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=2))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        multi_attack_action_2 = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
    elif name == "Ogre Chain Brute":
        # Melee attack
        # Fist
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d4', bonus=4))]
        action = Action(name='Fist', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
        # Chain Smash (special attack)
        # Todo Condition stunned on failed saving throw
        # "{@atk mw} {@hit 6} to hit, reach 10 ft., one target.
        # {@h}13 ({@damage 2d8 + 4}) bludgeoning damage, and the target must make a {@dc 14} Constitution saving throw or be {@condition stunned} for 1 minute.
        # The target repeats the saving throw if it takes damage and at the end of each of its turns, ending the effect on itself on a success."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=4))]
        dc_type = 'con'
        dc_value = 14
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=10)
        sa: SpecialAbility = SpecialAbility(name='Chain Smash',
                                                desc='',
                                                damages=damages,
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='none',
                                                area_of_effect=area_of_effect,
                                                effects=[Condition('stunned')],
                                                recharge_on_roll=1)
        special_abilities.append(sa)
        # Chain Sweep
        # "The ogre swings its chain, and every creature within 10 feet of it must make a {@dc 14} Dexterity saving throw.
        # On a failed saving throw, a creature takes 8 ({@damage 1d8 + 4}) bludgeoning damage and is knocked {@condition prone}.
        # On a successful save, the creature takes half as much damage and isn't knocked {@condition prone}."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=4))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=10)
        sa: SpecialAbility = SpecialAbility(name='Chain Smash',
                                                desc='',
                                                damages=damages,
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='half',
                                                area_of_effect=area_of_effect,
                                                effects=[Condition('prone')],
                                                recharge_on_roll=1)
        special_abilities.append(sa)
    elif name == "Young Kruthik":
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        action = Action(name='Stab', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
    elif name == "Adult Kruthik":
        # Multiattack
        # "The kruthik makes two Stab or Spike attacks."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=3))]
        multi_attack_action = Action(name='Stab', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        multi_attack_action = Action(name='Spike', desc='', type=ActionType.RANGED, attack_bonus=5, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Gnoll":
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=2))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=2))]
        action = Action(name='Spear', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=20, long_range=60)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=1))]
        action = Action(name='Longbow', desc='', type=ActionType.RANGED, attack_bonus=3, damages=damages, normal_range=150, long_range=600)
        actions.append(action)
    elif name == "Maw Demon":
        # Melee attack
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=2))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        actions.append(action)
        # Disgorge (special attack)
        # "The demon vomits in a 15-foot cube.
        # Each creature in that area must succeed on a {@dc 11} Dexterity saving throw or take 11 ({@damage 2d10}) acid damage and fall {@condition prone} in the spew."
        damage_type: DamageType = request_damage_type(index_name='acid')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d10'))]
        dc_type = 'dex'
        dc_value = 11
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cube', size=15)
        sa: SpecialAbility = SpecialAbility(name='Disgorge',
                                                desc='',
                                                damages=damages,
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='none',
                                                area_of_effect=area_of_effect,
                                                effects=[Condition('prone')],
                                                recharge_on_roll=1)
        special_abilities.append(sa)
    elif name == "Yuan-ti Pit Master":
        # Multiattack
        # "The yuan-ti makes three Bite attacks or two Spectral Fangs attacks."
        # Melee attack
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=3))]
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='2d6'))]
        multi_attack_action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
        # Spectral Fangs
        damage_type: DamageType = request_damage_type(index_name='poison')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='3d8', bonus=3))]
        multi_attack_action = Action(name='Spectral Fangs', desc='', type=ActionType.RANGED, attack_bonus=6, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Merrshaulk's Slumber (1/Day) (special attack)
        # "The yuan-ti targets up to five creatures that it can see within 60 feet of it.
        # Each target must succeed on a {@dc 13} Constitution saving throw or fall into a magical sleep and be {@condition unconscious} for 10 minutes.
        # A sleeping target awakens if it takes damage or if someone uses an action to shake or slap it awake.
        # This magical sleep has no effect on a creature immune to being {@condition charmed}."
        dc_type = 'con'
        dc_value = 13
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cube', size=60)
        sa: SpecialAbility = SpecialAbility(name='Disgorge',
                                                desc='',
                                                damages=[],
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='none',
                                                area_of_effect=area_of_effect,
                                                effects=[Condition('unconscious')],
                                                recharge_on_roll=1)
        special_abilities.append(sa)
        # Spellcasting
        caster_level = 3
        dc_type = 'cha'
        dc_value = 13
        spells = ['animal-friendship', 'guidance', 'mage-hand', 'message']
        spells +=  ['hold-person', 'invisibility']
        spells += ['suggestion']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 99, 99, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=0)
    elif name == "Kruthik Hive Lord":
        # Multiattack
        # "The kruthik makes two Stab or Spike attacks."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d10', bonus=4))]
        multi_attack_action = Action(name='Stab', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d6', bonus=4))]
        multi_attack_action = Action(name='Spike', desc='', type=ActionType.RANGED, attack_bonus=6, damages=damages, normal_range=30, long_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # "Acid Spray {@recharge 5}" (special attack)
        # "The kruthik sprays acid in a 15-foot cone.
        # Each creature in that area must make a {@dc 14} Dexterity saving throw, taking 22 ({@damage 4d10}) acid damage on a failed save, or half as much damage on a successful one."
        damage_type: DamageType = request_damage_type(index_name='acid')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d10'))]
        dc_type = 'dex'
        dc_value = 14
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=15)
        sa: SpecialAbility = SpecialAbility(name='Acid Spray',
                                                desc='',
                                                damages=damages,
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='half',
                                                area_of_effect=area_of_effect,
                                                recharge_on_roll=5)
        special_abilities.append(sa)
    elif name == "Frost giant":
        # Multiattack
        # "The giant makes two greataxe attacks."
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='3d12', bonus=6))]
        multi_attack_action = Action(name='Greataxe', desc='', type=ActionType.MELEE, attack_bonus=9, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Single attack
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d10', bonus=6))]
        action = Action(name='Rock', desc='', type=ActionType.RANGED, attack_bonus=9, damages=damages, normal_range=60, long_range=240)
        actions.append(action)
    elif name == "Bugbear Chief":
        # Multiattack
        # "The bugbear makes two melee attacks."
        # Morningstar (Melee)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=3))]
        multi_attack_action = Action(name='Morningstar', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Javelin (Melee)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        multi_attack_action = Action(name='Javelin', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Javelin (Ranged)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        action = Action(name='Javelin', desc='', type=ActionType.RANGED, attack_bonus=5, damages=damages, normal_range=30, long_range=120)
        actions.append(action)
    elif name == "Ogre Zombie":
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8', bonus=4))]
        action = Action(name='Morningstar', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
    elif name == "Hobgoblin Devastator":
        # Multiattack
        # "The hobgoblin makes two Quarterstaff or Devastating Bolt attacks."
        # "Quarterstaff"
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=1))]
        damage_type: DamageType = request_damage_type(index_name='force')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='3d8'))]
        multi_attack_action = Action(name='Quarterstaff', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages, normal_range=5, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # "Devastating Bolt"
        # TODO Condition prone
        damage_type: DamageType = request_damage_type(index_name='force')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d8', bonus=3))]
        multi_attack_action = Action(name='Devastating Bolt', desc='', type=ActionType.RANGED, attack_bonus=5, damages=damages, normal_range=5, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Spellcasting
        caster_level = 2
        dc_type = 'int'
        dc_value = 13
        spells = ['mage-hand', 'prestidigitation', 'fireball', 'fly', 'fog-cloud', 'gust-of-wind', 'lightning-bolt']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 1, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 5,
                                                    ability_modifier=5)
    elif name == "Stone Giant":
        # Multiattack
        # "The giant makes two greataxe attacks."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='3d8', bonus=6))]
        multi_attack_action = Action(name='Greataxe', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages, normal_range=15)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Single attack
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d10', bonus=6))]
        action = Action(name='Rock', desc='', type=ActionType.RANGED, attack_bonus=9, damages=damages, normal_range=60, long_range=240)
        actions.append(action)
    elif name == "Orc Hand of Yurtrus":
        # Melee attack
        damage_type: DamageType = request_damage_type(index_name='necrotic')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d8'))]
        action = Action(name='Touch of the White Hand', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages, normal_range=5)
        actions.append(action)
        # Spellcasting
        caster_level = 4
        dc_type = 'wis'
        dc_value = 12
        spells = ['guidance', 'mending', 'resistance', 'thaumaturgy', 'bane', 'detect magic', 'inflict wounds', 'protection from evil and good', 'blindness/deafness', 'silence']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[4, 3],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + 2,
                                                    ability_modifier=2)
    elif name == "Orc Nurtured One of Yurtrus":
        damage_type: DamageType = request_damage_type(index_name='slashing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2)), Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        action = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages, normal_range=5)
        actions.append(action)
        # TODO "Corrupted Vengeance"
        # "The orc reduces itself to 0 hit points, triggering its Corrupted Carrier trait."
    elif name == "Blue Dragon Wyrmling":
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d10', bonus=3))]
        damage_type: DamageType = request_damage_type(index_name='lighting')
        damages += [Damage(type=damage_type, dd=DamageDice(dice='1d6'))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='lighting')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='4d10'))]
        dc_type = 'dex'
        dc_value = 12
        area_of_effect: AreaOfEffect = AreaOfEffect(type='line', size=30)
        sa: SpecialAbility = SpecialAbility(name='Lightning Breath',
                                                desc='',
                                                damages=damages,
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='half',
                                                area_of_effect=area_of_effect,
                                                recharge_on_roll=5)
        special_abilities.append(sa)
    elif name == "Kobold Scale Sorcerer":
        # Multiattack
        # "The kobold makes two Dagger or Chromatic Bolt attacks. It can replace one attack with a use of Spellcasting."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d4', bonus=2))]
        multi_attack_action = Action(name='Dagger', desc='', type=ActionType.MIXED, attack_bonus=4, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        for damage_type_name in ['acid', 'cold', 'fire', 'lightning', 'poison', 'thunder']:
            damage_type: DamageType = request_damage_type(index_name=damage_type_name)
            damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=2))]
            multi_attack_action = Action(name='Chromatic Bolt', desc='', type=ActionType.RANGED, attack_bonus=4, damages=damages, normal_range=60)
            action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
            actions.append(action)
        # Spellcasting
        caster_level = 2
        dc_type = 'cha'
        dc_value = 12
        spells = ['mage-hand', 'prestidigitation', 'charm-person', 'fog-cloud', 'levitate']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 1, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=2)
    elif name == "Flind":
        # Multiattack
        # "The flind makes one Flail of Chaos attack, one Flail of Pain attack, and one Flail of Paralysis attack, or it makes three Longbow attacks."
        damage_type: DamageType = request_damage_type(index_name='bludgeoning')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d10', bonus=5))]
        multi_attack_action_1 = Action(name='Flail of Chaos', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages, normal_range=10)
        damage_type: DamageType = request_damage_type(index_name='psychic')
        multi_attack_action_2 = Action(name='Flail of Pain', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages + [Damage(type=damage_type, dd=DamageDice(dice='3d10'))], normal_range=10)
        multi_attack_action_3 = Action(name='Flail of Paralysis', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages, normal_range=10)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_3])
        actions.append(action)
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d8', bonus=2))]
        multi_attack_action = Action(name='Longbow', desc='', type=ActionType.RANGED, attack_bonus=6, damages=damages, normal_range=150, long_range=600)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
    elif name == "Young Brass Dragon":
        # Multiattack
        # "The dragon makes three attacks: one with its bite and two with its claws."
        damage_type: DamageType = request_damage_type(index_name='piercing')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='1d10', bonus=5))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MIXED, attack_bonus=7, damages=damages, normal_range=10)
        multi_attack_action_2 = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages, normal_range=5)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        # "Breath Weapons {@recharge 5}"
        # "The dragon uses one of the following breath weapons."
        damage_type: DamageType = request_damage_type(index_name='fire')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='12d6'))]
        dc_type = 'dex'
        dc_value = 14
        area_of_effect: AreaOfEffect = AreaOfEffect(type='line', size=40)
        sa: SpecialAbility = SpecialAbility(name='Fire Breath',
                                                desc='',
                                                damages=damages,
                                                dc_type=dc_type,
                                                dc_value=dc_value,
                                                dc_success='half',
                                                area_of_effect=area_of_effect,
                                                recharge_on_roll=5)
        special_abilities.append(sa)
        # TODO  "Sleep Breath"
    elif name == "Efreeti":
        # Multiattack
        # "The efreeti makes two scimitar attacks or uses its Hurl Flame twice."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d6', bonus=6))]
        damages +=  [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='2d6'))]
        multi_attack_action = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=10, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='5d6'))]
        multi_attack_action = Action(name='Hurl Flame', desc='', type=ActionType.MIXED, attack_bonus=7, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # "Innate Spellcasting"
        # "The efreeti's innate spellcasting ability is Charisma (spell save {@dc 15}, {@hit 7} to hit with spell attacks).
        # It can innately cast the following spells, requiring no material components:"
        caster_level = 3
        dc_type = 'cha'
        dc_value = 15
        spells = ['detect magic', 'enlarge/reduce', 'tongues', 'conjure elemental (fire elemental only)', 'gaseous form', 'invisibility', 'major image', 'plane shift', 'wall of fire']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[5, 5, 0, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=2)

    elif name == "Fire Elemental":
        # Multiattack
        # "The elemental makes two touch attacks."
        #  TODO If the target is a creature or a flammable object, it ignites.
        #  Until a creature takes an action to douse the fire, the target takes 5 ({@damage 1d10}) fire damage at the start of each of its turns."
        damage_type: DamageType = request_damage_type(index_name='fire')
        damages: List[Damage] = [Damage(type=damage_type, dd=DamageDice(dice='2d6', bonus=3))]
        multi_attack_action = Action(name='Touch', desc='', type=ActionType.MIXED, attack_bonus=6, damages=damages, normal_range=5)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Fire Giant":
        # Multiattack
        # "The giant makes two greatsword attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='6d6', bonus=7))]
        multi_attack_action = Action(name='Greatsword', desc='', type=ActionType.MIXED, attack_bonus=11, damages=damages, normal_range=10)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='4d10', bonus=7))]
        action = Action(name='Rock', desc='', type=ActionType.RANGED, attack_bonus=11, damages=damages, normal_range=60, long_range=240)
        actions.append(action)
    elif name == "Stone Giant Dreamwalker":
        # Multiattack
        # "The giant makes two Greatclub or Rock attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='4d8', bonus=6))]
        multi_attack_action = Action(name='Greatclub', desc='', type=ActionType.MIXED, attack_bonus=10, damages=damages, normal_range=15)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='3d10', bonus=6))]
        multi_attack_action = Action(name='Rock', desc='', type=ActionType.RANGED, attack_bonus=10, damages=damages, normal_range=60, long_range=240)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Owlbear":
        # Multiattack
        # "The owlbear makes two attacks: one with its beak and one with its claws."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d10', bonus=5))]
        multi_attack_action_1 = Action(name='Beak', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages, normal_range=5)
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d8', bonus=5))]
        multi_attack_action_2 = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages, normal_range=5)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
    elif name == "Orc Claw of Luthic":
        # Multiattack
        # "The orc makes two claw attacks,
        # TODO or four claw attacks if it has fewer than half of its hit points remaining."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='1d8', bonus=2))]
        multi_attack_action = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages, normal_range=5)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Spellcasting
        # "The orc is a 5th-level spellcaster.
        # Its spellcasting ability is Wisdom (spell save {@dc 12}, {@hit 4} to hit with spell attacks).
        # The orc has the following cleric spells prepared:"
        caster_level = 5
        dc_type = 'wis'
        dc_value = 12
        spells = ['guidance', 'mending', 'resistance', 'thaumaturgy', 'bane', 'cure wounds', 'guiding bolt', 'augury', 'warding bond', 'bestow curse', 'create food and water']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[4, 3, 2, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=4)
    elif name == "Venom Troll":
        # Multiattack
        # "The troll makes one Bite attack and two Claw attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6', bonus=4))]
        damages += [Damage(type=request_damage_type('poison'), dd=DamageDice(dice='1d8'))]
        # TODO the creature is {@condition poisoned} until the start of the troll's next turn.
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d6', bonus=4))]
        damages += [Damage(type=request_damage_type('poison'), dd=DamageDice(dice='1d8'))]
        multi_attack_action_2 = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        # "Venom Spray {@recharge}"
        # "The troll slices itself with a claw, releasing a spray of poison in a 15-foot cube.
        # The troll takes 7 ({@damage 2d6}) slashing damage (this damage can't be reduced in any way).
        # Each creature in the area must make a {@dc 16} Constitution saving throw.
        # TODO On a failed save, a creature takes 18 ({@damage 4d8}) poison damage and is {@condition poisoned} for 1 minute.
        # On a successful save, the creature takes half as much damage and isn't {@condition poisoned}. A {@condition poisoned} creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d6'))]
        sa: SpecialAbility = SpecialAbility(name='Venom Spray {@recharge}',
                                                desc='',
                                                damages=damages,
                                                dc_type='con',
                                                dc_value=16,
                                                dc_success='half',
                                                recharge_on_roll=1)
        special_abilities.append(sa)
    elif name == "Yuan-ti Nightmare Speaker":
        # Spellcasting
        caster_level = 3
        dc_type = 'cha'
        dc_value = 13
        spells = ['animal friendship', 'mage hand', 'message', 'prestidigitation', 'suggestion', 'darkness', 'fear']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[0, 1, 1, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=2)
        # Multiattack
        # "The yuan-ti makes one Constrict attack and one Scimitar attack, or it makes two Spectral Fangs attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='1d8', bonus=3))]
        multi_attack_action_1 = Action(name='Constrict', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=10)
        # TODO target is {@condition grappled} (escape {@dc 14}) if it is a Large or smaller creature.
        # TODO Until this grapple ends, the target is {@condition restrained}. The yuan-ti can constrict only one creature at a time."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='1d6', bonus=3))]
        multi_attack_action_2 = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('necrotic'), dd=DamageDice(dice='3d8', bonus=3))]
        multi_attack_action = Action(name='Spectral Fangs', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # "Invoke Nightmare (Recharges after a Short or Long Rest)"
        # "The yuan-ti taps into the nightmares of one creature it can see within 60 feet of it and creates an illusory, immobile manifestation of the creature's deepest fears, visible only to that creature.",
        # TODO "The target must make a {@dc 13} Intelligence saving throw. On a failed save, the target takes 22 ({@damage 4d10}) psychic damage and is {@condition frightened} of the manifestation, believing it to be real.
        # TODO The yuan-ti must concentrate to maintain the illusion (as if {@status concentration||concentrating} on a spell), which lasts for up to 1 minute and can't be harmed.
        # TODO The target can repeat the saving throw at the end of each of its turns, ending the illusion on a success or taking 11 ({@damage 2d10}) psychic damage on a failure."
        damages =  [Damage(type=request_damage_type('psychic'), dd=DamageDice(dice='4d10'))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='line', size=60)
        sa: SpecialAbility = SpecialAbility(name='Invoke Nightmare',
                                                desc='',
                                                damages=damages,
                                                area_of_effect=area_of_effect,
                                                dc_type='int',
                                                dc_value=13,
                                                dc_success='half',
                                                recharge_on_roll=1)
        special_abilities.append(sa)
    elif name == "Kobold Dragonshield":
        # Multiattack
        # "The kobold makes two Spear attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d8', bonus=1))]
        multi_attack_action = Action(name='Spear', desc='', type=ActionType.MELEE, attack_bonus=3, damages=damages, normal_range=5)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6', bonus=1))]
        multi_attack_action = Action(name='Spear', desc='', type=ActionType.RANGED, attack_bonus=3, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.RANGED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Lamia":
        # "Innate Spellcasting"
        # "The lamia's innate spellcasting ability is Charisma (spell save {@dc 13}). It can innately cast the following spells, requiring no material components."
        caster_level = 3
        dc_type = 'cha'
        dc_value = 13
        spells = ['disguise self', 'major image', 'geas', 'charm person', 'mirror image', 'scrying', 'suggestion']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 0, 1, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=4)
        # Multiattack
        # "The lamia makes two attacks: one with its claws and one with its dagger or Intoxicating Touch."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d10', bonus=3))]
        multi_attack_action_1 = Action(name='Claws', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages, normal_range=5)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d4', bonus=3))]
        multi_attack_action_2 = Action(name='Dagger', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages, normal_range=5)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        # TODO "Intoxicating Touch"
        # The target is magically cursed for 1 hour. Until the curse ends, the target has disadvantage on Wisdom saving throws and all ability checks."
    elif name == "Jackalwere":
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d4', bonus=2))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages, normal_range=5)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Scimitar', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages, normal_range=5)
        actions.append(action)
        # Special ability Sleep Gaze
        # TODO "The jackalwere gazes at one creature it can see within 30 feet of it.
        # The target must make a {@dc 10} Wisdom saving throw.
        # On a failed save, the target succumbs to a magical slumber, falling {@condition unconscious} for 10 minutes or until someone uses an action to shake the target awake.
        # A creature that successfully saves against the effect is immune to this jackalwere's gaze for the next 24 hours.
        # Undead and creatures immune to being {@condition charmed} aren't affected by it."
        # sa: SpecialAbility = SpecialAbility(name='Sleep Gaze',
        #                                         desc='',
        #                                         dc_type='wis',
        #                                         dc_value=10,
        #                                         dc_success='half',
        #                                         recharge_on_roll=1)
    elif name == "Gnoll Flesh Gnawer":
        # Multiattack
        # "The gnoll makes one Bite attack and two Shortsword attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d4', bonus=2))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6', bonus=2))]
        multi_attack_action_2 = Action(name='Shortsword', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        # TODO Sudden Rush
        # "Until the end of the turn, the gnoll's speed increases by 60 feet and it doesn't provoke {@action opportunity attack||opportunity attacks}."
        # Bonus action "Rampage"
        # TODO "After the gnoll reduces a creature to 0 hit points with a melee attack on its turn, the gnoll moves up to half its speed and makes a Bite attack."
    elif name == "Horned Devil":
        # Multiattack
        # "The devil makes three melee attacks: two with its fork and one with its tail. It can use Hurl Flame in place of any melee attack."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='2d8', bonus=6))]
        multi_attack_action_1 = Action(name='Fork', desc='', type=ActionType.MIXED, attack_bonus=10, damages=damages, normal_range=10)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d8', bonus=6))]
        # TODO If the target is a creature other than an undead or a construct, it must succeed on a {@dc 17} Constitution saving throw or lose 10 ({@dice 3d6}) hit points at the start of each of its turns due to an infernal wound. Each time the devil hits the wounded target with this attack, the damage dealt by the wound increases by 10 ({@dice 3d6}).
        # Any creature can take an action to stanch the wound with a successful {@dc 12} Wisdom ({@skill Medicine}) check. The wound also closes if the target receives magical healing."
        multi_attack_action_2 = Action(name='Tail', desc='', type=ActionType.MIXED, attack_bonus=10, damages=damages, normal_range=10)
        damages: List[Damage] = [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='4d6'))]
        # TODO If the target is a flammable object that isn't being worn or carried, it also catches fire.
        multi_attack_action_3 = Action(name='Hurl Flame', desc='', type=ActionType.MIXED, attack_bonus=7, damages=damages, normal_range=150)
        attack_choices = [[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2]]
        attack_choices.append([multi_attack_action_1, multi_attack_action_2, multi_attack_action_3])
        attack_choices.append([multi_attack_action_1, multi_attack_action_3, multi_attack_action_2])
        attack_choices.append([multi_attack_action_3, multi_attack_action_2, multi_attack_action_2])
        for multi_attack_choice in attack_choices:
            action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=multi_attack_choice)
            actions.append(action)
    elif name in ["Bearded Devil", "Barbed Devil"]:
        # Multiattack
        # "The devil makes three melee attacks: one with its tail and two with its claws. Alternatively, it can use Hurl Flame twice."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='2d6', bonus=3))]
        multi_attack_action_1 = Action(name='Tail', desc='', type=ActionType.MIXED, attack_bonus=6, damages=damages)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6', bonus=3))]
        multi_attack_action_2 = Action(name='Claw', desc='', type=ActionType.MIXED, attack_bonus=6, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='3d6'))]
        # TODO If the target is a flammable object that isn't being worn or carried, it also catches fire.
        multi_attack_action_3 = Action(name='Hurl Flame', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=150)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_3] * 2)
        actions.append(action)
    elif name == "Young Blue Dragon":
        # Multiattack
        # "The dragon makes three attacks: one with its bite and two with its claws."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='2d10', bonus=5))]
        damages += [Damage(type=request_damage_type('lightning'), dd=DamageDice(dice='1d10'))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages, normal_range=10)
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d6', bonus=5))]
        multi_attack_action_2 = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=9, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        # Special ability
        # "Lightning Breath {@recharge 5}"
        damages: List[Damage] = [Damage(type=request_damage_type('lightning'), dd=DamageDice(dice='10d10'))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='line', size=60)
        sa: SpecialAbility = SpecialAbility(name='Lightning Breath',
                                                desc='',
                                                dc_type='dex',
                                                dc_value=16,
                                                damages=damages,
                                                area_of_effect=area_of_effect,
                                                dc_success='half',
                                                recharge_on_roll=5)
        special_abilities.append(sa)
    elif name == "Warhorse Skeleton":
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='2d6', bonus=4))]
        action = Action(name='Hooves', desc='', type=ActionType.MELEE, attack_bonus=6, damages=damages)
        actions.append(action)
    elif name == 'Bone Devil':
        # Multiattack
        # "The devil makes three attacks: two with its claws and one with its sting."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='1d8', bonus=4))]
        multi_attack_action_1 = Action(name='Claw', desc='', type=ActionType.MIXED, attack_bonus=8, damages=damages, normal_range=10)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='2d8', bonus=4))]
        damages += [Damage(type=request_damage_type('poison'), dd=DamageDice(dice='5d6'))]
        multi_attack_action_2 = Action(name='Sting', desc='', type=ActionType.MIXED, attack_bonus=8, damages=damages, normal_range=10)
        # TODO the target must succeed on a {@dc 14} Constitution saving throw or become {@condition poisoned} for 1 minute.
        #  The target can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
    elif name == "Spined Devil":
        # Multiattack
        # "The devil makes two attacks: one with its bite and one with its fork or two with its tail spines."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d4'))]
        multi_attack_action_1 = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=2, damages=damages)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6'))]
        multi_attack_action_2 = Action(name='Fork', desc='', type=ActionType.MELEE, attack_bonus=2, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d4', bonus=2))]
        damages += [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='1d6'))]
        multi_attack_action = Action(name='Tail Spine', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages, normal_range=20, long_range=80)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Deathlock Wight":
        # Spellcasting
        caster_level = 1
        dc_type = 'cha'
        dc_value = 13
        spells = ['detect magic', 'disguise self', 'mage armor', 'fear', 'hold person']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=3)
        # Multiattack
        # "The deathlock makes two Life Drain or Grave Bolt attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('necrotic'), dd=DamageDice(dice='1d8', bonus=2))]
        multi_attack_action = Action(name='Life Drain', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        # TODO The target must succeed on a {@dc 13} Constitution saving throw, or its hit point maximum is reduced by an amount equal to the damage taken.
        #  This reduction lasts until the target finishes a long rest. The target dies if its hit point maximum is reduced to 0."
        #  A Humanoid slain by this attack rises 24 hours later as a {@creature zombie} under the deathlock's control, unless the Humanoid is restored to life or its body is destroyed.
        #  The deathlock can have no more than twelve zombies under its control at one time."
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('necrotic'), dd=DamageDice(dice='2d8', bonus=3))]
        multi_attack_action = Action(name='Grave Bolt', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
    elif name == "Hell Hound":
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d8', bonus=3))]
        damages += [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='2d6'))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        actions.append(action)
        # Special ability
        # "Fire Breath {@recharge 5}"
        damages: List[Damage] = [Damage(type=request_damage_type('fire'), dd=DamageDice(dice='6d6'))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=15)
        sa: SpecialAbility = SpecialAbility(name='Fire Breath',
                                                desc='',
                                                dc_type='dex',
                                                dc_value=12,
                                                damages=damages,
                                                area_of_effect=area_of_effect,
                                                dc_success='half',
                                                recharge_on_roll=5)
        special_abilities.append(sa)
    elif name == "Conjurer":
        # Spellcasting
        caster_level = 1
        dc_type = 'int'
        dc_value = 14
        spells = ['dancing lights', 'mage hand', 'prestidigitation', 'fireball', 'mage armor', 'unseen servant', 'fly', 'stinking cloud', 'web']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 1, 0, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=6)
        # Multiattack
        # "The conjurer makes three Arcane Burst attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('force'), dd=DamageDice(dice='3d10', bonus=3))]
        multi_attack_action = Action(name='Arcane Burst', desc='', type=ActionType.MIXED, attack_bonus=8, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 3)
        actions.append(action)
    elif name == "Alhoon":
        # Spellcasting
        caster_level = 1
        dc_type = 'int'
        dc_value = 16
        spells = ['dancing lights', 'detect magic', 'detect thoughts', 'disguise self', 'mage hand', 'prestidigitation']
        spells += ['dominate monster', 'globe of invulnerability', 'invisibility', 'modify memory', 'plane shift', 'wall of force']
        if spells:
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=[1, 0, 0, 0, 0, 0, 0, 0, 0],
                                                    learned_spells=list(filter(None, [request_spell(s) for s in spells])),
                                                    dc_type=dc_type,
                                                    dc_value=dc_value,
                                                    ability_modifier=8)
        # Multiattack
        # "The alhoon makes two Chilling Grasp or Arcane Bolt attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('cold'), dd=DamageDice(dice='4d6'))]
        multi_attack_action = Action(name='Chilling Grasp', desc='', type=ActionType.MELEE, attack_bonus=8, damages=damages)
        # TODO  the alhoon regains 14 hit points.
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('force'), dd=DamageDice(dice='8d6'))]
        multi_attack_action = Action(name='Arcane Bolt', desc='', type=ActionType.MIXED, attack_bonus=8, damages=damages, normal_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # Special ability
        # "Mind Blast {@recharge 5}"
        damages: List[Damage] = [Damage(type=request_damage_type('psychic'), dd=DamageDice(dice='4d8', bonus=4))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=60)
        sa: SpecialAbility = SpecialAbility(name='Mind Blast',
                                                desc='',
                                                dc_type='int',
                                                dc_value=16,
                                                damages=damages,
                                                area_of_effect=area_of_effect,
                                                dc_success='half',
                                                recharge_on_roll=5)
        special_abilities.append(sa)
        # Reaction
        # TODO Negate Spell (3/Day)
        #  "The alhoon targets one creature it can see within 60 feet of it that is casting a spell.
        #  If the spell is 3rd level or lower, the spell fails, but any spell slots or charges are not wasted."
    elif name == "Young Silver Dragon":
        # Multiattack
        # "The dragon makes three attacks: one with its bite and two with its claws."
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='2d10', bonus=6))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MIXED, attack_bonus=10, damages=damages, normal_range=10)
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d6', bonus=6))]
        multi_attack_action_2 = Action(name='Claw', desc='', type=ActionType.MELEE, attack_bonus=9, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2, multi_attack_action_2])
        actions.append(action)
        # Special ability
        # "Breath Weapons {@recharge 5}"
        damages: List[Damage] = [Damage(type=request_damage_type('cold'), dd=DamageDice(dice='12d8'))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=30)
        sa: SpecialAbility = SpecialAbility(name='Cold Breath',
                                                desc='',
                                                dc_type='dex',
                                                dc_value=17,
                                                damages=damages,
                                                area_of_effect=area_of_effect,
                                                dc_success='half',
                                                recharge_on_roll=5)
        special_abilities.append(sa)
        # TODO  "The dragon exhales paralyzing gas in a 30-foot cone.
        #  Each creature in that area must succeed on a {@dc 17} Constitution saving throw or be {@condition paralyzed} for 1 minute.
        #  A creature can repeat the saving throw at the end of each of its turns, ending the effect on itself on a success."
        # damages: List[Damage] = [Damage(type=request_damage_type('cold'), dd=DamageDice(dice='12d8'))]
        # area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=30)
        # sa: SpecialAbility = SpecialAbility(name='Paralyzing Breath',
        #                                         desc='',
        #                                         dc_type='dex',
        #                                         dc_value=17,
        #                                         damages=damages,
        #                                         area_of_effect=area_of_effect,
        #                                         dc_success='half',
        #                                         recharge_on_roll=5)
        # special_abilities.append(sa)
    elif name == "Orc Blade of Ilneval":
        # Multiattack
        # "The orc makes two melee attacks with its longsword or two ranged attacks with its javelins.
        # If Ilneval's Command is available to use, the orc can use it after these attacks."
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d8', bonus=3))]
        multi_attack_action = Action(name='Longsword', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6', bonus=3))]
        multi_attack_action = Action(name='Javelin', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=30, long_range=120)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # TODO "Ilneval's Command {@recharge 4}"
        #  "Up to three allied orcs within 120 feet of this orc that can hear it can use their reactions to each make one weapon attack."
    elif name == "Orc Red Fang of Shargaas":
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='3d6', bonus=3))]
        multi_attack_action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=5, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='3d4', bonus=3))]
        multi_attack_action = Action(name='Dart', desc='', type=ActionType.MIXED, attack_bonus=5, damages=damages, normal_range=20, long_range=60)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action] * 2)
        actions.append(action)
        # TODO "Veil of Shargaas (Recharges after a Short or Long Rest)"
        #  "The orc casts {@spell darkness} without any components. Wisdom is its spellcasting ability."
    elif name == "Giant Bat":
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d6', bonus=2))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=4, damages=damages)
        actions.append(action)
    elif name == "Tanarukk":
        damages: List[Damage] = [Damage(type=request_damage_type('piercing'), dd=DamageDice(dice='1d8', bonus=4))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        damages: List[Damage] = [Damage(type=request_damage_type('slashing'), dd=DamageDice(dice='2d6', bonus=4))]
        multi_attack_action_2 = Action(name='Greatsword', desc='', type=ActionType.MELEE, attack_bonus=7, damages=damages)
        action = Action(name='Multiattack', desc='', type=ActionType.MELEE, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
    elif name == "Fomorian":
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='3d8', bonus=6))]
        multi_attack_action_1 = Action(name='Bite', desc='', type=ActionType.MIXED, attack_bonus=9, damages=damages, normal_range=15)
        damages: List[Damage] = [Damage(type=request_damage_type('psychic'), dd=DamageDice(dice='6d8'))]
        area_of_effect: AreaOfEffect = AreaOfEffect(type='cone', size=60)
        multi_attack_action_2: SpecialAbility = SpecialAbility(name='Evil Eye',
                                                desc='',
                                                dc_type='cha',
                                                dc_value=14,
                                                damages=damages,
                                                area_of_effect=area_of_effect,
                                                dc_success='half',
                                                recharge_on_roll=1)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1, multi_attack_action_2])
        actions.append(action)
        action = Action(name='Multiattack', desc='', type=ActionType.MIXED, multi_attack=[multi_attack_action_1] * 2)
        actions.append(action)
        # TODO Curse of the Evil Eye (Recharges after a Short or Long Rest)
        #  "With a stare, the fomorian uses Evil Eye, but on a failed save, the creature is also cursed with magical deformities.
        #  While deformed, the creature has its speed halved and has disadvantage on ability checks, saving throws, and attacks based on Strength or Dexterity.",
        #  The transformed creature can repeat the saving throw whenever it finishes a long rest, ending the effect on a success."
    elif name == "Boggle":
        damages: List[Damage] = [Damage(type=request_damage_type('bludgeoning'), dd=DamageDice(dice='1d6', bonus=-1))]
        action = Action(name='Bite', desc='', type=ActionType.MELEE, attack_bonus=1, damages=damages, normal_range=15)
        actions.append(action)
        # TODO Oil Puddle
        # Slippery Oil
        # "Any non-boggle creature that enters the puddle or starts its turn there must succeed on a {@dc 11} Dexterity saving throw or fall {@condition prone}."
        # Sticky Oil
        # "Any non-boggle creature that enters the puddle or starts its turn there must succeed on a {@dc 11} Strength saving throw or be {@condition restrained}.
        # On its turn, a creature can use an action to try to extricate itself, ending the effect and moving into the nearest unoccupied space of its choice with a successful {@dc 11} Strength check."
    return actions, special_abilities, spell_caster

def remove_pattern(string, pattern):
    return re.sub(pattern, '', string).rstrip()

def get_monster_data(list_data, name):
    # monster_data = []
    for monster in list_data:
        cleaned_name = remove_pattern(monster['name'], r'\(.*\)')
        # if remove_pattern(cleaned_name.lower(), r'(.*)') == name.lower():
        if cleaned_name.lower() == name.lower():
            # monster_data.append({'name': cleaned_name})
            return monster
        elif name == 'Illusionist' and cleaned_name == 'Illusionist Wizard':
            return monster

def request_monster_other(name: str) -> Optional[Monster]:
    """
    Send a request to local database for a monster's characteristic
    :param monster_name: name of the monster
    :return: Monster object
    """
    with open(resource_path("maze/other_monsters/bestiary-sublist-data.json"), "r") as f:
        list_data = json.loads(f.read())
        # monster_data = [monster for monster in list_data if monster['name'].lower() == name.lower()]
        monster_data = get_monster_data(list_data, name)
        if not monster_data:
            return None
        data = monster_data

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
        # print(f'{name}: {xp} XP')
        speed_dict = data['speed']
        if 'fly' in speed_dict:
            if isinstance(speed_dict['fly'], dict):
                speed = speed_dict['fly']['number']
            else:
                speed = speed_dict['fly']
        elif 'walk' in speed_dict:
            speed = speed_dict['walk']
        else:
            speed = 30
        type: str = 'fly' if 'fly' in data['speed'] else 'walk'
        # print(f'{name} speed: {speed} type: {type}')

        return Monster(
                       index=name.lower().replace(' ', '-'),
                       name=data['name'],
                       abilities=Abilities(str=data['str'], dex=data['dex'], con=data['con'],
                                           int=data['int'], wis=data['wis'], cha=data['cha']),
                       proficiencies=proficiencies,
                       armor_class=ac,
                       hit_points=hit_dice.roll(),
                       hit_dice=data['hp']['formula'],
                       speed=speed,
                       xp=int(xp),
                       challenge_rating=parse_challenge_rating(data['cr']),
                       actions=actions,
                       sc=spell_caster,
                       sa=special_abilities)


def request_spell(index_name: str) -> Optional[Spell]:
    """
    Send a request to local database for a spell's characteristic
    :param index_name: name of the monster
    :return: Spell object
    """
    try:
        data = _load_json_data('spells', index_name)
    except (FileNotFoundError, Exception):
        return None

    allowed_classes: List[str] = [c['index'] for c in data['classes']]

    range: int = int(data['range'].split()[0]) if 'feet' in data['range'] else 5

    if 'area_of_effect' in data:
        area_of_effect = AreaOfEffect(type=data['area_of_effect']['type'], size=data['area_of_effect']['size'])
    else:
        area_of_effect = AreaOfEffect(type='sphere', size=range)

    school: str = data['school']['index']


    heal_at_slot_level: Optional[dict] = None
    if 'heal_at_slot_level' in data and data['duration'] == 'Instantaneous':
        heal_at_slot_level = data['heal_at_slot_level']

    damage_type: Optional[DamageType] = None
    damage_at_slot_level: Optional[dict] = None
    damage_at_character_level: Optional[dict] = None
    dc_type: Optional[str] = None
    dc_success: Optional[str] = None
    if "damage" in data:
        # print(data['index'], data['damage'])
        damage_type = data['damage']['damage_type']['index'] if "damage_type" in data['damage'] else None
        damage_at_slot_level = data['damage'].get('damage_at_slot_level')
        damage_at_character_level = data['damage'].get('damage_at_character_level')
        # print(f"{data['index']} - damage_at_character_level={damage_at_character_level}")
        # print(f"{data['index']} - damage_at_slot_level={damage_at_slot_level}")

        # print(data)
        if "dc" in data:
            dc_type = data['dc']['dc_type']['index']
            dc_success = data['dc']['dc_success']
            # print(f"{data['index']} - dc_type = {dc_type}")

    return Spell(index=data['index'],
                 name=data['name'],
                 desc=data['desc'],
                 level=data['level'],
                 allowed_classes=allowed_classes,
                 heal_at_slot_level=heal_at_slot_level,
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
    :return: Armor object (core business logic only - use GameEntity for positioning)
    """
    data = _load_json_data('armors', index_name)
    if "armor_class" in data:
        return Armor(
            index=data['index'],
            name=data['name'],
            armor_class=data['armor_class'],
            str_minimum=data['str_minimum'],
            category=request_equipment_category(data['equipment_category']['index']),
            stealth_disadvantage=data['stealth_disadvantage'],
            cost=Cost(data['cost']['quantity'], data['cost']['unit']),
            weight=data['weight'],
            desc=None,
            equipped=False
        )
    return None


def request_weapon_property(index_name: str) -> WeaponProperty:
    """
    Send a request to local database for a weapon's property characteristic
    :param index_name: name of the weapon's property
    :return: WeaponProperty object
    """
    data = _load_json_data('weapon-properties', index_name)
    return WeaponProperty(index=data['index'],
                          name=data['name'],
                          desc=data['desc'])


def request_weapon(index_name: str) -> Weapon:
    """
    Send a request to local database for a weapon's characteristic
    :param index_name: name of the weapon
    :return: Weapon object (core business logic only - use GameEntity for positioning)
    """
    data = _load_json_data('weapons', index_name)
    weapon_properties = None
    if 'properties' in data:
        weapon_properties: List[WeaponProperty] = [request_weapon_property(d['index']) for d in data['properties']]
    throw_range = None
    if 'throw_range' in data:
        throw_range = WeaponThrowRange(data['throw_range']['normal'], data['throw_range']['long'])
    if "damage" in data:
        damage_dice_two_handed: DamageDice = None
        if "two_handed_damage" in data:
            damage_dice_two_handed: DamageDice = DamageDice(data['two_handed_damage']['damage_dice'])
        return Weapon(
            index=data['index'],
            name=data['name'],
            category=request_equipment_category(data['equipment_category']['index']),
            category_type=CategoryType(data['weapon_category']),
            range_type=RangeType(data['weapon_range']),
            damage_dice=DamageDice(data['damage']['damage_dice']),
            damage_dice_two_handed=damage_dice_two_handed,
            damage_type=request_damage_type(index_name=data['damage']['damage_type']['index']),
            weapon_range=WeaponRange(normal=data['range']['normal'], long=data['range']['long']),
            throw_range=throw_range,
            is_magic=False,
            cost=Cost(data['cost']['quantity'], data['cost']['unit']),
            weight=data['weight'],
            properties=weapon_properties,
            desc=None,
            equipped=False
        )
    return None


def request_trait(index_name: str) -> Trait:
    """
    Send a request to local database for a trait's characteristic
    :param index_name: name of the trait
    :return: Trait object
    """
    data = _load_json_data('traits', index_name)
    return Trait(index=data['index'],
                 name=data['name'],
                 desc=data['desc'])


def request_race(index_name: str) -> Race:
    """
    Send a request to local database for a race's characteristic
    :param index_name: name of the race
    :return: Race object
    """
    data = _load_json_data('races', index_name)
    ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus']) for ability_bonus in data['ability_bonuses']])
    starting_proficiencies: List[Proficiency] = [request_proficiency(
        d['index']) for d in data.get('starting_proficiencies')]
    starting_proficiency_options: List[Tuple[List[Proficiency], int]] = []
    if data.get('starting_proficiency_options'):
        dat = data.get('starting_proficiency_options')
        choose: int = dat['choose']
        proficiencies_choose: List[Proficiency] = [request_proficiency(d['index']) for d in dat['from']]
        starting_proficiency_options.append((choose, proficiencies_choose))
    languages: List[Language] = [lang['index']for lang in data['languages']]
    traits: List[Trait] = [request_trait(d['index']) for d in data['traits']]
    subraces: List[SubRace] = [request_subrace(d['index']) for d in data['subraces']]
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
    data = _load_json_data('subraces', index_name)
    ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus'])
                            for ability_bonus in data['ability_bonuses']])
    starting_proficiencies: List[Proficiency] = [request_proficiency(d['index']) for d in data['starting_proficiencies']]
    racial_traits: List[Trait] = [request_trait(d['index']) for d in data['racial_traits']]
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
    data = _load_json_data('languages', index_name)
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
    data = _load_json_data('proficiencies', index_name)

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
            ref: List[Equipment] = list_equipment_category(index_name=index_name)
        case 'ability-scores':
            ref: AbilityType = AbilityType(index_name)

    return Proficiency(index=data['index'],
                       name=data['name'],
                       type=ProfType(data['type']),
                       ref=ref,
                       classes=classes,
                       races=races)



def request_equipment_category(index_name: str) -> EquipmentCategory:
    """
    Send a request to local database for an equipment category's characteristic
    :param index_name: name of the equipment category
    :return: EquipmentCategory object
    """
    data = _load_json_data('equipment-categories', index_name)
    return EquipmentCategory(index=data['index'],
                             name=data['name'],
                             url=data['url'])


def list_equipment_category(index_name: str) -> List[Equipment]:
    """
    Send a request to local database to list equipments inside an equipment category
    :param index_name: name of the equipment category
    :return: list of equipment's objects
    """
    data = _load_json_data('equipment-categories', index_name)
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
        data = _load_json_data('equipment', index_name)
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
                             cost=Cost(data['cost']['quantity'], data['cost']['unit']),
                             weight=data.get('weight'),
                             desc=data.get('desc'),
                             equipped=False)
    except (FileNotFoundError, Exception):
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
                spell_slots[int(char_level)] = [int(spell_slots_count)] * int(slot_level) + [0] * (5 - int(slot_level))
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
    data = _load_json_data('classes', index_name)
    proficiencies: List[Proficiency] = [request_proficiency(d['index']) for d in data['proficiencies']]
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
