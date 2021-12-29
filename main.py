from typing import List

import random

import json
from dataclasses import dataclass

import requests


@dataclass
class Character:
    name: str
    ac: int
    hp: int

    def __init__(self, name, armor_class, hit_points):
        self.name = name
        self.ac = armor_class
        self.hp = hit_points


@dataclass
class Monster:
    name: str
    ac: int
    hp: int
    hit_dice: str
    xp: int

    def __init__(self, name, armor_class, hit_points, hit_dice, xp):
        self.name = name
        self.ac = armor_class
        self.hp = hit_points
        self.hit_dice = hit_dice
        self.xp = xp

    def attack(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return sum([random.randint(1, roll_dice) for _ in range(dice_count)])


def populate_dungeon() -> List[Monster]:
    with open("monsters_list.json", "r") as f:
        data = json.loads(f.read())
        monsters_count = int(data['count'])
        monsters_json_list = data['results']
    monster_list = [json_data['index'] for json_data in monsters_json_list]
    return monster_list


def request_monster(index_name: str) -> Monster:
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/monsters/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    return Monster(name=data['name'], armor_class=data['armor_class'], hit_points=data['hit_points'], hit_dice=data['hit_dice'], xp=data['xp'])


if __name__ == '__main__':
    character: Character = Character(name='philRG', armor_class=10, hit_points=50)
    monsters: List[str] = populate_dungeon()
    attack_count = 0
    while character.hp > 0:
        monster_name = random.choice(monsters)
        monster: Monster = request_monster(index_name=monster_name)
        hp_damage = monster.attack()
        character.hp -= hp_damage
        print(f'{monster.name} attacks {character.name} and {character.name} takes {hp_damage} hp')
        attack_count += 1
    print(f'{character} has been finally killed by a {monster.name} after {attack_count} attacks')

