import json
import os
from typing import List

import requests


def download_data_old(data_type: str, index_name: str, url: str):
    """
    Downloads a DnD type's characteristic to a local .json file
    :param data_type: data's type (monsters, armors, weapons, classes, races)
    :param index_name: name of the data
    :return:
    """
    """
    :param index_name: name of the data belonging to a 
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co{url}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"data/{data_type}/{index_name}.json", "w") as f:
        f.write(str(data))


def populate_base_api() -> List[str]:
    """
    :return: list of all collection names
    """
    with open(f"base_api.json", "r") as f:
        data = json.loads(f.read())
    return data

def populate_api(index_name: str) -> List[str]:
    """
    :return: list of item names
    """
    with open(f"collections/{index_name}.json", "r") as f:
        data = json.loads(f.read())
    return data['results']

def download_collection(index_name: str, url: str):
    """
    Downloads a DnD type's characteristic to a local .json file
    :param data_type: data's type (monsters, armors, weapons, classes, races)
    :param index_name: name of the data
    :return:
    """
    """
    :param index_name: name of the data belonging to a 
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co{url}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"collections/{index_name}.json", "w") as f:
        f.write(str(data))

def download_data(api_name: str, index_name: str, url: str):
    """
    Downloads a DnD type's characteristic to a local .json file
    :param data_type: data's type (monsters, armors, weapons, classes, races)
    :param index_name: name of the data
    :return:
    """
    """
    :param index_name: name of the data belonging to a 
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co{url}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"data/{api_name}/{index_name}.json", "w") as f:
        f.write(str(data))

if __name__ == '__main__':
    # monsters_names: List[str] = populate(collection_name='monsters', key_name='results')
    # boltac_armors: List[str] = populate(collection_name='armors', key_name='equipment', with_url=True)
    # boltac_weapons: List[str] = populate(collection_name='weapons', key_name='equipment', with_url=True)
    # races = populate(collection_name='races', key_name='results')
    # classes: List[str] = populate(collection_name='classes', key_name='results')
    # alignments: List[str] = populate(collection_name='alignments', key_name='results')
    # subraces: List[str] = populate(collection_name='subraces', key_name='results')
    # proficiencies: List[str] = populate(collection_name='proficiencies', key_name='results')
    api_dict: dict() = populate_base_api()

    # for monster in monsters_names:
    #     download_data(data_type='monsters', index_name=monster, url=f'/api/monsters/{monster}')
    # for armor, url in boltac_armors:
    #     download_data(data_type='armors', index_name=armor, url=url)
    # for weapon, url in boltac_weapons:
    #     download_data(data_type='weapons', index_name=weapon, url=url)
    # for race in races:
    #     download_data(data_type='races', index_name=race, url=f'/api/monsters/{race}')
    # for class_name in classes:
    #     download_data(data_type='classes', index_name=class_name, url=f'/api/monsters/{class_name}')
    # for alignment in alignments:
    #     download_data(data_type='alignments', index_name=alignment, url=f'/api/alignments/{alignment}')
    # for subrace in subraces:
    #     download_data(data_type='subraces', index_name=subrace, url=f'/api/subraces/{subrace}')
    # for proficiency in proficiencies:
    #     download_data(data_type='proficiencies', index_name=proficiency, url=f'/api/proficiencies/{proficiency}')
    # for api_name, url in api_dict.items():
    #     download_collection(index_name=api_name, url=url)
    for api_name, url in api_dict.items():
        if not os.path.exists(f'data/{api_name}'):
            os.mkdir(f'data/{api_name}/')
        items_list = populate_api(api_name)
        print(f'processing {api_name}...')
        for item in items_list:
            new_api_name, new_url = item['index'], item['url']
            download_data(api_name, new_api_name, new_url)

