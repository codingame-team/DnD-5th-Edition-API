from __future__ import annotations

from copy import deepcopy, copy
from dataclasses import dataclass, field
from enum import Enum
from math import floor, prod
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
    sc: SpellCaster | None
    sa: List[SpecialAbility] | None

    def __repr__(self):
        return f"{self.name} (AC {self.armor_class} HD: {self.hit_dice} CR: {self.challenge_rating})"

    @property
    def can_cast(self) -> bool:
        return self.sc is not None

    @property
    def dc_value(self):
        return self.sc.dc_value

    @property
    def level(self) -> int:
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return dice_count * roll_dice

    def __copy__(self):
        return Monster(self.name, self.abilities, self.proficiencies, self.armor_class, self.hit_points, self.hit_dice,
                       self.xp, self.challenge_rating, self.actions, copy(self.sc), self.sa)

    def saving_throw(self, dc_type: str, dc_value: int) -> bool:
        """
            Determine resistance from a spell casted by a character
        :param dc_type: ability needed for ST
        :param dc_value: difficulty class
        :return:
        """
        # 2 - Calculate saving throw of monster
        st_type: str = f'saving-throw-{dc_type}'
        prof_modifiers: List[int] = [
            p.value for p in self.proficiencies if st_type == p.index]
        ability_modifier: int = prof_modifiers[0] if prof_modifiers else 0
        return randint(1, 20) + ability_modifier > dc_value

    def spell_attack(self, character: Character, spell: Spell) -> int:
        """
        :return: damage generated by monster's attack (returns 0 if attack missed)
        """
        # TODO modify spell_slots to [] for non casters
        total_damage: int = 0
        if spell.level > 0:
            self.sc.spell_slots[spell.level - 1] -= 1
        damage_dices: List[DamageDice] = spell.get_spell_damages(caster_level=self.sc.level,
                                                                 ability_modifier=self.sc.ability_modifier)
        for dd in damage_dices:
            total_damage += dd.roll()
        cprint(f'{color.GREEN}{self.name}{color.END} CAST SPELL ** {spell.name.upper()} ** on {character.name}')
        if spell.dc_type is None:
            # No saving throw available for this spell!
            cprint(f'{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!')
        else:
            st_success: bool = character.saving_throw(dc_type=spell.dc_type, dc_value=self.sc.dc_value)
            if st_success:
                cprint(f'{color.RED}{character.name}{color.END} resists the Spell!')
                if spell.dc_success == 'half':
                    total_damage //= 2
                    cprint(f'{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!')
                elif spell.dc_success == 'none':
                    total_damage = 0
            else:
                cprint(f'{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!')
        return total_damage

    def special_attack(self, character, sa: SpecialAbility) -> int:
        """
        :return: damage generated by monster's attack (returns 0 if attack missed)
        """
        total_damage: int = 0
        for damage in sa.damages:
            total_damage += damage.dd.roll()

        if sa.dc_type is None:
            # No saving throw available for this attack!
            cprint(f'{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!')
        else:
            st_success: bool = character.saving_throw(dc_type=sa.dc_type,
                                                      dc_value=sa.dc_value)
            if st_success:
                cprint(f'{color.RED}{character.name}{color.END} resists!')
                if sa.dc_success == 'half':
                    total_damage //= 2
                    cprint(f'{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!')
                elif sa.dc_success == 'none':
                    total_damage = 0
            else:
                cprint(f'{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!')
        return total_damage

    def melee_attack(self, character: Character) -> int:
        """
        :return: damage generated by monster's attack (returns 0 if attack missed)
        """
        total_damage: int = 0
        if not self.actions:
            cprint(f"{color.RED}{self.name}{color.END} has no melee attacks implemented!{color.END}")
        else:
            action: Action = choice(self.actions)
            if action.multi_attack:
                cprint(f"{color.RED}{self.name}{color.END} multi-attacks {color.GREEN}{character.name}!{color.END}")
                attacks: List[Action] = [a for a in action.multi_attack]
            else:
                attacks: List[Action] = [action]
            for attack in attacks:
                attack_roll = randint(1, 20) + attack.attack_bonus if attack.attack_bonus else randint(1, 20)
                if attack_roll >= character.armor_class:
                    if attack.damages:
                        for damage in attack.damages:
                            damage_given = damage.dd.roll()
                            total_damage += damage_given
                            cprint(f"{color.RED}{self.name}{color.END} {damage.type.index.replace('ing', 'es')} {color.GREEN}{character.name}{color.END} for {damage_given} hit points!")
                    if attack.effects:
                        character.conditions = [copy(e) for e in attack.effects]
                        for e in character.conditions:
                            if e.index == 'restrained':
                                e.creature = self
                        effects: str = ' and '.join([e.index for e in attack.effects])
                        cprint(f'{color.RED}{character.name}{color.END} is {effects}!')
                else:
                    cprint(f'{self.name} misses {character.name}!')
        return total_damage


""" Character classes """


class ProfType(Enum):
    SKILL = 'Skills'
    ARMOR = 'Armor'
    VEHICLE = 'Vehicles'
    OTHER = 'Other'
    TOOLS = 'Artisan\'s Tools'
    ST = 'Saving Throws'
    WEAPON = 'Weapons'
    MUSIC = 'Musical Instruments'
    GAMING = 'Gaming Sets'


@dataclass
class Proficiency:
    index: str
    name: str
    type: ProfType
    ref: object  # Equipment | List[Equipment] | AbilityType
    classes: Optional[List[str]] = None
    races: Optional[List[str]] = None
    value: Optional[int] = None

    def __repr__(self):
        return f'{self.name} - {self.type}'


# @dataclass
# class Inventory:
#     weapons: List[Weapon]
#     armors: List[Armor]
#     pass

class PotionRarity(Enum):
    COMMON = 60
    UNCOMMON = 80
    RARE = 95
    VERY_RARE = 100


@dataclass
class Potion:
    name: str
    hit_dice: str
    bonus: int
    rarity: PotionRarity

    @property
    def min_hp_restored(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return self.bonus + dice_count

    @property
    def max_hp_restored(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        return self.bonus + dice_count * roll_dice


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

    # equipments: List[Equipment]

    def __repr__(self):
        # e_list: List[str] = [e.index for e in self.equipments]
        return f"{self.index}"  # {e_list}"


@dataclass
class Equipment:
    index: str
    name: str
    cost: Cost
    weight: int
    desc: Optional[List[str]]
    category: EquipmentCategory
    equipped: bool = field(init=False)

    def __repr__(self):
        return f"{self.index} {self.category}"


@dataclass
class Inventory:
    quantity: str
    equipment: Equipment | EquipmentCategory

    def __repr__(self):
        return f"{self.quantity} {self.equipment.index}"


@dataclass
class WeaponProperty:
    index: str
    name: str
    desc: str


@dataclass
class WeaponThrowRange:
    normal: int
    long: int


@dataclass
class WeaponRange:
    normal: int
    long: Optional[int]


class CategoryType(Enum):
    SIMPLE = 'Simple'
    MARTIAL = 'Martial'


class RangeType(Enum):
    MELEE = 'Melee'
    RANGED = 'Ranged'


@dataclass
class DamageType:
    index: str
    name: str
    desc: str

    def __repr__(self):
        return f'{self.index}'


@dataclass
class Weapon(Equipment):
    properties: List[WeaponProperty]
    damage_type: DamageType
    range_type: RangeType
    category_type: CategoryType
    damage_dice: DamageDice
    damage_dice_two_handed: Optional[DamageDice]
    damage_type: str
    range: WeaponRange
    throw_range: WeaponThrowRange
    is_magic: bool
    category_range: str = field(init=False)

    def __post_init__(self):
        self.category_range = f'{self.category_type.value} {self.range_type.value}'

    def __repr__(self):
        return f"{self.index} ({self.category})"


@dataclass
class Armor(Equipment):
    armor_class: dict()
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
    dd: DamageDice

@dataclass
class Condition:
    index: str
    name: str
    desc: str
    dc_type: AbilityType = None
    dc_value: int = None
    creature: Monster = None

    def __copy__(self):
        return Condition(self.index, self.name, self.desc, self.dc_type, self.dc_value, self.creature)

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
        # {self.allowed_classes}'
        return f'{self.name} dc: {self.dc_type} lvl: {self.level}'

    def get_spell_damages(self, caster_level: int, ability_modifier: int) -> List[DamageDice]:
        # TODO modify request_class() in populate_functions to put int instead of str
        damage_dices: List[DamageDice] = []
        if self.damage_at_slot_level:
            damage_dice: str = self.damage_at_slot_level.get(str(self.level))
        else:
            if str(caster_level) in self.damage_at_character_level:
                damage_dice: str = self.damage_at_character_level.get(str(caster_level))
            else:
                for level in range(caster_level, -1, -1):
                    if str(level) in self.damage_at_character_level:
                        damage_dice: str = self.damage_at_character_level.get(str(level))
                        break
        # print(f'{self.index} -> damage_dice = {damage_dice}')
        if damage_dice and '+' in damage_dice:
            if damage_dice.count('d') == 0:
                damage_dices.append(DamageDice(dice=None, bonus=int(damage_dice)))
            elif damage_dice.count('d') > 1:
                for dd in damage_dice.split('+'):
                    damage_dices.append(DamageDice(dice=dd.strip()))
            else:
                damage_dice, damage_bonus = damage_dice.split('+')
                if 'MOD' in damage_bonus:
                    damage_bonus = ability_modifier
                else:
                    damage_bonus = int(damage_bonus.strip())
                damage_dices.append(DamageDice(dice=damage_dice, bonus=damage_bonus))
        else:
            damage_dices.append(DamageDice(dice=damage_dice, bonus=0))
        return damage_dices


class ActionType(Enum):
    MELEE = 'melee'
    RANGED = 'ranged'
    SPECIAL = 'special'
    # ABILITY = 'ability'
    # MAGIC = 'magic'



@dataclass
class SpecialAbility:
    name: str
    desc: str
    damages: List[Damage]
    dc_type: str
    dc_value: int
    dc_success: str
    recharge_on_roll: Optional[int]
    range: RangeType = None
    ready: int = True
    effects: List[Condition] = None
    targets_count: int = 6

    def __repr__(self):
        return f'{self.name} dc: {self.dc_type} damages: {self.damages}'

    @property
    def recharge_success(self) -> bool:
        return randint(1, 6) >= self.recharge_on_roll


@dataclass
class SpellCaster:
    level: int
    spell_slots: List[int]
    learned_spells: List[Spell]
    # dc: int
    dc_type: str
    dc_value: int | None
    ability_modifier: int | None

    def __copy__(self):
        return SpellCaster(self.level, self.spell_slots[:], self.learned_spells, self.dc_type, self.dc_value,
                           self.ability_modifier)


@dataclass
class Action:
    name: str
    desc: str
    type: ActionType
    attack_bonus: int | None
    multi_attack: List[Action] | None  # used for MELEE and RANGED attacks
    damages: List[Damage] | None
    effects: List[Condition] = None


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
    sc: SpellCaster | None
    conditions: List[Condition] | None
    status: str = 'OK'
    id_party: int = -1
    OUT: bool = False

    @property
    def can_cast(self) -> bool:
        #return hasattr(self, 'sc')
        return self.sc is not None

    @property
    def dc_value(self):
        # TODO Your Spell Save DC = 8 + your Spellcasting Ability modifier + your Proficiency Bonus + any Special Modifiers (???)
        def prof_bonus_char(x): return x // 4 + 1

        spell_casting_ability_modifier: int = int(
            self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability))
        prof_bonus: int = prof_bonus_char(self.level)
        return 8 + spell_casting_ability_modifier + prof_bonus

    @property
    def in_dungeon(self):
        return self.id_party != -1

    @property
    def attributes(self):
        return [self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charism]

    @property
    def strength(self):
        return self.abilities.str if 'str' not in self.race.ability_bonuses else self.abilities.str + \
                                                                                 self.race.ability_bonuses['str']

    @property
    def dexterity(self):
        return self.abilities.dex if 'dex' not in self.race.ability_bonuses else self.abilities.dex + \
                                                                                 self.race.ability_bonuses['dex']

    @property
    def constitution(self):
        return self.abilities.con if 'con' not in self.race.ability_bonuses else self.abilities.con + \
                                                                                 self.race.ability_bonuses['con']

    @property
    def intelligence(self):
        return self.abilities.int if 'int' not in self.race.ability_bonuses else self.abilities.int + \
                                                                                 self.race.ability_bonuses['int']

    @property
    def wisdom(self):
        return self.abilities.wis if 'wis' not in self.race.ability_bonuses else self.abilities.wis + \
                                                                                 self.race.ability_bonuses['wis']

    @property
    def charism(self):
        return self.abilities.cha if 'cha' not in self.race.ability_bonuses else self.abilities.cha + \
                                                                                 self.race.ability_bonuses['cha']

    def __repr__(self):
        race = self.subrace if self.subrace else self.race
        ethnic = f'ethnic: {self.ethnic} - ' if self.ethnic else ''
        return f"{self.name} - Age: {self.age // 52} - Abilities: {self.abilities} - Ability modifiers: {self.ability_modifiers} - ({ethnic}{self.gender} {race.name} - height: {self.height} weight: {self.weight}- class: {self.class_type} - AC {self.armor_class} Damage: {self.damage_dice} - w: {self.weapon.name} a: {self.armor.name} - potions: {len(self.healing_potions)})"

    @property
    def armor_class(self):
        return self.armor.armor_class['base']

    @property
    def damage_dice(self) -> DamageDice:
        """TODO Two handed weapon not possible with a shield """
        # print(f'error {self.weapon}')
        return self.weapon.damage_dice_two_handed if self.weapon.damage_dice_two_handed else self.weapon.damage_dice

    def drink_potion(self):
        """Healing (??? check rules): A Healing potion repairs one six-sided die, plus one, (2-7) points of damage, just like a Cure Light Wounds spell."""
        hp_to_recover = self.max_hit_points - self.hit_points
        available_potions = [
            p for p in self.healing_potions if p.max_hp_restored >= hp_to_recover]
        best_potion: Potion = min(available_potions, key=lambda p: p.max_hp_restored) if available_potions else max(
            self.healing_potions, key=lambda p: p.max_hp_restored)
        self.healing_potions.remove(best_potion)
        dice_count, roll_dice = map(int, best_potion.hit_dice.split('d'))
        hp_restored = best_potion.bonus + \
                      sum([randint(1, roll_dice) for _ in range(dice_count)])
        self.hit_points = min(
            self.hit_points + hp_restored, self.max_hit_points)
        if hp_to_recover <= hp_restored:
            cprint(
                f'{self.name} drinks {best_potion.name} potion and is {color.BOLD}*fully*{color.END} healed!')
        else:
            cprint(
                f'{self.name} drinks {best_potion.name} potion and has {min(hp_to_recover, hp_restored)} hit points restored!')

    def victory(self, monster: Monster, solo_mode=False):
        self.xp += monster.xp
        self.monster_kills += 1
        gold_msg: str = ''
        if solo_mode:
            gold_dice = randint(1, 3)
            if gold_dice == 1:
                max_gold: int = max(1, floor(10 * monster.xp / monster.level))
                gold: int = randint(1, max_gold + 1)
                gold_msg = f' and found {gold} gp!'
                self.gold += gold
        cprint(f'{monster.name.title()} is ** KILLED **!')
        cprint(f'{self.name} gained {monster.xp} XP{gold_msg}!')

    @property
    def allowed_weapons(self) -> List[Weapon]:
        weapons: List[Weapon] = []
        for p in self.proficiencies:
            if p.type == ProfType.WEAPON:
                weapons += p.ref if isinstance(p.ref, List) else [p.ref]
        return list(filter(None, weapons))

    @property
    def allowed_armors(self) -> List[Weapon]:
        armors: List[Armor] = []
        for p in self.proficiencies:
            if p.type == ProfType.ARMOR:
                armors += p.ref if isinstance(p.ref, List) else [p.ref]
        return list(filter(None, armors))

    def treasure(self, weapons, armors, equipments: List[Equipment], potions, solo_mode=False):
        treasure_dice = randint(1, 3)
        if treasure_dice == 1:
            potion = choice(potions)
            cprint(f"{self.name} found a {potion.name} potion!")
            self.healing_potions.append(choice(potions))
        elif treasure_dice == 2:
            new_weapon: Weapon = choice(self.allowed_weapons)
            if new_weapon.damage_dice > self.weapon.damage_dice:
                cprint(f"{self.name} found a better weapon {new_weapon}!")
                self.weapon = new_weapon
            else:
                cprint(
                    f"{self.name} found a lesser weapon {new_weapon}! ** SKIPPING IT **")
        else:
            if self.allowed_armors:
                new_armor: Armor = choice(self.allowed_armors)
                if new_armor.armor_class['base'] > self.armor.armor_class['base']:
                    cprint(f"{self.name} found a better armor {new_armor}!")
                    self.armor = new_armor
                else:
                    cprint(
                        f"{self.name} found a lesser armor {new_armor}! ** SKIPPING IT **")
            else:
                cprint(
                    f"{self.class_type.name} not allowed to wear an armor! ** SKIPPING IT **")
            # if better_armors:
            #     new_armor: Armor = choice(better_armors)
            #     try:
            #         if new_armor.armor_class['base'] > self.armor.armor_class['base']:
            #             cprint(f"{self.name} found a better armor {new_armor}!")
            #             self.armor = new_armor
            #         else:
            #             cprint(f"{self.name} found a lesser armor {new_armor}! ** SKIPPING IT **")
            #     except AttributeError:
            #         cprint(f"** SYSTEM ERROR ** {new_armor} has no attribute1 ! ** SKIPPING IT **")
            # else:
            #     cprint(f"** SYSTEM ERROR ** {self.name} cannot find armor ! ** SKIPPING IT **")

    def gain_level_arena(self, pause: bool):
        self.level += 1
        hp_gained = randint(1, 10)
        self.max_hit_points += hp_gained
        self.hit_points += hp_gained
        print(f'{color.BLUE}New level #{self.level} gained!!!{color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        if pause:
            input(
                f'{color.UNDERLINE}{color.DARKCYAN}hit Enter to continue adventure :-) (potions remaining: {len(self.healing_potions)}){color.END}')

    def gain_level(self, tome_spells: List[Spell] = None):
        self.level += 1
        hp_gained = randint(1, 10) + \
                    self.ability_modifiers.get_value_by_index('con')
        self.max_hit_points += hp_gained
        self.hit_points += hp_gained
        print(f'{color.BLUE}New level #{self.level} gained!!!{color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        #  PROCEDURE GAINLOST;  (* P010A20 *)
        attributes: List[str] = ['Strength', 'Dexterity',
                                 'Constitution', 'Intelligence', 'Wisdom', 'Charism']
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
            available_spell_levels: List[int] = [i + 1 for i, slot in enumerate(self.class_type.spell_slots[self.level])
                                                 if slot > 0]
            new_spells_known_count: int = self.class_type.spells_known[self.level - 1] - self.class_type.spells_known[
                self.level - 2]
            new_cantric_spells_count: int = 0
            if self.class_type.cantrips_known:
                new_cantric_spells_count = self.class_type.cantrips_known[self.level - 1] - \
                                           self.class_type.cantrips_known[self.level - 2]
            learnable_spells: List[Spell] = [s for s in tome_spells if s.level <= max(
                available_spell_levels) and s not in self.sc.learned_spells and s.damage_type]
            self.sc.spell_slots = deepcopy(
                self.class_type.spell_slots[self.level])
            learnable_spells.sort(key=lambda s: s.level)
            new_spells_count: int = 0
            while learnable_spells and (new_spells_known_count or new_cantric_spells_count):
                learned_spell: Spell = learnable_spells.pop()
                if learned_spell.level == 0 and new_cantric_spells_count > 0:
                    new_cantric_spells_count -= 1
                    self.sc.learned_spells.append(learned_spell)
                elif learned_spell.level > 0 and new_cantric_spells_count > 0:
                    new_spells_known_count -= 1
                    self.sc.learned_spells.append(learned_spell)
                new_spells_count += 1
            if new_spells_count:
                print(f'You learned new Spells!!!')

    def update_spell_slots(self, casted_spell: Spell):
        match self.class_type.name:
            case 'Warlock':
                # all of your spell slots are the same level
                for level, slot in enumerate(self.sc.spell_slots):
                    if slot:
                        self.sc.spell_slots[level] -= 1
            case _:
                self.sc.spell_slots[casted_spell.level - 1] -= 1

    def attack(self, monster: Monster):
        """
        :return: damage generated
        """
        damage_roll = 0
        if self.can_cast:
            cantric_spells: List[Spell] = [s for s in self.sc.learned_spells if not s.level]
            slot_spells: List[Spell] = [s for s in self.sc.learned_spells if s.level and self.sc.spell_slots[s.level - 1] > 0]
            castable_spells: List[Spell] = cantric_spells + slot_spells
        if self.can_cast and castable_spells:
            # TODO modify spell_slots to [] for non casters
            attack_spell: Spell = max(castable_spells, key=lambda s: s.level)
            # print(attack_spell)
            if attack_spell.level > 0:
                self.update_spell_slots(casted_spell=attack_spell)
            ability_modifier: int = int(self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability))
            damage_dices: List[DamageDice] = attack_spell.get_spell_damages(caster_level=self.level,
                                                                            ability_modifier=ability_modifier)
            damage_roll: int = 0
            for dd in damage_dices:
                damage_roll += dd.roll()
            cprint(f'{color.GREEN}{self.name}{color.END} ** CAST SPELL ** {attack_spell.name.upper()}')
            if attack_spell.dc_type is None:
                # No saving throw available for this spell!
                cprint(f'{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!')
            else:
                st_success: bool = monster.saving_throw(dc_type=self.class_type.spellcasting_ability,
                                                        dc_value=self.dc_value)
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
            multi_attacks = 2 if self.level >= 5 else 3 if self.level >= 11 else 4 if self.level >= 20 else 1
            damage_multi = 0
            for _ in range(multi_attacks):
                if self.hit_points <= 0:
                    break
                attack_roll = randint(1, 20) + self.ability_modifiers.get_value_by_index('str')
                if attack_roll >= monster.armor_class:
                    damage_roll = self.damage_dice.roll()
                if damage_roll:
                    #cprint(f'{color.GREEN}{self.name}{color.END} hits {color.RED}{monster.name}{color.END} for {damage_roll} hit points!')
                    cprint(f"{color.RED}{self.name}{color.END} {self.weapon.damage_type.index.replace('ing', 'es')} {color.GREEN}{monster.name}{color.END} for {damage_roll} hit points!")
                    if any([e for e in self.conditions if e.index == 'restrained']):
                        damage_roll //= 2
                        self.hit_points -= damage_roll
                        cprint(f'{self.name} inflicts himself {damage_roll} hit points!')
                        if self.hit_points <= 0:
                            cprint(f'{self.name} *** IS DEAD ***!')
                    damage_multi += damage_roll
                else:
                    cprint(f'{self.name} misses {monster.name}!')
            damage_roll = damage_multi
        return damage_roll

    def saving_throw(self, dc_type: str, dc_value: int) -> bool:
        """
            Determine resistance from a spell casted by a monster
        :param dc: difficulty class of the caster
        :param spell: spell of the caster
        :return:
        """

        # 2 - Calculate saving throw of monster
        # Determine ability for ST in Spell
        def ability_mod(x):
            return (x - 10) // 2

        def prof_bonus(x):
            return x // 5 + 2 if x < 5 else (x - 5) // 4 + 3

        st_type: str = f'saving-throw-{dc_type}'
        prof_modifiers: List[int] = [p.value for p in self.proficiencies if st_type == p.index]
        if prof_modifiers:
            ability_modifier: int = prof_modifiers[0]
        else:
            ability_modifier: int = ability_mod(self.abilities.get_value_by_index(dc_type)) + prof_bonus(self.level)
        return randint(1, 20) + ability_modifier > dc_value


@dataclass
class DamageDice:
    dice: str
    bonus: int = 0

    @property
    def max_score(self) -> int:
        return self.bonus + prod(map(int, self.dice.split('d')))

    def __eq__(self, other):
        return self.max_score == other.max_score

    def __lt__(self, other):
        return self.max_score < other.max_score

    def __gt__(self, other):
        return self.max_score > other.max_score

    def roll(self) -> int:
        if 'd' not in self.dice:
            # dice_count, damage_dice = int(self.dice), 6
            # return sum([randint(1, damage_dice) for _ in range(dice_count)])
            return int(self.dice)
        else:
            if '+' in self.dice:
                damage_dice, bonus_damage = self.dice.split('+')
                dice_count, damage_dice = map(int, damage_dice.split('d'))
                return sum([randint(1, damage_dice) for _ in range(dice_count)]) + int(bonus_damage)
            elif '-' in self.dice:
                damage_dice, bonus_damage = self.dice.split('-')
                dice_count, damage_dice = map(int, damage_dice.split('d'))
                return sum([randint(1, damage_dice) for _ in range(dice_count)]) - int(bonus_damage)
            else:
                dice_count, damage_dice = map(int, self.dice.split('d'))
                return sum([randint(1, damage_dice) for _ in range(dice_count)])

    def score(self, success_type: str = 'None') -> int:
        dice_count, roll_dice = map(int, self.dice.split('d'))
        factor: int = 1 if success_type in ('none', 'None') else 0.5
        return (self.bonus + roll_dice * (1 + dice_count)) * factor / 2