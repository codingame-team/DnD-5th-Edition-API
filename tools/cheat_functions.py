import os
from typing import List

from dao_classes import Character
from dungeon_pygame import load_character_gamestate, save_character_gamestate
from main import get_roster, save_character, load_character

from collections import Counter

from tools.common import get_save_game_path


def get_duplicate_ids(roster):
    roster_sprite_ids = [character.id for character in roster]
    # Compter le nombre d'occurrences de chaque ID
    id_counts = Counter(roster_sprite_ids)
    # Trouver les IDs en double
    duplicate_ids = [id for id, count in id_counts.items() if count > 1]
    return duplicate_ids


def get_duplicate_item_ids(character):
    item_ids = [item.id for item in character.inventory if item]
    # Compter le nombre d'occurrences de chaque ID
    id_counts = Counter(item_ids)
    # Trouver les IDs en double
    duplicate_ids = [id for id, count in id_counts.items() if count > 1]
    return duplicate_ids


def fix_duplicate_ids(roster, duplicate_ids):
    for character in roster:
        if character.id in duplicate_ids:
            character.id = (max(roster, key=lambda c: c.id).id + 1)
            save_character(char=character, _dir=characters_dir)
        duplicate_ids = get_duplicate_ids(roster)


def fix_duplicate_item_ids(character) -> bool:
    duplicate_item_ids = get_duplicate_item_ids(character)
    if duplicate_item_ids:
        character.inventory = [None] * 20
        for item in character.inventory:
            if item and item.id != -1 and item.id in duplicate_item_ids:
                print(f'fixing item id {item.id}')
                item.id = (max(character.inventory, key=lambda item: item.id).id + 1) if character.inventory else 1
                duplicate_item_ids = get_duplicate_item_ids(character)
        save_character(char=character, _dir=characters_dir)

        return True
    return False


def fix_inv(roster):
    for character in roster:
        if len(character.inventory) < 20 or character.name == 'Artin':
            print(f'fixing inventory for {character.name}')
            character.inventory = [None] * 20
            save_character(char=character, _dir=characters_dir)


def fix_duplicate_ids_all(roster):
    duplicate_ids = get_duplicate_ids(roster)
    if duplicate_ids:
        print(f'duplicate ids found! {duplicate_ids}')
        # sorted_roster_by_level = sorted(roster, key=lambda c: c.level)
        # fix_duplicate_ids(sorted_roster_by_level, duplicate_ids)
    else:
        print('no duplicate ids found :-)')
    duplicate_item_ids = [get_duplicate_item_ids(c) for c in roster]
    if duplicate_item_ids:
        for character in roster:
            fixed: bool = fix_duplicate_item_ids(character)
            print(f'{character.name}: duplicate item ids found! {duplicate_item_ids}' if fixed else f'{character.name}: no duplicate item ids found :-)')
    else:
        print('no duplicate item ids found :-)')

    fix_inv(roster)


def delete_inv_old(roster):
    for character in roster:
        for item in character.inventory:
            if item:
                print(f'deleting {item.name}')
                character.inventory.remove(item)
                save_character(char=character, _dir=characters_dir)

def delete_inv(roster):
    for character in roster:
        character.inventory = [None] * 20
        save_character(char=character, _dir=characters_dir)

def delete_char_inv(name: str):
    for char in roster:
        if char.name == name:
            print(f'deleting {char.name} inventory')
            char.inventory = [None] * 20
            save_character(char=char, _dir=characters_dir)


def cure_char(name: str):
    for char in roster:
        if char.name == name:
            print(f'curing {char.name}')
            char: Character
            char.hit_points = char.max_hit_points
            char.status = 'OK'
            save_character(char=char, _dir=characters_dir)


def fix_duplicate_spells(roster):
    for character in roster:
        if character.is_spell_caster:
            learned_spells: dict = {s.index: s for s in character.sc.learned_spells}
            if len(learned_spells) < len(character.sc.learned_spells):
                character.learned_spells = list(learned_spells.values())
                save_character(char=character, _dir=characters_dir)
                print(f'duplicates spells for char {character} fixed!')

def raise_dead_roster(roster, characters_dir):
    for character in roster:
        if character.hit_points <= 0:
            print(f'raising dead {character} and restoring all hit points')
            character.status = 'OK'
            character.hit_points = character.max_hit_points
            save_character(char=character, _dir=characters_dir)
        elif character.hit_points < character.max_hit_points:
            print(f'restoring all hit points to {character}')
            character.hit_points = character.max_hit_points
            save_character(char=character, _dir=characters_dir)


def raise_dead(character, characters_dir):
    print(f'raising dead {character}')
    character.status = 'OK'
    character.hit_points = 1
    save_character(char=character, _dir=characters_dir)

def delete_dart(param):
    for character in roster:
        if character.name == param:
            print(f'deleting dart {character}')
            darts = [item for item in character.inventory if item and item.name == 'Dart']
            for dart in darts:
                character.inventory.remove(dart)
            save_character(char=character, _dir=characters_dir)


def delete_arrow(param):
    for character in roster:
        if character.name == param:
            print(f'deleting arrow {character}')
            arrows = [item for item in character.inventory if item and item.name == 'Arrow']
            for arrow in arrows:
                character.inventory.remove(arrow)
            save_character(char=character, _dir=characters_dir)

if __name__ == "__main__":
    # path = os.path.dirname(__file__)
    # abspath = os.path.abspath(path)
    # gamestate_dir = f'{abspath}/../gameState/pygame'
    # characters_dir = f'{abspath}/../gameState/characters'
    # roster: List[Character] = get_roster(characters_dir)

    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    gamestate_dir = f'{game_path}/pygame'
    char_name = 'Brottor'
    saved_game = load_character_gamestate(char_name=char_name, _dir=gamestate_dir)
    if not saved_game:
        hero = load_character(char_name=char_name, _dir=characters_dir)
        hero.inventory = [None] * 20
        save_character(char=hero, _dir=characters_dir)
    else:
        hero = saved_game.hero
        hero.inventory = [None] * 20
        save_character_gamestate(hero, gamestate_dir, saved_game)


    # fix_duplicate_ids_all(roster)
    # delete_inv(roster)
    # delete_dart('Silaqui')
    # delete_arrow('Ehput-Ki')

    # cure_char(name='Vadania')
    # cure_char(name='Esvele')
    # delete_char_inv(name='Vola')
    # fix_duplicate_spells(roster)
