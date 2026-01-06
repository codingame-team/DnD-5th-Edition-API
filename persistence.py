"""
Persistence Module for DnD-5th-Edition-API
Handles character and party save/load operations
"""
import os
import pickle
from typing import List, Optional
from dnd_5e_core import Character


def get_roster(characters_dir: str = "characters") -> List[Character]:
    """
    Load all saved characters from directory.

    Args:
        characters_dir: Directory containing character files

    Returns:
        List of Character objects
    """
    roster: List[Character] = []

    if not os.path.exists(characters_dir):
        os.makedirs(characters_dir)
        return roster

    char_file_list = os.scandir(characters_dir)
    for entry in char_file_list:
        if entry.is_file() and entry.name.endswith(".dmp"):
            try:
                with open(entry, "rb") as f1:
                    roster.append(pickle.load(f1))
            except Exception as e:
                print(f"Error loading {entry.name}: {e}")

    return roster


def save_character(char: Character, directory: str = "characters") -> bool:
    """
    Save character to disk.

    Args:
        char: Character object to save
        directory: Directory to save to

    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        filename = os.path.join(directory, f"{char.name}.dmp")
        with open(filename, "wb") as f:
            pickle.dump(char, f)
        return True
    except Exception as e:
        print(f"Error saving character {char.name}: {e}")
        return False


def load_character(name: str, directory: str = "characters") -> Optional[Character]:
    """
    Load a specific character from disk.

    Args:
        name: Character name
        directory: Directory to load from

    Returns:
        Character object or None if not found
    """
    try:
        filename = os.path.join(directory, f"{name}.dmp")
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Error loading character {name}: {e}")

    return None


def save_party(party: List[Character], filename: str = "party.pkl") -> bool:
    """
    Save party to disk.

    Args:
        party: List of Character objects
        filename: Filename to save to

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, "wb") as f:
            pickle.dump(party, f)
        return True
    except Exception as e:
        print(f"Error saving party: {e}")
        return False


def load_party(filename: str = "party.pkl") -> Optional[List[Character]]:
    """
    Load party from disk.

    Args:
        filename: Filename to load from

    Returns:
        List of Character objects or None if not found
    """
    try:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Error loading party: {e}")

    return None


def delete_character(name: str, directory: str = "characters") -> bool:
    """
    Delete a character file.

    Args:
        name: Character name
        directory: Directory containing character files

    Returns:
        True if successful, False otherwise
    """
    try:
        filename = os.path.join(directory, f"{name}.dmp")
        if os.path.exists(filename):
            os.remove(filename)
            return True
    except Exception as e:
        print(f"Error deleting character {name}: {e}")

    return False


__all__ = [
    'get_roster',
    'save_character',
    'load_character',
    'save_party',
    'load_party',
    'delete_character',
]

