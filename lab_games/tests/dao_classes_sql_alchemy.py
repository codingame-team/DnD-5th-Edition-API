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

