import json
import random
from copy import copy
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class Character:
    name: str
    armor_class: int
    hit_points: int
    max_hit_points: int
    hit_dice: str
    xp: int
    level: int
    healing_potions: List[int]
    monster_kills: int

    def drink_potion(self):
        restore_hp = self.max_hit_points - self.hit_points
        available_potions = [p for p in self.healing_potions if p >= restore_hp]
        best_potion = min(available_potions) if available_potions else max(self.healing_potions)
        self.healing_potions.remove(best_potion)
        self.hit_points += best_potion
        print(f'{self.name} drinks healing potion and has {best_potion} hit points restored!')

    def victory(self, monster):
        self.xp += monster.xp
        self.monster_kills += 1
        print(f'{self.name} killed {monster.name} and gained {monster.xp} XP!')

    def treasure(self):
        treasure_dice = random.randint(1, 3)
        if treasure_dice == 3:
            print(f"{self.name} found a healing potion!")
            self.healing_potions.append(random.randint(5, 15))

    def raise_level(self):
        self.level += 1
        hp_gained = random.randint(1, 10)
        character.max_hit_points += hp_gained
        print(f'{self.name} reached level #{self.level} and gained {hp_gained} hit points')

    def attack(self):
        """
        :return: damage generated
        """
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return sum([random.randint(1, roll_dice) for _ in range(dice_count)])


@dataclass
class Monster:
    name: str
    armor_class: int
    hit_points: int
    hit_dice: str
    xp: int
    challenge_rating: int

    @property
    def level(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return dice_count * roll_dice

    def __copy__(self):
        return Monster(self.name, self.armor_class, self.hit_points, self.hit_dice, self.xp, self.challenge_rating)

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
    character: Character = Character(name='philRG', armor_class=10, hit_points=10, max_hit_points=10, hit_dice="1d10", xp=0, level=1, healing_potions=[20] * 10, monster_kills=0)
    infile = open("xp_levels.txt", "r")
    xp_levels = []
    for line in infile:
        xp_needed, level, master_bonus = line.split(' ')
        # xp_levels.append((xp_needed, master_bonus))
        xp_levels.append(int(xp_needed))
    monsters_names: List[str] = populate_dungeon()
    roster: List[Monster] = [request_monster(name) for name in monsters_names]
    attack_count = 0
    while character.hit_points > 0 and character.level < 20:
        # monsters_to_fight = [m for m in roster if m.challenge_rating < 1]
        monsters_to_fight = [m for m in roster if m.level <= 5 + character.level]
        if character.xp > xp_levels[character.level]:
            character.raise_level()
        monster: Monster = copy(random.choice(monsters_to_fight))
        print(f'new encounter! {monster}')
        while monster.hit_points > 0:
            if character.hit_points < 0.5 * character.max_hit_points and character.healing_potions:
                character.drink_potion()
            attack_count += 1
            monster_hp_damage = monster.attack()
            character_hp_damage = character.attack()
            priority_dice = random.randint(0, 1)
            if priority_dice == 0:  # monster attacks first
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    break
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    character.treasure()
                    break
            else:  # character attacks first
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    character.treasure()
                    break
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    break

    if character.hit_points <= 0:
        print(f'{character} has been finally killed by a {monster} after {attack_count} attack rounds and {character.monster_kills} monsters kills and reached level #{character.level}')
    else:
        print(f'{character} has killed {character.monster_kills} monsters and reached level #{character.level}')
