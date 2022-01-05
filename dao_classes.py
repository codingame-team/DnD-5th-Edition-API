import random
from dataclasses import dataclass
from enum import Enum
from typing import List

""" Needs to separate presentation layer from data layer """


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


""" Monster classes """


@dataclass
class Monster:
    name: str
    armor_class: int
    hit_points: int
    hit_dice: str
    xp: int
    challenge_rating: int

    def __repr__(self):
        return f"{self.name} (AC {self.armor_class} HD: {self.hit_dice})"

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


""" Character classes """


class ProficiencyType(Enum):
    ARMOR = 'Armor'
    WEAPON = 'Weapon'


@dataclass
class Proficiency:
    name: str
    prof_type: ProficiencyType


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


# @dataclass
# class Inventory:
#     weapons: List[Weapon]
#     armors: List[Armor]
#     pass


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
class Race:
    name: str
    ability_bonuses: dict()
    starting_proficiencies: List[Proficiency]
    speed: int
    size: str


@dataclass
class SubRace:
    name: str
    ability_bonuses: dict()
    starting_proficiencies: List[Proficiency]


# @dataclass
# class Class:
#     name: str
#     ability_bonuses: dict()
#     starting_proficiencies: List[Proficiency]
#     speed: int
#     size: str

@dataclass
class Abilities:
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int

    # def __init__(self, strength, dexterity, constitution, intelligence, wisdom, charisma):
    #     self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma = strength, dexterity, constitution, intelligence, wisdom, charisma

    def __repr__(self):
        # return f'str: {self.strength} dex: {self.dexterity} con: {self.constitution} int: {self.intelligence} wis: {self.wisdom} cha: {self.charisma}'
        return f'str: {self.str} dex: {self.dex} con: {self.con} int: {self.int} wis: {self.wis} cha: {self.cha}'


@dataclass
class Character:
    name: str
    race: Race
    sub_race: SubRace
    ethnic: str
    gender: str
    class_type: str
    abilities: Abilities
    hit_points: int
    max_hit_points: int
    xp: int
    level: int
    armor: Armor
    weapon: Weapon
    healing_potions: List[Potion]
    monster_kills: int

    @property
    def strength(self):
        return self.abilities.str if 'str' not in self.race.ability_bonuses else self.abilities.str + self.race.ability_bonuses['str']

    @property
    def dexterity(self):
        return self.abilities.dex if 'dex' not in self.race.ability_bonuses else self.abilities.dex + self.race.ability_bonuses['dex']

    @property
    def constitution(self):
        return self.abilities.con if 'con' not in self.race.ability_bonuses else self.abilities.con + self.race.ability_bonuses['con']

    @property
    def intelligence(self):
        return self.abilities.int if 'int' not in self.race.ability_bonuses else self.abilities.int + self.race.ability_bonuses['int']

    @property
    def wisdom(self):
        return self.abilities.wis if 'wis' not in self.race.ability_bonuses else self.abilities.wis + self.race.ability_bonuses['wis']

    @property
    def charism(self):
        return self.abilities.cha if 'cha' not in self.race.ability_bonuses else self.abilities.cha + self.race.ability_bonuses['cha']

    def __repr__(self):
        race = self.sub_race if self.sub_race else self.race
        ethnic = f'ethnic: {self.ethnic} - ' if self.ethnic else ''
        return f"{self.name} - Abilities: {self.abilities} - ({ethnic}{self.gender} {race} - class: {self.class_type} - AC {self.armor_class} HD: {self.hit_dice} - w: {self.weapon.name} a: {self.armor.name} - potions: {len(self.healing_potions)})"

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

    def gain_level(self, pause: bool):
        self.level += 1
        hp_gained = random.randint(1, 10)
        self.max_hit_points += hp_gained
        print(f'{color.BLUE}New level #{self.level} gained!!!{color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        if pause:
            input(f'{color.UNDERLINE}{color.DARKCYAN}hit Enter to continue adventure :-) (potions remaining: {len(self.healing_potions)}){color.END}')

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
