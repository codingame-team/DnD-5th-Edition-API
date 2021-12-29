import json
import random
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class Character:
    name: str
    armor_class: int
    hit_points: int
    xp: int


@dataclass
class Monster:
    name: str
    armor_class: int
    hit_points: int
    hit_dice: str
    xp: int
    challenge_rating: int

    def attack(self):
        """
        :return: damage generated
        """
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return sum([random.randint(1, roll_dice) for _ in range(dice_count)])


def download_monster(index_name: str):
    """
    Downloads a monster's characteristic to a local .json file
    :param index_name: name of the monster
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/monsters/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"monsters/{index_name}.json", "w") as f:
        f.write(str(data))


def populate_dungeon() -> List[str]:
    """
    :return: list of monsters names
    """
    with open("monsters_list.json", "r") as f:
        data = json.loads(f.read())
        monsters_count = int(data['count'])
        monsters_json_list = data['results']
    monster_list = [json_data['index'] for json_data in monsters_json_list]
    return monster_list


def request_monster_api(index_name: str) -> Monster:
    """
    Send a request to the DnD API for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/monsters/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    return Monster(name=data['name'],
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   challenge_rating=data['challenge_rating'])


def request_monster(index_name: str) -> Monster:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    with open(f"monsters/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return Monster(name=data['name'],
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   challenge_rating=data['challenge_rating'])


if __name__ == '__main__':
    character: Character = Character(name='philRG', armor_class=10, hit_points=500, xp=0)
    monsters_names: List[str] = populate_dungeon()
    roster: List[Monster] = [request_monster(name) for name in monsters_names]
    monsters_to_fight = [m for m in roster if m.challenge_rating > 20]
    attack_count = 0
    while character.hit_points > 0:
        monster = random.choice(monsters_to_fight)
        hp_damage = monster.attack()
        character.hit_points -= hp_damage
        character.xp += monster.xp
        print(f'{monster.name} attacks {character.name} and {character.name} takes {hp_damage} hp')
        attack_count += 1
    print(f'{character} has been finally killed by a {monster.name} after {attack_count} attacks')
