from __future__ import annotations

import csv
import json
import os
from typing import List, Tuple

from dao_classes import Monster, Armor, Weapon, Race, SubRace, Proficiency, Class, Language, Equipment, WeaponProperty, WeaponRange, AbilityType, WeaponThrowRange, Trait, EquipmentCategory, Inventory

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
    result = []
    with open(f'{path}/Tables/{filename}', newline='') as csv_file:
        reader = csv.reader(csv_file, delimiter=';')
        next(reader, None)
        return list(reader)


def height_weight_table() -> List:
    """
    :return: List of race height/weight modifier's parameters
    """
    """Race;Base Height;Height Modifier;Base Weight;Weight Modifier"""
    headers = ['Race', 'Base Height', 'Height Modifier', 'Base Weight', 'Weight Modifier']
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
        data_list = [(json_data['index'], json_data['url']) for json_data in collection_json_list]
    else:
        data_list = [json_data['index'] for json_data in collection_json_list]
    return data_list


def request_monster(index_name: str) -> Monster:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    with open(f"{path}/data/monsters/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return Monster(name=data['name'],
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   challenge_rating=data['challenge_rating'])


def request_armor(index_name: str) -> Armor:
    """
    Send a request to local database for a armor's characteristic
    :param index_name: name of the armor
    :return: Armor object
    """
    with open(f"{path}/data/armors/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    if "armor_class" in data:
        return Armor(index=data['index'],
                     name=data['name'],
                     armor_category=data['armor_category'],
                     armor_class=data['armor_class'],
                     str_minimum=data['str_minimum'],
                     stealth_disadvantage=data['stealth_disadvantage'],
                     equipment_category=EquipmentCategory('armor', 'Armor', '/api/equipment-categories/armor'),
                     gear_category=None,
                     tool_category=None,
                     vehicle_category=None,
                     cost=data['cost'],
                     weight=data['weight'],
                     desc=None)
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
        weapon_properties: List[WeaponProperty] = [request_weapon_property(d['index']) for d in data['properties']]
    throw_range = None
    if 'throw_range' in data:
        throw_range = WeaponThrowRange(data['throw_range']['normal'], data['throw_range']['long'])
    if "damage" in data:
        return Weapon(index=data['index'],
                      name=data['name'],
                      weapon_category=data['weapon_category'],
                      weapon_range=data['weapon_range'],
                      damage_dice=data['damage']['damage_dice'],
                      damage_type=data['damage']['damage_type']['index'],
                      range=WeaponRange(data['range']['normal'], data['range']['long']),
                      throw_range=throw_range,
                      is_magic=False,
                      equipment_category=EquipmentCategory('weapon', 'Weapon', '/api/equipment-categories/weapon'),
                      gear_category=None,
                      tool_category=None,
                      vehicle_category=None,
                      cost=data['cost'],
                      weight=data['weight'],
                      properties=weapon_properties,
                      desc=None)
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
        ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus']) for ability_bonus in data['ability_bonuses']])
        starting_proficiencies: List[Proficiency] = [request_proficiency(d['index']) for d in data.get('starting_proficiencies')]
        starting_proficiency_options: List[Tuple[List[Proficiency], int]] = []
        if data.get('starting_proficiency_options'):
            dat = data.get('starting_proficiency_options')
            choose: int = dat['choose']
            proficiencies_choose: List[Proficiency] = [request_proficiency(d['index']) for d in dat['from']]
            starting_proficiency_options.append((choose, proficiencies_choose))
        languages: List[Language] = [lang['index'] for lang in data['languages']]
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
    with open(f"{path}/data/subraces/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus']) for ability_bonus in data['ability_bonuses']])
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
        return Proficiency(index=data['index'],
                           name=data['index'],
                           prof_type=data['type'])


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
    :param index_name: name of the quipment category
    :return: EquipmentCategory object
    """
    with open(f"{path}/data/equipment-categories/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        return EquipmentCategory(index=data['index'],
                                 name=data['name'],
                                 url=data['url'])


def request_equipment(index_name: str) -> Equipment:
    """
    Send a request to local database for an equipment's characteristic
    :param index_name: name of the equipment
    :return: Equipment object
    """
    with open(f"{path}/data/equipment/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        equipment_category = data['equipment_category']['index']
        if equipment_category == 'weapon':
            return request_weapon(index_name)
        elif equipment_category == 'armor':
            return request_armor(index_name)
        else:
            gear_category = tool_category = vehicle_category = None
            if data['equipment_category']['index'] == 'adventuring-gear':
                gear_category = data['gear_category']
            if data['equipment_category']['index'] == 'tools':
                tool_category = data['tool_category']
            if data['equipment_category']['index'] == 'mounts-and-vehicles':
                vehicle_category = data['vehicle_category']
            d = data['equipment_category']
            equipment_category: EquipmentCategory = \
                EquipmentCategory(d['index'], d['name'], d['url'])
            return Equipment(index=data['index'],
                             name=data['name'],
                             equipment_category=equipment_category,
                             gear_category=gear_category,
                             tool_category=tool_category,
                             vehicle_category=vehicle_category,
                             cost=data['cost'],
                             weight=data.get('weight'),
                             desc=data.get('desc'))


def request_class(index_name: str, known_proficiencies: List[Proficiency] = None, abilities: List[AbilityType] = None) -> Class:
    """
    Send a request to local database for a class's characteristic
    :param index_name: name of the class
    :return: Class object
    """
    with open(f"{path}/data/classes/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        proficiencies: List[Proficiency] = [request_proficiency(d['index']) for d in data['proficiencies']]
        proficiency_choices: List[Tuple[List[Proficiency], int]] = []
        for dat in data['proficiency_choices']:
            choose: int = dat['choose']
            proficiencies_choose: List[Proficiency] = [request_proficiency(d['index']) for d in dat['from']]
            proficiency_choices.append((choose, proficiencies_choose))

        starting_equipment: List[Inventory] = []
        for equip_dict in data['starting_equipment']:
            quantity: int = equip_dict['quantity']
            equipment: Equipment = request_equipment(equip_dict['equipment']['index'])
            starting_equipment.append(Inventory(quantity=quantity, equipment=equipment))

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
                    equipment: Inventory = Inventory(quantity=eq_choice['quantity'], equipment=request_equipment(eq_choice['equipment']['index']))
                    equipments_choose.append(equipment)
                elif 'equipment_option' in eq_choice:
                    quantity: int = eq_choice['quantity'] if 'quantity' in eq_choice else 1
                    equipment_category: EquipmentCategory = request_equipment_category(eq_choice['equipment_option']['from']['equipment_category']['index'])
                    equipments_choose.append(Inventory(quantity=quantity, equipment=equipment_category))
                elif 'equipment_category' in eq_choice:
                    quantity: int = eq_choice['quantity'] if 'quantity' in eq_choice else 1
                    equipment_category: EquipmentCategory = request_equipment_category(eq_choice['equipment_category']['index'])
                    equipments_choose.append(Inventory(quantity=quantity, equipment=equipment_category))
                else:
                    equipments: List[Inventory] = []
                    for item_no, equip_dict in eq_choice.items():
                        # print(f'item_no: {item_no}, equip_dict: {equip_dict}')
                        if 'equipment' in equip_dict:
                            quantity: int = equip_dict['quantity'] if 'quantity' in equip_dict else 1
                            equipment: Equipment = request_equipment(equip_dict['equipment']['index'])
                            equipments.append(Inventory(quantity=quantity, equipment=equipment))
                    equipments_choose.append(equipments)
            if equipments_choose:
                # starting_equipment_options.append((choose, equipments_choose))
                starting_equipment_options.append(equipments_choose)
        saving_throws: List[AbilityType] = [AbilityType(d['index']) for d in data['saving_throws']]
        return Class(index=data['index'],
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
                     spellcasting=data.get('spellcasting'))
