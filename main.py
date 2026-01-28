from __future__ import annotations

import pickle
import sys
from copy import copy
from fractions import Fraction

from numpy import array

from collections import namedtuple, Counter
from random import seed, sample, shuffle, choice
from time import sleep, time

# ============================================
# PyQt5 imports (optional - only for GUI mode)
# ============================================
try:
    from PyQt5.QtWidgets import QApplication, QDialog
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    # Define dummy classes for console-only mode
    QApplication = None
    QDialog = None

# ============================================
# MIGRATION: Add dnd-5e-core to path (development mode)
# ============================================
import os

from game_entity import GameCharacter

_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_dnd_5e_core_path = os.path.join(_parent_dir, 'dnd-5e-core')
if os.path.exists(_dnd_5e_core_path) and _dnd_5e_core_path not in sys.path:
    sys.path.insert(0, _dnd_5e_core_path)

# ============================================
# MIGRATION: Import from dnd-5e-core package
# ============================================
from dnd_5e_core.entities import Character, Monster, Sprite
from dnd_5e_core.equipment import (
    Weapon, Armor, Equipment, Cost, EquipmentCategory, Inventory,
    HealingPotion, SpeedPotion, StrengthPotion, Potion, PotionRarity
)
from dnd_5e_core.spells import Spell, SpellCaster
from dnd_5e_core.combat import Action, ActionType, SpecialAbility, Damage, Condition, AreaOfEffect
from dnd_5e_core.races import Race, SubRace, Trait, Language
from dnd_5e_core.classes import ClassType, Proficiency, ProfType, Feature, Level, BackGround
from dnd_5e_core.abilities import Abilities, AbilityType
from dnd_5e_core.mechanics import DamageDice
from dnd_5e_core.equipment import WeaponProperty, WeaponRange, WeaponThrowRange, DamageType, CategoryType, RangeType
from dnd_5e_core.ui import cprint, Color, color
from dnd_5e_core.data import set_data_directory

# Set data directory to local data folder
_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
set_data_directory(_data_dir)

# Keep populate_functions for data loading
from populate_functions import *
from populate_rpg_functions import load_potion_image_name, load_potions_collections

# PyQt UI widgets (optional - only for GUI mode)
if PYQT5_AVAILABLE:
    try:
        from pyQTApp.qt_designer_widgets.character_dialog import Ui_character_Dialog
    except ImportError:
        Ui_character_Dialog = None
else:
    Ui_character_Dialog = None

from tools.ability_scores_roll import ability_rolls
from tools.common import exit_message, get_key, get_save_game_path

print("✅ [MIGRATION v2] main.py - Using dnd-5e-core package")
print()


def continue_message(message: str = "Do you want to continue? (Y/N)") -> bool:
    print(f"{color.DARKCYAN}{message}{color.END}")
    response = input()
    while response not in ["y", "n", "Y", "N"]:
        print(f"{color.DARKCYAN}{message}{color.END}")
        response = input()
    if response in ["y", "y"]:
        return True
    return False


def welcome_message_old():
    global PAUSE_ON_RAISE_LEVEL
    if PAUSE_ON_RAISE_LEVEL:
        print(f"{color.PURPLE}-----------------------------------------------------------{color.END}")
        print(f"{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}")
        print(f"{color.PURPLE}-----------------------------------------------------------{color.END}")
        print(f"{color.DARKCYAN}Do you want to pause output after new level? (Y/N){color.END}")
        response = input()
        while response not in ["y", "n", "Y", "N"]:
            print(f"{color.DARKCYAN} Do you want to pause output after new level? (Y/N){color.END}")
            response = input()
        PAUSE_ON_RAISE_LEVEL = True if response in ["y", "Y"] else False


def read_simple_text(input_message: str):
    text: str = None
    while not text:
        print(f"{input_message}: ")
        text = input()
    return text


def read_name(race: str, gender: str, names: dict(), reserved_names):
    """

    :param race: name of the race
    :param genre: name of the gender ['male', 'female', 'nickname', 'surname']
    :param names: dictionary of names
    :return:
    """
    if race in ["human", "half-elf"]:
        ethnic = read_choice(list(names.keys()), "Choose ethnic:")
        names_list = names[ethnic][gender]
        if len(names[ethnic]) > 2:
            other_key = [key for key in names[ethnic] if key not in ["male", "female"]][0]
            names_list += names[ethnic][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = read_choice(names, "Choose name:")
        return name, ethnic
    else:
        try:
            names_list = names[race][gender]
        except:
            print(names)
            exit(0)
        if len(names[race]) > 2:
            other_key = [key for key in names[race] if key not in ["male", "female"]][0]
            names_list += names[race][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = read_choice(names, "Choose name:")
        return name


def read_choice_tuple(choice_list: List, message: str = None) -> str:
    choice = None
    while choice not in range(1, len(choice_list) + 1):
        items_list = "\n".join([f'{i + 1}) {" ".join(map(str, item))}' for i, item in enumerate(choice_list)])
        items_list += "\n0) Exit"
        if message:
            print(message)
        print(f"{items_list}")
        err_msg = f"Bad value! Please enter a number between 1 and {len(choice_list)}"
        try:
            choice = int(input())
            if choice == 0:
                return "Exit"
            elif choice not in range(1, len(choice_list) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            sleep(2)
            efface_ecran()
            continue
    return choice_list[choice - 1][0]


def read_choice(choice_list: List[str], message: str = None) -> str:
    choice = None
    while choice not in range(1, len(choice_list) + 1):
        items_list = "\n".join([f"{i + 1}) {item}" for i, item in enumerate(choice_list)])
        if message:
            print(message)
        print(f"{items_list}")
        err_msg = f"Bad value! Please enter a number between 1 and {len(choice_list)}"
        try:
            choice = int(input())
            if choice not in range(1, len(choice_list) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            sleep(2)
            efface_ecran()
            continue
    return choice_list[choice - 1]


def read_choice_or_exit(choice_list: List[str], message: str = None) -> str:
    choice = None
    while choice not in range(1, len(choice_list) + 1):
        items_list = "\n".join([f"{i + 1}) {item}" for i, item in enumerate(choice_list)])
        items_list += "\n--------\n0) Exit"
        if message:
            print(message)
        print(f"{items_list}")
        err_msg = f"Bad value! Please enter a number between 1 and {len(choice_list)}"
        try:
            choice = int(input())
            if choice == 0:
                return "Exit"
            elif choice not in range(1, len(choice_list) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            sleep(2)
            efface_ecran()
            continue
    return choice_list[choice - 1]


def read_choice_or_escape_old(options: List[str], prompt: str) -> str:
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            if option.lower() != "esc":  # Don't show ESC in the menu
                print(f"{i}) {option}")

        key = get_key()
        if key == "escape":  # Handle Esc key
            return "Exit"
        try:
            choice = int(key)
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except ValueError:
            continue


def read_choice_or_escape(options: List[str], prompt: str) -> str:
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            if option.lower() != "esc":  # Don't show ESC in the menu
                print(f"{i}) {option}")

        buffer = ""
        while True:
            key = get_key()
            if key == "escape":  # Handle Esc key
                return "Exit"
            elif key == "return":  # Process the number when Enter is pressed
                if buffer:  # Only try to process if buffer is not empty
                    try:
                        choice = int(buffer)
                        if 1 <= choice <= len(options):
                            return options[choice - 1]
                    except ValueError:
                        pass
                break  # Break inner loop to show menu again
            elif key.isdigit():  # Add digits to buffer
                buffer += key
            elif key == "backspace" and buffer:  # Allow correction
                buffer = buffer[:-1]


def read_value(choice_list: List[int], message: str = None) -> int:
    choice = None
    while choice not in choice_list:
        if message:
            print(message)
        err_msg = f"Bad value! Please enter a number in {choice_list}"
        try:
            choice = int(input())
            if choice not in choice_list:
                raise ValueError
        except ValueError:
            print(err_msg)
            continue
    return choice


def read_char_choice(message: str, party: List[Character]) -> Character:
    choice = None
    while choice not in range(1, len(party) + 1):
        char_names: str = "\n".join([f"{i + 1}) {char.name}" for i, char in enumerate(party)])
        print(f"{message}:\n{char_names}")
        err_msg = f"Bad value! Please enter a number between 1 and {len(party)}"
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
                    label: str = ", ".join([f"{i.quantity} {i.equipment.index}" for i in inv])
                else:
                    # print(f'inv: {inv} - type: {type(inv)}')
                    label: str = inv.equipment.index
            except AttributeError:
                print(f"inv: {inv}")
                print(f"label: {label}")
                exit(0)
            inv_choices[label] = inv
        plural: str = "" if inv_count == 1 else "s"
        inv_choice: str = read_choice(list(inv_choices.keys()), f"Choose {inv_count} equipment{plural}:")
        chosen_inv: Inventory | List[Inventory] = inv_choices[inv_choice]
        if type(chosen_inv) is list:
            starting_equipment += [inv.equipment for inv in chosen_inv for _ in range(inv.quantity)]
        else:
            if isinstance(chosen_inv.equipment, EquipmentCategory):
                inv_options_cat: List[str] = populate(collection_name=chosen_inv.equipment.index, key_name="equipment", collection_path="data/equipment-categories", )
                plural: str = "" if inv_count == 1 else "s"
                inv_choice: str = read_choice(inv_options_cat, f"Choose {inv_count} {chosen_inv.equipment.name}{plural}:", )
                starting_equipment.append(request_equipment(inv_choice))
            else:
                starting_equipment.append(request_equipment(chosen_inv.equipment.index))  # print(f'removing chosen_inv: {chosen_inv}')  # inv_options.remove(chosen_inv)  # inv_count -= 1
    return starting_equipment


def get_height_and_weight(race, subrace):
    hw_conv_table = read_csvfile("Height and Weight-Height and Weight.csv")
    race_name = race.name if not subrace else subrace.name
    found_record = [x for x in hw_conv_table if x[0] == race_name]
    if not found_record:
        found_record = [x for x in hw_conv_table if x[0] == race.name]
    race_name, base_height, height_modifier, base_weight, weight_modifier = (found_record[0])
    feet2inch = lambda ft, inches: 12 * ft + inches
    inch2feet = lambda inches: f"{inches // 12}'{inches - (inches // 12) * 12}"
    height = feet2inch(*tuple((map(int, tuple(base_height.split("'"))))))
    roll_num, dice_num = map(int, height_modifier.split("d"))
    height_roll_result = sum([randint(1, dice_num) for _ in range(roll_num)])
    height += height_roll_result
    weight, unit = base_weight.split(" ")
    if "d" in weight_modifier:
        roll_num, dice_num = map(int, weight_modifier.split("d"))
        weight_roll_result = sum([randint(1, dice_num) for _ in range(roll_num)])
    else:
        weight_roll_result = 1
    weight = int(weight) + height_roll_result * weight_roll_result
    return inch2feet(height), f"{weight} {unit}"


def create_new_character_start(races: List[Race], subraces: List[SubRace], classes: List[ClassType], proficiencies: List[Proficiency], equipments: List[Equipment], names: dict(), human_names: dict(), roster: List[Character], ) -> tuple:
    """
        Character selection on 1st set of attributes
    :param races: list of available races
    :param subraces: list of available subraces
    :param classes: list of available classes
    :param proficiencies: list of available proficiencies
    :param equipments: list of available equipments
    :param names: list of available names (except humans)
    :param human_names: list of available human names
    :param reserved_names: list of names assigned to existing characters
    :return: tuple (race, subrace, class_type, abilities, ability_modifiers, name, gender, ethnic, height, weight, starting_equipment)
    """
    print(f"{color.PURPLE}-------------------------------------------------------{color.END}")
    print(f"{color.PURPLE} Character creation based on DnD 5th edition API{color.END}")
    print(f"{color.PURPLE}-------------------------------------------------------{color.END}")
    char_proficiencies: List[Proficiency] = []
    """ 1. Choose a race """
    races_names: List[str] = [r.index for r in races]
    race: str = read_choice(races_names, "Choose race:")
    race: Race = [r for r in races if r.index == race][0]
    subraces_names: List[str] = [s.index for s in subraces for r in races if r.index == race.index and r.index in s.index]
    subrace = None
    if subraces_names:
        subrace: str = read_choice(subraces_names, "Choose subrace")
        subrace: SubRace = [r for r in subraces if r.index == subrace][0]
    # Choose proficiencies within the race
    chosen_proficiencies: List[str] = []
    for starting_proficiency_option in race.starting_proficiency_options:
        choose, prof_list = starting_proficiency_option
        prof_count = min(choose, len(prof_list))  # Ensure we don't try to choose more than available
        prof_indexes: List[str] = [prof.index for prof in prof_list]
        while prof_count:
            prof_label = "proficiency" if prof_count == 1 else "proficiencies"
            prof_index: str = read_choice(prof_indexes, f"Choose {prof_count} race's {prof_label}:")
            chosen_proficiencies.append(prof_index)
            prof_indexes.remove(prof_index)
            prof_count -= 1
    for chosen_prof_index in chosen_proficiencies:
        chosen_prof: Proficiency = [prof for prof in proficiencies if prof.index == chosen_prof_index][0]
        char_proficiencies.append(chosen_prof)
    # should be deleted (duplicate with character.class_type.proficiencies)
    char_proficiencies += race.starting_proficiencies
    """ 2. Choose a class """
    class_indexes = [c.index for c in classes]
    class_index: str = read_choice(class_indexes, "Choose class:")
    class_type: ClassType = [c for c in classes if c.index == class_index][0]
    # Choose proficiencies within the class
    chosen_proficiencies: List[str] = []
    for proficiency_choice in class_type.proficiency_choices:
        choose, prof_list = proficiency_choice
        prof_count = min(choose, len(prof_list))  # Ensure we don't try to choose more than available
        prof_indexes: List[str] = [prof.index for prof in prof_list]
        while prof_count:
            prof_label = "proficiency" if prof_count == 1 else "proficiencies"
            prof_name: str = read_choice(prof_indexes, f"Choose {prof_count} class' {prof_label}:")
            chosen_proficiencies.append(prof_name)
            prof_indexes.remove(prof_name)
            prof_count -= 1
    for chosen_prof_index in chosen_proficiencies:
        chosen_prof: Proficiency = [prof for prof in proficiencies if prof.index == chosen_prof_index][0]
        char_proficiencies.append(chosen_prof)
    # should be deleted (duplicate with character.class_type.proficiencies)
    char_proficiencies += class_type.proficiencies

    """ 3. Determine ability scores (Strength, Dexterity, Constitution, Intelligence, Wisdom, and Charisma.)"""
    ability_scores: List[int] = ability_rolls()
    strength: int = read_choice(ability_scores, "Choose strength:")
    ability_scores.remove(strength)
    dexterity: int = read_choice(ability_scores, "Choose dexterity:")
    ability_scores.remove(dexterity)
    constitution: int = read_choice(ability_scores, "Choose constitution:")
    ability_scores.remove(constitution)
    intelligence: int = read_choice(ability_scores, "Choose intelligence:")
    ability_scores.remove(intelligence)
    wisdom: int = read_choice(ability_scores, "Choose wisdom:")
    ability_scores.remove(wisdom)
    charisma: int = read_choice(ability_scores, "Choose charisma:")
    abilities: Abilities = Abilities(strength, dexterity, constitution, intelligence, wisdom, charisma)
    mod = lambda x: (x - 10) // 2
    ability_modifiers: Abilities = Abilities(mod(strength), mod(dexterity), mod(constitution), mod(intelligence), mod(wisdom), mod(charisma), )

    """ 4. Describe your character (name, gender, clan/family/virtue/ethnic, height/weight, ...) """
    genders = ["male", "female"]
    gender: str = read_choice(genders, "Choose genre:")
    ethnic: str = None
    reserved_names: List[str] = [c.name for c in roster]
    if race.index in ["human", "half-elf"]:
        name, ethnic = read_name(race.index, gender, human_names, reserved_names)
    else:
        name = read_name(race.index, gender, names, reserved_names)
    height, weight = get_height_and_weight(race, subrace)

    """ 5. Choose equipment """
    # Choose starting equipment within the class
    starting_equipment: List[Equipment] = choose_equipment_from(class_type.starting_equipment_options)
    starting_equipment += [inv.equipment for inv in class_type.starting_equipment for _ in range(inv.quantity)]
    return (race, subrace, class_type, char_proficiencies, abilities, ability_modifiers, name, gender, ethnic, height, weight, starting_equipment,)


def load_character_collections() -> Tuple:
    """Character creation database"""
    races_names: List[str] = populate(collection_name="races", key_name="results")
    races: List[Race] = [request_race(name) for name in races_names]
    subraces_names: List[str] = populate(collection_name="subraces", key_name="results")
    subraces: List[Race] = [request_subrace(name) for name in subraces_names]
    names = dict()
    for race in races:
        if race.index not in ["human", "half-elf"]:
            names[race.index] = populate_names(race)
    human_names: dict() = populate_human_names()
    classes: List[str] = populate(collection_name="classes", key_name="results")
    classes = [request_class(name) for name in classes]
    alignments: List[str] = populate(collection_name="alignments", key_name="results")
    equipment_names: List[str] = populate(collection_name="equipment", key_name="results")
    equipments = [request_equipment(name) for name in equipment_names]
    proficiencies_names: List[str] = populate(collection_name="proficiencies", key_name="results")
    proficiencies = [request_proficiency(name) for name in proficiencies_names]
    spell_names: List[str] = populate(collection_name="spells", key_name="results")
    spells: List[Spell] = [request_spell(name) for name in spell_names]
    spells = [s for s in spells if s is not None]
    return (races, subraces, classes, alignments, equipments, proficiencies, names, human_names, spells,)


def load_dungeon_collections() -> Tuple:
    """Monster, Armor and Weapon databases"""
    monster_names: List[str] = populate(collection_name="monsters", key_name="results")
    monsters: List[Monster] = [request_monster(name) for name in monster_names]
    armor_names: List[str] = populate(collection_name="armors", key_name="equipment")
    armors: List[Armor] = [request_armor(name) for name in armor_names]
    weapon_names: List[str] = populate(collection_name="weapons", key_name="equipment")
    weapons: List[Weapon] = [request_weapon(name) for name in weapon_names]
    equipment_names: List[str] = populate(collection_name="equipment", key_name="results")
    equipments: List[Equipment] = [request_equipment(name) for name in equipment_names]
    equipment_category_names: List[str] = populate(collection_name="equipment-categories", key_name="results")
    equipment_categories: List[EquipmentCategory] = [request_equipment_category(name) for name in equipment_category_names]
    healing_potions: List[HealingPotion] = load_potions_collections()
    return monsters, armors, weapons, equipments, equipment_categories, healing_potions


def get_next_item_id(roster: List[Character]) -> int:
    """
    DEPRECATED: Items no longer have id in main.py (console version).
    IDs are only used in GameEntity for pygame games.
    Keeping this function for backward compatibility but it's not used anymore.
    """
    # return max([item.id for c in roster for item in c.inventory if item]) + 1 if roster else MAX_ROSTER + 1
    return MAX_ROSTER + 1  # Just return a default value


def get_spell_caster(class_type, char_level, spells) -> Optional[SpellCaster]:
    learned_spells: List[Spell] = []
    if class_type.can_cast:
        learnable_spells: List[Spell] = [s for s in spells if class_type.index in s.allowed_classes and s.level <= char_level and (s.damage_type or s.heal_at_slot_level)]
        if learnable_spells:
            cantrips_spells: List[Spell] = []
            if class_type.cantrips_known:
                cantrips_spells = [s for s in learnable_spells if not s.level]
                # Safely get cantrips_known value with bounds checking
                if char_level > 0 and char_level <= len(class_type.cantrips_known):
                    n_cantric_spells: int = min(len(cantrips_spells), class_type.cantrips_known[char_level - 1])
                else:
                    # Use last available value or a default
                    n_cantric_spells: int = min(len(cantrips_spells), class_type.cantrips_known[-1] if class_type.cantrips_known else 0)
                if n_cantric_spells > 0:
                    cantrips_spells = sample(cantrips_spells, n_cantric_spells)

            slot_spells: List[Spell] = [s for s in learnable_spells if s.level]
            # Safely get spells_known value with bounds checking
            if class_type.spells_known and char_level > 0 and char_level <= len(class_type.spells_known):
                n_slot_spells: int = min(len(slot_spells), class_type.spells_known[char_level - 1])
            elif class_type.spells_known:
                # Use last available value or default
                n_slot_spells: int = min(len(slot_spells), class_type.spells_known[-1] if class_type.spells_known else len(slot_spells))
            else:
                # For classes without spells_known (like Wizard), use all available slot spells
                n_slot_spells: int = len(slot_spells)

            if n_slot_spells > 0:
                slot_spells = sample(slot_spells, n_slot_spells)
            learned_spells = cantrips_spells + slot_spells

        # Get spell slots for this level, with fallback to empty list
        spell_slots_for_level = class_type.spell_slots.get(char_level) if class_type.spell_slots else None
        if spell_slots_for_level is None:
            # Fallback: try to get the highest level available
            if class_type.spell_slots:
                max_level = max(class_type.spell_slots.keys())
                spell_slots_for_level = class_type.spell_slots.get(max_level, [0, 0, 0, 0, 0, 0, 0, 0, 0])
            else:
                # Default empty spell slots
                spell_slots_for_level = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        return SpellCaster(
            level=char_level,
            spell_slots=copy(spell_slots_for_level),
            learned_spells=learned_spells,
            dc_type=class_type.spellcasting_ability,
            dc_value=None,
            ability_modifier=None,
        )


def get_char_image(class_type) -> str:
    sprites: dict = {
        "barbarian": "barbarian",
        "bard": "cleric",
        "cleric": "cleric",
        "druid": "cleric",
        "fighter": "knight",
        "monk": "monk",
        "paladin": "knight",
        "ranger": "ranger",
        "rogue": "rogue",
        "sorcerer": "necromant",
        "warlock": "necromant",
        "wizard": "wizzard",
    }
    return f"hero_{sprites[class_type.name.lower()]}.png"


def generate_random_proficiencies(race, class_type) -> List[str]:
    # Choose proficiencies within the race
    chosen_proficiencies: List[str] = []

    for starting_proficiency_option in race.starting_proficiency_options:
        choose, prof_list = starting_proficiency_option
        prof_count = min(choose, len(prof_list))  # Ensure we don't try to choose more than available

        # Randomly select proficiencies
        chosen_profs = sample(prof_list, prof_count)
        chosen_proficiencies.extend(chosen_profs)

    # Choose proficiencies within the class
    for proficiency_choice in class_type.proficiency_choices:
        choose, prof_list = proficiency_choice
        prof_count = min(choose, len(prof_list))  # Ensure we don't try to choose more than available

        # Randomly select proficiencies
        chosen_profs = sample(prof_list, prof_count)
        chosen_proficiencies.extend(chosen_profs)

    return chosen_proficiencies


def generate_random_name(race: str, gender: str, names: dict(), reserved_names):
    """

    :param race: name of the race
    :param genre: name of the gender ['male', 'female', 'nickname', 'surname']
    :param names: dictionary of names
    :return:
    """
    if race in ["human", "half-elf"]:
        ethnic = choice(list(names.keys()))
        names_list = names[ethnic][gender]
        if len(names[ethnic]) > 2:
            other_key = [key for key in names[ethnic] if key not in ["male", "female"]][0]
            names_list += names[ethnic][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = choice(names)
        return name, ethnic
    else:
        names_list = names[race][gender]
        if len(names[race]) > 2:
            other_key = [key for key in names[race] if key not in ["male", "female"]][0]
            names_list += names[race][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = choice(names)
        return name


def generate_random_character(roster: List[Character], races: List[Race], subraces: List[SubRace], classes: List[ClassType], names: dict[str, List[str]], human_names, spells: list[Spell]) -> Character:
    """
    Generate a preset character with random selections.

    :param races: List of available races
    :param classes: List of available classes
    :param names: Dictionary of names by race
    :return: A new Character instance with randomly selected attributes
    """

    # Phase 1: character selection

    char_proficiencies: List[Proficiency] = []
    """ 1. Choose a race """
    # Select random race
    race = choice(races)
    # Select optional subrace
    subraces_names: List[str] = [s.index for s in subraces for r in races if r.index == race.index and r.index in s.index]
    subrace: Optional[SubRace] = [r for r in subraces if r.index == choice(subraces_names)][0] if subraces_names else None
    char_proficiencies = race.starting_proficiencies

    """ 2. Choose a class """
    # Select random class
    class_type = choice(classes)
    char_proficiencies += class_type.proficiencies

    char_proficiencies += generate_random_proficiencies(race, class_type)

    char_proficiencies = [request_proficiency(prof_index) for prof_index in set([p.index for p in char_proficiencies])]

    """ 3. Determine ability scores (Strength, Dexterity, Constitution, Intelligence, Wisdom, and Charisma.)"""
    strength, dexterity, constitution, intelligence, wisdom, charisma = ability_rolls()
    abilities: Abilities = Abilities(strength, dexterity, constitution, intelligence, wisdom, charisma)
    mod = lambda x: (x - 10) // 2
    ability_modifiers: Abilities = Abilities(mod(strength), mod(dexterity), mod(constitution), mod(intelligence), mod(wisdom), mod(charisma))

    """ 4. Describe your character (name, gender, clan/family/virtue/ethnic, height/weight, ...) """
    # Generate random gender
    gender = choice(["male", "female"])

    ethnic: str = None
    reserved_names: List[str] = [c.name for c in roster]
    if race.index in ['human', 'half-elf']:
        name, ethnic = generate_random_name(race.index, gender, human_names, reserved_names)
    else:
        name = generate_random_name(race.index, gender, names, reserved_names)

    height, weight = get_height_and_weight(race, subrace)

    hit_points = class_type.hit_die + ability_modifiers.con

    # Phase 2: Spell selection
    char_level: int = 1  # could be changed to create higher level characters
    spell_caster: Optional[SpellCaster] = get_spell_caster(class_type, char_level, spells)

    # Note: Character no longer has id, x, y, old_x, old_y, image_name
    # These are now part of GameEntity for pygame games only
    return Character(
        race=race,
        subrace=subrace,
        class_type=class_type,
        proficiencies=char_proficiencies,
        abilities=abilities,
        ability_modifiers=ability_modifiers,
        gender=gender,
        name=name,
        ethnic=ethnic,
        height=height,
        weight=weight,
        inventory=[None] * 20,
        hit_points=hit_points,
        max_hit_points=hit_points,
        xp=0,
        level=1,
        age=18 * 52 + randint(0, 299),
        gold=90 + randint(0, 99),
        sc=spell_caster,
        conditions=[],
        speed=30,
        haste_timer=0,
        hasted=False,
        st_advantages=[]
    )


def create_new_character(roster: List[Character]) -> Character:
    """
        Character creation's procedure (split in 2 functions, calls create_character)
    :param roster: list of existing characters (needed for name selection as name is the character file's identifier)
    :return: Character object
    """
    # Phase 1: character selection
    # TODO: do not load spell data collections if class_type cannot perform spell casting
    (races, subraces, classes, alignments, equipments, proficiencies, names, human_names, spells,) = load_character_collections()
    prof_types: set() = set([p.type for p in proficiencies])
    # reserved_names: List[str] = [c.name for c in roster]
    (race, subrace, class_type, char_proficiencies, abilities, ability_modifiers, name, gender, ethnic, height, weight, starting_equipment,) = create_new_character_start(races=races, subraces=subraces, classes=classes, equipments=equipments, proficiencies=proficiencies, names=names, human_names=human_names, roster=roster, )
    # Equip the character with a weapon and an armor from the starting equipment list of the class
    available_weapons = {e.index: e for e in starting_equipment if e.category.index == "weapon"}
    available_armors = {e.index: e for e in starting_equipment if e.category.index == "armor"}
    chosen_weapon: str = read_choice(list(available_weapons.keys()), f"Choose 1 weapon to equip:")
    chosen_weapon: Weapon = request_weapon(available_weapons[chosen_weapon].index)
    chosen_weapon.equipped = True
    if not available_armors:
        available_armors = {"skin-armor": request_armor("skin-armor")}
    chosen_armor: str = read_choice(list(available_armors.keys()), f"Choose 1 armor to equip")
    chosen_armor: Armor = request_armor(available_armors[chosen_armor].index)
    chosen_armor.equipped = True
    hit_points = class_type.hit_die + ability_modifiers.con
    # Add a set of healing potions to the starting equipment
    starting_equipment += [copy(choice(potions)) for _ in range(POTION_INITIAL_PACK)]
    # Note: Items no longer need id assignment - that's only for GameEntity in pygame
    # for item in starting_equipment:
    #     item.id = max_item_id
    #     max_item_id += 1

    # Phase 2: Spell selection
    char_level: int = 1  # could be changed to create higher level characters
    spell_caster: Optional[SpellCaster] = get_spell_caster(class_type, char_level, spells)

    # Note: Character no longer has id, x, y, old_x, old_y, image_name
    # These are now part of GameEntity for pygame games only
    character: Character = Character(
        race=race,
        subrace=subrace,
        class_type=class_type,
        proficiencies=char_proficiencies,
        abilities=abilities,
        ability_modifiers=ability_modifiers,
        gender=gender,
        name=name,
        ethnic=ethnic,
        height=height,
        weight=weight,
        inventory=starting_equipment + [None] * (20 - len(starting_equipment)),
        hit_points=hit_points,
        max_hit_points=hit_points,
        xp=0,
        level=1,
        age=18 * 52 + randint(0, 299),
        gold=90 + randint(0, 99),
        sc=spell_caster,
        conditions=[],
        speed=30,
        haste_timer=0,
        hasted=False,
        st_advantages=[]
    )
    exit_message()
    return character


def save_char_to_party(char_to_party: List[Char2Party], _dir: str):
    with open(f"{_dir}/char_party_mappings.dmp", "wb") as f1:
        pickle.dump(char_to_party, f1)


def load_char_to_party(_dir: str) -> List[Char2Party]:
    try:
        with open(f"{_dir}/char_party_mappings.dmp", "rb") as f1:
            return pickle.load(f1)
    except FileNotFoundError:
        return []

def load_party(_dir: str) -> List[Character]:
    try:
        with open(f"{_dir}/party.dmp", "rb") as f1:
            return pickle.load(f1)
    except FileNotFoundError:
        return []

def save_party(party: List[Character], _dir: str):
    with open(f"{_dir}/party.dmp", "wb") as f1:
        pickle.dump(party, f1)


def save_character(char: Character, _dir: str):
    # print(f'Sauvegarde personnage {char.name}')
    with open(f"{_dir}/{char.name}.dmp", "wb") as f1:
        pickle.dump(char, f1)


def load_character(char_name: str, _dir: str) -> Character:
    with open(f"{_dir}/{char_name}.dmp", "rb") as f1:
        return pickle.load(f1)


def get_roster(characters_dir: str) -> List[Character]:
    roster: List[Character] = []
    char_file_list = os.scandir(characters_dir)
    for entry in char_file_list:
        if entry.is_file() and entry.name.endswith(".dmp"):
            with open(entry, "rb") as f1:
                # print(f1)
                # print(entry)
                roster.append(pickle.load(f1))
    return roster


def display_adventurers(roster: List[Character], party: List[Character], location: str):
    toc: str = "{:-^53}\n".format(f" {location} ")
    if party:
        toc += "{:-^53}\n".format(f" ** NOT AVAILABLE (in dungeon) ** ")
    for char in roster:
        if char.in_dungeon:
            char_status: str = f" ({char.status})" if char.status != "OK" else ""
            toc += "|{:^51}|\n".format(f"{char.name}{char_status} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})")
    toc += "{:-^53}\n".format(f" ** AVAILABLE ** ")
    for char in roster:
        if not char.in_dungeon:
            char_status: str = f" ({char.status})" if char.status != "OK" else ""
            toc += "|{:^51}|\n".format(f"{char.name}{char_status} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})")
    toc += "|{:-^51}|\n".format("")
    print(toc)


def adventure_prompt_ok() -> bool:
    return input(f"{color.DARKCYAN}Do you want to continue adventure? (Y/N){color.END}").lower() == 'y'


def location_prompt_ok(location: str) -> bool:
    return input(f"{color.DARKCYAN}Do you want to go to {location}? (Y/N){color.END}").lower() == 'y'


def handle_equipment(char, items, item_type, display_info):
    if not items:
        print(f"\nNo {item_type}s available in inventory!")
        return

    print(f"\nAvailable {item_type}s:")
    for i, item in enumerate(items, 1):
        prof_items = char.prof_weapons if isinstance(item, Weapon) else char.prof_armors
        prof_label = f'{Color.RED} ** NOT PROFICIENT **{Color.END}' if not any(x.index == item.index for x in prof_items) else ''
        status = f"{Color.GREEN}equipped{Color.END}{prof_label}" if item.equipped else f"unequipped{prof_label}"
        print(f"{i}. {item.name.title()} ({display_info(item)}) - {status}")

    try:
        choice = int(input(f"\nChoose {item_type} to equip/unequip (0 to cancel): "))
        if 0 < choice <= len(items):
            selected = items[choice - 1]
            messages, success = char.equip(selected, verbose=False)
            if success:
                print(f"\n{'Equipped' if selected.equipped else 'Unequipped'} {selected.name}")
            else:
                print(f"\n{messages}")
            sleep(4)
    except ValueError:
        print("\nInvalid input!")

def select_equipment_in_inventory(char: Character, action: str = 'trade') -> Optional[Equipment]:
    items = list(filter(None, char.inventory))
    if not items:
        print("\nNo equipment available in inventory!")
        return None

    print("\nAvailable equipment:")
    items = list(items)  # Convert filter object to list
    for i, item in enumerate(items, 1):
        prof_items = char.prof_weapons if isinstance(item, Weapon) else char.prof_armors if isinstance(item, Weapon) else None
        prof = f'{Color.RED} ** NOT PROFICIENT **{Color.END}' if prof_items and not any(x.index == item.index for x in prof_items) else ''
        if isinstance(item, (Weapon, Armor)):
            print(f"{i}. {item.name.title()} - {Color.GREEN if item.equipped else ''}{'equipped' if item.equipped else 'unequipped'}{Color.END}{prof}")
        else:
            print(f"{i}. {item.name.title()} ({type(item).__name__})")

    try:
        if (choice := int(input(f"\nChoose equipment to {action} (0 to cancel): "))) in range(1, len(items) + 1):
            selected = items[choice - 1]
            if selected.equipped:
                print(f"\nInvalid action! Please un-equip {selected} first")
                sleep(2)
                return None
            return selected
    except ValueError:
        print("\nInvalid input!")
        sleep(4)


def trade_equipment(char: Character, party: List[Character], equipment: Equipment) -> bool:
    print("\nAvailable party members:")
    other_party_members = [c for c in party if c != char]
    for i, member in enumerate(other_party_members, 1):
        print(f"{i}. {member.name}")
    try:
        if (choice := int(input("\nChoose party member to trade with (0 to cancel): "))) in range(1, len(other_party_members) + 1):
            selected = other_party_members[choice - 1]
            if selected.is_full:
                cprint(f"{selected.name}'s inventory is full - no trade!!!")
                return False
            free_slot: int = [i for i, item in enumerate(char.inventory) if item is None][0]
            selected.inventory[free_slot] = equipment
            char.inventory[char.inventory.index(equipment)] = None
            print(f"\n{equipment.name} traded with {selected.name}!")
            sleep(4)
    except ValueError:
        print("\nInvalid input!")

def drop_equipment(char: Character, equipment: Equipment) -> bool:
    char.inventory[char.inventory.index(equipment)] = None
    print(f"\n{equipment.name} dropped!")
    sleep(4)


def view_equipment(char):
    print("\nAvailable equipment:")
    items = list(filter(None, char.inventory))
    for i, item in enumerate(items, 1):
        prof_items = char.prof_weapons if isinstance(item, Weapon) else char.prof_armors if isinstance(item, Weapon) else None
        prof = f'{Color.RED} ** NOT PROFICIENT **{Color.END}' if prof_items and not any(x.index == item.index for x in prof_items) else ''
        if isinstance(item, (Weapon, Armor)):
            print(f"{i}. {item.name.title()} - {Color.GREEN if item.equipped else ''}{'equipped' if item.equipped else 'unequipped'}{Color.END}{prof}")
        else:
            print(f"{i}. {item.name.title()} ({type(item).__name__})")
    exit_message()


def menu_read_options(char: Character, party: List[Character]):
    while True:
        efface_ecran()
        display_character_sheet(char)
        # Menu
        options_menu = ["View Inventory", "Equip/Unequip Armor", "Equip/Unequip Weapon", "Trade Equipment", "Drop Equipment", "Monster kills", "Return"]
        print("\nOptions:", *[f"\n{i}. {opt}" for i, opt in enumerate(options_menu, 1)])

        choice = input("\nEnter your choice (1-7): ")

        if choice == '1':
            view_equipment(char)
        elif choice == '2':
            items = [item for item in char.inventory if isinstance(item, Armor)]
            handle_equipment(char, items, "armor", lambda x: f"AC: {x.armor_class}")
        elif choice == '3':
            items = [item for item in char.inventory if isinstance(item, Weapon)]
            handle_equipment(char, items, "weapon", lambda x: f"Damage: {x.damage_dice.dice}")
        elif choice == '4':
            selected = select_equipment_in_inventory(char, 'trade')
            if not selected:
                continue
            trade_equipment(char, party, selected)
        elif choice == '5':
            selected = select_equipment_in_inventory(char, 'drop')
            if not selected:
                continue
            drop_equipment(char, selected)
        elif choice == '6':
            print(f"\nMonster kills: {len(char.kills)}")
            if hasattr(char, "kills"):
                monsters_count = Counter([m.name for m in char.kills])
                # cprint(f"{len(monsters_count)} different types of monsters killed by {char.name} for a total of {len(char.kills)} kills")
                monsters = {m.name: (m.challenge_rating, monsters_count[m.name]) for m in char.kills}
                monsters = {m.name: (m.challenge_rating, monsters_count[m.name]) for m in char.kills}
                monsters = dict(sorted(monsters.items(), key=lambda x: x[1], reverse=True))
                for k, (cr, count) in monsters.items():
                    print(f"{count} {k} (cr {cr})")
            exit_message()
        elif choice == '7':
            break
        else:
            print("\nInvalid choice!")

def display_character_sheet(char: Character):
    efface_ecran()
    # print(char.id)
    # Attributes section
    sheet = "+{:-^51}+\n".format(f" {char.name} (age: {char.age // 52} - {char.status})")
    sheet += f"| str: {str(char.strength).rjust(2)} | int: {str(char.strength).rjust(2)} | hp: {str(char.hit_points).rjust(3)} / {str(char.max_hit_points).ljust(4)}| {str(char.class_type).upper().ljust(14)}|\n"
    sheet += f"| dex: {str(char.dexterity).rjust(2)} | wis: {str(char.wisdom).rjust(2)} | xp: {str(char.xp).ljust(10)}| {str(char.race).title().ljust(14)}|\n"
    sheet += f"| con: {str(char.constitution).rjust(2)} | cha: {str(char.charism).rjust(2)} | level: {str(char.level).ljust(7)}| AC: {str(char.armor_class).ljust(10)}|\n"
    sheet += "+{:-^51}+\n".format("")
    sheet += "|{:^51}|\n".format(f"kills = {len(char.kills)}")

    # Potions section
    rarity_types: dict() = {PotionRarity.COMMON: "C", PotionRarity.UNCOMMON: "U", PotionRarity.RARE: "R", PotionRarity.VERY_RARE: "VR", }
    potions: dict() = {"C": 0, "U": 0, "R": 0, "VR": 0}
    healing_potions: List[HealingPotion] = [item for item in char.inventory if isinstance(item, HealingPotion)]
    for p in healing_potions:
        rarity: str = rarity_types[p.rarity]
        potions[rarity] += 1
    potions = dict(filter(lambda p: p[1] > 0, potions.items()))
    sheet += "|{:^51}|\n".format(f"healing potions = {potions}") if potions else ""

    strength_potions: List[StrengthPotion] = [item for item in char.inventory if isinstance(item, StrengthPotion)]
    sheet += ("|{:^51}|\n".format(f"strength potions = {len(strength_potions)}") if strength_potions else "")

    speed_potions: List[SpeedPotion] = [item for item in char.inventory if isinstance(item, SpeedPotion)]
    sheet += ("|{:^51}|\n".format(f"speed potions = {len(speed_potions)}") if speed_potions else "")

    # Equipment section
    char_armors: List[Armor] = [item for item in char.inventory if isinstance(item, Armor) and item.equipped]
    char_weapons: List[Weapon] = [item for item in char.inventory if isinstance(item, Weapon) and item.equipped]
    armors_list: str = " + ".join([a.name.title() for a in char_armors]) if char_armors else "None"
    sheet += "|{:^51}|\n".format(f"armors in use = {armors_list}")
    # sheet += "|{:^51}|\n".format(f"shield in use = {char.used_shield}")
    if char_weapons:
        for weapon in char_weapons:
            prof_label = '*' if not any(weapon.index == w.index for w in char.prof_weapons) else ''
            sheet += "|{:^51}|\n".format(f"weapon in use = {weapon.name.title()}{prof_label} - Damage = {weapon.damage_dice.dice}")
    else:
        sheet += "|{:^51}|\n".format(f"weapon in use = None")

    sheet += "|{:^51}|\n".format(f"gold = {char.gold} gp")
    sheet += "+{:-^51}+\n".format("")

    # Spells section
    if char.is_spell_caster:
        slots: str = "/".join(map(str, char.sc.spell_slots))
        sheet += "|{:^51}|\n".format(f"spell slots: {slots}")
        known_spells: int = len(char.sc.learned_spells)
        sheet += "|{:^51}|\n".format(f"{known_spells} known spells:")
        learned_spells: List[Spell] = [s for s in char.sc.learned_spells]
        learned_spells.sort(key=lambda s: s.level)
        for spell in learned_spells:
            sheet += "|{:^51}|\n".format(str(spell))
        sheet += "+{:-^51}+\n".format("")

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
    """Select Character"""
    character_name: str = read_choice([c.name for c in roster],f"Choose a character to {Color.GREEN}* Begin adventure *{Color.END}")
    character = [c for c in roster if c.name == character_name][0]
    return character


def arena(character: Character):
    """Combat simulation"""
    print(f"{color.PURPLE}-----------------------------------------------------------{color.END}")
    print(f"{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}")
    print(f"{color.PURPLE}-----------------------------------------------------------{color.END}")
    attack_count: int = 0
    killed_monsters: int = 0
    previous_level: int = character.level

    difficulty: List[str] = ["HARD", "MEDIUM", "EASY", "KIDDIE"]
    arena_level: str = read_choice(difficulty, "Select difficulty:")

    match arena_level:
        case "HARD":
            # monsters_to_fight = [m for m in monsters if m.level > character.level]
            monsters_to_fight = [m for m in monsters if m.challenge_rating > character.level]
        case "MEDIUM":
            # monsters_to_fight = [m for m in monsters if m.level < character.level + 5]
            monsters_to_fight = [m for m in monsters if m.challenge_rating == character.level]
        case "EASY":
            monsters_to_fight = [m for m in monsters if m.challenge_rating < character.level]
        case "KIDDIE":
            monsters_to_fight = [m for m in monsters if m.level < character.level + 5]

    # while character.hit_points > 0 and character.level < 5:
    while character.hit_points > 0 and attack_count < 500:
        # if character.level < len(xp_levels) and character.xp > xp_levels[character.level]:
        #     character.gain_level(pause=PAUSE_ON_RAISE_LEVEL)
        monster: Monster = copy(choice(monsters_to_fight))
        cprint(f"{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}")
        cprint(f"{color.PURPLE} New encounter! {character} vs {monster}{color.END}")
        cprint(f"{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}")
        round_num = 0
        monster_max_hp = monster.hit_points
        while monster.hit_points > 0:
            round_num += 1
            cprint("-------------------------------------------------------")
            cprint(f"Round {round_num}: {character.name} ({character.hit_points}/{character.max_hit_points}) vs {monster.name} ({monster.hit_points}/{monster_max_hp})")
            cprint("-------------------------------------------------------")
            if character.hit_points < 0.5 * character.max_hit_points and character.healing_potions:
                cprint(f"{len(character.healing_potions)} remaining potions")
                potion = character.choose_best_potion()
                drink_msg, success, hp_restored = character.drink(potion, verbose=False)
                print(drink_msg)
                # Remove potion from inventory
                p_idx = next(i for i, item in enumerate(character.inventory) if item is not None and item == potion)
                character.inventory[p_idx] = None
            attack_count += 1
            monster_attack_msg, monster_hp_damage, damage_type = monster.attack(character)
            print(monster_attack_msg)
            character_attack_msg, character_hp_damage = character.attack(monster, in_melee=True, verbose=False)
            print(character_attack_msg)
            priority_dice = randint(0, 1)
            if priority_dice == 0:  # monster attacks first
                actual_damage = character.take_damage(monster_hp_damage, damage_type)
                if character.hit_points <= 0:
                    character.status = "DEAD"
                    break
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    victory_msg, xp, gold = character.victory(monster, solo_mode=True, verbose=False)
                    print(victory_msg)
                    character.kills.append(monster)
                    treasure_msg, item = character.treasure(weapons, armors, equipment_categories, [], verbose=False)
                    print(treasure_msg)
                    break
            else:  # character attacks first
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    victory_msg, xp, gold = character.victory(monster, solo_mode=True, verbose=False)
                    print(victory_msg)
                    killed_monsters += 1
                    treasure_msg, item = character.treasure(weapons, armors, equipment_categories, [], verbose=False)
                    print(treasure_msg)
                    break
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    character.status = "DEAD"
                    break

    level_up_msg: str = (f" and reached level #{character.level}" if previous_level > character.level else "")

    if character.hit_points <= 0:
        print(f"{character.name} has been killed by a {monster.name} after {attack_count} attack rounds and {len(character.kills)} monsters kills{level_up_msg}")
    else:
        print(f"{character.name} has killed {len(character.kills)} monsters{level_up_msg}")

    character.kills.append(monster)
    save_character(character, _dir=characters_dir)
    display_character_sheet(character)


def display(party: List[Character]) -> str:
    FormatTable = namedtuple("CharacterTable", ["name", "level", "class_type", "AC", "hits", "status", "age", "kills", "max_cr"])
    max_cr = 15
    if party: max_cr = max(max((len(str(m)) for m in char.kills), default=max_cr) for char in party if hasattr(char, "kills"))
    ft: FormatTable = FormatTable(name=15, level=3, class_type=10, AC=3, hits=8, status=8, age=3, kills=5, max_cr=max_cr)
    n_cols: int = sum(ft) + 3 * len(ft) - 1
    formatter: str = "+{:-^" + str(n_cols) + "}+\n"
    sheet = formatter.format(f" Party")
    sheet += f"| {str('Name').ljust(ft.name)} | {str('LVL').center(ft.level)} | {str('Class').center(ft.class_type)} | {str('AC').center(ft.AC)} | {str('Hits').center(ft.hits)} | {str('Status').center(ft.status)} | {str('Age').center(ft.age)} | {str('Kills').center(ft.kills)} | {str('Highest monster').center(ft.max_cr)} |\n"
    if party:
        sheet += formatter.format("")
    dead_chars: List[Character] = [c for c in party if c.status == "DEAD"]
    alive_chars: List[Character] = [c for c in party if c.status != "DEAD"]
    for char in alive_chars:
        m: Optional[Monster] = max(char.kills, key=lambda m: m.challenge_rating, default=None) if hasattr(char, "kills") else None
        #monster_killed: str = f'{m.name.title()} (cr {m.challenge_rating})' if m else ''
        monster_killed = str(m)
        sheet += f"| {str(char.name).ljust(ft.name)} | {str(char.level).center(ft.level)} | {str(char.class_type).title().center(ft.class_type)} | {str(char.armor_class).center(ft.AC)} | {f'{char.hit_points}/{char.max_hit_points}'.center(ft.hits)} | {str(char.status).center(ft.status)} | {str(char.age // 52).center(ft.age)} | {str(len(char.kills)).center(ft.kills)} | {monster_killed.center(ft.max_cr)} |\n"
    for char in dead_chars:
        m: Optional[Monster] = max(char.kills, key=lambda m: m.challenge_rating, default=None) if hasattr(char, "kills") else None
        monster_killed: str = f'{m.name.title()} (cr {m.challenge_rating})' if m else ''
        sheet += f"| {str(char.name).ljust(ft.name)} | {str(char.level).center(ft.level)} | {str(char.class_type).title().center(ft.class_type)} | {str(char.armor_class).center(ft.AC)} | {f'{char.hit_points}/{char.max_hit_points}'.center(ft.hits)} | {str(char.status).center(ft.status)} | {str(char.age // 52).center(ft.age)} | {str(len(char.kills)).center(ft.kills)} | {monster_killed.center(ft.max_cr)} |\n"
    sheet += formatter.format("")
    return sheet

def add_member_to_party(roster: List[Character], party: List[Character]):
    if len(party) == 6:
        print(f"Party is **FULL**")
        sleep(1)
        return
    if not roster:
        print(f"No more character in roster! Go to [Training Grounds] to create one.")
        sleep(2)
        return
    roster = sorted(roster, key=lambda c: c.level)
    # char_names: List[tuple] = [(c.name, c.class_type, f'Lvl {c.level}') for c in roster if c.status == 'OK' and c not in party and not c.in_dungeon]
    char_names: List[tuple] = [(c.name, c.class_type, f"Lvl {c.level}") for c in roster if c.status == "OK" and c not in party]
    if not char_names:
        print(f"No available character to join party!")
        sleep(2)
        return
    name: str = read_choice_tuple(char_names, "Select character to add in party")
    if name == "Exit":
        return
    char: Character = get_character(name, roster)
    if char:
        party.append(char)
        char.id_party = len(party) - 1
        save_character(char, _dir=characters_dir)
    else:
        print(f"Program error! {name} unknown in Castle - Please contact the administrator...")
        sleep(1)


def delete_member_from_party(roster: List[Character], party: List[Character]):
    if not party:
        print(f"no member in **PARTY**")
        sleep(1)
        return
    char_names: List[str] = [c.name for c in party]
    char_name: str = read_choice_or_exit(char_names, "Select character to remove from party")
    if char_name == "Exit":
        return
    char: Character = get_character(char_name, party)
    if char:
        party.remove(char)
        char.id_party = -1
        save_character(char, _dir=characters_dir)
    else:
        print(f"Program error! {char_name} not in the party - Please contact the administrator...")
        sleep(1)


def read_bool(param):
    while (value := input(param).lower()) not in {'y', 'n'}:
        print("Invalid input. Please enter 'y' or 'n'.")
    return value == 'y'



def gilgamesh_tavern(party: List[Character], roster: List[Character]):
    exit_tavern: bool = False
    while not exit_tavern:
        efface_ecran()
        message = "+-----------------------------+\n"
        message += "|  ** GILGAMESH'S TAVERN **   |\n"
        message += "+-----------------------------+\n"
        message += display(party)
        gt_options: List[str] = [
            "Add Member",
            "Remove Member",
            "Character Status",
            # "Character Equip",
            "Reorder",
            "Divvy Gold",
            "Disband Party",
            "Exit Tavern",
        ]
        option: str = read_choice(gt_options, message)
        match option:
            case "Add Member":
                add_member_to_party(roster, party)
            case "Remove Member":
                delete_member_from_party(roster, party)
            case "Character Status":
                if not party:
                    print("No characters remains in the party!")
                    sleep(2)
                    continue
                char_names: List[str] = [c.name for c in party]
                select_name: str = read_choice_or_exit(char_names, "Select a Character:")
                if select_name == "Exit":
                    continue
                char: Character = get_character(select_name, party)
                menu_read_options(char, party)
            case "Character Equip":
                if not party:
                    print("No characters remains in the party!")
                    sleep(2)
                    continue
                char_names: List[str] = [c.name for c in party]
                select_name: str = read_choice_or_exit(char_names, "Select a Character:")
                if select_name == "Exit":
                    continue
                char: Character = get_character(select_name, party)
                display_character_sheet_pyQT(char)
            case "Reorder":
                if not party:
                    print("No characters remains in the party!")
                    sleep(2)
                    continue
                available_pos: List[int] = list(range(1, len(party) + 1))
                new_pos: dict() = {}
                for i, char in enumerate(party):
                    order: int = read_value(available_pos, f"new img_pos for {char.name} {available_pos}:")
                    available_pos.remove(order)
                    new_pos[char.name] = order
                new_pos = dict(sorted(new_pos.items(), key=lambda x: x[1]))
                for i, char_name in enumerate(list(new_pos.keys())):
                    party[i] = get_character(char_name, roster)
                    party[i].id_party = i
                    save_character(char=party[i], _dir=characters_dir)
            case "Divvy Gold":
                if not party:
                    print("No characters remains in the party!")
                    sleep(2)
                    continue
                total_gold: int = sum([c.gold for c in party])
                for char in party:
                    char.gold = total_gold // len(party)
                print("All the party's gold has been divided.")
                for char in party:
                    save_character(char, _dir=characters_dir)
                sleep(1)
            case "Disband Party":
                if not party:
                    print("No characters remains in the party!")
                    sleep(2)
                    continue
                if read_bool("Are you sure?"):
                    for char in party:
                        char.id_party = -1
                        save_character(char, _dir=characters_dir)
                    party.clear()
            case "Exit Tavern":
                exit_tavern = True
            case _:
                continue


def display_rest_message(char: Character):
    efface_ecran()
    print(f"{char.name} is Sleeping...")
    print(f"\tHits {char.hit_points}/{char.max_hit_points}")
    print(f"\t\tYou have {char.gold}GP")
    sleep(1)


def rest_character(char: Character, fee: int, weeks: int, xp_levels, console_mode: bool = True) -> str:
    display_msg: List[str] = []
    if console_mode:
        display_rest_message(char)
    else:
        display_msg += [f"{char.name} is Sleeping..."]
        display_msg += [f"\tHits {char.hit_points}/{char.max_hit_points}"]
        display_msg += [f"\t\tYou have {char.gold}GP"]
    former_age_in_weeks: int = char.age
    while fee and char.hit_points < char.max_hit_points and char.gold >= fee:
        char.hit_points = min(char.max_hit_points, char.hit_points + fee // 10)
        char.gold -= fee
        char.age += weeks
        if console_mode:
            display_rest_message(char)
    if char.hit_points == char.max_hit_points:
        display_msg += [f"{char.name} is fully healed!"]
    else:
        display_msg += [f"{char.name} is partially healed!"]
    if char.class_type.can_cast:
        if char.sc.spell_slots != char.class_type.spell_slots[char.level]:
            display_msg += [f"{char.name} has memorized all his spells"]
            char.sc.spell_slots = copy(char.class_type.spell_slots[char.level])
    if char.level < len(xp_levels) and char.xp >= xp_levels[char.level]:
        if char.class_type.can_cast:
            spell_names: List[str] = populate(collection_name="spells", key_name="results")
            all_spells: List[Spell] = [request_spell(name) for name in spell_names]
            class_tome_spells = [s for s in all_spells if s is not None and char.class_type.index in s.allowed_classes]
            display_message, new_spells = char.gain_level(tome_spells=class_tome_spells)
        else:
            display_message, new_spells = char.gain_level()
        display_msg += [display_message]
    if char.age // 52 == former_age_in_weeks // 52 + 1:
        display_msg += ["Happy birthday!"]
    return "\n".join(display_msg)


def temple_of_cant(party: List[Character], roster: List[Character]):
    exit_temple: bool = False
    while not exit_temple:
        efface_ecran()
        message = "+----------------------------+\n"
        message += "|    ** TEMPLE OF CANT **    |\n"
        message += "+----------------------------+\n"
        message += "Temple of Cant -- Praise God!!!"
        print(message)
        cures_costs_per_level = {"PARALYZED": 100, "STONED": 200, "DEAD": 250, "ASHES": 500, }
        candidates_to_cure = [f"{c.name} ({cures_costs_per_level[c.status] * c.level} GP)" for c in roster if c.status not in ("OK", "LOST")]
        if not candidates_to_cure:
            print("No more character to save ** HERE! **")
            exit_temple = True
            sleep(3)
            continue
        choice: str = read_choice_or_exit(candidates_to_cure, "Who do You Want to Save?")
        if choice == "Exit":
            exit_temple = True
        else:
            efface_ecran()
            char_to_save: Character = get_character(choice.split('(')[0].strip(), roster)
            contributor_names: List[str] = [c.name for c in party]
            char_name: str = read_choice_or_exit(contributor_names, "Who will Contribute?")
            if char_name == "Exit":
                exit_temple = True
                continue
            char_to_contribute: Character = get_character(char_name, party)
            if not party:
                print("No character remains in the party.")
                sleep(2)
                exit_temple = True
            # cprint(f'{char_to_save.hit_points}  -> {char_to_save.status} : \n{char_to_save}')
            if char_to_contribute.gold < cures_costs_per_level[char_to_save.status] * char_to_save.level:
                print("Go away! You don't have enough of money!")
                sleep(2)
            elif char_to_save.status == "DEAD":
                success: bool = randint(1, 100) < 50 + 3 * char_to_save.constitution
                if success:
                    # cprint(f"{char_to_save.name} ** LIVES! ***", color.RED)
                    char_to_save.status = "OK"
                    char_to_save.hit_points = 1
                    char_to_save.age += randint(1, 52)
                    print(f"{char_to_save.name} ** LIVES! ***")
                else:
                    char_to_save.status = "ASHES"
                    print(f"{char_to_save.name} converts to ** ASHES! ***")
                save_character(char_to_save, _dir=characters_dir)
                sleep(2)
            elif char_to_save.status == "ASHES":
                success: bool = randint(1, 100) < 40 + 3 * char_to_save.constitution
                if success:
                    char_to_save.status = "OK"
                    char_to_save.hit_points = char_to_save.max_hit_points
                    char_to_save.age += randint(1, 52)
                    exit_message(f"{char_to_save.name} ** LIVES! ***")
                else:
                    char_to_save.status = "LOST"
                    print(f"{char_to_save.name} is ** LOST! ***")
                save_character(char_to_save, _dir=characters_dir)
                sleep(2)


def buy_items(char: Character):
    shop = get_boltac_shop()
    exit_buy: bool = False
    while not exit_buy:
        efface_ecran()
        # Build list: unlimited weapons/armors (from loader) + magic items in stock
        menu_entries = []
        # Non-magical weapons and armors (unlimited)
        for w in shop.get_all_weapons():
            menu_entries.append((w, -1))
        for a in shop.get_all_armors():
            menu_entries.append((a, -1))

        # Magical items with limited stock
        for item, stock in shop.get_magic_items_in_stock():
            menu_entries.append((item, stock))

        item_names = []
        for item, stock in menu_entries:
            cost_display = str(item.cost) if hasattr(item, 'cost') else f"{getattr(item, 'cost', 'N/A')}"
            stock_label = 'Unlimited' if stock == -1 else f'Stock: {stock}'
            prof_label = ''
            if isinstance(item, Weapon) and hasattr(char, 'prof_weapons') and item not in char.prof_weapons:
                prof_label = f' {Color.RED}** NOT PROFICIENT **{Color.END}'
            item_names.append(f"{item.name} ({cost_display}) [{stock_label}]{prof_label}")

        message = f"Which item do you want to buy?\n\tYou Have {char.gold} GP.\n"
        choice = read_choice_or_exit(item_names, message)
        if choice == 'Exit':
            exit_buy = True
            continue

        # find selected
        sel_name = choice.split('(')[0].strip()
        sel_index = next(i for i, (it, st) in enumerate(menu_entries) if it.name == sel_name)
        item, stock = menu_entries[sel_index]

        # Determine price in cp for comparison
        price_cp = item.cost.value if hasattr(item, 'cost') and hasattr(item.cost, 'value') else (item.cost if isinstance(item.cost, int) else 0)
        if char.gold * 100 < price_cp:
            print("Go away! You don't have enough of money!")
            sleep(2)
            continue

        # Deduct gold (cost stored in gp?), many existing costs are in gp units -> item.cost.value is gp
        gp_cost = price_cp // 100 if price_cp >= 100 else price_cp // 1
        # Conservative approach: if cost.value exists and unit is 'gp', use that
        if hasattr(item, 'cost') and hasattr(item.cost, 'unit') and item.cost.unit == 'gp':
            gp_cost = item.cost.quantity if hasattr(item.cost, 'quantity') else (item.cost.value // 100 if hasattr(item.cost, 'value') else 0)

        if char.gold < gp_cost:
            print("Go away! You don't have enough of money!")
            sleep(2)
            continue

        # Process purchase
        if stock == -1:
            # Unlimited: give a copy
            char.gold -= gp_cost
            free_slots = [i for i, it in enumerate(char.inventory) if not it]
            if free_slots:
                char.inventory[free_slots[0]] = deepcopy(item)
                print(f"{char.name} buys {item.name} for {item.cost}")
                save_character(char, _dir=characters_dir)
            else:
                print("Inventory is full!")
            sleep(2)
        else:
            # Limited stock (magic item)
            if shop.buy_item(item, quantity=1):
                char.gold -= gp_cost
                free_slots = [i for i, it in enumerate(char.inventory) if not it]
                if free_slots:
                    # create instance: if potion (concrete type) it's returned already by factory
                    new_item = deepcopy(item)
                    char.inventory[free_slots[0]] = new_item
                    print(f"{char.name} buys {item.name} for {item.cost}")
                    save_character(char, _dir=characters_dir)
                else:
                    print("Inventory is full! Transaction reversed.")
                    # Refund and restore stock
                    char.gold += gp_cost
                    shop.sell_item(item, sell_price_cp=gp_cost*100)
                sleep(2)
            else:
                print("Item out of stock!")
                sleep(1)


def sell_items(char):
    shop = get_boltac_shop()
    exit_sell: bool = False
    while not exit_sell:
        efface_ecran()
        item_names: List[str] = []
        inv_items = [i for i in char.inventory if i]
        for i in inv_items:
            prof_label = f'{Color.RED} ** NOT PROFICIENT **{Color.END}' if isinstance(i, Weapon) and i not in char.prof_weapons else ''
            equipped_label = ' (Equipped)' if (isinstance(i, Weapon) or isinstance(i, Armor)) and getattr(i, 'equipped', False) else ''
            cost = i.cost.quantity if hasattr(i, 'cost') and hasattr(i.cost, 'quantity') else (i.cost if isinstance(i.cost, int) else getattr(i, 'cost', 'N/A'))
            item_name = f"{i.name} ({cost}){equipped_label}{prof_label}"
            item_names.append(item_name)

        message = f"Which item do you want to sell?\n\tYou Have {char.gold} GP.\n"
        choice = read_choice_or_exit(item_names, message)
        if choice == 'Exit':
            exit_sell = True
            continue

        sel_name = choice.split('(')[0].strip()
        item = next(e for e in char.inventory if e and e.name == sel_name)
        if isinstance(item, (Weapon, Armor)) and getattr(item, 'equipped', False):
            print(f"Please un-equip {item.name} first!")
            sleep(2)
            continue

        cost_value = item.cost.quantity if hasattr(item, 'cost') and hasattr(item.cost, 'quantity') else (item.cost if isinstance(item.cost, int) else 0)
        sell_price_cp = cost_value * 100 // 4 if cost_value else 0
        # Sell to shop (shop accepts everything)
        shop.sell_item(item, sell_price_cp=sell_price_cp)
        # Remove from character inventory
        char.inventory[char.inventory.index(item)] = None
        char.gold += sell_price_cp // 100
        save_character(char, _dir=characters_dir)
        print(f"{char.name} sells {item.name} for {sell_price_cp} cp")
        sleep(2)


def boltac_trading_post(party):
    shop = get_boltac_shop()
    exit_trading_post: bool = False
    while not exit_trading_post:
        efface_ecran()
        banner = "+--------------------------------+\n"
        banner += "|  ** BOLTAC'S TRADING POST **   |\n"
        banner += "+--------------------------------+\n"
        banner += "\tWelcome to Boltac's!\n"
        message = "  Everyday, Everything Low Price!!\n\n\tWho will Enter?\n"
        select_name: str = read_choice_or_exit([c.name for c in party], banner + message)
        if select_name == "Exit":
            exit_trading_post = True
        else:
            char: Character = get_character(select_name, party)
            exit_character_menu: bool = False
            while not exit_character_menu:
                efface_ecran()
                message = f"\t  Hello, {char.name}!\n"
                choice: str = read_choice_or_exit(["Buy", "Sell", "Pool Gold"], banner + message)
                match choice:
                    case "Buy":
                        buy_items(char)
                    case "Sell":
                        sell_items(char)
                    case "Pool Gold":
                        total_gold: int = sum([c.gold for c in party])
                        for ch in party:
                            ch.gold = total_gold if ch == char else 0
                        print("All Gold has Pooled.")
                        sleep(1)
                    case "Exit":
                        exit_character_menu = True
                    case _:
                        continue


def adventurer_inn(party):
    exit_inn: bool = False
    while not exit_inn:
        efface_ecran()
        message = "+-----------------------------+\n"
        message += "|   ** ADVENTURER'S INN **   |\n"
        message += "+-----------------------------+\n"
        message += "Welcome to Adventurer's Inn!"
        print(message)
        choice: str = read_choice_or_exit([c.name for c in party], "Who will Enter?")
        if choice == "Exit":
            exit_inn = True
        else:
            efface_ecran()
            char: Character = get_character(choice, party)
            rooms: List[str] = [
                "The Stables (Free!)",
                "A Cot (10 GP / Week)",
                "Economy Room (100 GP / Week)",
                "Merchant Suites (200 GP / Week)",
                "The Royal Suites (500 GP / Week)",
            ]
            fees: List[int] = [0, 10, 100, 200, 500]
            weeks: List[int] = [0, 1, 3, 7, 10]
            room_select: str = read_choice_or_exit(rooms, f"Welcome {char.name}.")
            if room_select == "Exit":
                continue
            room_number: int = rooms.index(room_select)
            if fees[room_number] > char.gold:
                print(f"You Don't Have Enough Gold.")
                sleep(2)
                continue
            # print(f'{char.name} selected {room} - Fee is {fees[fee_no]} GP / Week!')
            display_msg = rest_character(char, fees[room_number], weeks[room_number], xp_levels)
            print(display_msg)
            exit_message(f"{char.name} has rested for {weeks[room_number]} weeks.")
            save_character(char, _dir=characters_dir)


def get_character(name: str, roster: List[Character]) -> Optional[Character]:
    char_list = [c for c in roster if c.name == name]
    return char_list[0] if char_list else None


def simulate_arena(roster: List[Character]):
    ok_roster: List[Character] = [c for c in roster if c.status != "DEAD"]
    if not ok_roster:
        print(f"no available characters for arena!")
        exit_message()
        return
    char: Character = select_character(ok_roster)
    while char.status != "OK":
        print(f"{char.name} is ** {char.status} ** - Please select another character!")
        char: Character = select_character(roster)
    display_character_sheet(char)
    while continue_message(message="Do you want to start a new combat simulation? (Y/N)"):
        # efface_ecran()
        # display_character_sheet_pyQT(character)
        ok_roster: List[Character] = [c for c in roster if c.status != "DEAD"]
        if not ok_roster:
            print(f"no available characters for arena!")
            exit_message()
            return
        while char.status != "OK":
            print(f"{char.name} is ** {char.status} ** - Please select another character!")
            char: Character = select_character(ok_roster)
            continue
        arena(char)


def rename_character_prompt_ok(char: Character, new_name: str) -> bool:
    print(f"Are you sure you want to rename {char.name} to {new_name} (Y/N)?")
    response: bool = get_key().lower() == 'y'
    print(f"{char.name} has been ** RENAMED ** to {new_name}" if response else f"Renaming of {char.name} cancelled.")
    sleep(2)
    return response



def delete_character_prompt_ok(char: Character) -> bool:
    print(f"Are you sure you want to delete {char.name} (Y/N)?")
    response: bool = get_key().lower() == 'y'
    if response:
        os.remove(f"{characters_dir}/{char.name}.dmp")
    print(f"{char.name} has been ** DELETED **" if response else f"Deletion cancelled :-) {char.name} ** STILL IN GAME **")
    sleep(2)
    return response


def training_grounds(roster: List[Character]):
    tg_options: List[str] = ["Create a New Character", "Create a Random Character", "Character Status", "Delete a Character", "Rename a Character", "Change a Character's class", "System", "Return to Castle", ]
    exit_training_grounds: bool = False
    while not exit_training_grounds:
        efface_ecran()
        message = "+------------------------+\n"
        message += "| ** TRAINING GROUNDS ** |\n"
        message += "+------------------------+"
        option: str = read_choice(tg_options, message)
        char_names: List[str] = [c.name for c in roster if c not in party]
        match option:
            case "Create a New Character":
                if len(roster) > MAX_ROSTER:
                    print(f"maximum number ({MAX_ROSTER}) of characters exceeded!!! Please delete existing characters to create a new one...")
                    continue
                character = create_new_character(roster)
                save_character(character, _dir=characters_dir)
                roster.append(character)
            case "Create a Random Character":
                if len(roster) > MAX_ROSTER:
                    print(f"maximum number ({MAX_ROSTER}) of characters exceeded!!! Please delete existing characters to create a new one...")
                    continue
                races, subraces, classes, alignments, equipments, proficiencies, names, human_names, spells = load_character_collections()
                random_char: Character = generate_random_character(roster, races, subraces, classes, names, human_names, spells)
                display_character_sheet(char=random_char)
                if input(f"\nKeep {random_char.name}? (y/n): ").lower() == 'y':
                    roster.append(random_char)
                    save_character(random_char, _dir=characters_dir)
                    print(f'{random_char.name} successfully added to roster!')
                    sleep(2)
                else:
                    print("Character discarded.")
                    sleep(2)

            case "Character Status":
                efface_ecran()
                roster = sorted(roster, key=lambda c: c.level)
                # char_names: List[tuple] = [(c.name, c.class_type, f'Lvl {c.level}') for c in roster if c.status == 'OK' and c not in party and not c.in_dungeon]
                char_names: List[tuple] = [(c.name, c.class_type, f"Lvl {c.level}") for c in roster if c not in party]
                select_name: str = read_choice_tuple(char_names, "Select a Character.")
                # select_name: str = read_choice_or_exit(char_names, "Select a Character.")
                if select_name == "Exit":
                    continue
                char: Character = get_character(select_name, roster)
                menu_read_options(char, roster)
            case "Delete a Character":
                select_name: str = read_choice_or_exit(char_names, "Select a Character to Delete.")
                if select_name == "Exit":
                    continue
                char: Character = get_character(select_name, roster)
                # display_character_sheet(char)
                if delete_character_prompt_ok(char):
                    if char in party:
                        party.remove(char)
                    roster.remove(char)
            case "Rename a Character":
                select_name: str = read_choice_or_exit(char_names, "Select a Character to Rename.")
                if select_name == "Exit":
                    continue
                char: Character = get_character(select_name, roster + party)
                print(f"Current Name is {char.name}.")
                name_ok: bool = False
                while not name_ok:
                    new_name: str = input("Input New Name: ")
                    if new_name in char_names:
                        print(f"{new_name} already taken! Please choose another one!")
                        continue
                    name_ok = True
                if not rename_character_prompt_ok(char, new_name):
                    continue
                os.remove(f"{characters_dir}/{char.name}.dmp")
                char.name = new_name
                save_character(char, _dir=characters_dir)
                sleep(2)
            case "Change a Character's class":
                input("not yet created!... [Return] to main menu")
            case "System":
                input("not yet created!... [Return] to main menu")
            case "Return to Castle":
                exit_training_grounds = True


def load_encounter_table() -> dict():
    csv_filename: str = f"Encounter_Levels.csv"
    data = read_csvfile(csv_filename)
    enc_keys: List[str] = ["1", "2", "3", "4", "5-6-7", "7-8-9", "10-11-12"]
    enc_table: dict() = {}
    for line in data:
        enc_level, cr_pair, *cr_list = line
        cr_dict: dict() = {}
        for i, enc_key in enumerate(enc_keys):
            if enc_level == "20" and i == 0:
                # tmp_cr_list: List[str] =
                cr_dict[enc_key] = [cr_list[0].replace("+", "")]
            else:
                cr_dict[enc_key] = [Fraction(cr) for cr in cr_list[i].split(",")]
        enc_table[int(enc_level)] = [tuple(map(Fraction, cr_pair.split("+"))), cr_dict]
    return enc_table


def load_encounter_gold_table() -> List[int]:
    csv_filename: str = f"Encounter_Gold.csv"
    data = read_csvfile(csv_filename)
    return [int(gold) for enc_level, gold in data]


def generate_encounter(available_crs: List[Fraction], encounter_table: dict, encounter_level: int, monsters: List[Monster], monster_groups_count: int, spell_casters_only: bool = False, ) -> List[Monster]:
    if monster_groups_count > 2:
        exit_message("System Error!... only 2 groups of monsters allowed here. Please contact the Dungeon Master :-)")
        return
    encounter_level = min(19, encounter_level)
    if not spell_casters_only and monster_groups_count == 2:
        cr1, cr2 = encounter_table[encounter_level][0]
        # print(f'(cr_1, cr2) = {(cr1, cr2)}')
        if cr1 not in available_crs:
            cr1 = min(available_crs, key=lambda cr: cr - cr1)
        cr1_monsters: List[Monster] = [m for m in monsters if Fraction(str(m.challenge_rating)) == cr1]
        # print(f'{len(cr1_monsters)} cr_1_monsters = {cr1_monsters}')
        if cr2 not in available_crs:
            cr2 = min(available_crs, key=lambda cr: cr - cr2)
        if spell_casters_only:
            cr2_monsters: List[Monster] = [m for m in monsters if Fraction(str(m.challenge_rating)) == cr2 and m.is_spell_caster]
        else:
            cr2_monsters: List[Monster] = [m for m in monsters if Fraction(str(m.challenge_rating)) == cr2]
        # print(f'{len(cr2_monsters)} cr2_monsters = {cr2_monsters}')
        monster_1: Monster = choice(cr1_monsters)
        monster_2: Monster = choice(cr2_monsters)
        return [request_monster(monster_1.index), request_monster(monster_2.index)]
    else:
        matching_monsters: List[Tuple[Monster, int]] = []
        cr_dict: dict() = encounter_table[encounter_level][1]
        for enc_key, cr_list in cr_dict.items():
            monsters_count: int = choice(list(map(int, enc_key.split("-"))))
            if encounter_level == 20:
                cr: int = cr_list[0]
                matching_monsters += [(m, monsters_count) for m in monsters if Fraction(str(m.challenge_rating)) >= cr and m.is_spell_caster]
            else:
                matching_monsters += [(m, monsters_count) for m in monsters if Fraction(str(m.challenge_rating)) in cr_list and m.is_spell_caster]
        monster, monster_count = choice(matching_monsters)
        group_of_monsters: List[Monster] = [request_monster(monster.index) for m in matching_monsters]
        for _ in range(monster_count - 1):
            m: Monster = request_monster(monster.index)
            m.hp_roll()
            group_of_monsters.append(m)
        return group_of_monsters


def display_group_of_monsters(monsters: List[Monster]):
    mixed_pair: bool = len(set([m.name for m in monsters])) == 2
    alive_monsters = list(filter(lambda m: m.hit_points > 0, monsters))
    if not mixed_pair:
        monsters.sort(key=lambda m: m.hit_points, reverse=True)
        hp_display: str = " - ".join([f"HP {m.hit_points}" for m in monsters if m.hit_points > 0])
        cprint(f"{color.PURPLE}Group of {len(alive_monsters)} {monsters[0].name} ({hp_display}){color.END}")
    else:
        for i, monster in enumerate(monsters):
            if monster.hit_points > 0:
                cprint(f"{color.PURPLE} Monster #{i} : {monster.name} ({monster.hit_points} HP){color.END}")


def generate_encounter_levels(party_level: int) -> List[int]:
    """
        Adjust encounter's level based on table Encounter_Difficulty.csv (not parsed here)
    :param party_level:
    :return: list of 20 encounter levels
    """
    diff_stats: array = array([30, 50, 15, 5]) // 5
    encounter_levels: List[int] = []
    for i, stat_number in enumerate(diff_stats):
        match i:
            case 0:
                encounter_levels += [(randint(1, party_level - 1) if party_level > 1 else 1) for _ in range(stat_number)]
            case 1:
                encounter_levels += [party_level] * stat_number
            case 2:
                encounter_levels += [(party_level + randint(1, 4)) for _ in range(stat_number)]
            case 3:
                encounter_levels += [(party_level + randint(5, 20)) for _ in range(stat_number)]
    shuffle(encounter_levels)
    return encounter_levels


def explore_dungeon(party: List[Character], monsters_db: List[Monster]):
    """Combat simulation using CombatSystem from dnd-5e-core"""
    from dnd_5e_core.combat import CombatSystem

    print(f"{color.PURPLE}-----------------------------------------------------------{color.END}")
    print(f"{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}")
    print(f"{color.PURPLE}-----------------------------------------------------------{color.END}")

    max_level_char: int = max([c.level for c in party])
    party_level: int = round(sum([c.level for c in party]) / len(party))

    encounter_levels: List[int] = generate_encounter_levels(party_level=party_level)
    spell_casters_only: bool = False

    # Initialize combat system with verbose mode
    combat_system = CombatSystem(verbose=True, message_callback=None)

    alive_chars: List[Character] = [c for c in party if c.hit_points > 0]

    while alive_chars:
        if continue_message(f"Do you want to go back to [Castle]? (Y/N)"):
            return

        # Generate new encounter
        monster_groups_count: int = randint(1, 2)
        if not encounter_levels:
            encounter_levels: List[int] = generate_encounter_levels(party_level=party_level)
        encounter_level: int = encounter_levels.pop()
        monsters: List[Monster] = generate_encounter(
            available_crs=available_crs,
            encounter_table=encounter_table,
            encounter_level=encounter_level,
            monsters=monsters_db,
            monster_groups_count=monster_groups_count,
            spell_casters_only=spell_casters_only
        )

        cprint(f"{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}")
        cprint(f"{color.PURPLE} New encounter!{color.END}")
        display_group_of_monsters(monsters)
        cprint(f"{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}")

        # Initiative rolls
        attack_queue = [(c, randint(1, c.abilities.dex)) for c in party] + [(m, randint(1, m.abilities.dex)) for m in monsters]
        attack_queue.sort(key=lambda x: x[1], reverse=True)
        attackers = [c for c, init_roll in attack_queue]

        alive_monsters: List[Monster] = [c for c in monsters if c.hit_points > 0]
        alive_chars: List[Character] = [c for c in party if c.hit_points > 0]
        round_num = 0
        flee_combat: bool = False

        while alive_monsters and alive_chars:
            if round_num:
                cprint("-------------------------------------------------------")
                cprint(f"{color.DARKCYAN} Round {round_num} results:{color.END}")
                display_group_of_monsters(monsters)
                cprint("-------------------------------------------------------")
                print(display(party))

            message: str = "engage" if not round_num else "continue"
            if not continue_message(f"Do you want to {message} combat? (Y/N)"):
                flee_combat = True
                break

            round_num += 1

            # Combat round using CombatSystem
            queue = [c for c in attackers if c.hit_points > 0]

            while queue:
                attacker = queue.pop()
                if attacker.hit_points > 0:
                    if isinstance(attacker, Monster):
                        # Monster turn
                        combat_system.monster_turn(
                            monster=attacker,
                            alive_chars=alive_chars,
                            alive_monsters=alive_monsters,
                            round_num=round_num,
                            party=party
                        )
                    else:  # Character turn
                        # Character turn
                        combat_system.character_turn(
                            character=attacker,
                            alive_chars=alive_chars,
                            alive_monsters=alive_monsters,
                            party=party,
                            weapons=weapons,
                            armors=armors,
                            equipments=equipments,
                            potions=potions
                        )

            # End of Round
            alive_chars: List[Character] = [c for c in party if c.hit_points >= 0]
            alive_monsters: List[Monster] = [c for c in monsters if c.hit_points >= 0]

        # End of encounter
        if not alive_chars:
            for target_char in party:
                target_char.conditions.clear()
            exit_message(f"** DEFEAT! ALL PARTY HAS BEEN KILLED **")
            break
        elif not alive_monsters:
            exit_message(f"** VICTORY! **")
            earned_gold: int = encounter_gold_table[party_level - 1]
            xp_gained: int = sum([m.xp for m in monsters])
            for target_char in alive_chars:
                target_char.gold += earned_gold // len(party)
                target_char.xp += xp_gained // len(alive_chars)
                target_char.conditions.clear()
            exit_message(f"Party has earned {earned_gold} GP and gained {xp_gained} XP!")
        elif flee_combat:
            exit_message(f"** Party successfully escaped! **")



def restore_all_roster(roster: List[Character]):
    """Cheat function used for debugging"""
    for char in roster:
        char.status = "OK"
        char.hit_points = char.max_hit_points
        char.spell_slots = copy(char.class_type.spell_slots.get(char.level))


def cheat_function(roster: List[Character]):
    for char in roster:
        char.xp += 10000
        char.gold += 1000
        char.hit_points = char.max_hit_points
        char.status = "OK"


def delete_all_potions(roster: List[Character]):
    """Needs to purge old potions from char's inventory"""
    for char in roster:
        if char.healing_potions:
            char.healing_potions.clear()
            save_character(char, _dir=characters_dir)


def delete_armors_weapons(roster: List[Character]):
    dagger: Weapon = request_weapon("dagger")
    skin: Armor = request_armor("skin-armor")
    for char in roster:
        char.weapon = dagger
        char.armor = skin

def delete_weapons(char):
    for item in char.inventory:
        if isinstance(item, Weapon):
            char.inventory[char.inventory.index(item)] = None
    save_character(char, _dir=characters_dir)

def give_best_armors_weapons(roster: List[Character]):
    for char in roster:
        weapon = char.inventory[0] = max(char.prof_weapons, key=lambda w: w.damage_dice.max_score)
        weapon.equipped = True
        if char.prof_armors:
            armor = char.inventory[1] = max(char.prof_armors, key=lambda a: int(a.armor_class["base"]))
            armor.equipped = True


def load_xp_levels() -> List[int]:
    levels = read_csvfile("XP Levels-XP Levels.csv")
    return [int(xp_needed) for xp_needed, level, master_bonus in levels]


if __name__ == "__main__":
    seed(time())
    PAUSE_ON_RAISE_LEVEL = True
    POTION_INITIAL_PACK = 15
    MAX_ROSTER = 100  # maximum number of characters allowed in this game
    path = os.path.dirname(__file__)
    abspath = os.path.abspath(path)
    # print(f'path = {path}')
    # print(f'abspath = {abspath}')
    # characters_dir = f'{abspath}/gameState/characters'
    game_path = get_save_game_path()
    characters_dir = f"{game_path}/characters"
    # cprint(characters_dir)
    # exit()

    """ Load XP Levels """
    xp_levels: List[int] = load_xp_levels()

    """ Load Monster, Armor, Weapon databases """
    monsters, armors, weapons, equipments, equipment_categories, potions = load_dungeon_collections()

    armors = list(filter(lambda a: a, armors))
    weapons = list(filter(lambda w: w, weapons))

    locations: List[str] = ["Edge of Town", "Castle"]
    castle_destinations: List[str] = [
        "Gilgamesh's Tavern",
        "Adventurer's Inn",
        "Temple of Cant",
        "Boltac's Trading Post",
        "Edge of Town",
    ]
    edge_of_town_destinations: List[str] = [
        "Training Grounds",
        "Maze",
        "Leave Game",
        "Castle",
    ]
    roster: List[Character] = get_roster(characters_dir)
    # party_ids: List[int] = set([c.id_party for c in roster if c.in_dungeon])
    # adventurer_groups: dict() = {p_id: [c for c in roster if c.id_party == p_id] for p_id in party_ids}
    # char_to_party: List[Char2Party] = load_char_to_party(_dir=game_path)
    # if not char_to_party:
    #     for c in roster:
    #         char_to_party.append(Char2Party(char_name=c.name))
    # party: List[Character] = [c for c in roster for c2p in char_to_party if c2p.char_name == c.name and c2p.id != -1]
    # party.sort(key=lambda c: c.id_party)

    party: List[Character] = load_party(_dir=game_path)

    encounter_table: dict() = load_encounter_table()
    encounter_gold_table: List[int] = load_encounter_gold_table()
    available_crs: List[Fraction] = [Fraction(str(m.challenge_rating)) for m in monsters]

    location = "Castle"

    # cheat_function(party)
    # restore_all_roster(roster)
    # delete_all_potions(roster)
    # delete_armors_weapons(roster)
    # Automatic level up
    # give_best_armors_weapons(party)
    # for c in party:
    #     if c.level < 20:
    #         c.xp = 400000
    # for c in party:
    #     while c.level < 20:
    # #         rest_character(c, 0, 1)
    # # delete_weapons(char=get_character(name="Iados", roster=party))
    # Iltazyara = get_character(name="Iltazyara", roster=roster)
    # Iltazyara.status = "DEAD"

    # Set TERM if it's not already set
    if "TERM" not in os.environ:
        # os.environ['TERM'] = 'xterm'  # or another appropriate terminal type
        os.environ["TERM"] = "xterm-256color"  # or another appropriate terminal type

    while True:
        efface_ecran()
        if location == "Castle":
            message = "+----------------------+\n"
            message += "|     ** CASTLE **     |\n"
            message += "+----------------------+"
            destination: str = read_choice(castle_destinations, message)
            for c in party:
                if c.status != "OK":
                    party.remove(c)
                    if c not in roster:
                        roster.append(c)
            # party = [c for c in party if c.status == 'OK']
            match destination:
                case "Gilgamesh's Tavern":
                    gilgamesh_tavern(party, roster)
                case "Adventurer's Inn":
                    if not party:
                        print("No characters remains in the party!")
                        sleep(2)
                        continue
                    adventurer_inn(party)
                case "Temple of Cant":
                    if not party:
                        print("No characters remains in the party!")
                        sleep(2)
                        continue
                    temple_of_cant(party, roster)
                case "Boltac's Trading Post":
                    boltac_trading_post(party)
                    # input('not yet created!... [Return] to Castle')
                case "Edge of Town":
                    location = "Edge of Town"
                    continue
                case _:
                    continue
        else:
            message = "+----------------------+\n"
            message += "|  ** EDGE OF TOWN **  |\n"
            message += "+----------------------+"
            destination: str = read_choice(edge_of_town_destinations, message)
            match destination:
                case "Training Grounds":
                    efface_ecran()
                    training_grounds(roster)
                    location = "Castle"
                case "Maze":
                    efface_ecran()
                    game_modes: List[str] = [
                        "ARENA (Simulation)",
                        "WIZARDRY (Enter Dungeon)",
                    ]
                    game_mode: str = read_choice(game_modes, "Choose game mode:")
                    if game_mode == "ARENA (Simulation)":
                        display_adventurers(roster=roster, party=party, location=location)
                        # simulate_arena(roster)
                        exit_message(message="*** NOT MAINTAINED ANYMORE (Sorry) - please return to Castle! ***")
                        location = "Castle"
                    else:
                        if party:
                            print(display(party))
                            explore_dungeon(party, monsters)
                            for char in party:
                                if char.hit_points <= 0:
                                    char.status = "DEAD"
                                save_character(char, _dir=characters_dir)
                            location = "Castle"
                            continue
                        else:
                            if roster:
                                print(f"** NO PARTY FOUND! ** Return to {Color.RED}Castle{Color.END} to recruit adventurers!")
                                location = "Castle"
                                sleep(2)
                            else:
                                print(f"** NO CHARACTERS FOUND! ** Return to {Color.RED}Training grounds{Color.END} to create one or more adventurer(s)!")
                                sleep(2)
                case "Leave Game":
                    for c in party:
                        save_character(c, _dir=characters_dir)
                    save_party(party=party, _dir=game_path)
                    # for c in party:
                    #     for c2p in char_to_party:
                    #         if c2p.char_name == c.name:
                    #             c2p.id = c.id_party
                    # save_char_to_party(char_to_party=char_to_party, _dir=game_path)
                    print(f"Bye, see you in a next adventure :-)")
                    exit(0)
                case "Castle":
                    location = "Castle"
                    continue
                case _:
                    continue
        efface_ecran()

    # print(f'Sauvegarde Roster')
    # for character in roster_list:
    #     with open(f'{characters_dir}/{character.name}.dmp', 'wb') as f1:
    #         pickle.dump(character, f1)

