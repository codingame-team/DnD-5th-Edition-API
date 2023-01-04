from __future__ import annotations

import pickle
import sys
from copy import copy
from os import listdir
from os.path import isfile, join

from PyQt5.QtWidgets import QApplication, QDialog

from dao_classes import *
from populate_functions import *
from pyQTApp.character_sheet import display_char_sheet
from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
from tools.ability_scores_roll import ability_rolls
from tools.common import cprint, Color


def continue_message():
    print(f'{color.DARKCYAN}Do you want to start a combat simulation? (Y/N){color.END}')
    response = input()
    while response not in ['y', 'n', 'Y', 'N']:
        print(f'{color.DARKCYAN}Do you want to start a combat simulation? (Y/N){color.END}')
        response = input()
    if response in ['y', 'y']:
        return True
    return False


def welcome_message():
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


def read_name(race: str, gender: str, names: dict()):
    """

    :param race: name of the race
    :param genre: name of the gender ['male', 'female', 'nickname', 'surname']
    :param names: dictionary of names
    :return:
    """
    if race in ['human', 'half-elf']:
        ethnic = read_choice('ethnic', list(names.keys()))
        names_list = names[ethnic][gender]
        if len(names[ethnic]) > 2:
            other_key = [key for key in names[ethnic] if key not in ['male', 'female']][0]
            names_list += names[ethnic][other_key]
        name = read_choice('name', names_list)
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
        name = read_choice('name', names_list)
        return name


def read_choice(item_name: str, choice_list: List[str]) -> str:
    choice = None
    while choice not in range(1, len(choice_list) + 1):
        items_list = '\n'.join([f'{i + 1}) {item}' for i, item in enumerate(choice_list)])
        print(f'Choose {item_name}:\n{items_list}')
        err_msg = f'Bad value! Please enter a number between 1 and {len(choice_list)}'
        try:
            choice = int(input())
            if choice not in range(1, len(choice_list) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            continue
    return choice_list[choice - 1]


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
        inv_choice: str = read_choice(f'{inv_count} equipment{plural}', list(inv_choices.keys()))
        chosen_inv: Inventory | List[Inventory] = inv_choices[inv_choice]
        if type(chosen_inv) is list:
            starting_equipment += [inv.equipment for inv in chosen_inv for _ in range(inv.quantity)]
        else:
            if isinstance(chosen_inv.equipment, EquipmentCategory):
                inv_options_cat: List[str] = populate(collection_name=chosen_inv.equipment.index, key_name='equipment', collection_path='data/equipment-categories')
                plural: str = '' if inv_count == 1 else 's'
                inv_choice: str = read_choice(f'{inv_count} {chosen_inv.equipment.name}{plural}', inv_options_cat)
                starting_equipment.append(request_equipment(inv_choice))
            else:
                starting_equipment.append(request_equipment(chosen_inv.equipment.index))
        # print(f'removing chosen_inv: {chosen_inv}')
        # inv_options.remove(chosen_inv)
        # inv_count -= 1
    return starting_equipment


def create_character(races: List[Race], subraces: List[SubRace], classes: List[Class], proficiencies: List[Proficiency], equipments: List[Equipment], names: dict(), human_names: dict()):
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    print(f'{color.PURPLE} Character creation based on DnD 5th edition API{color.END}')
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    """ 1. Choose a race """
    races_names: List[str] = [r.index for r in races]
    race: str = read_choice('race', races_names)
    race: Race = [r for r in races if r.index == race][0]
    subraces_names: List[str] = [s.index for s in subraces for r in races if r.index == race.index and r.index in s.index]
    subrace = None
    if subraces_names:
        subrace: str = read_choice('subrace', subraces_names)
        subrace: SubRace = [r for r in subraces if r.index == subrace][0]
    # Choose proficiencies within the race
    chosen_proficiencies: List[str] = []
    for choose, proficiency_options in race.starting_proficiency_options:
        proficiency_names: List[str] = [prof.index for prof in proficiency_options]
        prof_count = choose
        while prof_count:
            prof_label = 'proficiency' if prof_count == 1 else 'proficiencies'
            prof_name: str = read_choice(f'{prof_count} race\'s {prof_label}', proficiency_names)
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
    class_type: str = read_choice('class', class_names)
    class_type: Class = [c for c in classes if c.index == class_type][0]
    # Choose proficiencies within the class
    chosen_proficiencies: List[str] = []
    for choose, proficiency_choices in class_type.proficiency_choices:
        proficiency_names: List[str] = [prof.index for prof in proficiency_choices]
        prof_count = choose
        while prof_count:
            prof_label = 'proficiency' if prof_count == 1 else 'proficiencies'
            prof_name: str = read_choice(f'{prof_count} class\' {prof_label}', proficiency_names)
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
    strength: int = read_choice('strength', ability_scores)
    ability_scores.remove(strength)
    dexterity: int = read_choice('dexterity', ability_scores)
    ability_scores.remove(dexterity)
    constitution: int = read_choice('constitution', ability_scores)
    ability_scores.remove(constitution)
    intelligence: int = read_choice('intelligence', ability_scores)
    ability_scores.remove(intelligence)
    wisdom: int = read_choice('wisdom', ability_scores)
    ability_scores.remove(wisdom)
    charisma: int = read_choice('charisma', ability_scores)
    abilities: Abilities = Abilities(strength, dexterity, constitution, intelligence, wisdom, charisma)
    mod = lambda x: (x - 10) // 2
    ability_modifiers: Abilities = Abilities(mod(strength), mod(dexterity), mod(constitution), mod(intelligence), mod(wisdom), mod(charisma))

    """ 4. Describe your character (name, gender, clan/family/virtue/ethnic, height/weight, ...) """
    genders = ['male', 'female']
    gender: str = read_choice('genre', genders)
    ethnic: str = None
    if race.index in ['human', 'half-elf']:
        name, ethnic = read_name(race.index, gender, human_names)
    else:
        name = read_name(race.index, gender, names)
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
    height_roll_result = sum([random.randint(1, dice_num) for _ in range(roll_num)])
    height += height_roll_result
    weight, unit = base_weight.split(' ')
    if 'd' in weight_modifier:
        roll_num, dice_num = map(int, weight_modifier.split('d'))
        weight_roll_result = sum([random.randint(1, dice_num) for _ in range(roll_num)])
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
    human_names: List[str] = populate_human_names()
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


def init_character() -> Character:
    """ Character creation """
    races, subraces, classes, alignments, equipments, proficiencies, names, human_names = load_character_collections()
    race, subrace, class_type, abilities, ability_modifiers, name, gender, ethnic, height, weight, starting_equipment \
        = create_character(races=races, subraces=subraces, classes=classes, equipments=equipments, proficiencies=proficiencies, names=names, human_names=human_names)
    # Equip the character with a weapon and an armor from the starting equipment list of the class
    available_weapons = {e.index: e for e in starting_equipment if e.category.index == 'weapon'}
    available_armors = {e.index: e for e in starting_equipment if e.category.index == 'armor'}
    chosen_weapon: str = read_choice(f'1 weapon to equip', list(available_weapons.keys()))
    chosen_weapon: Weapon = available_weapons[chosen_weapon]
    if not available_armors:
        available_armors = {'skin-armor': request_armor('skin-armor')}
    chosen_armor: str = read_choice(f'1 armor to equip', list(available_armors.keys()))
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
                                     gold=random.randint(30, 150))
    print(f'Sauvegarde personnage {character.name}')
    with open(f'{characters_dir}/{character.name}.dmp', 'wb') as f1:
        pickle.dump(character, f1)
    return character

def save_character(char: Character):
    # print(f'Sauvegarde personnage {char.name}')
    with open(f'{characters_dir}/{char.name}.dmp', 'wb') as f1:
        pickle.dump(char, f1)

def list_roster() -> List[Character]:
    roster: List[Character] = []
    for character_filename in char_file_list:
        with open(f'{path}/gameState/characters/{character_filename}', 'rb') as f1:
            roster.append(pickle.load(f1))
    return roster

def raise_characters(healing_char: Character, roster: List[Character]):
    chars_to_raise: List[Character] = [c for c in roster if c.hit_points <= 0]
    if healing_char.gold > 1000:
        roster_list: List[str] = [c.name for c in chars_to_raise]
        selected_char: str = read_choice(f'character', roster_list)
        char: Character = [c for c in chars_to_raise if c.name == selected_char][0]
        char.hit_points = 1
        print(f'{char.name} has been raised by {healing_char.name}!')
        healing_char.gold -= 1000
        save_character(healing_char)
        save_character(char)

def cure_characters(healing_char: Character, roster: List[Character]):
    if healing_char.gold > 10:
        roster_list: List[str] = [f'{c.name} ({c.hit_points}/{c.max_hit_points})' for c in roster]
        selected_char: str = read_choice(f'character', roster_list)
        char: Character = [c for c in roster if c.name == selected_char.split()[0]][0]
        recovered_hp = min(char.max_hit_points - char.hit_points, healing_char.gold // 10)
        char.hit_points += recovered_hp
        print(f'{healing_char.name} has cured {char.name} -> {char.hit_points}/{char.max_hit_points}!')
        healing_char.gold -= recovered_hp * 10
        save_character(healing_char)
        save_character(char)

def heal_prompt_ok(heal_type: str = 'raise') -> bool:
    print(f'{color.DARKCYAN}Some characters needs to be cured. Do you want to {heal_type} them? (Y/N){color.END}')
    response = input()
    while response not in ['y', 'n', 'Y', 'N']:
        print(f'{color.DARKCYAN}Some characters needs to be cured. Do you want to {heal_type} them? (Y/N){color.END}')
        response = input()
    return True if response in ['Y', 'y'] else False

def display_roster(location: str = 'Temple of Cant'):
    toc: str = '{:-^53}\n'.format(f' {location} ')
    injured_characters: List[str] = []
    dead_characters: List[str] = []
    ok_characters: List[str] = []
    for character_filename in char_file_list:
        with open(f'{path}/gameState/characters/{character_filename}', 'rb') as f1:
            char: Character = pickle.load(f1)
            if char.hit_points <= 0:
                dead_characters.append(char)
            elif char.hit_points < char.max_hit_points:
                injured_characters.append(char)
            else:
                ok_characters.append(char)
    if ok_characters:
        toc += '{:-^53}\n'.format(f' OK Characters ')
        for char in ok_characters:
            toc += '|{:^51}|\n'.format(f'{char.name} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})')
    if injured_characters:
        toc += '{:-^53}\n'.format(f' Injured Characters ')
        for char in injured_characters:
            toc += '|{:^51}|\n'.format(f'{char.name} -> {char.hit_points}/{char.max_hit_points} (Level {char.level})')
    if dead_characters:
        toc += '{:-^51}\n'.format(f' DEAD Characters ')
        for char in dead_characters:
            toc += '|{:^51}|\n'.format(f'{char.name} (Level {char.level})')

    toc += '|{:-^51}|\n'.format('')
    print(toc)

def adventure_prompt_ok() -> bool:
    print(f'{color.DARKCYAN}Do you want to continue adventure? (Y/N){color.END}')
    response = input()
    while response not in ['y', 'n', 'Y', 'N']:
        print(f'{color.DARKCYAN}Do you want to continue adventure? (Y/N){color.END}')
        response = input()
    return True if response in ['Y', 'y'] else False

def display_character_sheet(char: Character):
    sheet = '{:-^51}\n'.format(f' {char.name} ')
    sheet += f'| str: {str(char.strength).rjust(2)} | int: {str(char.strength).rjust(2)} | hp: {str(char.hit_points).rjust(3)} / {str(char.max_hit_points).ljust(4)}| {str(char.class_type).upper().ljust(14)}|\n'
    sheet += f'| dex: {str(char.dexterity).rjust(2)} | wis: {str(char.wisdom).rjust(2)} | xp: {str(char.xp).ljust(10)}| {str(char.race).title().ljust(14)}|\n'
    sheet += f'| con: {str(char.constitution).rjust(2)} | cha: {str(char.charism).rjust(2)} | level: {str(char.level).ljust(7)}| AC: {str(char.armor_class).ljust(10)}|\n'
    sheet += '|{:-^51}|\n'.format('')
    sheet += '|{:^51}|\n'.format(f'kills = {char.monster_kills}')
    sheet += '|{:^51}|\n'.format(f'healing potions = {len(char.healing_potions)}')
    sheet += '|{:^51}|\n'.format(f'armor = {char.armor.name.title()}')
    sheet += '|{:^51}|\n'.format(f'weapon = {char.weapon.name.title()} - Damage = {char.weapon.damage_dice}')
    sheet += '|{:^51}|\n'.format(f'gold = {char.gold} gp')
    sheet += '|{:^51}|\n'.format('')
    sheet += '|{:^51}|\n'.format('')
    sheet += '|{:-^51}|\n'.format('')
    print(sheet)


def display_character_sheet_pyQT(char: Character):
    app = QApplication(sys.argv)

    dialog = QDialog()
    ui = Ui_character_Dialog()
    ui.setupUi(dialog)
    display_char_sheet(dialog, ui, char)


if __name__ == '__main__':
    random.seed()
    PAUSE_ON_RAISE_LEVEL = False
    POTION_INITIAL_PACK = 5
    path = os.path.dirname(__file__)
    characters_dir = f'{path}/gameState/characters'
    char_file_list: List[str] = os.listdir(f'{path}/gameState/characters')

    """ Load XP Levels """
    xp_levels = []
    levels = read_csvfile("XP Levels-XP Levels.csv")
    for xp_needed, level, master_bonus in levels:
        # xp_levels.append((xp_needed, master_bonus))
        xp_levels.append(int(xp_needed))
    # infile = open("Tables/XP Levels-XP Levels.csv", "r")
    # xp_levels = []
    # for line in infile:
    #     xp_needed, level, master_bonus = line.split(' ')
    #     # xp_levels.append((xp_needed, master_bonus))
    #     xp_levels.append(int(xp_needed))
    """ Load Monster, Armor and Weapon databases """
    monsters, armors, weapons = load_dungeon_collections()
    armors = list(filter(lambda a: a, armors))
    weapons = list(filter(lambda w: w, weapons))

    roster_list: List[Character] = list_roster()

    while True:
        alive_characters: List[Character] = [c for c in roster_list if c.hit_points > 0]
        if not alive_characters:
            print(f'no alive characters... Redirect to {color.BLUE}Training Grounds{color.END} to create a new one!')
            character = init_character()
        else:
            injured_characters: List[Character] = [c for c in alive_characters if c.hit_points < c.max_hit_points]
            dead_characters: List[Character] = [c for c in roster_list if c.hit_points <= 0]
            can_raise_chars: List[Character] = [c for c in alive_characters if c.gold > 1000]
            can_heal_chars: List[Character] = [c for c in alive_characters if c.gold > 10]
            while (dead_characters and can_raise_chars) or (injured_characters and can_heal_chars):
                """ Display Temple of Cant """
                display_roster()
                can_raise_chars: List[Character] = [c for c in alive_characters if c.gold > 1000]
                if dead_characters and can_raise_chars:
                    if not heal_prompt_ok():
                        break
                    healing_char: Character = random.choice(can_raise_chars)
                    raise_characters(healing_char, dead_characters)
                can_heal_chars: List[Character] = [c for c in alive_characters if c.gold > 10]
                if injured_characters and can_heal_chars:
                    if not heal_prompt_ok(heal_type='cure'):
                        break
                    healing_char: Character = random.choice(can_heal_chars)
                    cure_characters(healing_char, injured_characters)
                injured_characters: List[Character] = [c for c in alive_characters if c.hit_points < c.max_hit_points]
                dead_characters: List[Character] = [c for c in roster_list if c.hit_points <= 0]
                can_raise_chars: List[Character] = [c for c in alive_characters if c.gold > 1000]
                can_heal_chars: List[Character] = [c for c in alive_characters if c.gold > 10]

        """ Load Character """
        alive_characters: List[Character] = [c for c in roster_list if c.hit_points > 0]
        roster_names_list: List[str] = [c.name for c in alive_characters]
        display_roster(location='Training Grounds')
        character_name: str = read_choice(f'character to {Color.GREEN}* Begin adventure *{Color.END}', roster_names_list)
        character = [c for c in alive_characters if c.name == character_name][0]

        display_character_sheet_pyQT(character)
        display_character_sheet(character)

        if not continue_message():
            print(f'Bye {character.name}, see you in a next adventure :-)')
            exit(0)
        """ Combat simulation """
        welcome_message()
        attack_count: int = 0
        killed_monsters: int = 0
        previous_level: int = character.level

        # while character.hit_points > 0 and character.level < 5:
        while character.hit_points > 0 and attack_count < 100:
            # monsters_to_fight = [m for m in roster if m.challenge_rating < 1]
            # monsters_to_fight = [m for m in roster if 2 + character.level <= m.level <= 5 + character.level]
            monsters_to_fight = [m for m in monsters if m.level <= 5 + character.level]
            if character.level < len(xp_levels) and character.xp > xp_levels[character.level]:
                character.gain_level(pause=PAUSE_ON_RAISE_LEVEL)
            monster: Monster = copy(random.choice(monsters_to_fight))
            cprint(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
            cprint(f'{color.PURPLE} New encounter! {character} vs {monster}{color.END}')
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
                priority_dice = random.randint(0, 1)
                if priority_dice == 0:  # monster attacks first
                    character.hit_points -= monster_hp_damage
                    if character.hit_points <= 0:
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
                        break

        level_up_msg: str = f' and reached level #{character.level}' if previous_level > character.level else ''

        if character.hit_points <= 0:
            print(f'{character.name} has been killed by a {monster.name} after {attack_count} attack rounds and {killed_monsters} monsters kills{level_up_msg}')
        else:
            print(f'{character.name} has killed {killed_monsters} monsters{level_up_msg}')

        character.monster_kills += killed_monsters
        save_character(character)
        display_character_sheet(character)

        if not adventure_prompt_ok():
            break

    # print(f'Sauvegarde Roster')
    # for character in roster_list:
    #     with open(f'{characters_dir}/{character.name}.dmp', 'wb') as f1:
    #         pickle.dump(character, f1)
