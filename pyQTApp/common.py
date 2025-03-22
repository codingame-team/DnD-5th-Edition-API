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

def save_party(party: List[Character]):
    print(f'Sauvegarde groupe d\'aventuriers')
    path = os.path.dirname(__file__)
    with open(f'{path}/../gameState/party.dmp', 'wb') as f1:
        pickle.dump(party, f1)


def load_party() -> List[Character]:
    print(f'Chargement groupe d\'aventuriers')
    path = os.path.dirname(__file__)
    party_file: str = f'{path}/../gameState/party.dmp'
    debug(f'party file = {party_file}')
    if not os.path.exists(party_file):
        return []
    with open(party_file, 'rb') as f1:
        return pickle.load(f1)
