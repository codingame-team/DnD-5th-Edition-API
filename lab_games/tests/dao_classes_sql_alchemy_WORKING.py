from __future__ import annotations

import random
from dataclasses import dataclass

from sqlalchemy import Column, Integer, Text, Identity, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from tools.common import Color

Base = declarative_base()  # Required

""" Monster classes """


class Monster(Base):
    __tablename__ = 'T_Monsters'

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    name = Column(Text, nullable=False)
    armor_class = Column(Integer, nullable=False)
    hit_points = Column(Integer)
    hit_dice = Column(Text, nullable=False)
    xp = Column(Integer)
    challenge_rating = Column(Integer)

    def __init__(self, name: str, armor_class: int, hit_points: int, hit_dice: str, xp: int, challenge_rating: int):
        self.name = name
        self.armor_class = armor_class
        self.hit_points = hit_points
        self.hit_dice = hit_dice
        self.xp = xp
        self.challenge_rating = challenge_rating

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
            print(f'{Color.RED}{self.name}{Color.END} hits {Color.GREEN}{character.name}{Color.END} for {damage_roll} hit points!')
        else:
            print(f'{self.name} misses {character.name}!')
        return damage_roll


""" Character classes """

class Proficiency(Base):
    __tablename__ = "T_Proficiencies"

    id = Column(Integer, primary_key=True)

    index = Column(Text)
    name = Column(Text)
    type = Column(Text)

    def __init__(self, index: str, name: str, type: str):
        self.index = index
        self.name = name
        self.type = type


class CharacterProf(Base):
    __tablename__ = "T_CharacterProfs"

    id = Column(Integer, primary_key=True)

    idCharacter = Column(Integer, ForeignKey("T_Characters.idCharacter"))
    character = relationship("Character")

    idProf = Column(Integer, ForeignKey("T_Proficiencies.idProf"))
    prof = relationship("Proficiency")

    def __repr__(self):
        return self.character, self.prof


class CharacterPotion(Base):
    __tablename__ = "T_CharacterPotions"

    id = Column(Integer, primary_key=True)

    idCharacter = Column(Integer, ForeignKey("T_Characters.idCharacter"))
    character = relationship("Character")

    idPotion = Column(Integer, ForeignKey("T_Potions.idPotion"))
    potion = relationship("Potion")

    def __repr__(self):
        return self.character, self.potion


class CharacterEquipment(Base):
    __tablename__ = "T_CharacterEquipments"

    id = Column(Integer, primary_key=True)

    idCharacter = Column(Integer, ForeignKey("T_Characters.idCharacter"))
    character = relationship("Character")

    idEquipment = Column(Integer, ForeignKey("T_Equipments.idEquipment"))
    equipment = relationship("Equipment")

    def __repr__(self):
        return self.character, self.equipment


class Character(Base):
    __tablename__ = 'T_Characters'

    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)

    idRace = Column(Integer, ForeignKey("T_Races.idRace"))
    race = relationship("Race")

    ethnic = Column(Text)
    gender = Column(Text)
    height = Column(Text)
    weight = Column(Text)
    class_type = Column(Text)

    proficiencies = relationship("CharacterProf", backref="CharacterProf.id")

    idAbilities = Column(Integer, ForeignKey("T_Abilities.id"))
    abilities = relationship("Abilities")

    hit_points = Column(Integer)
    max_hit_points = Column(Integer)
    xp = Column(Integer)
    level = Column(Integer)

    healing_potions = relationship("CharacterPotions", backref="CharacterPotion.id")

    monster_kills = Column(Integer)

    inventory = relationship("CharacterEquipment", backref="CharacterEquipment.id")

    idArmor = Column(Integer, ForeignKey("T_Armor.id"))
    armor = relationship("Armor")

    idWeapon = Column(Integer, ForeignKey("T_Weapon.id"))
    weapon = relationship("Weapon")

    OUT = Column(Boolean)

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
        self.healing_potions.remove_from_inv(best_potion)
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        hp_restored = 2 + random.randint(1, roll_dice) + random.randint(1, roll_dice)
        self.hit_points = min(self.hit_points + hp_restored, self.max_hit_points)
        if hp_to_recover <= hp_restored:
            print(f'{self.name} drinks healing potion and is {Color.BOLD}*fully*{Color.END} healed!')
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
            if new_weapon.damage_dice > self.weapon.damage_dice:
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
        print(f'{Color.BLUE}New level #{self.level} gained!!!{Color.END}')
        print(f'{self.name} gained {hp_gained} hit points')
        if pause:
            input(f'{Color.UNDERLINE}{Color.DARKCYAN}hit Enter to continue adventure :-) (potions remaining: {len(self.healing_potions)}){Color.END}')

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
            print(f'{Color.GREEN}{self.name}{Color.END} hits {Color.RED}{monster.name}{Color.END} for {damage_roll} hit points!')
        else:
            print(f'{self.name} misses {monster.name}!')
        return damage_roll


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