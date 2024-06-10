""" Needs to separate presentation layer from data layer """
import os
import pickle
import sys
import termios
import tty
from enum import Enum
from random import randint, choice
from typing import List


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


def cprint(*args):
    # return
    # print(*args, file=sys.stderr, flush=True)
    print(*args, flush=True)


def get_key():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            # if len(b) == 3:
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
                66: 'down',
                67: 'right',
                68: 'left'
            }
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def exit_message(message: str = None):
    if message:
        print(message)
    print('[Return] to continue')
    while True:
        k = get_key()
        if k == 'return':
            break


def generate_maze(width: int, height: int, n_cells: int) -> List[str]:
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


if __name__ == '__main__':
    level = 7
    min_value, max_value = (level - 4) * 4, (level - 4) * 8
    width, height = randint(min_value, max_value), randint(min_value, max_value)
    n_cells = (width * height) // 3
    maze = generate_maze(width, height, n_cells)
    for row in maze:
        print(''.join(row))
