import json
import os

def parse_dungeon_json(json_filename: str = 'dungeon.json') -> dict:
    # json_filename = 'The Shrine of Awesome Necromancy 01.json'
    # json_filename = 'The Chambers of Profane Ruin 01.json'
    # json_filename = 'dungeon.json'
    # json_filename =  json_filename.replace(" ", "\\ ")
    abs_path = os.path.abspath(os.path.dirname(__file__))
    abs_project_path = os.path.abspath(os.path.join(abs_path, os.pardir))
    json_pathname = os.path.join(abs_project_path, 'maze', json_filename)
    # print(json_pathname)

    if os.path.exists(json_pathname):
        # print(f'Found {json_pathname}')
        with open(json_pathname, 'r') as file:
            data = json.load(file)
            return data

if __name__ == "__main__":
    dungeon = parse_dungeon_json()
    print(dungeon)
