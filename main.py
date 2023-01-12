from __future__ import annotations

import os
import pickle
import sys
from copy import copy
from os import listdir
from os.path import isfile, join
from random import randint, seed, sample
from time import sleep, time

from PyQt5.QtWidgets import QApplication, QDialog

from dao_classes import *
from populate_functions import *
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from tools.ability_scores_roll import ability_rolls
from tools.common import cprint, Color, get_key


def continue_message(message: str = 'Do you want to continue? (Y/N)') -> bool:
    print(f'{color.DARKCYAN}{message}{color.END}')
    response = input()
    while response not in ['y', 'n', 'Y', 'N']:
        print(f'{color.DARKCYAN}{message}{color.END}')
        response = input()
    if response in ['y', 'y']:
        return True
    return False


def welcome_message_old():
    global PAUSE_ON_RAISE_LEVEL
    if PAUSE_ON_RAISE_LEVEL:
        print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
        print(f'{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}')
        print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
        print(f'{color.DARKCYAN}Do you want to pause output after new level? (Y/N){color.END}')
        response = input()
        while response not in ['y', 'n', 'Y', 'N']:
            print(f'{color.DARKCYAN} Do you want to pause output after new level? (Y/N){color.END}')
            response = input()
        PAUSE_ON_RAISE_LEVEL = True if response in ['y', 'Y'] else False


def read_simple_text(input_message: str):
    text: str = None
    while not text:
        print(f'{input_message}: ')
        text = input()
    return text


def read_name(race: str, gender: str, names: dict(), reserved_names):
    """

    :param race: name of the race
    :param genre: name of the gender ['male', 'female', 'nickname', 'surname']
    :param names: dictionary of names
    :return:
    """
    if race in ['human', 'half-elf']:
        ethnic = read_choice(list(names.keys()), 'Choose ethnic:')
        names_list = names[ethnic][gender]
        if len(names[ethnic]) > 2:
            other_key = [key for key in names[ethnic] if key not in ['male', 'female']][0]
            names_list += names[ethnic][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = read_choice(names, 'Choose name:')
        return name, ethnic
    else:
        try:
            names_list = names[race][gender]
        except:
            print(names)
            exit(0)
        if len(names[race]) > 2:
            other_key = [key for key in names[race] if key not in ['male', 'female']][0]
            names_list += names[race][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = read_choice(names, 'Choose name:')
        return name


def read_choice(choice_list: List[str], message: str = None) -> str:
    choice = None
    while choice not in range(1, len(choice_list) + 1):
        items_list = '\n'.join([f'{i + 1}) {item}' for i, item in enumerate(choice_list)])
        if message:
            print(message)
        print(f'{items_list}')
        err_msg = f'Bad value! Please enter a number between 1 and {len(choice_list)}'
        try:
            choice = int(input())
            if choice not in range(1, len(choice_list) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            continue
    return choice_list[choice - 1]


def read_char_choice(message: str, party: List[Character]) -> Character:
    choice = None
    while choice not in range(1, len(party) + 1):
        char_names: str = '\n'.join([f'{i + 1}) {char.name}' for i, char in enumerate(party)])
        print(f'{message}:\n{char_names}')
        err_msg = f'Bad value! Please enter a number between 1 and {len(party)}'
        try:
            choice = int(input())
            if choice not in range(1, len(party) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            continue
    return party[choice - 1]


def choose_equipment_from(starting_equipment_options: List[List[Inventory]]):
    starting_equipment: List[Equipment] = []
    for inv_options in starting_equipment_options:
        inv_count = 1
        inv_choices = {}
        for inv in inv_options:
            try:
                if isinstance(inv, list):
                    label: str = ', '.join([f'{i.quantity} {i.equipment.index}' for i in inv])
                else:
                    # print(f'inv: {inv} - type: {type(inv)}')
                    label: str = inv.equipment.index
            except AttributeError:
                print(f'inv: {inv}')
                print(f'label: {label}')
                exit(0)
            inv_choices[label] = inv
        plural: str = '' if inv_count == 1 else 's'
        inv_choice: str = read_choice(list(inv_choices.keys()), f'Choose {inv_count} equipment{plural}:')
        chosen_inv: Inventory | List[Inventory] = inv_choices[inv_choice]
        if type(chosen_inv) is list:
            starting_equipment += [inv.equipment for inv in chosen_inv for _ in range(inv.quantity)]
        else:
            if isinstance(chosen_inv.equipment, EquipmentCategory):
                inv_options_cat: List[str] = populate(collection_name=chosen_inv.equipment.index, key_name='equipment', collection_path='data/equipment-categories')
                plural: str = '' if inv_count == 1 else 's'
                inv_choice: str = read_choice(inv_options_cat, f'Choose {inv_count} {chosen_inv.equipment.name}{plural}:')
                starting_equipment.append(request_equipment(inv_choice))
            else:
                starting_equipment.append(request_equipment(chosen_inv.equipment.index))
        # print(f'removing chosen_inv: {chosen_inv}')
        # inv_options.remove(chosen_inv)
        # inv_count -= 1
    return starting_equipment


def create_character(races: List[Race], subraces: List[SubRace], classes: List[Class], proficiencies: List[Proficiency], equipments: List[Equipment], names: dict(), human_names: dict(),
                     reserved_names: List[str]):
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    print(f'{color.PURPLE} Character creation based on DnD 5th edition API{color.END}')
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    """ 1. Choose a race """
    races_names: List[str] = [r.index for r in races]
    race: str = read_choice(races_names, 'Choose race:')
    race: Race = [r for r in races if r.index == race][0]
    subraces_names: List[str] = [s.index for s in subraces for r in races if r.index == race.index and r.index in s.index]
    subrace = None
    if subraces_names:
        subrace: str = read_choice(subraces_names, 'Choose subrace')
        subrace: SubRace = [r for r in subraces if r.index == subrace][0]
    # Choose proficiencies within the race
    chosen_proficiencies: List[str] = []
    for choose, proficiency_options in race.starting_proficiency_options:
        proficiency_names: List[str] = [prof.index for prof in proficiency_options]
        prof_count = choose
        while prof_count:
            prof_label = 'proficiency' if prof_count == 1 else 'proficiencies'
            prof_name: str = read_choice(proficiency_names, f'Choose {prof_count} race\'s {prof_label}:')
            chosen_proficiencies.append(prof_name)
            proficiency_names.remove(prof_name)
            prof_count -= 1
    for chosen_prof_name in chosen_proficiencies:
        chosen_prof: Proficiency = [prof for prof in proficiencies if prof.name == chosen_prof_name][0]
        proficiencies.append(chosen_prof)
    # should be deleted (duplicate with character.class_type.proficiencies)
    proficiencies += race.starting_proficiencies
    """ 2. Choose a class """
    class_names = [c.index for c in classes]
    class_type: str = read_choice(class_names, 'Choose class:')
    class_type: Class = [c for c in classes if c.index == class_type][0]
    # Choose proficiencies within the class
    chosen_proficiencies: List[str] = []
    for choose, proficiency_choices in class_type.proficiency_choices:
        proficiency_names: List[str] = [prof.index for prof in proficiency_choices]
        prof_count = choose
        while prof_count:
            prof_label = 'proficiency' if prof_count == 1 else 'proficiencies'
            prof_name: str = read_choice(proficiency_names, f'Choose {prof_count} class\' {prof_label}:')
            chosen_proficiencies.append(prof_name)
            proficiency_names.remove(prof_name)
            prof_count -= 1
    for chosen_prof_name in chosen_proficiencies:
        chosen_prof: Proficiency = [prof for prof in proficiencies if prof.name == chosen_prof_name][0]
        proficiencies.append(chosen_prof)
    # should be deleted (duplicate with character.class_type.proficiencies)
    proficiencies += class_type.proficiencies

    """ 3. Determine ability scores (Strength, Dexterity, Constitution, Intelligence, Wisdom, and Charisma.)"""
    ability_scores: List[int] = ability_rolls()
    strength: int = read_choice(ability_scores, 'Choose strength:')
    ability_scores.remove(strength)
    dexterity: int = read_choice(ability_scores, 'Choose dexterity:')
    ability_scores.remove(dexterity)
    constitution: int = read_choice(ability_scores, 'Choose constitution:')
    ability_scores.remove(constitution)
    intelligence: int = read_choice(ability_scores, 'Choose intelligence:')
    ability_scores.remove(intelligence)
    wisdom: int = read_choice(ability_scores, 'Choose wisdom:')
    ability_scores.remove(wisdom)
    charisma: int = read_choice(ability_scores, 'Choose charisma:')
    abilities: Abilities = Abilities(strength, dexterity, constitution, intelligence, wisdom, charisma)
    mod = lambda x: (x - 10) // 2
    ability_modifiers: Abilities = Abilities(mod(strength), mod(dexterity), mod(constitution), mod(intelligence), mod(wisdom), mod(charisma))

    """ 4. Describe your character (name, gender, clan/family/virtue/ethnic, height/weight, ...) """
    genders = ['male', 'female']
    gender: str = read_choice(genders, 'Choose genre:')
    ethnic: str = None
    if race.index in ['human', 'half-elf']:
        name, ethnic = read_name(race.index, gender, human_names, reserved_names)
    else:
        name = read_name(race.index, gender, names, reserved_names)
    hw_conv_table = read_csvfile("Height and Weight-Height and Weight.csv")
    race_name = race.name if not subrace else subrace.name
    found_record = [x for x in hw_conv_table if x[0] == race_name]
    if not found_record:
        found_record = [x for x in hw_conv_table if x[0] == race.name]
    try:
        race_name, base_height, height_modifier, base_weight, weight_modifier = found_record[0]
    except IndexError:
        print(f'found_record: {found_record}')
    feet2inch = lambda ft, inches: 12 * ft + inches
    inch2feet = lambda inches: f"{inches // 12}'{inches - (inches // 12) * 12}"
    height = feet2inch(*tuple((map(int, tuple(base_height.split("'"))))))
    roll_num, dice_num = map(int, height_modifier.split('d'))
    height_roll_result = sum([randint(1, dice_num) for _ in range(roll_num)])
    height += height_roll_result
    weight, unit = base_weight.split(' ')
    if 'd' in weight_modifier:
        roll_num, dice_num = map(int, weight_modifier.split('d'))
        weight_roll_result = sum([randint(1, dice_num) for _ in range(roll_num)])
    else:
        weight_roll_result = 1
    weight = int(weight) + height_roll_result * weight_roll_result
    """ 5. Choose equipment """
    # Choose starting equipment within the class
    starting_equipment: List[Equipment] = choose_equipment_from(class_type.starting_equipment_options)
    starting_equipment += [inv.equipment for inv in class_type.starting_equipment for _ in range(inv.quantity)]
    return race, subrace, class_type, abilities, ability_modifiers, name, gender, ethnic, inch2feet(height), f'{weight} {unit}', starting_equipment


def load_character_collections() -> Tuple:
    """ Character creation database """
    races_names: List[str] = populate(collection_name='races', key_name='results')
    races: List[Race] = [request_race(name) for name in races_names]
    subraces_names: List[str] = populate(collection_name='subraces', key_name='results')
    subraces: List[Race] = [request_subrace(name) for name in subraces_names]
    names = dict()
    for race in races:
        if race.index not in ['human', 'half-elf']:
            names[race.index] = populate_names(race)
    human_names: dict() = populate_human_names()
    classes: List[str] = populate(collection_name='classes', key_name='results')
    classes = [request_class(name) for name in classes]
    alignments: List[str] = populate(collection_name='alignments', key_name='results')
    equipment_names: List[str] = populate(collection_name='equipment', key_name='results')
    equipments = [request_equipment(name) for name in equipment_names]
    proficiencies_names: List[str] = populate(collection_name='proficiencies', key_name='results')
    proficiencies = [request_proficiency(name) for name in proficiencies_names]
    return races, subraces, classes, alignments, equipments, proficiencies, names, human_names


def load_dungeon_collections() -> Tuple:
    """ Monster, Armor and Weapon databases """
    monsters_names: List[str] = populate(collection_name='monsters', key_name='results')
    monsters: List[Monster] = [request_monster(name) for name in monsters_names]
    armors_names: List[str] = populate(collection_name='armors', key_name='equipment')
    armors: List[Armor] = [request_armor(name) for name in armors_names]
    weapons_names: List[str] = populate(collection_name='weapons', key_name='equipment')
    weapons: List[Weapon] = [request_weapon(name) for name in weapons_names]
    return monsters, armors, weapons


def create_new_character(roster) -> Character:
    """ Character creation """
    races, subraces, classes, alignments, equipments, proficiencies, names, human_names = load_character_collections()
    reserved_names: List[str] = [c.name for c in roster]
    race, subrace, class_type, abilities, ability_modifiers, name, gender, ethnic, height, weight, starting_equipment \
        = create_character(races=races, subraces=subraces, classes=classes, equipments=equipments, proficiencies=proficiencies, names=names, human_names=human_names, reserved_names=reserved_names)
    # Equip the character with a weapon and an armor from the starting equipment list of the class
    available_weapons = {e.index: e for e in starting_equipment if e.category.index == 'weapon'}
    available_armors = {e.index: e for e in starting_equipment if e.category.index == 'armor'}
    chosen_weapon: str = read_choice(list(available_weapons.keys()), f'Choose 1 weapon to equip:')
    chosen_weapon: Weapon = available_weapons[chosen_weapon]
    if not available_armors:
        available_armors = {'skin-armor': request_armor('skin-armor')}
    chosen_armor: str = read_choice(list(available_armors.keys()), f'Choose 1 armor to equip')
    chosen_armor: Armor = available_armors[chosen_armor]
    hit_points = class_type.hit_die
    character: Character = Character(race=race,
                                     subrace=subrace,
                                     class_type=class_type,
                                     proficiencies=class_type.proficiencies + race.starting_proficiencies,
                                     abilities=abilities,
                                     ability_modifiers=ability_modifiers,
                                     gender=gender,
                                     name=name,
                                     ethnic=ethnic,
                                     height=height,
                                     weight=weight,
                                     inventory=starting_equipment,
                                     armor=chosen_armor,
                                     weapon=chosen_weapon,
                                     hit_points=hit_points,
                                     max_hit_points=hit_points,
                                     xp=0, level=1,
                                     healing_potions=[Potion('2d4')] * POTION_INITIAL_PACK,
                                     monster_kills=0,
                                     age=18 * 52 + randint(0, 299),
                                     gold=90 + randint(0, 99))
    return character


def save_character(char: Character):
    # print(f'Sauvegarde personnage {char.name}')
    with open(f'{characters_dir}/{char.name}.dmp', 'wb') as f1:
        pickle.dump(char, f1)


def get_roster(characters_dir: str) -> List[Character]:
    roster: List[Character] = []
    # char_file_list: List[str] = os.listdir(characters_dir)
    char_file_list = os.scandir(characters_dir)
    for entry in char_file_list:
        if entry.is_file():
            with open(entry, 'rb') as f1:
                roster.append(pickle.load(f1))
    # for character_filename in char_file_list:
    #     with open(f'{path}/gameState/characters/{character_filename}', 'rb') as f1:
    #         roster.append(pickle.load(f1))
    return roster


def display_adventurers(roster: List[Character], party: List[Character], location: str):
    toc: str = '{:-^53}\n'.format(f' {location} ')
    if party:
        toc += '{:-^53}\n'.format(f' ** NOT AVAILABLE (in dungeon) ** ')
    for char in roster:
        if char.in_dungeon:
            char_status: str = f' ({char.status})' if char.status != 'OK' else ''
            toc += '|{:^51}|\n'.format(f'{char.name}{char_status} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})')
    toc += '{:-^53}\n'.format(f' ** AVAILABLE ** ')
    for char in roster:
        if not char.in_dungeon:
            char_status: str = f' ({char.status})' if char.status != 'OK' else ''
            toc += '|{:^51}|\n'.format(f'{char.name}{char_status} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})')
    toc += '|{:-^51}|\n'.format('')
    print(toc)


def adventure_prompt_ok() -> bool:
    print(f'{color.DARKCYAN}Do you want to continue adventure? (Y/N){color.END}')
    response = input()
    while response not in ['y', 'n', 'Y', 'N']:
        print(f'{color.DARKCYAN}Do you want to continue adventure? (Y/N){color.END}')
        response = input()
    return True if response in ['Y', 'y'] else False


def location_prompt_ok(location: str) -> bool:
    print(f'{color.DARKCYAN}Do you want to go to {location}? (Y/N){color.END}')
    response = input()
    while response not in ['y', 'n', 'Y', 'N']:
        print(f'{color.DARKCYAN}Do you want to go to {location}? (Y/N){color.END}')
        response = input()
    return True if response in ['Y', 'y'] else False


def display_character_sheet(char: Character):
    sheet = '+{:-^51}+\n'.format(f' {char.name} (age: {char.age // 52})')
    sheet += f'| str: {str(char.strength).rjust(2)} | int: {str(char.strength).rjust(2)} | hp: {str(char.hit_points).rjust(3)} / {str(char.max_hit_points).ljust(4)}| {str(char.class_type).upper().ljust(14)}|\n'
    sheet += f'| dex: {str(char.dexterity).rjust(2)} | wis: {str(char.wisdom).rjust(2)} | xp: {str(char.xp).ljust(10)}| {str(char.race).title().ljust(14)}|\n'
    sheet += f'| con: {str(char.constitution).rjust(2)} | cha: {str(char.charism).rjust(2)} | level: {str(char.level).ljust(7)}| AC: {str(char.armor_class).ljust(10)}|\n'
    sheet += '+{:-^51}+\n'.format('')
    sheet += '|{:^51}|\n'.format(f'kills = {char.monster_kills}')
    sheet += '|{:^51}|\n'.format(f'healing potions = {len(char.healing_potions)}')
    sheet += '|{:^51}|\n'.format(f'armor = {char.armor.name.title()}')
    sheet += '|{:^51}|\n'.format(f'weapon = {char.weapon.name.title()} - Damage = {char.weapon.damage_dice}')
    sheet += '|{:^51}|\n'.format(f'gold = {char.gold} gp')
    sheet += '+{:-^51}+\n'.format('')
    print(sheet)


def efface_ecran():
    """
    Efface l’écran de la console
    """
    if sys.platform.startswith("win"):
        # Si système Windows
        os.system("cls")
    else:
        # Si système Linux ou OS X
        os.system("clear")


def display_character_sheet_pyQT(char: Character):
    app = QApplication(sys.argv)

    dialog = QDialog()
    ui = Ui_character_Dialog()
    ui.setupUi(dialog)
    display_char_sheet(dialog, ui, char)


def select_character(roster: List[Character]) -> Character:
    """ Select Character """
    character_name: str = read_choice([c.name for c in roster], f'Choose a character to {Color.GREEN}* Begin adventure *{Color.END}')
    character = [c for c in roster if c.name == character_name][0]
    return character


def arena(character: Character):
    """ Combat simulation """
    print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
    print(f'{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}')
    print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
    attack_count: int = 0
    killed_monsters: int = 0
    previous_level: int = character.level

    difficulty: List[str] = ['HARD', 'MEDIUM', 'EASY', 'KIDDIE']
    arena_level: str = read_choice(difficulty, 'Select difficulty:')

    match arena_level:
        case 'HARD':
            # monsters_to_fight = [m for m in monsters if m.level > character.level]
            monsters_to_fight = [m for m in monsters if m.challenge_rating > character.level]
        case 'MEDIUM':
            # monsters_to_fight = [m for m in monsters if m.level < character.level + 5]
            monsters_to_fight = [m for m in monsters if m.challenge_rating == character.level]
        case 'EASY':
            monsters_to_fight = [m for m in monsters if m.challenge_rating < character.level]
        case 'KIDDIE':
            monsters_to_fight = [m for m in monsters if m.level < character.level + 5]

    # while character.hit_points > 0 and character.level < 5:
    while character.hit_points > 0 and attack_count < 500:
        # if character.level < len(xp_levels) and character.xp > xp_levels[character.level]:
        #     character.gain_level(pause=PAUSE_ON_RAISE_LEVEL)
        monster: Monster = copy(choice(monsters_to_fight))
        cprint(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        cprint(f'{color.PURPLE} New explore_dungeon! {character} vs {monster}{color.END}')
        cprint(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        round_num = 0
        monster_max_hp = monster.hit_points
        while monster.hit_points > 0:
            round_num += 1
            cprint('-------------------------------------------------------')
            cprint(f'Round {round_num}: {character.name} ({character.hit_points}/{character.max_hit_points}) vs {monster.name} ({monster.hit_points}/{monster_max_hp})')
            cprint('-------------------------------------------------------')
            if character.hit_points < 0.5 * character.max_hit_points and character.healing_potions:
                cprint(f'{len(character.healing_potions)} remaining potions')
                character.drink_potion()
            attack_count += 1
            monster_hp_damage = monster.attack(character)
            character_hp_damage = character.attack(monster)
            priority_dice = randint(0, 1)
            if priority_dice == 0:  # monster attacks first
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    character.status = 'DEAD'
                    break
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    killed_monsters += 1
                    character.treasure(weapons, armors)
                    break
            else:  # character attacks first
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    killed_monsters += 1
                    character.treasure(weapons, armors)
                    break
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    character.status = 'DEAD'
                    break

    level_up_msg: str = f' and reached level #{character.level}' if previous_level > character.level else ''

    if character.hit_points <= 0:
        print(f'{character.name} has been killed by a {monster.name} after {attack_count} attack rounds and {killed_monsters} monsters kills{level_up_msg}')
    else:
        print(f'{character.name} has killed {killed_monsters} monsters{level_up_msg}')

    character.monster_kills += killed_monsters
    save_character(character)
    display_character_sheet(character)


def display_party(party: List[Character]):
    cols = 53
    formatter: str = "+{:-^" + str(cols) + "}+\n"
    sheet = formatter.format(f' Party')
    col1, col2, col3, col4, col5 = 10, 10, 3, 5, 6
    col_level = 3
    sheet += f'| {str("Name").ljust(col1)} | {str("LVL").rjust(col_level)} | {str("Class").ljust(col2)} | {str("AC").rjust(col3)} | {str("Hits").ljust(col4)}| {str("Status ").rjust(col5)}|\n'
    if party:
        sheet += formatter.format('')
    for char in party:
        sheet += f'| {str(char.name).ljust(col1)} | {str(char.level).rjust(col_level)} | {str(char.class_type).ljust(col2)} | {str(char.armor_class).rjust(col3)} | {str(char.hit_points).ljust(col4)}| {str(char.status).rjust(col5)} |\n'
    sheet += formatter.format('')
    print(sheet)


def add_member_to_party(roster: List[Character], party: List[Character]):
    if len(party) == 6:
        print(f'Party is **FULL**')
        sleep(1)
        return
    if not roster:
        print(f'No more character in roster! Go to [Training Grounds] to create one.')
        sleep(2)
        return
    char_names: List[str] = [c.name for c in roster if c.status == 'OK' and c not in party and not c.in_dungeon]
    if not char_names:
        print(f'No available character to join party!')
        sleep(2)
        return
    name: str = read_choice(char_names, 'Select character to add in party')
    char: Character = get_character(name, roster)
    if char:
        party.append(char)
    else:
        print(f'Program error! {name} unknown in Castle - Please contact the administrator...')
        sleep(1)


def delete_member_from_party(roster: List[Character], party: List[Character]):
    if not party:
        print(f'no member in **PARTY**')
        sleep(1)
        return
    char_names: List[str] = [c.name for c in party]
    char_name: str = read_choice(char_names, 'Select character to remove from party')
    char: Character = get_character(char_name, party)
    if char:
        party.remove(char)
    else:
        print(f'Program error! {char_name} not in the party - Please contact the administrator...')
        sleep(1)


def gilgamesh_tavern(party: List[Character], roster: List[Character]):
    exit_tavern: bool = False
    while not exit_tavern:
        efface_ecran()
        print('+-----------------------------+')
        print('|  ** GILGAMESH\'S TAVERN **  |')
        print('+-----------------------------+')
        display_party(party)
        gt_options: List[str] = ['Add Member', 'Remove Member', 'Character Status', 'Divvy Gold', 'Exit Tavern']
        option: str = read_choice(gt_options)
        match option:
            case 'Add Member':
                add_member_to_party(roster, party)
            case 'Remove Member':
                delete_member_from_party(roster, party)
            case 'Character Status':
                if not party:
                    print('No characters remains in the party!')
                    sleep(2)
                    continue
                char_names: List[str] = [c.name for c in party]
                name: str = read_choice(char_names, 'Select a Character:')
                char: Character = get_character(name, party)
                display_character_sheet(char)
                exit_message()
            case 'Divvy Gold':
                if not party:
                    print('No characters remains in the party!')
                    sleep(2)
                    continue
                total_gold: int = sum([c.gold for c in party])
                for char in party:
                    char.gold = total_gold // len(party)
                print("All the party's gold has been divided.")
                for char in party:
                    save_character(char)
                sleep(1)
            case 'Exit Tavern':
                exit_tavern = True
            case _:
                continue


def display_rest_message(char: Character):
    efface_ecran()
    print(f'{char.name} is Sleeping...')
    print(f'\tHits {char.hit_points}/{char.max_hit_points}')
    print(f'\t\tYou have {char.gold}GP')
    sleep(1)


def rest_character(char: Character, fee: int, weeks: int):
    display_rest_message(char)
    while fee and char.hit_points < char.max_hit_points and char.gold >= fee:
        print(f'{char.name} gains {fee / 10} hp')
        char.hit_points = min(char.max_hit_points, char.hit_points + fee // 10)
        char.gold -= fee
        char.age += weeks
        display_rest_message(char)
    if char.level < len(xp_levels) and char.xp > xp_levels[char.level]:
        char.gain_level()
    exit_message()


def exit_message(message: str = None):
    if message:
        print(message)
    print('[Return] to continue')
    while True:
        k = get_key()
        if k == 'return':
            break


def temple_of_cant(party: List[Character, roster: List[Character]]):
    exit_temple: bool = False
    while not exit_temple:
        efface_ecran()
        print('+----------------------------+')
        print('|    ** TEMPLE OF CANT **    |')
        print('+----------------------------+')
        print('Temple of Cant -- Praise God!!!')
        cures_costs_per_level: dict() = {'PARALYZED': 100, 'STONED': 200, 'DEAD': 250, 'ASHES': 500}
        cures_candidates: dict() = [f'{c.name} ({cures_costs_per_level[c.status] * c.level} GP)' for c in roster + party if c.status not in ('OK', 'LOST')]
        if not cures_candidates:
            print('No more character to save ** HERE! **')
            exit_temple = True
            sleep(3)
            continue
        choice: str = read_choice(cures_candidates + ['Exit Temple'], 'Who do You Want to Save?')
        if choice == 'Exit Temple':
            exit_temple = True
        else:
            efface_ecran()
            char_to_save: Character = get_character(choice.split()[0], roster + party)
            contributor_names: List[str] = [c.name for c in party if c.status == 'OK']
            char_name: str = read_choice(contributor_names, 'Who will Contribute?')
            char_to_contribute: Character = get_character(char_name, party)
            if not party:
                print('No character remains in the party.')
                sleep(2)
                exit_temple = True
            if char_to_contribute.gold < cures_costs_per_level[char_to_save.status] * char_to_save.level:
                print('Go away! You don\'t have enough of money!')
                sleep(2)
            elif char_to_save.status == 'DEAD':
                success: bool = randint(1, 100) < 50 + 3 * char_to_save.constitution
                if success:
                    char_to_save.status = 'OK'
                    char_to_save.hit_points = 1
                    char_to_save.age += randint(1, 52)
                    print(f'{char_to_save.name} ** LIVES! ***')
                else:
                    char_to_save.status = 'ASHES'
                    print(f'{char_to_save.name} converts to ** ASHES! ***')
                save_character(char_to_save)
                sleep(2)
            elif char_to_save.status == 'ASHES':
                success: bool = randint(1, 100) < 40 + 3 * char_to_save.constitution
                if success:
                    char_to_save.status = 'OK'
                    char_to_save.hit_points = char_to_save.max_hit_points
                    char_to_save.age += randint(1, 52)
                    exit_message(f'{char_to_save.name} ** LIVES! ***')
                else:
                    char_to_save.status = 'LOST'
                    print(f'{char_to_save.name} is ** LOST! ***')
                save_character(char_to_save)
                sleep(2)


def adventurer_inn(party):
    exit_inn: bool = False
    while not exit_inn:
        efface_ecran()
        print('+-----------------------------+')
        print('|   ** ADVENTURER\'S INN **   |')
        print('+-----------------------------+')
        print('Welcome to Adventurer\'s Inn!')
        choice: str = read_choice([c.name for c in party] + ['Exit Adventurer\'s Inn'], 'Who will Enter?')
        if choice == 'Exit Adventurer\'s Inn':
            exit_inn = True
        else:
            efface_ecran()
            char: Character = get_character(choice, party)
            print(f'Welcome, {char.name}!')
            rooms: List[str] = ['The Stables (Free!)', 'A Cot (10 GP / Week)', 'Economy Room (100 GP / Week)', 'Merchant Suites (200 GP / Week)', 'The Royal Suites (500 GP / Week)']
            fees: List[int] = [0, 10, 100, 200, 500]
            weeks: List[int] = [0, 1, 3, 7, 10]
            room: str = read_choice(rooms, f'Hello {char.name}.')
            room_number: int = rooms.index(room)
            if fees[room_number] > char.gold:
                print(f'You Don\'t Have Enough Gold.')
                sleep(2)
                continue
            # print(f'{char.name} selected {room} - Fee is {fees[fee_no]} GP / Week!')
            rest_character(char, fees[room_number], weeks[room_number])
            save_character(char)


def get_character(name: str, roster: List[Character]) -> Optional[Character]:
    char_list = [c for c in roster if c.name == name]
    return char_list[0] if char_list else None


def simulate_arena(roster: List[Character]):
    if not roster:
        print(f'no available characters for arena!')
        sleep(2)
        return
    char: Character = select_character(roster)
    while char.status != 'OK':
        print(f'{char.name} is ** {char.status} ** - Please select another character!')
        char: Character = select_character(roster)
    display_character_sheet(char)
    while continue_message(message='Do you want to start a new combat simulation? (Y/N)'):
        # efface_ecran()
        # display_character_sheet_pyQT(character)
        while char.status != 'OK':
            print(f'{char.name} is ** {char.status} ** - Please select another character!')
            char: Character = select_character(roster)
            continue
        arena(char)


def rename_character_prompt_ok(char: Character, new_name: str) -> bool:
    print(f'Are you sure you want to rename {char.name} to {new_name}(Y/N)?')
    while True:
        key = get_key()
        if key in ['y', 'Y']:
            print(f'{char.name} has been ** RENAMED ** to {new_name}')
            sleep(2)
            return True
        elif key in ['n', 'N']:
            print(f'Renaming of {char.name} cancelled.')
            sleep(2)
            return False


def delete_character_prompt_ok(char: Character) -> bool:
    print(f'Are you sure you want to delete {char.name} (Y/N)?')
    while True:
        key = get_key()
        if key in ['y', 'Y']:
            os.remove(f'{characters_dir}/{char.name}.dmp')
            print(f'{char.name} has been ** DELETED **')
            sleep(2)
            return True
        elif key in ['n', 'N']:
            print(f'Deletion cancelled :-) {char.name} ** STILL IN GAME **')
            sleep(2)
            return False


def training_grounds(roster: List[Character]):
    tg_options: List[str] = ['Create a New Character', 'Character Status', 'Delete a Character', 'Rename a Character', 'Change a Character\'s class', 'System', 'Return to Castle']
    exit_training_grounds: bool = False
    while not exit_training_grounds:
        efface_ecran()
        print('+------------------------+')
        print('| ** TRAINING GROUNDS ** |')
        print('+------------------------+')
        option: str = read_choice(tg_options)
        char_names: List[str] = [c.name for c in roster]
        match option:
            case 'Create a New Character':
                character = create_new_character(roster)
                save_character(character)
                roster.append(character)
            case 'Character Status':
                efface_ecran()
                name: str = read_choice(char_names, 'Select a Character.')
                char: Character = get_character(name, roster)
                display_character_sheet(char)
                exit_message()
            case 'Delete a Character':
                name: str = read_choice(char_names, 'Select a Character to Delete.')
                char: Character = get_character(name, roster)
                display_character_sheet(char)
                if delete_character_prompt_ok(char):
                    if char in party:
                        party.remove(char)
                    roster.remove(char)
            case 'Rename a Character':
                name: str = read_choice(char_names, 'Select a Character to Rename.')
                char: Character = get_character(name, roster + party)
                print(f'Current Name is {char.name}.')
                name_ok: bool = False
                while not name_ok:
                    new_name: str = input('Input New Name: ')
                    if new_name in char_names:
                        print(f'{new_name} already taken! Please choose another one!')
                        continue
                    name_ok = True
                if not rename_character_prompt_ok(char, new_name):
                    continue
                os.remove(f'{characters_dir}/{char.name}.dmp')
                char.name = new_name
                save_character(char)
                sleep(2)
            case 'Change a Character\'s class':
                input('not yet created!... [Return] to main menu')
            case 'System':
                input('not yet created!... [Return] to main menu')
            case 'Return to Castle':
                exit_training_grounds = True


def explore_dungeon(party: List[Character], monsters: List[Monster]):
    """ Combat simulation """
    print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
    print(f'{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}')
    print(f'{color.PURPLE}-----------------------------------------------------------{color.END}')
    # encounters_count: int = 0
    # killed_monsters: int = 0

    difficulty: List[str] = ['HARD', 'MEDIUM', 'EASY']
    arena_level: str = read_choice(difficulty, 'Select difficulty:')

    max_level_char: int = max([c.level for c in party])

    match arena_level:
        case 'HARD':
            monsters_to_fight = [m for m in monsters if m.challenge_rating > max_level_char]
        case 'MEDIUM':
            monsters_to_fight = [m for m in monsters if m.challenge_rating == max_level_char]
        case 'EASY':
            monsters_to_fight = [m for m in monsters if m.challenge_rating < max_level_char]

    alive_chars: List[Character] = [c for c in party if c.hit_points > 0]
    while alive_chars:
        if continue_message(f'Do you want to go back to [Castle]? (Y/N)'):
            return
        monsters_selection: List[Monster] = sample(monsters_to_fight, randint(1, 2))
        monsters: List[Monster] = [copy(m) for m in monsters_selection]
        cprint(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        cprint(f'{color.PURPLE} New encounter!{color.END}')
        for i, monster in enumerate(monsters):
            cprint(f'{color.PURPLE} Monster #{i} : {monster.name} ({monster.hit_points} HP){color.END}')
        cprint(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        attack_queue = [(c, randint(1, c.abilities.dex)) for c in party] + [(m, randint(1, m.abilities.dex)) for m in monsters]
        attack_queue.sort(key=lambda x: x[1], reverse=True)
        attackers = [c for c, init_roll in attack_queue]
        alive_monsters: List[Monster] = [c for c in monsters if c.hit_points > 0]
        round_num = 0
        flee_combat: bool = False
        while alive_monsters:
            message: str = 'engage' if not round_num else 'continue'
            if not continue_message(f'Do you want to {message} combat? (Y/N)'):
                flee_combat = True
                break
            round_num += 1
            cprint('-------------------------------------------------------')
            cprint(f'{color.DARKCYAN} Round {round_num} :{color.END}')
            for i, monster in enumerate(alive_monsters):
                cprint(f'{color.PURPLE} Monster #{i} : {monster.name} ({monster.hit_points} HP){color.END}')
            cprint('-------------------------------------------------------')
            display_party(party)
            # Start of Round
            queue = [c for c in attackers if c.hit_points > 0]
            while queue:
                attacker = queue.pop()
                if attacker.hit_points > 0:
                    if isinstance(attacker, Monster):
                        # Monster attacks the weakest alive character
                        chars: List[Character] = [c for c in attackers if isinstance(c, Character) if c.hit_points > 0]
                        if not chars:
                            break
                        char: Character = min(chars, key=lambda c: c.hit_points)
                        char.hit_points -= monster.attack(char)
                        if char.hit_points <= 0:
                            char.status = 'DEAD'
                            cprint(f'{char.name} is ** KILLED **!')
                    else:
                        monsters: List[Monster] = [c for c in attackers if isinstance(c, Monster) if c.hit_points > 0]
                        if not monsters:
                            break
                        if attacker.hit_points < 0.5 * attacker.max_hit_points and attacker.healing_potions:
                            attacker.drink_potion()
                            cprint(f'{attacker.name} has {len(attacker.healing_potions)} remaining potions')
                        else:
                            # Character attacks the weakest alive monster
                            monster: Monster = min(monsters, key=lambda m: m.hit_points)
                            monster.hit_points -= attacker.attack(monster)
                            if monster.hit_points <= 0:
                                attacker.victory(monster)
                                attacker.treasure(weapons, armors)
            # End of Round
            alive_chars: List[Character] = [c for c in party if c.hit_points > 0]
            alive_monsters: List[Monster] = [c for c in monsters if c.hit_points > 0]
        if not alive_chars:
            exit_message(f'** DEFEAT! ALL PARTY HAS BEEN KILLED **')
            break
        elif not alive_monsters:
            exit_message(f'** VICTORY! **')
        elif flee_combat:
            exit_message(f'** Party successfully escaped! **')


if __name__ == '__main__':
    seed(time())
    PAUSE_ON_RAISE_LEVEL = True
    POTION_INITIAL_PACK = 5
    path = os.path.dirname(__file__)
    characters_dir = f'{path}/gameState/characters'

    """ Load XP Levels """
    xp_levels = []
    levels = read_csvfile("XP Levels-XP Levels.csv")
    for xp_needed, level, master_bonus in levels:
        xp_levels.append(int(xp_needed))

    """ Load Monster, Armor and Weapon databases """
    monsters, armors, weapons = load_dungeon_collections()
    armors = list(filter(lambda a: a, armors))
    weapons = list(filter(lambda w: w, weapons))

    locations: List[str] = ['Edge of Town', 'Castle']
    castle_destinations: List[str] = ['Gilgamesh\'s Tavern', 'Adventurer\'s Inn', 'Temple of Cant', 'Boltac\'s Trading Post', 'Edge of Town']
    edge_of_town_destinations: List[str] = ['Training Grounds', 'Maze', 'Leave Game', 'Castle']
    roster: List[Character] = get_roster(characters_dir)
    party_ids: List[int] = set([c.id_party for c in roster if c.in_dungeon])
    adventurer_groups: dict() = {p_id: [c for c in roster if c.id_party == p_id] for p_id in party_ids}

    location = 'Castle'
    party: List[Character] = []
    while True:
        efface_ecran()
        if location == 'Castle':
            print('+----------------------+')
            print('|     ** CASTLE **     |')
            print('+----------------------+')
            destination: str = read_choice(castle_destinations)
            party = [c for c in party if c.status == 'OK']
            match destination:
                case 'Gilgamesh\'s Tavern':
                    gilgamesh_tavern(party, roster)
                case 'Adventurer\'s Inn':
                    if not party:
                        print('No characters remains in the party!')
                        sleep(2)
                        continue
                    adventurer_inn(party)
                case 'Temple of Cant':
                    if not party:
                        print('No characters remains in the party!')
                        sleep(2)
                        continue
                    temple_of_cant(party)
                case 'Boltac\'s Trading Post':
                    input('not yet created!... [Return] to Castle')
                case 'Edge of Town':
                    location = 'Edge of Town'
                    continue
                case _:
                    continue
        else:
            print('+----------------------+')
            print('|  ** EDGE OF TOWN **  |')
            print('+----------------------+')
            destination: str = read_choice(edge_of_town_destinations)
            match destination:
                case 'Training Grounds':
                    efface_ecran()
                    training_grounds(roster)
                    location = 'Castle'
                case 'Maze':
                    efface_ecran()
                    game_modes: List[str] = ['ARENA (Simulation)', 'WIZARDRY (Enter Dungeon)']
                    game_mode: str = read_choice(game_modes, 'Choose game mode:')
                    if game_mode == 'ARENA (Simulation)':
                        display_adventurers(roster=roster, party=party, location=location)
                        simulate_arena(roster)
                        location = 'Castle'
                    else:
                        if party:
                            display_party(party)
                            explore_dungeon(party, monsters)
                            for char in party:
                                if char.hit_points <= 0:
                                    char.status = 'DEAD'
                                save_character(char)
                            location = 'Castle'
                        else:
                            if roster:
                                print(f'** NO PARTY FOUND! ** Return to {Color.RED}Castle{Color.END} to recruit adventurers!')
                                location = 'Castle'
                                sleep(2)
                            else:
                                print(f'** NO CHARACTERS FOUND! ** Return to {Color.RED}Training grounds{Color.END} to create one or more adventurer(s)!')
                                sleep(2)
                case 'Leave Game':
                    print(f'Bye, see you in a next adventure :-)')
                    exit(0)
                case 'Castle':
                    location = 'Castle'
                    continue
                case _:
                    continue
        efface_ecran()

    # print(f'Sauvegarde Roster')
    # for character in roster_list:
    #     with open(f'{characters_dir}/{character.name}.dmp', 'wb') as f1:
    #         pickle.dump(character, f1)
