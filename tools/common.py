""" Needs to separate presentation layer from data layer """
import math
from enum import Enum
from pathlib import Path
from random import randint, choice
from time import time
import numpy as np
# from tools.dungeon_perl import create_dungeon
from tools import cell_bits_dnd as cb
from tools.parse_json_dungeon import parse_dungeon_json
import sys
import os
import termios
import tty
import select

# Dimensions de la fenêtre du menu principal
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 300

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

UNIT_SIZE = 5
MAX_LEVELS = 20

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class AbilityType(Enum):
    STR = 'str'
    CON = 'con'
    DEX = 'dex'
    INT = 'int'
    WIS = 'wis'
    CHA = 'cha'

from typing import List

def read(choice_list: List[str], message: str = None) -> str:
    """
    Prompts the user to enter a choice from a given list of choices.

    Args:
        choice_list (List[str]): A list of valid choices.
        message (str, optional): A message to display before prompting for input.

    Returns:
        str: The user's choice from the provided list.

    Raises:
        ValueError: If the user enters an invalid choice.
    """
    while True:
        if message:
            print(message)

        user_input = input("Enter your choice: ")

        if user_input in choice_list:
            return user_input

        print(f"Invalid choice! Please enter one of the following: {', '.join(choice_list)}")


def resource_path_old(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def resource_path(relative_path):
    """ Get the absolute path to a resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled executable
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running in development environment
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Navigate up to the project root (assuming this file is in a subdirectory)
        project_root = os.path.dirname(current_dir)

        # Join the project root with the relative path
        return os.path.join(project_root, relative_path)

# nicola: Dans Linusque, tu peux utiliser f'{Path.home()}/.config/{folder_name}'.
def get_save_game_path(folder_name="Saved_Games_DnD_5th"):
    """
    Retourne le chemin d'un dossier pour sauvegarder les jeux en cours en fonction du système d'exploitation.

    :param folder_name: Nom du sous-dossier pour les sauvegardes (optionnel).
    :return: Chemin absolu du dossier de sauvegarde.
    """
    # Récupère le dossier utilisateur en fonction du système d'exploitation
    if os.name == 'nt':  # Système Windows
        save_path = f'{Path.home()}/Documents/{folder_name}'
    elif os.name == 'posix':  # Systèmes Unix-like (Linux, macOS)
        save_path = f'{Path.home()}/{folder_name}'
    else:
        raise OSError("Système d'exploitation non supporté")

    return save_path

def is_tty():
    return sys.stdin.isatty()

def get_key():
    return get_key_tty()
    # if is_tty():
    #     return get_key_tty()
    # else:
    #     return get_key_non_tty()

def get_key_tty():
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        while True:
            if select.select([sys.stdin], [], [], 0)[0]:
                b = os.read(sys.stdin.fileno(), 3).decode()
                if len(b) > 1:
                    k = ord(b[1])
                else:
                    k = ord(b)
                key_mapping = {
                    127: 'backspace',
                    10: 'return',
                    32: 'space',
                    9: 'tab',
                    27: 'esc',
                    65: 'up',
                    # Add more mappings as needed
                }
                return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def get_key_non_tty():
    return input("Enter key: ")

def cprint(message: str, color: Color = None):
    if color:
        print(f'{color}{message}{Color.END}', flush=True)
    else:
        print(message, flush=True)



def exit_message_old(message: str = None):
    if message:
        print(message)
    print('[Return] to continue')
    while True:
        k = get_key()
        if k == 'return':
            break


def exit_message(message: str = None):
    """
    Display a message and wait for user to press Return/Enter to continue.

    Args:
        message (str, optional): Message to display before the prompt
    """
    if message:
        print(message)
    print('[Return] to continue')

    try:
        # Try to use get_key() for better control
        while True:
            try:
                k = get_key()
                # Check for both 'return' and '\r' as different systems might return different values
                if k and k.lower() in ('return', '\r', '\n', '\r\n'):
                    break
            except (OSError, IOError, AttributeError, TypeError) as e:
                # If get_key() fails (ioctl error, etc.), fall back to simple input()
                if "ioctl" in str(e).lower() or "Inappropriate" in str(e):
                    input()  # Simple fallback
                    break
                else:
                    # For other errors, try input() as fallback
                    input()
                    break
            except KeyboardInterrupt:
                print("\nExiting...")
                break
    except Exception as e:
        # Final fallback - just use input()
        try:
            input()
        except:
            pass  # If even input() fails, just continue
        # Ensure the program doesn't hang even if there's an error
        input("Press Enter to continue...")


# Cave generation algorithm
def generate_cave(width: int, height: int, n_cells: int) -> List[str]:
    """
        Method used to generate levels with shapes of caves (walls only)
    :param width: parameter to adjust to get nice looking caves
    :param height: parameter to adjust to get nice looking caves
    :param n_cells: parameter to adjust to get nice looking caves
    :return:
    """
    maze: List[List[str]] = [['#'] * width for _ in range(height)]
    x, y = randint(1, width - 2), randint(1, height - 2)
    maze[y][x] = '.'
    dirs = [(-1, 0), (1, 0), (0, 1), (0, -1)]
    while n_cells:
        candidates = [(x + dx, y + dy) for dx, dy in dirs if 0 < x + dx < width - 1 and 0 < y + dy < height - 1]
        x, y = choice(candidates)
        if maze[y][x] == '#':
            maze[y][x] = '.'
            n_cells -= 1
    return maze


# Dungeon generation algorithm (First Draft
def create_grid(width, height):
    return np.zeros((height, width), dtype=int)


def place_chambers(grid, grid_width, grid_height, num_chambers, min_size, max_size):
    chambers = []
    for _ in range(num_chambers):
        w, h = randint(min_size, max_size), randint(min_size, max_size)
        x, y = randint(1, grid_width - w - 1), randint(1, grid_height - h - 1)
        chambers.append((x, y, w, h))
        grid[y:y + h, x:x + w] = 1
    return chambers


def add_doors(grid, chambers):
    doors = []
    for (x, y, w, h) in chambers:
        possible_doors = []
        # Check walls on the left and right
        for dy in range(y, y + h):
            if x > 0 and grid[dy, x - 1] == 0:
                possible_doors.append((dy, x - 1))
            if x + w < grid.shape[1] and grid[dy, x + w] == 0:
                possible_doors.append((dy, x + w))
        # Check walls on the top and bottom
        for dx in range(x, x + w):
            if y > 0 and grid[y - 1, dx] == 0:
                possible_doors.append((y - 1, dx))
            if y + h < grid.shape[0] and grid[y + h, dx] == 0:
                possible_doors.append((y + h, dx))
        if possible_doors:
            door_y, door_x = choice(possible_doors)
            grid[door_y, door_x] = 2  # Use '2' to represent doors
            doors.append((door_y, door_x))
    return doors


def connect_chambers(grid, chambers):
    for i in range(len(chambers) - 1):
        x1, y1 = chambers[i][0] + chambers[i][2] // 2, chambers[i][1] + chambers[i][3] // 2
        x2, y2 = chambers[i + 1][0] + chambers[i + 1][2] // 2, chambers[i + 1][1] + chambers[i + 1][3] // 2

        while x1 != x2:
            grid[y1, x1] = 1
            x1 += 1 if x1 < x2 else -1
        while y1 != y2:
            grid[y1, x1] = 1
            y1 += 1 if y1 < y2 else -1

        # Place a door where the corridor meets the next chamber
        if grid[y1, x1] == 1:
            grid[y1 - (1 if y1 > y2 else 0), x1 - (1 if x1 > x2 else 0)] = 2  # Place door in the previous position
        else:
            grid[y1, x1] = 2  # Place door at the current position


def connect_chambers_new(grid, chambers):
    doors = []
    for i in range(len(chambers) - 1):
        x1, y1 = chambers[i][0], chambers[i][1]
        x2, y2 = chambers[i + 1][0], chambers[i + 1][1]
        door_1, door_2 = False, False
        while x1 != x2 or y1 != y2:
            x1_pred, y1_pred = x1, y1
            if x1 != x2:
                x1 += 1 if x1 < x2 else -1
            elif y1 != y2:
                y1 += 1 if y1 < y2 else -1
            if not door_1 and grid[y1, x1] == 0:
                doors.append((y1, x1))
                # grid[y1, x1] = 2
                door_1 = True
            elif not door_2 and grid[y1, x1] == 1:
                doors.append((y1_pred, x1_pred))
                # grid[y1_pred, x1_pred] = 2
                door_2 = True
            else:
                grid[y1, x1] = 1


def generate_dungeon(width: int, height: int, num_chambers: int, chamber_min_size: int, chamber_max_size: int):
    # Create grid
    grid = create_grid(width, height)

    # Place chambers
    chambers = place_chambers(grid, width, height, num_chambers, chamber_min_size, chamber_max_size)

    # Connect chambers
    connect_chambers(grid, chambers)

    # Add doors to chambers
    doors = add_doors(grid, chambers)

    return grid


# Officiel DnD 5th edition dungeon generation algorithm (https://donjon.bin.sh/code/dungeon/)
def generate_dnd_dungeon(options: dict) -> dict:
    dungeon = create_dungeon(options)
    return dungeon

def parse_monster_record(record: str) -> dict:
    pattern = r"(?:(\d+) x )?(\w+)"
    matches = re.findall(pattern, record)

    monsters = {}
    for match in matches:
        if match[1] != 'and':
            monsters[match[1]] = match[0] if match[0] else 1
    return monsters

def parse_challenge_rating(cr_str: str):
    if '/' in cr_str:
        num, denom = map(int, cr_str.split('/'))
        return num / denom
    else:
        return int(cr_str)


if __name__ == '__main__':
    level = 1
    # maze_type = 'cave'
    maze_type = 'dungeon'
    maze_type = 'dnd'
    if maze_type == 'cave':
        min_value, max_value = (level - 4) * 4, (level - 4) * 8
        width, height = randint(min_value, max_value), randint(min_value, max_value)
        n_cells = (width * height) // 3
        maze = generate_cave(width, height, n_cells)
    elif maze_type == 'dungeon':
        min_value, max_value = (level + 1) * 10, (level + 1) * 20
        width, height = randint(min_value, max_value), randint(min_value, max_value)
        num_chambers = int(math.sqrt(width * height)) // 6
        cprint(f'num chambers: {num_chambers}')
        maze = generate_dungeon(width, height, num_chambers, 3, 10)
        # maze = [['.' if cell else '#' for cell in row] for row in maze]
        maze = [['.' if cell == 1 else '#' if cell == 0 else 'D' for cell in row] for row in maze]
        for row in maze:
            print(''.join(row))
    else:
        opts = {
            'seed': time(),
            'n_rows': 39,  # must be an odd number
            'n_cols': 39,  # must be an odd number
            'dungeon_layout': 'None',
            'room_min': 3,  # minimum room size
            'room_max': 9,  # maximum room size
            'room_layout': 'Scattered',  # Packed, Scattered
            'corridor_layout': 'Bent',
            'remove_deadends': 50,  # percentage
            'add_stairs': 2,  # number of stairs
            'map_style': 'Standard',
            'cell_size': 18,  # pixels
        }
        # dungeon = generate_dnd_dungeon(options=opts)
        dungeon = parse_dungeon_json()
        maze = [['.' if cell & cb.OPENSPACE else '#' for cell in row] for row in dungeon['cell']]
        # maze = [['D' if cell & cb.DOORSPACE else '.' if cell & cb.OPENSPACE else '#' for cell in row] for row in dungeon['cell']]
        doors = [(door['col'], door['row']) for door in dungeon['door']]
        # for door in doors:
        #     maze[door[1]][door[0]] = 'D'
        for row in maze:
            print(' '.join(row))
        # visualize_grid(maze)
