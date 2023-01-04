from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from math import floor
from typing import List, Optional, Tuple

from tools.common import cprint

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
            cprint(f'{color.RED}{self.name}{color.END} hits {color.GREEN}{character.name}{color.END} for {damage_roll} hit points!')
        else:
            cprint(f'{self.name} misses {character.name}!')
        return damage_roll


""" Character classes """


@dataclass
class Proficiency:
    index: str
    name: str
    prof_type: str


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
class Language:
    index: str
    name: str
    desc: str
    type: str
    typical_speakers: List[str]
    script: str


@dataclass
class Trait:
    index: str
    name: str
    desc: str


@dataclass
class SubRace:
    index: str
    name: str
    desc: str
    ability_bonuses: dict()
    starting_proficiencies: List[Proficiency]
    racial_traits: List[Trait]


@dataclass
class Race:
    index: str
    name: str
    speed: int
    ability_bonuses: dict()
    alignment: str
    age: str
    size: str
    size_description: str
    starting_proficiencies: List[Proficiency]
    starting_proficiency_options: List[Tuple[int, List[Proficiency]]]
    languages: List[Language]
    language_desc: str
    traits: List[Trait]
    subraces: List[SubRace]

    def __repr__(self):
        return f"{self.index}"


@dataclass
class Cost:
    quantity: int
    unit: str


@dataclass
class EquipmentCategory:
    index: str
    name: str
    url: str

    def __repr__(self):
        return f"{self.index}"


@dataclass
class Equipment:
    index: str
    name: str
    cost: Cost
    weight: int
    desc: Optional[List[str]]
    category: EquipmentCategory
    gear_category: str
    tool_category: str
    vehicle_category: str
    equipped: bool = field(init=False)

    def __repr__(self):
        return f"{self.index} ({self.category})"


@dataclass
class Inventory:
    quantity: str
    equipment: Equipment | EquipmentCategory

    def __repr__(self):
        return f"{self.quantity} {self.equipment.index}"


@dataclass
class WeaponProperty():
    index: str
    name: str
    desc: str


@dataclass
class WeaponThrowRange():
    normal: int
    long: int


@dataclass
class WeaponRange():
    normal: int
    long: Optional[int]


@dataclass
class DamageType():
    index: str
    name: str
    desc: str


@dataclass
class Weapon(Equipment):
    properties: List[WeaponProperty]
    damage_type: DamageType
    weapon_category: str
    weapon_range: str
    damage_dice: str
    damage_type: str
    range: WeaponRange
    throw_range: WeaponThrowRange
    is_magic: bool
    category_range: str = field(init=False)

    def __post_init__(self):
        self.category_range = f'{self.weapon_category} {self.weapon_range}'

    def __repr__(self):
        return f"{self.index} ({self.category})"


@dataclass
class Armor(Equipment):
    armor_category: str
    armor_class: int
    str_minimum: int
    stealth_disadvantage: bool

    def __repr__(self):
        return f"{self.index} ({self.category})"


class AbilityType(Enum):
    STR = 'str'
    CON = 'con'
    DEX = 'dex'
    INT = 'int'
    WIS = 'wis'
    CHA = 'cha'


@dataclass
class Class:
    index: str
    name: str
    hit_die: int
    proficiency_choices: List[Tuple[int, List[Proficiency]]]
    proficiencies: List[Proficiency]
    saving_throws: List[AbilityType]
    starting_equipment: List[Inventory]
    starting_equipment_options: List[List[Inventory | List[Inventory]]]
    class_levels: List[str]  # Not yet implemented
    multi_classing: List[str]  # Not yet implemented
    subclasses: List[str]  # Not yet implemented
    spellcasting: str  # Not yet implemented

    def __repr__(self):
        return f"{self.index}"


@dataclass
class Feature:
    index: str
    name: str
    class_type: Class
    class_level: int
    prerequisites: List[str]
    desc: List[str]


@dataclass
class Level:
    index: str
    class_type: Class
    ability_score_bonuses: int
    prof_bonus: int
    features: List[Feature]
    class_specific: dict()
    spell_casting: Optional[dict]


@dataclass
class BackGround:
    index: str
    name: str
    starting_proficiencies: List[Proficiency]
    languages: List[Language]
    starting_equipment: List[Equipment]
    starting_equipment_options: List[Equipment]


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

    def __repr__(self):
        return f'str: {self.str} dex: {self.dex} con: {self.con} int: {self.int} wis: {self.wis} cha: {self.cha}'


@dataclass
class Character:
    name: str
    race: Race
    subrace: SubRace
    ethnic: str
    gender: str
    height: str
    weight: str
    class_type: str
    proficiencies: List[Proficiency]
    abilities: Abilities
    ability_modifiers: Abilities
    hit_points: int
    max_hit_points: int
    xp: int
    level: int
    healing_potions: List[Potion]
    monster_kills: int
    inventory: List[Equipment]
    armor: Armor
    weapon: Weapon
    gold: int
    OUT: bool = False

    # armor: Armor = field(init=False)
    # weapon: Weapon = field(init=False)

    # def __post_init__(self):
    #     self.armor = [equipment for equipment in self.inventory if equipment.category == 'armor' and equipment.equiped]
    #     self.weapon = [equipment for equipment in self.inventory if equipment.category == 'weapon' and equipment.equiped]

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
        race = self.subrace if self.subrace else self.race
        ethnic = f'ethnic: {self.ethnic} - ' if self.ethnic else ''
        return f"{self.name} - Abilities: {self.abilities} - Ability modifiers: {self.ability_modifiers} - ({ethnic}{self.gender} {race.name} - height: {self.height} weight: {self.weight}- class: {self.class_type} - AC {self.armor_class} HD: {self.hit_dice} - w: {self.weapon.name} a: {self.armor.name} - potions: {len(self.healing_potions)})"

    @property
    def armor_class(self):
        return self.armor.armor_class['base']

    @property
    def hit_dice(self):
        return self.weapon.damage_dice

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
            cprint(f'{self.name} drinks healing potion and is {color.BOLD}*fully*{color.END} healed!')
        else:
            cprint(f'{self.name} drinks healing potion and has {min(hp_to_recover, hp_restored)} hit points restored!')

    def victory(self, monster: Monster):
        self.xp += monster.xp
        self.monster_kills += 1
        gold_dice = random.randint(1, 3)
        gold_msg: str = ''
        if gold_dice == 1:
            max_gold: int = max(1, floor(10 * monster.xp / monster.level))
            gold: int = random.randint(1, max_gold + 1)
            gold_msg = f' and found {gold} gp!'
            self.gold += gold
        cprint(f'{monster.name.title()} killed!')
        cprint(f'{self.name} gained {monster.xp} XP{gold_msg}!')

    def treasure(self, weapons, armors):
        treasure_dice = random.randint(1, 3)
        if treasure_dice == 1:
            cprint(f"{self.name} found a healing potion!")
            self.healing_potions.append(Potion('2d4'))
        elif treasure_dice == 2:
            new_weapon: Weapon = random.choice(weapons)
            if new_weapon.damage_dice > self.weapon.damage_dice:
                cprint(f"{self.name} found a better weapon {new_weapon}!")
                self.weapon = new_weapon
        else:
            new_armor: Armor = random.choice(armors)
            if new_armor.armor_class['base'] > self.armor.armor_class['base']:
                cprint(f"{self.name} found a better armor {new_armor}!")
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
            cprint(f'{color.GREEN}{self.name}{color.END} hits {color.RED}{monster.name}{color.END} for {damage_roll} hit points!')
        else:
            cprint(f'{self.name} misses {monster.name}!')
        return damage_roll
