import os
import pickle

from dao_classes import Character

character_name: str = 'Ghesh. Heskan'

path = os.path.dirname(__file__)
with open(f'{path}/characters/{character_name}.dmp', 'rb') as f1:
    character: Character = pickle.load(f1)

print(character)