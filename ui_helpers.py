"""
UI Helpers Module for DnD-5th-Edition-API
Display and interaction functions for console interfaces
"""
import os
import sys
from typing import List, Optional
from collections import Counter
from dnd_5e_core import Character
from dnd_5e_core.equipment import Armor, Weapon, Equipment
from dnd_5e_core.equipment.potion import HealingPotion, StrengthPotion, SpeedPotion, PotionRarity
from dnd_5e_core.spells import Spell

# Color utilities (assuming color module exists)
try:
    from dao_classes import color, Color
except ImportError:
    # Fallback if color module not available
    class color:
        DARKCYAN = ""
        RED = ""
        GREEN = ""
        PURPLE = ""
        END = ""

    class Color:
        RED = ""
        GREEN = ""
        END = ""


def efface_ecran():
    """Clear the console screen"""
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


def display_character_sheet(char: Character):
    """
    Display character sheet in console format.

    Args:
        char: Character to display
    """
    efface_ecran()

    # Attributes section
    sheet = "+{:-^51}+\n".format(f" {char.name} (age: {char.age // 52} - {char.status})")
    sheet += f"| str: {str(char.abilities.str).rjust(2)} | int: {str(char.abilities.int).rjust(2)} | hp: {str(char.hit_points).rjust(3)} / {str(char.max_hit_points).ljust(4)}| {str(char.class_type.name).upper().ljust(14)}|\n"
    sheet += f"| dex: {str(char.abilities.dex).rjust(2)} | wis: {str(char.abilities.wis).rjust(2)} | xp: {str(char.xp).ljust(10)}| {str(char.race.name).title().ljust(14)}|\n"
    sheet += f"| con: {str(char.abilities.con).rjust(2)} | cha: {str(char.abilities.cha).rjust(2)} | level: {str(char.level).ljust(7)}| AC: {str(char.armor_class).ljust(10)}|\n"
    sheet += "+{:-^51}+\n".format("")

    # Kills section
    if hasattr(char, 'kills'):
        sheet += "|{:^51}|\n".format(f"kills = {len(char.kills)}")

    # Potions section
    if hasattr(char, 'inventory'):
        rarity_types = {
            PotionRarity.COMMON: "C",
            PotionRarity.UNCOMMON: "U",
            PotionRarity.RARE: "R",
            PotionRarity.VERY_RARE: "VR",
        }
        potions = {"C": 0, "U": 0, "R": 0, "VR": 0}
        healing_potions = [item for item in char.inventory if isinstance(item, HealingPotion)]
        for p in healing_potions:
            rarity = rarity_types.get(p.rarity, "C")
            potions[rarity] += 1
        potions = dict(filter(lambda p: p[1] > 0, potions.items()))
        sheet += "|{:^51}|\n".format(f"healing potions = {potions}") if potions else ""

        strength_potions = [item for item in char.inventory if isinstance(item, StrengthPotion)]
        sheet += ("|{:^51}|\n".format(f"strength potions = {len(strength_potions)}") if strength_potions else "")

        speed_potions = [item for item in char.inventory if isinstance(item, SpeedPotion)]
        sheet += ("|{:^51}|\n".format(f"speed potions = {len(speed_potions)}") if speed_potions else "")

        # Equipment section
        char_armors = [item for item in char.inventory if isinstance(item, Armor) and item.equipped]
        char_weapons = [item for item in char.inventory if isinstance(item, Weapon) and item.equipped]
        armors_list = " + ".join([a.name.title() for a in char_armors]) if char_armors else "None"
        sheet += "|{:^51}|\n".format(f"armors in use = {armors_list}")

        if char_weapons:
            for weapon in char_weapons:
                prof_label = '*' if hasattr(char, 'prof_weapons') and not any(
                    weapon.index == w.index for w in char.prof_weapons
                ) else ''
                sheet += "|{:^51}|\n".format(
                    f"weapon in use = {weapon.name.title()}{prof_label} - Damage = {weapon.damage_dice.dice}"
                )
        else:
            sheet += "|{:^51}|\n".format(f"weapon in use = None")

    sheet += "|{:^51}|\n".format(f"gold = {char.gold} gp")
    sheet += "+{:-^51}+\n".format("")

    # Spells section
    if hasattr(char, 'sc') and char.sc:
        slots = "/".join(map(str, char.sc.spell_slots))
        sheet += "|{:^51}|\n".format(f"spell slots: {slots}")
        known_spells = len(char.sc.learned_spells)
        sheet += "|{:^51}|\n".format(f"{known_spells} known spells:")
        learned_spells = [s for s in char.sc.learned_spells]
        learned_spells.sort(key=lambda s: s.level)
        for spell in learned_spells:
            sheet += "|{:^51}|\n".format(str(spell))
        sheet += "+{:-^51}+\n".format("")

    print(sheet)


def display_adventurers(roster: List[Character], party: List[Character], location: str):
    """
    Display list of adventurers with their status.

    Args:
        roster: List of all characters
        party: Current party in dungeon
        location: Current location name
    """
    toc = "{:-^53}\n".format(f" {location} ")
    if party:
        toc += "{:-^53}\n".format(f" ** NOT AVAILABLE (in dungeon) ** ")

    for char in roster:
        if char.in_dungeon:
            char_status = f" ({char.status})" if char.status != "OK" else ""
            toc += "|{:^51}|\n".format(
                f"{char.name}{char_status} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})"
            )

    toc += "{:-^53}\n".format(f" ** AVAILABLE ** ")
    for char in roster:
        if not char.in_dungeon:
            char_status = f" ({char.status})" if char.status != "OK" else ""
            toc += "|{:^51}|\n".format(
                f"{char.name}{char_status} -> {char.hit_points}/{char.max_hit_points}  (Level {char.level})"
            )

    toc += "|{:-^51}|\n".format("")
    print(toc)


def menu_read_options(options: List[str], prompt: str = "Enter your choice: ") -> str:
    """
    Display a menu and read user choice.

    Args:
        options: List of menu options
        prompt: Input prompt text

    Returns:
        User's choice as string
    """
    print("\nOptions:", *[f"\n{i}. {opt}" for i, opt in enumerate(options, 1)])
    return input(f"\n{prompt}")


def delete_character_prompt_ok(char_name: str, stdscr=None, push_panel=None) -> bool:
    """
    Confirme la suppression du personnage, compatible ncurses.
    Affiche le prompt juste au-dessus de la barre de menu si stdscr est fourni.
    """
    prompt = f"Êtes-vous sûr de vouloir supprimer {char_name} ? (Y/N)"
    if stdscr is not None:
        import curses
        lines, cols = stdscr.getmaxyx()
        # Affiche le prompt juste au-dessus de la barre de menu (avant-dernière ligne)
        stdscr.move(lines - 2, 0)
        stdscr.clrtoeol()
        stdscr.addstr(lines - 2, 0, prompt[:cols - 1], curses.A_BOLD)
        stdscr.refresh()
        while True:
            c = stdscr.getch()
            if c in (ord('y'), ord('Y')):
                # Efface le prompt après validation
                stdscr.move(lines - 2, 0)
                stdscr.clrtoeol()
                stdscr.refresh()
                return True
            elif c in (ord('n'), ord('N'), 27):
                # Efface le prompt après annulation
                stdscr.move(lines - 2, 0)
                stdscr.clrtoeol()
                stdscr.refresh()
                return False
    else:
        response = input(f"{color.DARKCYAN}Are you sure you want to delete {char_name}? (Y/N){color.END}").lower()
        return response == 'y'


def rename_character_prompt_ok() -> Optional[str]:
    """
    Prompt for new character name.

    Returns:
        New name or None if cancelled
    """
    new_name = input(f"{color.DARKCYAN}Enter new character name (or leave blank to cancel): {color.END}")
    return new_name if new_name.strip() else None


def adventure_prompt_ok() -> bool:
    """Ask if user wants to continue adventure"""
    return input(
        f"{color.DARKCYAN}Do you want to continue adventure? (Y/N){color.END}"
    ).lower() == 'y'


def location_prompt_ok(location: str) -> bool:
    """Ask if user wants to go to a location"""
    return input(
        f"{color.DARKCYAN}Do you want to go to {location}? (Y/N){color.END}"
    ).lower() == 'y'


def continue_message(message: str) -> bool:
    """
    Display a yes/no prompt.

    Args:
        message: Message to display

    Returns:
        True if user answers yes
    """
    return input(f"{color.DARKCYAN}{message}{color.END}").lower() == 'y'


def exit_message(message: str = "Press Enter to continue..."):
    """Wait for user to press Enter"""
    input(f"{color.PURPLE}{message}{color.END}")


def display_monster_kills(char: Character):
    """
    Display character's monster kills statistics.

    Args:
        char: Character to show kills for
    """
    print(f"\nMonster kills: {len(char.kills) if hasattr(char, 'kills') else 0}")
    if hasattr(char, "kills") and char.kills:
        monsters_count = Counter([m.name for m in char.kills])
        monsters = {m.name: (m.challenge_rating, monsters_count[m.name]) for m in char.kills}
        monsters = dict(sorted(monsters.items(), key=lambda x: x[1], reverse=True))
        for k, (cr, count) in monsters.items():
            print(f"{count} {k} (cr {cr})")


__all__ = [
    'efface_ecran',
    'display_character_sheet',
    'display_adventurers',
    'menu_read_options',
    'delete_character_prompt_ok',
    'rename_character_prompt_ok',
    'adventure_prompt_ok',
    'location_prompt_ok',
    'continue_message',
    'exit_message',
    'display_monster_kills',
]
