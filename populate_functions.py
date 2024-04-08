from __future__ import annotations

import csv
import json
import os
from copy import deepcopy
from logging import debug
from typing import List, Tuple, Optional
import re

from dao_classes import CategoryType, DamageDice, Monster, Armor, RangeType, SpecialAbility, SpellCaster, Weapon, Race, \
    SubRace, Proficiency, ClassType, Language, Equipment, WeaponProperty, WeaponRange, AbilityType, WeaponThrowRange, \
    Trait, EquipmentCategory, \
    Abilities, Action, Damage, ActionType, DamageType, Spell, ProfType, Condition, Inventory
from populate_rpg_functions import load_armor_image_name, load_weapon_image_name

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
                            attack_bonus=action_dict.get('attack_bonus'), multi_attack=None, damages=damages,
                            effects=effects)
            actions.append(action)
            return actions


def request_monster(index_name: str) -> Monster:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
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
    if "special_abilities" in data:
        for special_ability in data['special_abilities']:
            if special_ability['name'] == 'Spellcasting':
                caster_level = special_ability['spellcasting']['level']
                dc_type = special_ability['spellcasting']['ability']['index']
                dc_value = special_ability['spellcasting']['dc']
                ability_modifier = special_ability['spellcasting']['modifier']
                slots = [s for s in special_ability['spellcasting']['slots'].values()]
                for spell_dict in special_ability['spellcasting']['spells']:
                    spell_index_name: str = spell_dict['url'].split('/')[3]
                    spell = request_spell(spell_index_name)
                    if spell is None:
                        continue
                    spells.append(spell)
        if spells:
            can_attack = True
            spell_caster: SpellCaster = SpellCaster(level=caster_level,
                                                    spell_slots=slots,
                                                    learned_spells=spells,
                                                    dc_type=dc_type,
                                                    dc_value=dc_value + ability_modifier,
                                                    ability_modifier=ability_modifier)

    actions: List[Action] = []
    special_abilities: List[SpecialAbility] = []

    if "actions" in data:
        # Melee attacks
        for action in data['actions']:
            # print(f"{data['name']} - action = {action}")
            if action['name'] != 'Multiattack' and "damage" in action and re.search("(Weapon|Melee).*Attack",
                                                                                    action['desc']):
                damages: List[Damage] = []
                for damage in action['damage']:
                    # print(f'damage = {damage}')
                    if "damage_type" in damage:
                        damage_type: DamageType = request_damage_type(index_name=damage['damage_type']['index'])
                        damages.append(Damage(type=damage_type, dd=DamageDice(damage['damage_dice'])))
                if damages:
                    can_attack = True
                    actions.append(Action(name=action['name'], desc=action['desc'], type=ActionType.MELEE,
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
                if "usage" in action:
                    if action['usage'].get('type') == 'recharge on roll':
                        recharge_on_roll = action['usage']['min_value']
                if damages:
                    special_abilities.append(SpecialAbility(name=action['name'],
                                                            desc=action['desc'],
                                                            damages=damages,
                                                            dc_type=action['dc']['dc_type']['index'],
                                                            dc_value=action['dc']['dc_value'],
                                                            dc_success=action['dc']['success_type'],
                                                            recharge_on_roll=recharge_on_roll))

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
                   x=-1,
                   y=-1,
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


def request_spell(index_name: str) -> Spell:
    """
    Send a request to local database for a spell's characteristic
    :param index_name: name of the monster
    :return: Spell object
    """
    with open(f"{path}/data/spells/{index_name}.json", "r") as f:
        data = json.loads(f.read())

    allowed_classes: List[str] = [c['index'] for c in data['classes']]

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

        return Spell(index=data['index'],
                     name=data['name'],
                     desc=data['desc'],
                     level=data['level'],
                     allowed_classes=allowed_classes,
                     damage_type=damage_type,
                     damage_at_slot_level=damage_at_slot_level,
                     damage_at_character_level=damage_at_character_level,
                     dc_type=dc_type,
                     dc_success=dc_success
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
                     x=-1, y=-1,
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
                      x=-1, y=-1,
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
                                 x=-1, y=-1,
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
