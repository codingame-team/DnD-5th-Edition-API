from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from math import floor
from typing import List, Optional, Tuple
from random import randint, choice

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
    abilities: Abilities
    proficiencies: List[Proficiency]
    armor_class: int
    hit_points: int
    hit_dice: str
    xp: int
    challenge_rating: int
    actions: List[Action]

    def __repr__(self):
        return f"{self.name} (AC {self.armor_class} HD: {self.hit_dice} CR: {self.challenge_rating})"

    @property
    def level(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return dice_count * roll_dice

    def __copy__(self):
        return Monster(self.name, self.abilities, self.proficiencies, self.armor_class, self.hit_points, self.hit_dice, self.xp, self.challenge_rating, self.actions)

    def saving_throw(self, dc: int, spell: Spell) -> bool:
        """
            Determine resistance from a spell casted by a character
        :param dc: ability needed to defend against the spell
        :param spell: spell of the caster
        :return:
        """
        # 2 - Calculate saving throw of monster
        # Determine ability for ST in Spell
        ability_mod = lambda x: (x - 10) // 2
        prof_bonus = lambda x: x // 5 + 2 if x < 5 else (x - 5) // 4 + 3
        # print(f'monster.abilities={self.abilities}')
        # print(f'attack_spell={spell.name} - dc_type={spell.dc_type}')
        # print(f'monster.abilities.get_value_by_index(attack_spell.dc_type)={self.abilities.get_value_by_index(spell.dc_type)}')
        st_type: str = f'saving-throw-{spell.dc_type}'
        prof_modifiers: List[int] = [p.value for p in self.proficiencies if st_type == p.index]
        if prof_modifiers:
            ability_modifier: int = prof_modifiers[0]
            # print(f'standard ability_modifier = {ability_modifier} ')
        else:
            ability_modifier: int = ability_mod(self.abilities.get_value_by_index(spell.dc_type)) + prof_bonus(self.challenge_rating)
            # print(f'special ability_modifier = {ability_modifier} ')
        return randint(1, 20) + ability_modifier > dc

    def attack(self, character) -> int:
        """
        :return: damage generated by character's attack (returns 0 if attack missed)
        """
        total_damage: int = 0
        if self.actions:
            melee_attack: Action = choice(self.actions)
            attack_roll = randint(1, 20) + melee_attack.attack_bonus if melee_attack.attack_bonus else randint(1, 20)
            if attack_roll >= character.armor_class:
                if melee_attack.damages:
                    for damage in melee_attack.damages:
                        damage_given: int = 0
                        if 'd' not in damage.dice:
                            dice_count, damage_dice = damage.dice, 6
                            damage_given = sum([randint(1, damage_dice) for _ in range(int(dice_count))])
                        else:
                            dice_count, damage_dice = damage.dice.split('d')
                            if '+' in damage_dice:
                                damage_dice, bonus_damage = map(int, damage_dice.split('+'))
                                damage_given = sum([randint(1, damage_dice) + bonus_damage for _ in range(int(dice_count))])
                            elif '-' in damage_dice:
                                damage_dice, bonus_damage = map(int, damage_dice.split('-'))
                                damage_given = sum([randint(1, damage_dice) - bonus_damage for _ in range(int(dice_count))])
                        cprint(f"{color.RED}{self.name}{color.END} {damage.type.index.replace('ing', 'es')} {color.GREEN}{character.name}{color.END} for {damage_given} hit points!")
                        total_damage += damage_given
            else:
                cprint(f'{self.name} misses {character.name}!')
        return total_damage


""" Character classes """


@dataclass
class Proficiency:
    index: str
    name: str
    value: Optional[int] = None


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

    def __repr__(self):
        return f'{self.index}'


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
class ClassType:
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
    spellcasting_level: int
    spellcasting_ability: str
    can_cast: bool
    spell_slots: dict()
    spells_known: List[int]
    cantrips_known: List[int]

    def __repr__(self):
        return f"{self.index}"


@dataclass
class Feature:
    index: str
    name: str
    class_type: ClassType
    class_level: int
    prerequisites: List[str]
    desc: List[str]


@dataclass
class Level:
    index: str
    class_type: ClassType
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


@dataclass
class Abilities:
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int

    def get_value_by_name(self, name) -> int:
        match name:
            case 'Strength':
                return self.str
            case 'Dexterity':
                return self.dex
            case 'Constitution':
                return self.con
            case 'Intelligence':
                return self.int
            case 'Wisdom':
                return self.wis
            case 'Charism':
                return self.cha

    def set_value_by_name(self, name, value):
        match name:
            case 'Strength':
                self.str = value
            case 'Dexterity':
                self.dex = value
            case 'Constitution':
                self.con = value
            case 'Intelligence':
                self.int = value
            case 'Wisdom':
                self.wis = value
            case 'Charism':
                self.cha = value

    def get_value_by_index(self, name) -> int:
        match name:
            case 'str':
                return self.str
            case 'dex':
                return self.dex
            case 'con':
                return self.con
            case 'int':
                return self.int
            case 'wis':
                return self.wis
            case 'cha':
                return self.cha

    def set_value_by_index(self, name, value):
        match name:
            case 'str':
                self.str = value
            case 'dex':
                self.dex = value
            case 'con':
                self.con = value
            case 'int':
                self.int = value
            case 'wis':
                self.wis = value
            case 'cha':
                self.cha = value

    def __repr__(self):
        return f'str: {self.str} dex: {self.dex} con: {self.con} int: {self.int} wis: {self.wis} cha: {self.cha}'


@dataclass
class Damage:
    type: DamageType
    dice: str


@dataclass
class Spell:
    index: str
    name: str
    desc: str
    level: int
    allowed_classes: List[str]
    damage_type: DamageType  # For saving throw
    damage_at_slot_level: dict()
    damage_at_character_level: dict()
    dc_type: str
    dc_success: str

    def __repr__(self):
        return f'{self.name} dc: {self.dc_type} lvl: {self.level}'# {self.allowed_classes}'

    def get_spell_damage(self, char: Character) -> Tuple[DamageType, str, int]:
        # TODO modify request_class() in populate_functions to put int instead of str
        # print(self)
        damage_dice: str = None
        if self.damage_at_slot_level:
            damage_dice = self.damage_at_slot_level.get(str(self.level))
        else:
            if str(char.level) in self.damage_at_character_level:
                damage_dice = self.damage_at_character_level.get(str(char.level))
            else:
                for level in range(char.level, -1, -1):
                    if str(level) in self.damage_at_character_level:
                        damage_dice = self.damage_at_character_level.get(str(level))
                        break
        # print(f'{self.index} -> damage_dice = {damage_dice}')
        if damage_dice and '+' in damage_dice:
            damage_dice, damage_bonus = damage_dice.split('+')
            if 'MOD' in damage_bonus:
                damage_bonus = int(char.ability_modifiers.get_value_by_index(name=char.class_type.spellcasting_ability))
        else:
            damage_dice, damage_bonus = damage_dice, 0
        return self.damage_type, damage_dice.rstrip() if damage_dice else None, int(damage_bonus)


class ActionType(Enum):
    MELEE = 'melee'
    RANGED = 'ranged'
    ABILITY = 'ability'
    MAGIC = 'magic'


@dataclass
class Action:
    name: str
    desc: str
    type: ActionType
    attack_bonus: Optional[int]
    multi_attack: Optional[List[Action]]
    damages: Optional[List[Damage]]


@dataclass
class Character:
    name: str
    race: Race
    subrace: SubRace
    ethnic: str
    gender: str
    height: str
    weight: str
    age: int
    class_type: ClassType
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
    spell_slots: List[int]
    learned_spells: List[Spell]
    status: str = 'OK'
    id_party: int = -1
    OUT: bool = False

    # armor: Armor = field(init=False)
    # weapon: Weapon = field(init=False)

    # def __post_init__(self):
    #     self.armor = [equipment for equipment in self.inventory if equipment.category == 'armor' and equipment.equiped]
    #     self.weapon = [equipment for equipment in self.inventory if equipment.category == 'weapon' and equipment.equiped]

    @property
    def in_dungeon(self):
        return self.id_party != -1

    @property
    def attributes(self):
        return [self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charism]

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
        return f"{self.name} - Age: {self.age // 52} - Abilities: {self.abilities} - Ability modifiers: {self.ability_modifiers} - ({ethnic}{self.gender} {race.name} - height: {self.height} weight: {self.weight}- class: {self.class_type} - AC {self.armor_class} Damage: {self.damage_dice} - w: {self.weapon.name} a: {self.armor.name} - potions: {len(self.healing_potions)})"

    @property
    def armor_class(self):
        return self.armor.armor_class['base']

    @property
    def damage_dice(self):
        return self.weapon.damage_dice

    """Healing (??? check rules): A Healing potion repairs one six-sided die, plus one, (2-7) points of damage, just like a Cure Light Wounds spell."""

    def drink_potion(self):
        hp_to_recover = self.max_hit_points - self.hit_points
        available_potions = [p for p in self.healing_potions if p.max_hp_restored >= hp_to_recover]
        best_potion: Potion = min(available_potions, key=lambda p: p.max_hp_restored) if available_potions else max(self.healing_potions, key=lambda p: p.max_hp_restored)
        self.healing_potions.remove(best_potion)
        dice_count, roll_dice = map(int, best_potion.hit_dice.split('d'))
        hp_restored = 2 + randint(1, roll_dice) + randint(1, roll_dice)
        self.hit_points = min(self.hit_points + hp_restored, self.max_hit_points)
        if hp_to_recover <= hp_restored:
            cprint(f'{self.name} drinks healing potion and is {color.BOLD}*fully*{color.END} healed!')
        else:
            cprint(f'{self.name} drinks healing potion and has {min(hp_to_recover, hp_restored)} hit points restored!')

    def victory(self, monster: Monster):
        self.xp += monster.xp
        self.monster_kills += 1
        gold_dice = randint(1, 3)
        gold_msg: str = ''
        if gold_dice == 1:
            max_gold: int = max(1, floor(10 * monster.xp / monster.level))
            gold: int = randint(1, max_gold + 1)
            gold_msg = f' and found {gold} gp!'
            self.gold += gold
        cprint(f'{monster.name.title()} is ** KILLED **!')
        cprint(f'{self.name} gained {monster.xp} XP{gold_msg}!')

    def treasure(self, weapons, armors):
        treasure_dice = randint(1, 3)
        if treasure_dice == 1:
            cprint(f"{self.name} found a healing potion!")
            self.healing_potions.append(Potion('2d4'))
        elif treasure_dice == 2:
            new_weapon: Weapon = choice(weapons)
            if new_weapon.damage_dice > self.weapon.damage_dice:
                cprint(f"{self.name} found a better weapon {new_weapon}!")
                self.weapon = new_weapon
        else:
            new_armor: Armor = choice(armors)
            if new_armor.armor_class['base'] > self.armor.armor_class['base']:
                cprint(f"{self.name} found a better armor {new_armor}!")
                self.armor = new_armor

    def gain_level_arena(self, pause: bool):
        self.level += 1
        hp_gained = randint(1, 10)
        self.max_hit_points += hp_gained
        self.hit_points += hp_gained
        print(f'{color.BLUE}New level #{self.level} gained!!!{color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        if pause:
            input(f'{color.UNDERLINE}{color.DARKCYAN}hit Enter to continue adventure :-) (potions remaining: {len(self.healing_potions)}){color.END}')

    def gain_level(self, tome_spells: List[Spell] = None):
        self.level += 1
        hp_gained = randint(1, 10)
        self.max_hit_points += hp_gained
        self.hit_points += hp_gained
        print(f'{color.BLUE}New level #{self.level} gained!!!{color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        #  PROCEDURE GAINLOST;  (* P010A20 *)
        attributes: List[str] = ['Strength', 'Dexterity', 'Constitution', 'Intelligence', 'Wisdom', 'Charism']
        for attr_name in attributes:
            attr_value: int = self.abilities.get_value_by_name(name=attr_name)
            if randint(0, 3) % 4:
                if randint(0, 129) < self.age // 52:
                    if attr_value == 18 and randint(0, 5) != 4:
                        continue
                    attr_value -= 1
                    if attr_name == 'Constitution' and attr_value == 2:
                        print('** YOU HAVE DIED OF OLD AGE **')
                        self.status = 'LOST'
                        self.hit_points = 0
                    else:
                        print(f'You lost {attr_name}')
                elif attr_value < 18:
                    attr_value += 1
                    print(f'You gained {attr_name}')
            self.abilities.set_value_by_name(name=attr_name, value=attr_value)
        if self.class_type.can_cast:
            available_spell_levels: List[int] = [i + 1 for i, slot in enumerate(self.class_type.spell_slots[self.level]) if slot > 0]
            new_spells_known_count: int = self.class_type.spells_known[self.level - 1] - self.class_type.spells_known[self.level - 2]
            new_cantric_spells_count: int = self.class_type.cantrips_known[self.level - 1] - self.class_type.cantrips_known[self.level - 2]
            learnable_spells: List[Spell] = [s for s in tome_spells if s.level <= max(available_spell_levels) and s not in self.learned_spells and s.damage_type]
            self.spell_slots = deepcopy(self.class_type.spell_slots[self.level])
            learnable_spells.sort(key=lambda s: s.level)
            new_spells_count: int = 0
            while learnable_spells and (new_spells_known_count or new_cantric_spells_count):
                learned_spell: Spell = learnable_spells.pop()
                if learned_spell.level == 0 and new_cantric_spells_count > 0:
                    new_cantric_spells_count -= 1
                    self.learned_spells.append(learned_spell)
                elif learned_spell.level > 0 and new_cantric_spells_count > 0:
                    new_spells_known_count -= 1
                    self.learned_spells.append(learned_spell)
                new_spells_count += 1
            if new_spells_count:
                print(f'You learned new Spells!!!')

    def update_spell_slots(self, casted_spell: Spell):
        match self.class_type.name:
            case 'Warlock':
                # all of your spell slots are the same level
                for level, slot in enumerate(self.spell_slots):
                    if slot:
                        self.spell_slots[level] -= 1
            case _:
                self.spell_slots[casted_spell.level - 1] -= 1

    def attack(self, monster: Monster, order: int):
        """
        :return: damage generated
        """
        damage_roll = 0
        cantric_spells: List[Spell] = [s for s in self.learned_spells if not s.level]
        slot_spells: List[Spell] = [s for s in self.learned_spells if s.level and self.spell_slots[s.level - 1] > 0]
        castable_spells: List[Spell] = cantric_spells + slot_spells
        if castable_spells:
            # TODO modify spell_slots to [] for non casters
            attack_spell: Spell = max(castable_spells, key=lambda s: s.level)
            # print(attack_spell)
            self.update_spell_slots(casted_spell=attack_spell)
            damage_type, damage_dice, damage_bonus = attack_spell.get_spell_damage(char=self)
            dice_count, roll_dice = map(int, damage_dice.split('d'))
            damage_roll = sum([randint(1, roll_dice) for _ in range(dice_count)]) + damage_bonus
            cprint(f'{color.GREEN}{self.name}{color.END} ** CAST SPELL {attack_spell.name.upper()} **')
            if attack_spell.dc_type is None:
                # No saving throw available for this spell!
                cprint(f'{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!')
            else:
                # 1 - Calculate spell's DC (Difficulty Class) for saving throw
                prof_bonus_char = lambda x: x // 4 + 1
                # TODO Your Spell Save DC = 8 + your Spellcasting Ability modifier + your Proficiency Bonus + any Special Modifiers (???)
                # print(f'name={self.class_type.spellcasting_ability}')
                # print(f'value={self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability)}')
                spell_casting_ability_modifier: int = int(self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability))
                prof_bonus: int = prof_bonus_char(self.level)
                dc: int = 8 + spell_casting_ability_modifier + prof_bonus
                st_success: bool = monster.saving_throw(dc=dc, spell=attack_spell)
                if st_success:
                    cprint(f'{color.RED}{monster.name}{color.END} resists the Spell!')
                    if attack_spell.dc_success == 'half':
                        damage_roll //= 2
                        cprint(f'{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!')
                    elif attack_spell.dc_success == 'none':
                        damage_roll = 0
                else:
                    cprint(f'{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!')
        else:
            attack_roll = randint(1, 20)
            if attack_roll >= monster.armor_class:
                dice_count, roll_dice = map(int, self.damage_dice.split('d'))
                damage_roll = sum([randint(1, roll_dice) for _ in range(dice_count)])
            if damage_roll:
                cprint(f'{color.GREEN}{self.name}{color.END} hits {color.RED}{monster.name}{color.END} for {damage_roll} hit points!')
            else:
                cprint(f'{self.name} misses {monster.name}!')
        return damage_roll
