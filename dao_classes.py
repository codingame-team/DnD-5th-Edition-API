from __future__ import annotations

import time
from abc import ABC, abstractmethod
from copy import deepcopy, copy
from dataclasses import dataclass, field
from enum import Enum
from math import floor, prod
from typing import List, Optional, Tuple
from random import randint, choice

import pygame
from numpy import sign
from pygame import Surface, SurfaceType

from tools.common import cprint, UNIT_SIZE, Color

""" Needs to separate presentation layer from data layer """


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


""" Monster classes """


@dataclass
class Sprite:
    id: int
    image_name: str
    x: int
    y: int
    old_x: int
    old_y: int

    def __repr__(self):
        return f"#{self.id} {self.image_name} ({self.x}, {self.y})"

    @property
    def pos(self) -> tuple:
        return self.x, self.y

    @property
    def old_pos(self) -> tuple:
        return self.old_x, self.old_y

    # def __eq__(self, other: Sprite):
    #     return self.id == other.id

    def check_collision(self, other: Sprite):
        return self.x == other.x and self.y == other.y

    def draw(self, screen, image, tile_size, viewport_x, viewport_y, viewport_width, viewport_height, ):
        if self.image_name:
            # Calculate the position of the sprite relative to the viewport
            draw_x = (self.x - viewport_x) * tile_size
            draw_y = (self.y - viewport_y) * tile_size

            # Check if the sprite is within the viewport boundaries
            if (0 <= draw_x <= viewport_width * tile_size and 0 <= draw_y <= viewport_height * tile_size):
                screen.blit(image, (draw_x, draw_y))

    def draw_effect(self, screen, sprites, tile_size, fps, viewport_x, viewport_y, viewport_width, viewport_height, sound_file=None, reduce_ratio=1, ):
        # Calculate the position of the sprite relative to the viewport
        draw_x = (self.x - viewport_x) * tile_size
        draw_y = (self.y - viewport_y) * tile_size
        # cprint(sprites)
        # cprint(str((draw_x, draw_y)))
        frame_delay = 2 / fps  # Calculate delay between frames

        # sprite_size = sprites[0].get_size()[0]
        # reduce_ratio = sprite_size // (tile_size * 2) if sprite_size > tile_size else 1
        # reduce_ratio = 1

        # Load and play the sound effect if provided
        if sound_file:
            sound = pygame.mixer.Sound(sound_file)
            sound.play()

        while sprites:
            start_time = time.time()  # Get the start time of this frame

            # Get the first sprite
            original_sprite = sprites.pop(0)

            # Get the original dimensions
            original_width, original_height = original_sprite.get_size()

            # Create a new surface with half the dimensions
            reduced_sprite = pygame.transform.scale(original_sprite, (original_width // reduce_ratio, original_height // reduce_ratio), )

            # Calculate the offset to center the sprite on the tile
            offset_x = (tile_size - reduced_sprite.get_width()) // 2
            offset_y = (tile_size - reduced_sprite.get_height()) // 2

            # Adjust the drawing position to center the sprite
            centered_x = draw_x + offset_x
            centered_y = draw_y + offset_y

            # Check if the centered sprite is within the viewport boundaries
            # if 0 <= centered_x <= viewport_width * tile_size and 0 <= centered_y <= viewport_height * tile_size:
            screen.blit(reduced_sprite, (centered_x, centered_y))
            pygame.display.flip()

            # Calculate how long to wait
            elapsed_time = time.time() - start_time
            wait_time = max(frame_delay - elapsed_time, 0)

            # Wait for the remainder of the frame time
            time.sleep(wait_time)

            # Ensure the final frame is displayed for the full duration
        time.sleep(frame_delay)


@dataclass
class Monster(Sprite):
    index: str
    name: str
    abilities: Abilities
    proficiencies: List[Proficiency]
    armor_class: int
    hit_points: int
    hit_dice: str
    xp: int
    speed: int
    challenge_rating: float
    actions: List[Action]
    sc: SpellCaster | None
    sa: List[SpecialAbility] | None
    attack_round: int = 0
    max_hit_points: int = field(init=False)

    def __post_init__(self):
        self.max_hit_points = self.hit_points

    def __repr__(self):
        return f"{self.name} (AC {self.armor_class} HD: {self.hit_dice} HP: {self.hit_points} CR: {self.challenge_rating})"

    def __hash__(self):
        return self.name

    def __lt__(self, other: "Monster"):
        return self.challenge_rating < other.challenge_rating

    def __gt__(self, other: "Monster"):
        return self.challenge_rating > other.challenge_rating

    @property
    def is_spell_caster(self) -> bool:
        return self.sc is not None

    @property
    def dc_value(self):
        return self.sc.dc_value

    @property
    def level(self) -> int:
        hit_dice, bonus = (self.hit_dice.split(" + ") if "+" in self.hit_dice else (self.hit_dice, "0"))
        dice_count, roll_dice = map(int, hit_dice.split("d"))
        return dice_count * roll_dice + int(bonus)

    def __copy__(self):
        return Monster(self.name, self.abilities, self.proficiencies, self.armor_class, self.hit_points, self.hit_dice, self.xp, self.challenge_rating, self.actions, copy(self.sc), self.sa, )

    def hp_roll(self):
        dice_count, roll_dice = map(int, self.hit_dice.split("d"))
        self.hit_points = sum([randint(1, roll_dice) for _ in range(dice_count)])

    def saving_throw(self, dc_type: str, dc_value: int) -> bool:
        """
            Determine resistance from a spell casted by a character
        :param dc_type: ability needed for ST
        :param dc_value: difficulty class
        :return:
        """
        # 2 - Calculate saving throw of monster
        st_type: str = f"saving-throw-{dc_type}"
        prof_modifiers: List[int] = [p.value for p in self.proficiencies if st_type == p.index]
        ability_modifier: int = prof_modifiers[0] if prof_modifiers else 0
        return randint(1, 20) + ability_modifier > dc_value

    def cast_heal(self, spell: Spell, slot_level: int, targets: List[Monster]):
        dd: DamageDice = spell.get_heal_effect(slot_level=slot_level, ability_modifier=self.sc.ability_modifier)
        cprint(f"{color.GREEN}{self.name}{color.END} ** CAST SPELL ** {spell.name.upper()}")
        for char in targets:
            if char.hit_points < char.max_hit_points:
                hp_gained: int = min(dd.roll(), char.max_hit_points - char.hit_points)
                char.hit_points += hp_gained
                cprint(f"{color.RED}{char.name}{color.END} is healed for {hp_gained} hit points!")
                if char.hit_points == char.max_hit_points:
                    cprint(f"{color.RED}{char.name}{color.END} is fully healed!")
            else:
                cprint(f"{color.RED}{char.name}{color.END} is already at full health!")

    def cast_attack(self, character: Character, spell: Spell) -> int:
        """
        :return: damage generated by monster's attack (returns 0 if attack missed)
        """
        # TODO modify spell_slots to [] for non casters
        total_damage: int = 0
        if spell.level > 0:
            self.sc.spell_slots[spell.level - 1] -= 1
        damage_dices: List[DamageDice] = spell.get_spell_damages(caster_level=self.sc.level, ability_modifier=self.sc.ability_modifier)
        for dd in damage_dices:
            total_damage += dd.roll()
        cprint(f"{color.GREEN}{self.name}{color.END} CAST SPELL ** {spell.name.upper()} ** on {character.name}")
        if spell.dc_type is None:
            # No saving throw available for this spell!
            cprint(f"{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!")
        else:
            st_success: bool = character.saving_throw(dc_type=spell.dc_type, dc_value=self.sc.dc_value)
            if st_success:
                cprint(f"{color.RED}{character.name}{color.END} resists the Spell!")
                if spell.dc_success == "half":
                    total_damage //= 2
                    cprint(f"{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!")
                elif spell.dc_success == "none":
                    total_damage = 0
            else:
                cprint(f"{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!")
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
            cprint(f"{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!")
        else:
            st_success: bool = character.saving_throw(dc_type=sa.dc_type, dc_value=sa.dc_value)
            if st_success:
                cprint(f"{color.RED}{character.name}{color.END} resists!")
                if sa.dc_success == "half":
                    total_damage //= 2
                    cprint(f"{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!")
                elif sa.dc_success == "none":
                    total_damage = 0
            else:
                cprint(f"{color.RED}{character.name}{color.END} is hit for {total_damage} hit points!")
        return total_damage

    def attack(self, character: Character, actions: List[Action], distance: float = UNIT_SIZE) -> int:
        """
            MELEE/RANGED/SA Attacks only
        :param character:
        :param actions:
        :param distance:
        :return: damage generated by monster's attack (0 if attack missed)
        """
        total_damage: int = 0
        if not actions:
            cprint(f"{color.RED}{self.name}{color.END} has no attack implemented!{color.END}")
        else:
            action: Action = choice(actions)
            if action.multi_attack:
                cprint(f"{color.RED}{self.name}{color.END} multi-attacks {color.GREEN}{character.name}!{color.END}")
                attacks: List[Action] = [a for a in action.multi_attack]
            else:
                attacks: List[Action] = [action]
            for attack in attacks:
                if isinstance(attack, SpecialAbility):
                    total_damage += self.special_attack(character, attack)
                else:
                    if attack.type == ActionType.MELEE:
                        try:
                            attack_roll = randint(1, 20) + attack.attack_bonus
                        except:
                            attack_roll = randint(1, 20)
                    else:
                        disadvantage: bool = (True if distance <= attack.normal_range else False)
                        # https://roll20.net/compendium/dnd5e/Ability%20Scores?expansion=0#toc_2
                        if not disadvantage:
                            attack_roll = randint(1, 20) + attack.attack_bonus
                        else:
                            attack_roll = min([randint(1, 20) + attack.attack_bonus for _ in range(2)])
                    if attack_roll >= character.armor_class:
                        if attack.damages:
                            for damage in attack.damages:
                                damage_given = damage.dd.roll()
                                total_damage += damage_given
                                cprint(f"{color.RED}{self.name}{color.END} {damage.type.index.replace('ing', 'es')} {color.GREEN}{character.name}{color.END} for {damage_given} hit points!")
                        if attack.effects:
                            character.conditions = [copy(e) for e in attack.effects]
                            for e in character.conditions:
                                if e.index == "restrained":
                                    e.creature = self
                            effects: str = " and ".join([e.index for e in attack.effects])
                            cprint(f"{color.RED}{character.name}{color.END} is {effects}!")
                    else:
                        cprint(f"{self.name} misses {character.name}!")
        return total_damage


""" Character classes """


class ProfType(Enum):
    SKILL = "Skills"
    ARMOR = "Armor"
    VEHICLE = "Vehicles"
    OTHER = "Other"
    TOOLS = "Artisan's Tools"
    ST = "Saving Throws"
    WEAPON = "Weapons"
    MUSIC = "Musical Instruments"
    GAMING = "Gaming Sets"


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
        return f"{self.name} - {self.type}"


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
    SIMPLE = "Simple"
    MARTIAL = "Martial"


class RangeType(Enum):
    MELEE = "Melee"
    RANGED = "Ranged"


@dataclass
class DamageType:
    index: str
    name: str
    desc: str

    def __repr__(self):
        return f"{self.index}"


@dataclass
class Cost:
    quantity: int
    unit: str

    @property
    def value(self) -> int:
        rates = {"sp": 10, "ep": 50, "gp": 100, "pp": 1000}
        return self.quantity * rates.get(self.unit, 1)  # value in copper pieces

    def __repr__(self):
        return f"{self.quantity} {self.unit}"


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
class Equipment(Sprite):
    index: str
    name: str
    cost: Cost
    weight: int
    desc: Optional[List[str]]
    category: EquipmentCategory
    equipped: bool

    @property
    def price(self):
        # buy value in cp
        return self.cost.value

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"#{self.id} {self.index} ({self.category})"


@dataclass
class Inventory:
    quantity: str
    equipment: Equipment | EquipmentCategory

    def __repr__(self):
        return f"{self.quantity} {self.equipment.index}"


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
        self.category_range = f"{self.category_type.value} {self.range_type.value}"

    def __repr__(self):
        return self.name


@dataclass
class Armor(Equipment):
    armor_class: dict()
    str_minimum: int
    stealth_disadvantage: bool

    def __repr__(self):
        return self.name


class PotionRarity(Enum):
    COMMON = 60
    UNCOMMON = 80
    RARE = 95
    VERY_RARE = 99
    LEGENDARY = 100


class Potion(ABC, Sprite):
    def __init__(self, id: int, image_name: str, x: int, y: int, old_x: int, old_y: int, name: str, rarity: PotionRarity, min_cost: int, max_cost: int, min_level: int = 1, ):
        # Initialize Sprite class
        super().__init__(id, image_name, x, y, old_x, old_y)

        # Initialize Potion-specific fields
        self.name = name
        self.rarity = rarity
        self.min_cost = min_cost
        self.max_cost = max_cost
        self.min_level = min_level
        self.cost = Cost(randint(self.min_cost, self.max_cost), "gp")

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        result.rarity = copy(self.rarity)
        result.cost = copy(self.cost)
        return result

    @abstractmethod
    def effect(self):
        pass


class StrengthPotion(Potion):
    def __init__(self, id: int, image_name: str, x: int, y: int, old_x: int, old_y: int, name: str, rarity: PotionRarity, min_cost: int, max_cost: int, value: int, duration: int, min_level: int = 1, ):
        super().__init__(id, image_name, x, y, old_x, old_y, name, rarity, min_cost, max_cost, min_level, )
        self.value = value
        self.duration = duration

    def effect(self):
        return f"Increases strength to {self.value} for {self.duration // 60} minutes"


class SpeedPotion(Potion):
    def __init__(self, id: int, image_name: str, x: int, y: int, old_x: int, old_y: int, name: str, rarity: PotionRarity, min_cost: int, max_cost: int, duration: int, min_level: int = 1, ):
        super().__init__(id, image_name, x, y, old_x, old_y, name, rarity, min_cost, max_cost, min_level, )
        self.duration = duration

    def effect(self):
        return f"Increases speed for {self.duration} seconds"


class HealingPotion(Potion):
    def __init__(self, id: int, image_name: str, x: int, y: int, old_x: int, old_y: int, name: str, rarity: PotionRarity, hit_dice: str, bonus: int, min_cost: int, max_cost: int, min_level: int = 1, ):
        super().__init__(id, image_name, x, y, old_x, old_y, name, rarity, min_cost, max_cost, min_level, )
        self.hit_dice = hit_dice
        self.bonus = bonus

    def effect(self):
        return f"Restores {self.min_hp_restored} to {self.max_hp_restored} HP"

    @property
    def min_hp_restored(self):
        dice_count, roll_dice = map(int, self.hit_dice.split("d"))
        return self.bonus + dice_count * roll_dice

    @property
    def max_hp_restored(self):
        dice_count, roll_dice = map(int, self.hit_dice.split("d"))
        return self.bonus + dice_count * roll_dice

    @property
    def score(self) -> float:
        return (self.min_hp_restored + self.max_hp_restored) / 2 + self.bonus



class AbilityType(Enum):
    STR = "str"
    CON = "con"
    DEX = "dex"
    INT = "int"
    WIS = "wis"
    CHA = "cha"


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
        attr_map = {"Strength": "str", "Dexterity": "dex", "Constitution": "con", "Intelligence": "int", "Wisdom": "wis", "Charism": "cha"}
        return getattr(self, attr_map[name])

    def set_value_by_name(self, name, value):
        attr_map = {"Strength": "str", "Dexterity": "dex", "Constitution": "con", "Intelligence": "int", "Wisdom": "wis", "Charism": "cha"}
        setattr(self, attr_map[name], value)

    def get_value_by_index(self, name) -> int:
        return getattr(self, name)

    def set_value_by_index(self, name, value):
        setattr(self, name, value)

    def __repr__(self):
        return f"str: {self.str} dex: {self.dex} con: {self.con} int: {self.int} wis: {self.wis} cha: {self.cha}"


@dataclass
class Damage:
    type: DamageType
    dd: DamageDice


@dataclass
class Condition:
    index: str
    name: str = ""
    desc: str = ""
    dc_type: AbilityType = None
    dc_value: int = None
    creature: Monster = None

    def __copy__(self):
        return Condition(self.index, self.name, self.desc, self.dc_type, self.dc_value, self.creature)


@dataclass
class AreaOfEffect:
    type: str  # sphere, cube, ...
    size: int


@dataclass
class Spell:
    index: str
    name: str
    desc: str
    level: int
    allowed_classes: List[str]
    heal_at_slot_level: Optional[dict]
    damage_type: Optional[DamageType]  # For saving throw
    damage_at_slot_level: Optional[dict]
    damage_at_character_level: Optional[dict]
    dc_type: Optional[str]
    dc_success: Optional[str]
    range: int
    area_of_effect: Optional[AreaOfEffect]
    school: str
    id: int = -1

    def __repr__(self):
        # {self.allowed_classes}'
        return f"{self.name} dc: {self.dc_type} lvl: {self.level}"

    def __eq__(self, other):
        return self.index == other.index

    @property
    def is_cantrip(self) -> bool:
        return self.level == 0

    def get_heal_effect(self, slot_level: int, ability_modifier: int) -> DamageDice:
        heal_dice: str = self.heal_at_slot_level.get(str(slot_level + 1))
        if 'd' not in heal_dice:
            return DamageDice(dice=None, bonus=int(heal_dice))

        if '+' not in heal_dice:
            return DamageDice(dice=heal_dice, bonus=0)

        dice, bonus = heal_dice.split("+")
        bonus = ability_modifier if bonus.strip() == "MOD" else int(bonus.strip())
        return DamageDice(dice=dice, bonus=bonus)

    def get_spell_damages(self, caster_level: int, ability_modifier: int) -> List[DamageDice]:
        if self.damage_at_slot_level:
            damage_dice = self.damage_at_slot_level.get(str(self.level))
        else:
            level_str = str(caster_level)
            # cprint(f"caster_level: {level_str} - spell: {self}")
            # cprint(f"damage_at_character_level: {self.damage_at_character_level}")
            if level_str in self.damage_at_character_level:
                damage_dice = self.damage_at_character_level.get(level_str)
            else:
                for level in range(caster_level, -1, -1):
                    if str(level) in self.damage_at_character_level:
                        damage_dice = self.damage_at_character_level.get(str(level))
                        break

        if not damage_dice or "+" not in damage_dice:
            return [DamageDice(dice=damage_dice, bonus=0)]

        if damage_dice.count("d") == 0:
            return [DamageDice(dice=None, bonus=int(damage_dice))]

        if damage_dice.count("d") > 1:
            return [DamageDice(dice=dd.strip()) for dd in damage_dice.split("+")]

        dice, bonus = damage_dice.split("+")
        bonus = ability_modifier if "MOD" in bonus else int(bonus.strip())
        return [DamageDice(dice=dice, bonus=bonus)]


class ActionType(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    MIXED = "melee+ranged"
    SPECIAL = "special"
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
    area_of_effect: Optional[AreaOfEffect] = None
    ready: bool = True
    effects: List[Condition] = None
    targets_count: int = 6

    def can_use_after_death(self, monster: Monster) -> bool:
        return monster.index == "magma-mephit" and self.name == "Death Burst"

    def __repr__(self):
        return f"{self.name} dc: {self.dc_type} damages: {self.damages}"

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
        return SpellCaster(self.level, self.spell_slots[:], self.learned_spells, self.dc_type, self.dc_value, self.ability_modifier)


@dataclass
class Action:
    name: str
    desc: str
    type: ActionType
    damages: List[Damage] = None
    effects: List[Condition] = None
    multi_attack: List[Action | SpecialAbility] = None  # used for MELEE and RANGED attacks
    attack_bonus: int = 0
    normal_range: int = 5
    long_range: float = None
    disadvantage: bool = False


@dataclass
class Char2Party:
    char_name: str
    id: int = -1


@dataclass
class Character(Sprite):
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
    speed: int
    haste_timer: float
    hasted: bool
    xp: int
    level: int
    inventory: List[Equipment]
    gold: int
    sc: SpellCaster | None
    conditions: List[Condition] | None
    # attributes for Speed potion
    st_advantages: List[str] | None
    ac_bonus: int = 0
    multi_attack_bonus: int = 0
    # attributes for Strength potion
    str_effect_modifier: int = -1
    str_effect_timer: float = 0.0
    # other attributes
    status: str = "OK"
    id_party: int = -1
    OUT: bool = False
    kills: List[Monster] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, Character):
            return NotImplemented
        # Compare based on attributes that uniquely identify a character
        # For example, if name uniquely identifies a character:
        return self.name == other.name

    @property
    def weapon(self) -> Optional[Weapon]:
        equipped_weapons: List[Weapon] = [item for item in self.inventory if isinstance(item, Weapon) if item.equipped]
        return equipped_weapons[0] if equipped_weapons else None

    @property
    def armor(self) -> Optional[Armor]:
        equipped_armors: List[Armor] = [item for item in self.inventory if isinstance(item, Armor) if item.equipped and item.index != 'shield']
        return equipped_armors[0] if equipped_armors else None

    @property
    def shield(self) -> Optional[Armor]:
        equipped_shields: List[Armor] = [item for item in self.inventory if isinstance(item, Armor) if item.equipped and item.index == 'shield']
        return equipped_shields[0] if equipped_shields else None

    @property
    def is_dead(self) -> bool:
        return self.hit_points <= 0

    def can_equip(self, eq: Equipment) -> bool:
        return eq.category.index == "armor" and eq in self.prof_armors  # or (eq.category.index == "armor" and eq in self.prof_weapons)

    def can_drink(self, eq: Equipment) -> bool:
        return eq.category.index == "potion"

    @property
    def healing_potions(self) -> List[HealingPotion]:
        return [item for item in self.inventory if isinstance(item, HealingPotion)]

    @property
    def speed_potions(self) -> List[SpeedPotion]:
        return [item for item in self.inventory if isinstance(item, SpeedPotion)]

    @property
    def is_spell_caster(self) -> bool:
        return self.sc is not None

    def can_cast(self, spell: Spell) -> bool:
        return self.is_spell_caster and spell in self.sc.learned_spells and (self.sc.spell_slots[spell.level - 1] > 0 or spell.is_cantrip)

    @property
    def dc_value(self):
        # TODO Your Spell Save DC = 8 + your Spellcasting Ability modifier + your Proficiency Bonus + any Special Modifiers (???)
        def prof_bonus_char(x):
            return x // 4 + 1

        spell_casting_ability_modifier: int = int(self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability))
        prof_bonus: int = prof_bonus_char(self.level)
        return 8 + spell_casting_ability_modifier + prof_bonus

    @property
    def in_dungeon(self): return self.id_party != -1

    @property
    def attributes(self):
        return [self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charism]

    def _get_ability(self, attr: str) -> int:
        return getattr(self.abilities, attr) + self.race.ability_bonuses.get(attr, 0)

    @property
    def strength(self):
        return self.str_effect_modifier if self.str_effect_modifier != -1 else self._get_ability("str")

    @property
    def dexterity(self):
        dex_bonus = self.used_armor.armor_class['max_bonus'] if self.used_armor and self.used_armor.armor_class['dex_bonus'] != 'False' else 0
        return self._get_ability("dex") + int(0 if dex_bonus == 'None' else dex_bonus)

    @property
    def constitution(self): return self._get_ability("con")

    @property
    def intelligence(self): return self._get_ability("int")

    @property
    def wisdom(self): return self._get_ability("wis")

    @property
    def charism(self): return self._get_ability("cha")

    def __repr__(self):
        # return f'{self.id} {self.name} {self.class_type} {self.image_name}'
        race = self.subrace if self.subrace else self.race
        ethnic = f"ethnic: {self.ethnic} - " if self.ethnic else ""
        weapon_name = "None" if not self.weapon else self.weapon.name
        armor_name = "None" if not self.armor else self.armor.name
        return f"{self.name} - Age: {self.age // 52} - Abilities: {self.abilities} - Ability modifiers: {self.ability_modifiers} - ({ethnic}{self.gender} {race.name} - height: {self.height} weight: {self.weight}- class: {self.class_type} - AC {self.armor_class} Damage: {self.damage_dice} - w: {weapon_name} a: {armor_name} - potions: {len(self.healing_potions)})"

    @property
    def multi_attacks(self) -> int:
        if self.class_type.index == "fighter":
            attack_counts: int = 1 if self.level < 5 else 2 if self.level < 11 else 3
        elif self.class_type.index in ("paladin", "ranger", "monk", "barbarian"):
            attack_counts: int = 1 if self.level < 5 else 2
        else:
            attack_counts: int = 1
        return (attack_counts + self.multi_attack_bonus if hasattr(self, "multi_attack_bonus") else attack_counts)

    @property
    def armor_class(self):
        equipped_armors: List[Armor] = [item for item in self.inventory if isinstance(item, Armor) and item.equipped and item.name != "Shield"]
        equipped_shields: List[Armor] = [item for item in self.inventory if isinstance(item, Armor) and item.name == "Shield" and item.equipped]
        ac: int = (sum([item.armor_class["base"] for item in equipped_armors]) if equipped_armors else 10)
        ac += sum([item.armor_class["base"] for item in equipped_shields])
        return ac + self.ac_bonus if hasattr(self, "ac_bonus") else ac

    @property
    def damage_dice(self) -> DamageDice:
        """TODO Two handed weapon not possible with a shield"""
        # print(f'error {self.weapon}')
        return self.weapon.damage_dice_two_handed if self.weapon and self.weapon.damage_dice_two_handed else self.weapon.damage_dice if self.weapon else DamageDice("1d2")

    @property
    def used_armor(self) -> Optional[Armor]:
        equipped_armors: List[Armor] = [item for item in self.inventory if isinstance(item, Armor) and item.equipped and item.name != "Shield"]
        return equipped_armors[0] if equipped_armors else None

    @property
    def used_shield(self) -> Optional[Armor]:
        equipped_shields: List[Armor] = [item for item in self.inventory if isinstance(item, Armor) and item.name == "Shield" and item.equipped]
        return equipped_shields[0] if equipped_shields else None

    @property
    def used_weapon(self) -> Optional[Weapon]:
        equipped_weapons: List[Weapon] = [item for item in self.inventory if isinstance(item, Weapon) and item.equipped]
        return equipped_weapons[0] if equipped_weapons else None

    @property
    def is_full(self) -> bool:
        return all(item for item in self.inventory)

    def choose_best_potion(self) -> HealingPotion:
        hp_to_recover = self.max_hit_points - self.hit_points
        available_potions = [p for p in self.healing_potions if p.max_hp_restored >= hp_to_recover and hasattr(p, "min_level") and self.level >= p.min_level]
        return (min(available_potions, key=lambda p: p.max_hp_restored) if available_potions else max(self.healing_potions, key=lambda p: p.max_hp_restored))

    def cancel_haste_effect(self):
        self.hasted = False
        self.speed = 25 if self.race.index in ["dwarf", "halfling", "gnome"] else 30
        self.ac_bonus = 0
        self.multi_attack_bonus = 0
        if not hasattr(self, "st_advantages"):
            self.st_advantages = ["dex"]
        if "dex" in self.st_advantages:
            self.st_advantages.remove("dex")
        cprint(f"{self.name} is no longer {color.PURPLE}{color.BOLD}*hasted*{color.END}!")

    def cancel_strength_effect(self):
        self.str_effect_modifier = -1
        cprint(f"{self.name} is no longer {color.PURPLE}{color.BOLD}*strong*{color.END}!")

    def drink(self, potion: Potion) -> bool:
        if not hasattr(potion, "min_level"):
            potion.min_level = 1
        if self.level < potion.min_level:
            return False
        else:
            if isinstance(potion, StrengthPotion):
                self.str_effect_modifier = potion.value
                self.str_effect_timer = time.time()
                cprint(potion.effect())
            elif isinstance(potion, SpeedPotion):
                self.hasted = True
                self.haste_timer = time.time()
                self.speed *= 2
                self.ac_bonus = 2
                self.multi_attack_bonus = 1
                if not hasattr(self, "st_advantages"):
                    self.st_advantages = []
                self.st_advantages += ["dex"]
                cprint(f"{self.name} drinks {potion.name} potion and is {color.PURPLE}{color.BOLD}*hasted*{color.END}!")
            else:
                """Healing (??? check rules): A Healing potion repairs one six-sided die, plus one, (2-7) points of damage, just like a Cure Light Wounds spell."""
                hp_to_recover = self.max_hit_points - self.hit_points
                dice_count, roll_dice = map(int, potion.hit_dice.split("d"))
                hp_restored = potion.bonus + sum([randint(1, roll_dice) for _ in range(dice_count)])
                self.hit_points = min(self.hit_points + hp_restored, self.max_hit_points)
                if hp_to_recover <= hp_restored:
                    cprint(f"{self.name} drinks {potion.name} potion and is {color.BOLD}*fully*{color.END} healed!")
                else:
                    cprint(f"{self.name} drinks {potion.name} potion and has {min(hp_to_recover, hp_restored)} hit points restored!")
            # cprint(potion.effect())
            return True

    def equip(self, item) -> bool:
        if isinstance(item, Armor):
            if item.index == "shield":
                if self.used_shield:
                    if item == self.used_shield:
                        # un-equip shield
                        item.equipped = not item.equipped
                        return True
                    else:
                        cprint(f"Hero cannot equip {Color.RED}{item.name}{Color.END}> - Please un-equip <{self.used_shield.name}> first!")
                else:
                    if self.used_weapon:
                        is_two_handed = [p for p in self.used_weapon.properties if p.index == "two-handed"]
                        if is_two_handed:
                            cprint(f"Hero cannot equip <{item.name}> with a 2-handed weapon - Please un-equip <{self.used_weapon}> first!")
                        else:
                            # equip shield
                            item.equipped = not item.equipped
                            return True
                    else:
                        # equip shield
                        item.equipped = not item.equipped
                        return True
            else:
                if self.used_armor:
                    if item == self.used_armor:
                        # un-equip armor
                        item.equipped = not item.equipped
                        return True
                    else:
                        cprint(f"Hero cannot equip <{item.name}> - Please un-equip <{self.used_armor.name}> first!")
                else:
                    if self.strength < item.str_minimum:
                        cprint(f"Hero cannot equip <{item.name}> - Minimum strength required is <{item.str_minimum}>!")
                    else:
                        # equip armor
                        item.equipped = not item.equipped
                        return True
        elif isinstance(item, Weapon):
            if self.used_weapon:
                if item == self.used_weapon:
                    # un-equip weapon
                    item.equipped = not item.equipped
                    return True
                else:
                    cprint(f"Hero cannot equip <{item.name}> - Please un-equip <{self.used_weapon.name}> first!")
            else:
                is_two_handed = [p for p in item.properties if p.index == "two-handed"]
                if is_two_handed and self.used_shield:
                    cprint(f"Hero cannot equip <{item.name}> with a shield - Please un-equip <{self.used_shield}> first!")
                else:
                    # equip weapon
                    item.equipped = not item.equipped
                    return True
        else:
            cprint(f"Hero cannot equip <{item.name}>!")
        return False

    def victory(self, monster: Monster, solo_mode=False):
        self.xp += monster.xp
        self.kills.append(monster)
        gold_msg: str = ""
        if solo_mode:
            gold_dice = randint(1, 3)
            if gold_dice == 1:
                max_gold: int = max(1, floor(10 * monster.xp / monster.level))
                gold: int = randint(1, max_gold + 1)
                gold_msg = f" and found {gold} gp!"
                self.gold += gold
        cprint(f"{self.name} gained {monster.xp} XP{gold_msg}!")

    @property
    def prof_weapons(self) -> List[Weapon]:
        weapons: List[Weapon] = []
        for p in self.proficiencies:
            if p.type == ProfType.WEAPON:
                weapons += p.ref if isinstance(p.ref, List) else [p.ref]
        return list(filter(None, weapons))

    @property
    def prof_armors(self) -> List[Armor]:
        armors: List[Armor] = []
        for p in self.proficiencies:
            if p.type == ProfType.ARMOR:
                armors += p.ref if isinstance(p.ref, List) else [p.ref]
        return list(filter(None, armors))

    def treasure(self, weapons, armors, equipments: List[Equipment], potions, solo_mode=False):
        if self.is_full:
            cprint(f"{self.name}'s inventory is full - no treasure!!!")
            return
        free_slot = min([i for i, item in enumerate(self.inventory) if item is None])
        treasure_dice = randint(1, 3)
        if treasure_dice == 1:
            potion = choice(potions)
            cprint(f"{self.name} found a {potion.name} potion!")
            self.inventory[free_slot] = choice(potions)
        elif treasure_dice == 2:
            new_weapon: Weapon = choice(self.prof_weapons)
            if not self.weapon or new_weapon.damage_dice > self.weapon.damage_dice:
                cprint(f"{self.name} found a better weapon {new_weapon.name}!")
                #new_weapon.equipped = True
            else:
                cprint(f"{self.name} found a lesser weapon {new_weapon.name}!")
            self.inventory[free_slot] = new_weapon
        else:
            if self.prof_armors:
                new_armor: Armor = choice(self.prof_armors)
                if new_armor.armor_class["base"] > self.armor_class:
                    cprint(f"{self.name} found a better armor {new_armor.name}!")
                    for item in self.inventory:
                        if isinstance(item, Armor) and item.equipped:
                            item.equipped = False
                    # new_armor.equipped = True
                else:
                    cprint(f"{self.name} found a lesser armor {new_armor.name}!")
                self.inventory[free_slot] = new_armor

    def gain_level_arena(self, pause: bool):
        self.level += 1
        hp_gained = randint(1, 10)
        self.max_hit_points += hp_gained
        self.hit_points += hp_gained
        print(f"{color.BLUE}New level #{self.level} gained!!!{color.END}")
        print(f"{self.name} gained {hp_gained} hit points")
        if pause:
            input(f"{color.UNDERLINE}{color.DARKCYAN}hit Enter to continue adventure :-) (potions remaining: {len(self.healing_potions)}){color.END}")

    def gain_level(self, tome_spells: List[Spell] = None) -> tuple[str, Optional[List[Spell]]]:
        display_msg: List[str] = []
        new_spells: List[Spell] = []
        self.level += 1
        level_up_hit_die = {12: 7, 10: 6, 8: 5, 6: 4}
        hp_gained = (randint(1, level_up_hit_die[self.class_type.hit_die]) + self.ability_modifiers.con)
        self.max_hit_points += max(1, hp_gained)
        self.hit_points += hp_gained
        display_msg += [f"New level #{self.level} gained!!!"]
        display_msg += [f"{self.name} gained {hp_gained} hit points"]
        #  PROCEDURE GAINLOST;  (* P010A20 *)
        attrs = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charism", ]
        for attr in attrs:
            val = self.abilities.get_value_by_name(name=attr)
            if randint(0, 3) % 4:
                if randint(0, 129) < self.age // 52:
                    if val == 18 and randint(0, 5) != 4:
                        continue
                    val -= 1
                    if attr == "Constitution" and val == 2:
                        display_msg += ["** YOU HAVE DIED OF OLD AGE **"]
                        self.status, self.hit_points = "LOST", 0
                    else:
                        display_msg += [f"You lost {attr}"]
                elif val < 18:
                    val += 1
                    display_msg += [f"You gained {attr}"]
            self.abilities.set_value_by_name(name=attr, value=val)
        if self.class_type.can_cast:
            available_spell_levels: List[int] = [i + 1 for i, slot in enumerate(self.class_type.spell_slots[self.level]) if slot > 0]
            new_spells_known_count: int = (self.class_type.spells_known[self.level - 1] - self.class_type.spells_known[self.level - 2])
            new_cantric_spells_count: int = 0
            if self.class_type.cantrips_known:
                new_cantric_spells_count = (self.class_type.cantrips_known[self.level - 1] - self.class_type.cantrips_known[self.level - 2])
            learnable_spells: List[Spell] = [s for s in tome_spells if s.level <= max(available_spell_levels) and s not in self.sc.learned_spells and s.damage_type]
            self.sc.spell_slots = deepcopy(self.class_type.spell_slots[self.level])
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
                new_spells.append(learned_spell)
            if new_spells_count:
                display_msg += [f"You learned new Spells!!!"]
        return '\n'.join(display_msg), new_spells

    def update_spell_slots(self, spell: Spell, slot_level: Optional[int] = None):
        slot_level: int = slot_level + 1 if slot_level else spell.level
        match self.class_type.name:
            case "Warlock":
                # all of your spell slots are the same level
                for level, slot in enumerate(self.sc.spell_slots):
                    if slot:
                        self.sc.spell_slots[level] -= 1
            case _:
                self.sc.spell_slots[slot_level - 1] -= 1

    def get_best_slot_level(self, heal_spell: Spell, target: Character) -> int:
        max_slot_level = max(i for i, slot in enumerate(self.sc.spell_slots) if slot)
        best_slot_level = None
        max_score = 0
        for slot_level in range(heal_spell.level - 1, max_slot_level + 1):
            dd: DamageDice = heal_spell.get_heal_effect(slot_level, self.sc.ability_modifier)
            score = min(target.hit_points + dd.avg, target.max_hit_points) / dd.avg
            # cprint(f'slot_level: {slot_level}, score: {score}, dd: {dd}')
            if score > max_score:
                max_score = score
                best_slot_level = slot_level
        return best_slot_level

    def cast_heal(self, spell: Spell, slot_level: int, targets: List[Character]):
        ability_modifier: int = int(self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability))
        dd: DamageDice = spell.get_heal_effect(slot_level=slot_level, ability_modifier=ability_modifier)
        heal_roll: int = dd.roll()
        cprint(f"{color.GREEN}{self.name}{color.END} ** CAST SPELL ** {spell.name.upper()}")
        for char in targets:
            if char.hit_points < char.max_hit_points:
                hp_gained: int = min(dd.roll(), char.max_hit_points - char.hit_points)
                char.hit_points += hp_gained
                cprint(f"{color.RED}{char.name}{color.END} is healed for {hp_gained} hit points!")
                if char.hit_points == char.max_hit_points:
                    cprint(f"{color.RED}{char.name}{color.END} is fully healed!")
            else:
                cprint(f"{color.RED}{char.name}{color.END} is already at full health!")

    def cast_attack(self, spell: Spell, monster: Monster) -> int:
        # print(attack_spell)
        ability_modifier: int = int(self.ability_modifiers.get_value_by_index(name=self.class_type.spellcasting_ability))
        damage_dices: List[DamageDice] = spell.get_spell_damages(caster_level=self.level, ability_modifier=ability_modifier)
        damage_roll: int = 0
        for dd in damage_dices:
            damage_roll += dd.roll()
        cprint(f"{color.GREEN}{self.name}{color.END} ** CAST SPELL ** {spell.name.upper()}")
        if spell.dc_type is None:
            # No saving throw available for this spell!
            cprint(f"{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!")
        else:
            st_success: bool = monster.saving_throw(dc_type=self.class_type.spellcasting_ability, dc_value=self.dc_value)
            if st_success:
                cprint(f"{color.RED}{monster.name}{color.END} resists the Spell!")
                if spell.dc_success == "half":
                    damage_roll //= 2
                    cprint(f"{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!")
                elif spell.dc_success == "none":
                    damage_roll = 0
            else:
                cprint(f"{color.RED}{monster.name}{color.END} is hit for {damage_roll} hit points!")
        return damage_roll

    def attack(self, monster: Monster, in_melee: bool = True, cast: bool = True) -> int:
        """
        :return: damage generated
        """

        def prof_bonus(x):
            return x // 5 + 2 if x < 5 else (x - 5) // 4 + 3

        damage_roll = 0
        castable_spells: List[Spell] = []
        if self.is_spell_caster:
            cantric_spells: List[Spell] = [s for s in self.sc.learned_spells if not s.level]
            slot_spells: List[Spell] = [s for s in self.sc.learned_spells if s.level and self.sc.spell_slots[s.level - 1] > 0 and s.damage_type]
            castable_spells = cantric_spells + slot_spells
        if cast and castable_spells and not in_melee:
            # TODO modify spell_slots to [] for non casters
            attack_spell: Spell = max(castable_spells, key=lambda s: s.level)
            damage_roll = self.cast_attack(attack_spell, monster)
            if not attack_spell.is_cantrip:
                self.update_spell_slots(spell=attack_spell)
        else:
            damage_multi = 0
            for _ in range(self.multi_attacks):
                if self.hit_points <= 0:
                    break
                attack_roll = (randint(1, 20) + self.ability_modifiers.get_value_by_index("str") + prof_bonus(self.level))
                if attack_roll >= monster.armor_class:
                    damage_roll = self.damage_dice.roll()
                if damage_roll:
                    # cprint(f'{color.GREEN}{self.name}{color.END} hits {color.RED}{monster.name}{color.END} for {damage_roll} hit points!'
                    attack_type: str = (self.weapon.damage_type.index.replace("ing", "es") if self.weapon else "punches")
                    cprint(f"{color.RED}{self.name}{color.END} {attack_type} {color.GREEN}{monster.name}{color.END} for {damage_roll} hit points!")
                    if any([e for e in self.conditions if e.index == "restrained"]):
                        damage_roll //= 2
                        self.hit_points -= damage_roll
                        cprint(f"{self.name} inflicts himself {damage_roll} hit points!")
                        if self.hit_points <= 0:
                            cprint(f"{self.name} *** IS DEAD ***!")
                    damage_multi += damage_roll
                else:
                    cprint(f"{self.name} misses {monster.name}!")
            damage_roll = damage_multi
        return damage_roll

    def saving_throw(self, dc_type: str, dc_value: int) -> bool:
        """
            Determine resistance from a spell casted by a monster
        :param dc_type: ability needed for ST
        :param dc_value: difficulty class
        :return:
        """

        # 2 - Calculate saving throw of monster
        # Determine ability for ST in Spell
        def ability_mod(x):
            return (x - 10) // 2

        def prof_bonus(x):
            return x // 5 + 2 if x < 5 else (x - 5) // 4 + 3

        st_type: str = f"saving-throw-{dc_type}"
        prof_modifiers: List[int] = [p.value for p in self.proficiencies if st_type == p.index]
        if prof_modifiers:
            ability_modifier: int = prof_modifiers[0]
        else:
            ability_modifier: int = ability_mod(self.abilities.get_value_by_index(dc_type)) + prof_bonus(self.level)
        return (any(randint(1, 20) + ability_modifier > dc_value for _ in range(2)) if hasattr(self, "st_advantages") and dc_type in self.st_advantages else randint(1, 20) + ability_modifier > dc_value)

class CharActionType(Enum):
    MELEE_ATTACK = "Attack"
    RANGED_ATTACK = "Attack"
    SPELL_ATTACK = "Spell"
    SPELL_DEFENSE = "spell_defense"
    PARRY = "Parry"

@dataclass
class CharAction:
    type: CharActionType
    spell: Optional[Spell] = field(default=None)
    targets: Optional[List[Character|Monster]] = field(default_factory=list)

    def __repr__(self):
        return f"{self.type.value} - {self.spell.name if self.spell else ''} - {self.targets[0].name if self.targets else ''}"

@dataclass
class DamageDice:
    dice: str
    bonus: int = 0

    def __repr__(self):
        bonus: str = '' if not self.bonus else f" {sign(self.bonus)}{self.bonus}"
        return f"{self.dice}{bonus}"

    @property
    def max_score(self) -> int:
        return self.bonus + prod(map(int, self.dice.split("d")))

    def __eq__(self, other):
        return self.max_score == other.max_score

    def __lt__(self, other):
        return self.max_score < other.max_score

    def __gt__(self, other):
        return self.max_score > other.max_score

    def roll(self) -> int:
        if "d" not in self.dice:
            # dice_count, damage_dice = int(self.dice), 6
            # return sum([randint(1, damage_dice) for _ in range(dice_count)])
            return int(self.dice)
        else:
            if "+" in self.dice:
                damage_dice, bonus_damage = self.dice.split("+")
                dice_count, damage_dice = map(int, damage_dice.split("d"))
                return sum([randint(1, damage_dice) for _ in range(dice_count)]) + int(bonus_damage)
            elif "-" in self.dice:
                damage_dice, bonus_damage = self.dice.split("-")
                dice_count, damage_dice = map(int, damage_dice.split("d"))
                return sum([randint(1, damage_dice) for _ in range(dice_count)]) - int(bonus_damage)
            else:
                dice_count, damage_dice = map(int, self.dice.split("d"))
                return sum([randint(1, damage_dice) for _ in range(dice_count)])

    @property
    def avg(self) -> int:
        dice_count, roll_dice = map(int, self.dice.split("d"))
        bonus = self.bonus if self.bonus else 0
        return bonus + dice_count * roll_dice // 2

    def score(self, success_type: str = "None") -> int:
        dice_count, roll_dice = map(int, self.dice.split("d"))
        factor: int = 1 if success_type in ("none", "None") else 0.5
        return (self.bonus + roll_dice * (1 + dice_count)) * factor / 2


@dataclass
class Treasure(Sprite):
    # type: Potion | Armor | Weapon
    gold: int
    has_item: bool

    def __repr__(self):
        return f"#{self.id} {self.gold} {self.has_item}"
