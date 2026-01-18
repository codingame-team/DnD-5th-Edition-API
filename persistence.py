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


def save_character(char: Character, directory: str = "characters", _dir: str = None) -> bool:
    """
    Save character to disk.

    Args:
        char: Character object to save
        directory: Directory to save to
        _dir: Alias for directory (for compatibility)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Support old API with _dir parameter
        save_dir = _dir if _dir is not None else directory

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        filename = os.path.join(save_dir, f"{char.name}.dmp")
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


def save_party(party: List[Character], filename: str = "party.pkl", _dir: str = None) -> bool:
    """
    Save party to disk.

    Args:
        party: List of Character objects
        filename: Filename to save to (used if _dir is None)
        _dir: Directory to save to (if provided, saves to _dir/party.dmp)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Support old API with _dir parameter
        if _dir is not None:
            filepath = os.path.join(_dir, "party.dmp")
        else:
            filepath = filename

        with open(filepath, "wb") as f:
            pickle.dump(party, f)
        return True
    except Exception as e:
        print(f"Error saving party: {e}")
        return False


def load_party(filename: str = "party.pkl", _dir: str = None) -> Optional[List[Character]]:
    """
    Load party from disk.

    Args:
        filename: Filename to load from (used if _dir is None)
        _dir: Directory to load from (if provided, loads from _dir/party.dmp)

    Returns:
        List of Character objects or empty list if not found
    """
    try:
        # Support old API with _dir parameter
        if _dir is not None:
            filepath = os.path.join(_dir, "party.dmp")
        else:
            filepath = filename

        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        print(f"Error loading party: {e}")

    return []  # Return empty list instead of None

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

