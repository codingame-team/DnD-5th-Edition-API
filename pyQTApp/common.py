import os
import pickle
import sys
from typing import List

from dao_classes import Character


def debug(*args):
    # return
    print(*args, file=sys.stderr, flush=True)


def save_party(party: List[Character]):
    global dialog
    print(f'Sauvegarde groupe d''aventuriers')
    path = os.path.dirname(__file__)
    with open(f'{path}/gameState/party.dmp', 'wb') as f1:
        pickle.dump(party, f1)
    dialog.accept()


def load_party() -> List[Character]:
    print(f'Chargement groupe d''aventuriers')
    path = os.path.dirname(__file__)
    party_file: str = f'{path}/gameState/party.dmp'
    if not os.path.exists(party_file):
        return []
    with open(party_file, 'rb') as f1:
        return pickle.load(f1)


def get_roster()-> List[Character]:
    path = os.path.dirname(__file__)
    party: List[Character] = load_party()
    party_names: List[str] = [char.name for char in party]

    roster: List[str] = os.listdir(f'{path}/gameState/characters')
    # debug(roster)
    roster: List[str] = [filename for filename in roster if os.path.isfile(f'{path}/gameState/characters/{filename}') and filename.split('.')[:-1] not in party_names]
    training_grounds: List[Character] = []
    for character_file in roster:
        with open(f'{path}/gameState/characters/{character_file}', 'rb') as f1:
            char: Character = pickle.load(f1)
            training_grounds.append(char)
    return training_grounds
