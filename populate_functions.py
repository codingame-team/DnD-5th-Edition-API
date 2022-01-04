import csv
import json
from typing import List

from dao_classes import Monster, Armor, Weapon, Race


def populate(collection_name: str, key_name: str, with_url=False) -> List[str]:
    """
    :return: list of collection names
    """
    with open(f"collections/{collection_name}.json", "r") as f:
        data = json.loads(f.read())
        # collection_count = int(data['count'])
        collection_json_list = data[key_name]
    if with_url:
        data_list = [(json_data['index'], json_data['url']) for json_data in collection_json_list]
    else:
        data_list = [json_data['index'] for json_data in collection_json_list]
    return data_list


def populate_names(race: str) -> List[str]:
    """
    :return: list of names (except humans and half-elf)
    """
    names_list = dict()
    with open(f"data/races/names/{race}.csv", newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        for sex, name in csv_data:
            if sex not in names_list:
                names_list[sex] = []
            else:
                names_list[sex].append(name)
    return names_list


def populate_human_names() -> List[str]:
    """
    :return: list of names (humans and half-elf)
    """
    names_list = dict()
    with open(f"data/races/names/human.csv", newline='') as csv_file:
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


def request_monster(index_name: str) -> Monster:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    with open(f"data/monsters/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return Monster(name=data['name'],
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   challenge_rating=data['challenge_rating'])


def request_armor(index_name: str) -> Armor:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    with open(f"data/armors/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    if "armor_class" in data:
        return Armor(name=data['name'],
                     armor_category=data['armor_category'],
                     armor_class=data['armor_class'],
                     str_minimum=data['str_minimum'],
                     stealth_disadvantage=data['stealth_disadvantage'])
    return None


def request_weapon(index_name: str) -> Weapon:
    """
    Send a request to local database for a weapon's characteristic
    :param index_name: name of the weapon
    :return: Weapon object
    """
    with open(f"data/weapons/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    if "damage" in data:
        return Weapon(name=data['name'],
                      weapon_category=data['weapon_category'],
                      weapon_range=data['weapon_range'],
                      hit_dice=data['damage']['damage_dice'],
                      damage_type=data['damage']['damage_type']['index'],
                      range_dict=data['range'])
    return None


def request_race(index_name: str) -> Race:
    """
    Send a request to local database for a weapon's characteristic
    :param index_name: name of the weapon
    :return: Weapon object
    """
    with open(f"data/races/{index_name}.json", "r") as f:
        data = json.loads(f.read())
        ability_bonuses = dict([(ability_bonus['ability_score']['index'], ability_bonus['bonus']) for ability_bonus in data['ability_bonuses']])
        return Race(name=data['index'],
                    ability_bonuses=ability_bonuses,
                    speed=data['speed'],
                    size=data['size'])
