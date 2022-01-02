import json
import random
from copy import copy
from dataclasses import dataclass
from typing import List

import requests

PAUSE_ON_RAISE_LEVEL = True
POTION_FREQUENCY = 2
POTION_INITIAL_PACK = 10
POTION_HEALING_FACTOR = 10


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


@dataclass
class Monster:
    name: str
    armor_class: int
    hit_points: int
    hit_dice: str
    xp: int
    challenge_rating: int

    def __repr__(self):
        return f"{self.name} (AC {self.armor_class} HD: {character.hit_dice})"

    @property
    def level(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return dice_count * roll_dice

    def __copy__(self):
        return Monster(self.name, self.armor_class, self.hit_points, self.hit_dice, self.xp, self.challenge_rating)

    def attack(self, character):
        """
        :return: damage generated
        """
        attack_roll = random.randint(1, 20)
        damage_roll = 0
        if attack_roll >= character.armor_class:
            dice_count, roll_dice = map(int, self.hit_dice.split('d'))
            damage_roll = sum([random.randint(1, roll_dice) for _ in range(dice_count)])
        if damage_roll:
            print(f'{color.RED}{self.name}{color.END} hits {color.GREEN}{character.name}{color.END} for {damage_roll} hit points!')
        else:
            print(f'{self.name} misses {character.name}!')
        return damage_roll


@dataclass
class Weapon:
    name: str
    weapon_category: str
    weapon_range: str
    hit_dice: str
    damage_type: str
    range_dict: dict()


@dataclass
class Armor:
    name: str
    armor_category: str
    armor_class: int
    str_minimum: int
    stealth_disadvantage: bool


@dataclass
class Inventory:
    weapons: List[Weapon]
    armors: List[Armor]
    pass

@dataclass
class Potion:
    hit_dice: str

    @property
    def min_hp_restored(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return 2 + dice_count

    @property
    def max_hp_restored(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return 2 + dice_count * roll_dice

@dataclass
class Character:
    name: str
    hit_points: int
    max_hit_points: int
    xp: int
    level: int
    armor: Armor
    weapon: Weapon
    healing_potions: List[Potion]
    monster_kills: int

    def __repr__(self):
        return f"{self.name} (AC {self.armor_class} HD: {character.hit_dice} - w: {self.weapon.name} a: {self.armor.name} - potions: {len(self.healing_potions)})"

    @property
    def armor_class(self):
        return self.armor.armor_class['base']

    @property
    def hit_dice(self):
        return self.weapon.hit_dice

    """Healing (??? check rules): A Healing potion repairs one six-sided die, plus one, (2-7) points of damage, just like a Cure Light Wounds spell."""
    def drink_potion(self):
        hp_to_recover = self.max_hit_points - self.hit_points
        available_potions = [p for p in self.healing_potions if p.max_hp_restored >= hp_to_recover]
        best_potion = min(available_potions, key=lambda p: p.max_hp_restored) if available_potions else max(self.healing_potions, key=lambda p: p.max_hp_restored)
        self.healing_potions.remove(best_potion)
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        hp_restored = 2 + random.randint(1, roll_dice) + random.randint(1, roll_dice)
        self.hit_points = min(self.hit_points + hp_restored, self.max_hit_points)
        if hp_to_recover <= hp_restored:
            print(f'{self.name} drinks healing potion and is {color.BOLD}*fully*{color.END} healed!')
        else:
            print(f'{self.name} drinks healing potion and has {min(hp_to_recover, hp_restored)} hit points restored!')
    #
    def victory(self, monster):
        self.xp += monster.xp
        self.monster_kills += 1
        print(f'{self.name} killed {monster.name} and gained {monster.xp} XP!')

    def treasure(self, weapons, armors):
        treasure_dice = random.randint(1, 3)
        if treasure_dice == 1:
            print(f"{self.name} found a healing potion!")
            self.healing_potions.append(Potion('2d4'))
        elif treasure_dice == 2:
            new_weapon: Weapon = random.choice(weapons)
            if new_weapon.hit_dice > self.weapon.hit_dice:
                print(f"{self.name} found a better weapon {new_weapon}!")
                self.weapon = new_weapon
        else:
            new_armor: Armor = random.choice(armors)
            if new_armor.armor_class['base'] > self.armor.armor_class['base']:
                print(f"{self.name} found a better armor {new_armor}!")
                self.armor = new_armor

    def gain_level(self):
        self.level += 1
        hp_gained = random.randint(1, 10)
        character.max_hit_points += hp_gained
        print(f'{color.BLUE}New level #{self.level} gained!!!{color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        if PAUSE_ON_RAISE_LEVEL:
            input(f'{color.UNDERLINE}{color.DARKCYAN}hit Enter to continue adventure :-) (potions remaining: {len(character.healing_potions)}){color.END}')

    def attack(self, monster: Monster):
        """
        :return: damage generated
        """
        attack_roll = random.randint(1, 20)
        damage_roll = 0
        if attack_roll >= monster.armor_class:
            dice_count, roll_dice = map(int, self.hit_dice.split('d'))
            damage_roll = sum([random.randint(1, roll_dice) for _ in range(dice_count)])
        if damage_roll:
            print(f'{color.GREEN}{self.name}{color.END} hits {color.RED}{monster.name}{color.END} for {damage_roll} hit points!')
        else:
            print(f'{self.name} misses {monster.name}!')
        return damage_roll


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


def populate_boltac_weapons() -> List[str]:
    """
    :return: list of weapons names
    """
    with open("weapons_list.json", "r") as f:
        data = json.loads(f.read())
        weapons_json_list = data['equipment']
    weapons_list = [(json_data['index'], json_data['url']) for json_data in weapons_json_list]
    return weapons_list


def populate_boltac_armors() -> List[str]:
    """
    :return: list of armors names
    """
    with open("armors_list.json", "r") as f:
        data = json.loads(f.read())
        armors_json_list = data['equipment']
    armors_list = [(json_data['index'], json_data['url']) for json_data in armors_json_list]
    return armors_list


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


def request_armor(index_name: str) -> Armor:
    """
    Send a request to local database for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    with open(f"armors/{index_name}.json", "r") as f:
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
    with open(f"weapons/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    if "damage" in data:
        return Weapon(name=data['name'],
                      weapon_category=data['weapon_category'],
                      weapon_range=data['weapon_range'],
                      hit_dice=data['damage']['damage_dice'],
                      damage_type=data['damage']['damage_type']['index'],
                      range_dict=data['range'])
    return None


def welcome_message():
    global PAUSE_ON_RAISE_LEVEL
    if PAUSE_ON_RAISE_LEVEL:
        print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
        print(f'{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}')
        print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
        print(f'{color.DARKCYAN}Do you want to pause output after new level? (Y/N){color.END}')
        response = input()
        while response not in ['y', 'n', 'Y', 'N']:
            print(f'{color.DARKCYAN} Do you want to pause output after new level? (Y/N){color.END}')
            response = input()
        PAUSE_ON_RAISE_LEVEL = True if response in ['y', 'Y'] else False


if __name__ == '__main__':
    random.seed()
    """ Load XP Levels """
    infile = open("xp_levels.txt", "r")
    xp_levels = []
    for line in infile:
        xp_needed, level, master_bonus = line.split(' ')
        # xp_levels.append((xp_needed, master_bonus))
        xp_levels.append(int(xp_needed))
    """ Load Monster, Armor and Weapon databases """
    monsters_names: List[str] = populate_dungeon()
    armors_names: List[str] = [x[0] for x in populate_boltac_armors()]
    weapons_names: List[str] = [x[0] for x in populate_boltac_weapons()]
    roster: List[Monster] = [request_monster(name) for name in monsters_names]
    boltac_armors: List[Armor] = [request_armor(name) for name in armors_names]
    boltac_armors = [a for a in boltac_armors if a]
    boltac_weapons: List[Armor] = [request_weapon(name) for name in weapons_names]
    boltac_weapons = [w for w in boltac_weapons if w]
    # Create character
    armor, weapon = boltac_armors[0], boltac_weapons[1]
    character: Character = Character(name='philRG',
                                     armor=boltac_armors[0],
                                     weapon=boltac_weapons[1],
                                     hit_points=10,
                                     max_hit_points=10,
                                     xp=0, level=1,
                                     healing_potions=[Potion('2d4')] * POTION_INITIAL_PACK,
                                     monster_kills=0)
    welcome_message()
    attack_count = 0
    while character.hit_points > 0 and character.level < 20:
        # monsters_to_fight = [m for m in roster if m.challenge_rating < 1]
        # monsters_to_fight = [m for m in roster if 2 + character.level <= m.level <= 5 + character.level]
        monsters_to_fight = [m for m in roster if m.level <= 5 + character.level]
        if character.xp > xp_levels[character.level]:
            character.gain_level()
        monster: Monster = copy(random.choice(monsters_to_fight))
        print(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        print(f'{color.PURPLE} New encounter! {character} vs {monster}{color.END}')
        print(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        round_num = 0
        monster_max_hp = monster.hit_points
        while monster.hit_points > 0:
            round_num += 1
            print('-------------------------------------------------------')
            print(f'Round {round_num}: {character.name} ({character.hit_points}/{character.max_hit_points}) vs {monster.name} ({monster.hit_points}/{monster_max_hp})')
            print('-------------------------------------------------------')
            if character.hit_points < 0.5 * character.max_hit_points and character.healing_potions:
                print(f'{len(character.healing_potions)} remaining potions')
                character.drink_potion()
            attack_count += 1
            monster_hp_damage = monster.attack(character)
            character_hp_damage = character.attack(monster)
            priority_dice = random.randint(0, 1)
            if priority_dice == 0:  # monster attacks first
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    break
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    character.treasure(boltac_weapons, boltac_armors)
                    break
            else:  # character attacks first
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    character.treasure(boltac_weapons, boltac_armors)
                    break
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    break

    if character.hit_points <= 0:
        print(f'{character.name} has been killed by a {monster.name} after {attack_count} attack rounds and {character.monster_kills} monsters kills and reached level #{character.level}')
    else:
        print(f'{character} has killed {character.monster_kills} monsters and reached level #{character.level}')
