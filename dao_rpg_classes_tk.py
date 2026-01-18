from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from random import randint
from typing import List

import pygame
from pygame import Surface
from pygame.surface import SurfaceType


@dataclass
class Weapon:
    name: str
    damage_dice: str
    img: Surface | SurfaceType


@dataclass
class Armor:
    name: str
    ac: int
    img: Surface | SurfaceType


class PotionType(Enum):
    LIGHT_HEAL = '1d6'
    MEDIUM_HEAL = '2d6'
    HEAVY_HEAL = '3d6'
    CURE = 'Poison'
    SPEED = 'Speed'


@dataclass
class Potion:
    name: str
    type: PotionType
    img: Surface | SurfaceType


@dataclass
class Sprite:
    x: int
    y: int
    img: Surface | SurfaceType

    @property
    def pos(self) -> tuple:
        return self.x, self.y

    def draw_old(self, screen, tile_size):
        screen.blit(self.img, (self.x * tile_size, self.y * tile_size))

    def draw(self, screen, tile_size, viewport_x, viewport_y, viewport_width, viewport_height):
        if self.img:
            # Calculate the position of the sprite relative to the viewport
            draw_x = (self.x - viewport_x) * tile_size
            draw_y = (self.y - viewport_y) * tile_size

            # Check if the sprite is within the viewport boundaries
            if 0 <= draw_x <= viewport_width * tile_size and 0 <= draw_y <= viewport_height * tile_size:
                screen.blit(self.img, (draw_x, draw_y))


@dataclass
class Monster(Sprite):
    name: str
    hit_dice: str
    damage_dice: str
    attack_bonus: int
    ac: int
    speed: int
    xp: int
    cr: int
    hp: int = field(init=False)
    max_hp: int = field(init=False)

    def __post_init__(self):
        dice_count, roll_dice = map(int, self.hit_dice.split('d'))
        print(dice_count)
        self.hp = sum([randint(1, roll_dice) for _ in range(dice_count)])
        self.max_hp = self.hp

    def __repr__(self):
        return f'{self.name} {(self.x, self.y)}'

    def damage_roll(self) -> int:
        if 'd' not in self.damage_dice:
            return int(self.damage_dice)
        dice_count, damage_dice = self.damage_dice.split('d')
        if '+' in damage_dice:
            damage_dice, bonus_damage = map(int, damage_dice.split('+'))
            return sum([randint(1, damage_dice) + bonus_damage for _ in range(int(dice_count))])
        elif '-' in damage_dice:
            damage_dice, bonus_damage = map(int, damage_dice.split('-'))
            return sum([randint(1, damage_dice) - bonus_damage for _ in range(int(dice_count))])

    def attack(self, hero):
        attack_roll = randint(1, 20) + self.attack_bonus
        if self.hp > 0 and attack_roll > hero.armor.ac:
            damage: int = self.damage_roll
            print(f'{self.name.title()} hits hero for {damage} hp')
            hero.hp -= damage
            if hero.hp <= 0:
                print(f'Hero is killed!')
                print(f'GAME OVER!!!')
                hero.img = pygame.image.load(f"sprites/rip.png")
        else:
            print(f'{self.name.title()} misses hero')


@dataclass
class Character(Sprite):
    speed: int
    hp: int
    max_hp: int
    weapon: Weapon
    armor: Armor
    gold: int = 0
    xp: int = 0
    potions: int = 0
    level: int = 1

    def check_collision(self, other: "Monster"):
        return self.x == other.x and self.y == other.y

    def drink_potion(self, app):
        if self.potions:
            hp_recovered = randint(1, 80)
            self.hp = min(self.hp + hp_recovered, self.max_hp)
            status: str = 'fully' if self.hp == self.max_hp else 'partially'
            print(f'Hero drinks potion and is ** {status} ** healed!')
            self.potions -= 1
            # app.refresh_title()
        else:
            print(f'Hero has ** no potion ** left!')

    @property
    def damage_roll(self) -> int:
        dice_count, roll_dice = map(int, self.weapon.damage_dice.split('d'))
        return sum([randint(1, roll_dice) for _ in range(dice_count)])

    def attack(self, monster: Monster):
        attack_roll = randint(1, 20)
        if attack_roll > monster.ac:
            damage: int = self.damage_roll
            print(f'Hero hits {monster.name.title()} for {damage} hp')
            monster.hp -= damage
            if monster.hp < 0:
                print(f'{monster.name.title()} is killed!')
                self.xp += monster.xp
                if self.xp > 500 * self.level:
                    self.level += 1
                    print(f'Hero ** gained a level! **')
                    new_hp = randint(1, 10)
                    print(f'Hero ** gained {new_hp} HP! **')
                    self.hp += new_hp
                    self.max_hp += new_hp
        else:
            print(f'Hero misses {monster.name.title()}')


@dataclass
class Treasure(Sprite):
    # type: Potion | Armor | Weapon
    gold: int
    potion: bool

    def __repr__(self):
        return f'{self.gold} {self.potion}'
