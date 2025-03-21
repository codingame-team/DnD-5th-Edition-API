import random
from typing import List, Dict, Optional

from dao_classes import Character, Race, ClassType, SubRace, color, Proficiency, Abilities, SpellCaster
from main import load_character_collections, get_roster, get_height_and_weight, get_spell_caster, get_char_image, save_character
from populate_functions import request_proficiency
from tools.ability_scores_roll import ability_rolls
from tools.common import get_save_game_path


def generate_random_proficiencies(race, class_type) -> List[str]:
    # Choose proficiencies within the race
    chosen_proficiencies: List[str] = []

    for starting_proficiency_option in race.starting_proficiency_options:
        choose, prof_list = starting_proficiency_option
        prof_count = min(choose, len(prof_list))  # Ensure we don't try to choose more than available

        # Randomly select proficiencies
        chosen_profs = random.sample(prof_list, prof_count)
        chosen_proficiencies.extend(chosen_profs)

    # Choose proficiencies within the class
    for proficiency_choice in class_type.proficiency_choices:
        choose, prof_list = proficiency_choice
        prof_count = min(choose, len(prof_list))  # Ensure we don't try to choose more than available

        # Randomly select proficiencies
        chosen_profs = random.sample(prof_list, prof_count)
        chosen_proficiencies.extend(chosen_profs)

    return chosen_proficiencies

def generate_random_name(race: str, gender: str, names: dict(), reserved_names):
    """

    :param race: name of the race
    :param genre: name of the gender ['male', 'female', 'nickname', 'surname']
    :param names: dictionary of names
    :return:
    """
    if race in ['human', 'half-elf']:
        ethnic = random.choice(list(names.keys()))
        names_list = names[ethnic][gender]
        if len(names[ethnic]) > 2:
            other_key = [key for key in names[ethnic] if key not in ['male', 'female']][0]
            names_list += names[ethnic][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = random.choice(names)
        return name, ethnic
    else:
        names_list = names[race][gender]
        if len(names[race]) > 2:
            other_key = [key for key in names[race] if key not in ['male', 'female']][0]
            names_list += names[race][other_key]
        names: List[str] = [name for name in names_list if name not in reserved_names]
        name = random.choice(names)
        return name

def generate_random_character(races: List[Race], subraces: List[SubRace], classes: List[ClassType], names: Dict[str, List[str]]) -> Character:
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
    race = random.choice(races)
    # Select optional subrace
    subraces_names: List[str] = [s.index for s in subraces for r in races if r.index == race.index and r.index in s.index]
    subrace: Optional[SubRace] = [r for r in subraces if r.index == random.choice(subraces_names)][0] if subraces_names else None
    char_proficiencies = race.starting_proficiencies

    """ 2. Choose a class """
    # Select random class
    class_type = random.choice(classes)
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
    gender = random.choice(["male", "female"])

    ethnic: str = None
    reserved_names: List[str] = [c.name for c in roster]
    if race.index in ['human', 'half-elf']:
        name, ethnic = generate_random_name(race.index, gender, human_names, reserved_names)
    else:
        name = generate_random_name(race.index, gender, names, reserved_names)

    height, weight = get_height_and_weight(race, subrace)

    hit_points = class_type.hit_die + ability_modifiers.con

    # Phase 2: Spell selection
    char_level: int = 1 # could be changed to create higher level characters
    spell_caster: Optional[SpellCaster] = get_spell_caster(class_type, char_level, spells)

    free_id = max([c.id for c in roster]) + 1 if roster else 1
    return Character(id=free_id,
                     image_name=get_char_image(class_type),
                     x=-1, y=-1, old_x=-1, old_y=-1,
                     race=race,
                     subrace=subrace,
                     class_type=class_type,
                     proficiencies=char_proficiencies,
                     # proficiencies=class_type.proficiencies + race.starting_proficiencies,
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
                     xp=0, level=1,
                     age=18 * 52 + random.randint(0, 299),
                     gold=90 + random.randint(0, 99),
                     sc=spell_caster,
                     conditions=[],
                     speed=30,
                     haste_timer=0,
                     hasted=False,
                     st_advantages=[])


if __name__ == "__main__":
    # Assuming you have lists of races and classes, and a dictionary of names
    races, subraces, classes, alignments, equipments, proficiencies, names, human_names, spells = load_character_collections()

    game_path = get_save_game_path()
    characters_dir = f'{game_path}/characters'
    roster: List[Character] = get_roster(characters_dir)

    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    print(f'{color.PURPLE} Character creation based on DnD 5th edition API{color.END}')
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')

    # Generate a preset character
    new_character: Character = generate_random_character(races, subraces, classes, names)

    # Print character details
    print(f"Name: {new_character.name}")
    print(f"Race: {new_character.race.name}")
    print(f"Class: {new_character.class_type.name}")
    print(f"Abilities: {new_character.abilities}")
    print(f"Gender: {new_character.gender}")
    print(f"Height: {new_character.height} cm")
    print(f"Weight: {new_character.weight} kg")
    print(f"Hit Points: {new_character.hit_points}")
    print(f"Gold: {new_character.gold}")
    print(f"Proficiencies: {new_character.proficiencies}")
    print(f"Spell Caster: {new_character.sc}")
    print(f"Equipment: {new_character.inventory}")

    save_character(char=new_character, _dir=characters_dir)

