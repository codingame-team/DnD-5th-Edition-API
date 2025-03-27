import os
import pickle
import sys
from typing import List

from PyQt5.QtGui import QPixmap

from dao_classes import Character


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)

def load_welcome() -> QPixmap:
    path = os.path.dirname(__file__)
    image_file: str = f'{path}/images/welcome.png'
    pixmap = QPixmap(image_file)
    return pixmap

