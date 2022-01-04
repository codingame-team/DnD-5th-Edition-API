from copy import copy

from dao_classes import *
from populate_functions import *


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
        print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
        print(f'{color.PURPLE} Combat simulation engine based on DnD 5th edition API{color.END}')
        print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
        print(f'{color.DARKCYAN}Do you want to pause output after new level? (Y/N){color.END}')
        response = input()
        while response not in ['y', 'n', 'Y', 'N']:
            print(f'{color.DARKCYAN} Do you want to pause output after new level? (Y/N){color.END}')
            response = input()
        PAUSE_ON_RAISE_LEVEL = True if response in ['y', 'Y'] else False


def read_name_simple(race: str, sex: str):
    name: str = None
    while not name or not name.isalpha():
        print(f'Enter name of character: ')
        name = input()
    return name


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
        names_list = names[race][gender]
        if len(names[race]) > 2:
            other_key = [key for key in names[race] if key not in ['male', 'female']][0]
            names_list += names[race][other_key]
        name = read_choice('name', names_list)
        return name


def read_choice(item_name: str, choice_list: List[str]) -> str:
    choice = None
    while choice not in range(1, len(choice_list) + 1):
        items_list = '\n'.join([f'{i + 1}) {item}' for i, item in enumerate(choice_list)])
        print(f'Choose a {item_name}:\n{items_list}')
        err_msg = f'Bad value! Please enter a number between 1 and {len(choice_list)}'
        try:
            choice = int(input())
            if choice not in range(1, len(choice_list) + 1):
                raise ValueError
        except ValueError:
            print(err_msg)
            continue
    return choice_list[choice - 1]


def create_character(races: List[str], classes: List[Class], names: dict(), human_names: dict()):
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    print(f'{color.PURPLE} Character creation based on DnD 5th edition API{color.END}')
    print(f'{color.PURPLE}-------------------------------------------------------{color.END}')
    race = read_choice('race', races)
    genders = ['male', 'female']
    gender = read_choice('genre', genders)
    ethnic = None
    if race in ['human', 'half-elf']:
        name, ethnic = read_name(race, gender, human_names)
    else:
        name = read_name(race, gender, names)
    class_type = read_choice('class', classes)
    return race, gender, name, class_type, ethnic


if __name__ == '__main__':
    random.seed()
    PAUSE_ON_RAISE_LEVEL = True
    POTION_INITIAL_PACK = 5
    """ Load XP Levels """
    infile = open("Tables/xp_levels.txt", "r")
    xp_levels = []
    for line in infile:
        xp_needed, level, master_bonus = line.split(' ')
        # xp_levels.append((xp_needed, master_bonus))
        xp_levels.append(int(xp_needed))
    """ Load Monster, Armor and Weapon databases """
    monsters_names: List[str] = populate(collection_name='monsters', key_name='results')
    armors_names: List[str] = populate(collection_name='armors', key_name='equipment')
    weapons_names: List[str] = populate(collection_name='weapons', key_name='equipment')
    roster: List[Monster] = [request_monster(name) for name in monsters_names]
    boltac_armors: List[Armor] = [request_armor(name) for name in armors_names]
    boltac_armors = [a for a in boltac_armors if a]
    boltac_weapons: List[Armor] = [request_weapon(name) for name in weapons_names]
    boltac_weapons = [w for w in boltac_weapons if w]
    """ Character creation """
    races: List[str] = populate(collection_name='races', key_name='results')
    names = dict()
    for race in races:
        if race not in ['human', 'half-elf']:
            names[race] = populate_names(race)
    human_names: List[str] = populate_human_names()
    classes: List[str] = populate(collection_name='classes', key_name='results')
    alignments: List[str] = populate(collection_name='alignments', key_name='results')
    race, genre, name, class_type, ethnic = create_character(races, classes, names, human_names)
    character: Character = Character(name=name,
                                     race=race,
                                     ethnic=ethnic,
                                     genre=genre,
                                     class_type=class_type,
                                     armor=boltac_armors[0],
                                     weapon=boltac_weapons[1],
                                     hit_points=10,
                                     max_hit_points=10,
                                     xp=0, level=1,
                                     healing_potions=[Potion('2d4')] * POTION_INITIAL_PACK,
                                     monster_kills=0)
    print(character)
    if not continue_message():
        print(f'Bye {character.name}, see you in a next adventure :-)')
        exit(0)
    """ Combat simulation """
    welcome_message()
    attack_count = 0
    while character.hit_points > 0 and character.level < 20:
        # monsters_to_fight = [m for m in roster if m.challenge_rating < 1]
        # monsters_to_fight = [m for m in roster if 2 + character.level <= m.level <= 5 + character.level]
        monsters_to_fight = [m for m in roster if m.level <= 5 + character.level]
        if character.xp > xp_levels[character.level]:
            character.gain_level(pause=PAUSE_ON_RAISE_LEVEL)
        monster: Monster = copy(random.choice(monsters_to_fight))
        print(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        print(f'{color.PURPLE} New encounter! {character} vs {monster}{color.END}')
        print(f'{color.PURPLE}-------------------------------------------------------------------------------------------------------------------------------------------{color.END}')
        round_num = 0
        monster_max_hp = monster.hit_points
        while monster.hit_points > 0:
            round_num += 1
            print('-------------------------------------------------------')
            print(f'Round {round_num}: {character.name} ({character.hit_points}/{character.max_hit_points}) vs {monster.name} ({monster.hit_points}/{monster_max_hp})')
            print('-------------------------------------------------------')
            if character.hit_points < 0.5 * character.max_hit_points and character.healing_potions:
                print(f'{len(character.healing_potions)} remaining potions')
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
                    character.treasure(boltac_weapons, boltac_armors)
                    break
            else:  # character attacks first
                monster.hit_points -= character_hp_damage
                if monster.hit_points <= 0:
                    character.victory(monster)
                    character.treasure(boltac_weapons, boltac_armors)
                    break
                character.hit_points -= monster_hp_damage
                if character.hit_points <= 0:
                    break

    if character.hit_points <= 0:
        print(f'{character.name} has been killed by a {monster.name} after {attack_count} attack rounds and {character.monster_kills} monsters kills and reached level #{character.level}')
    else:
        print(f'{character} has killed {character.monster_kills} monsters and reached level #{character.level}')
