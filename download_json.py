from typing import List

import requests

from populate_functions import populate


def download_data(data_type: str, index_name: str, url: str):
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
    with open(f"{data_type}/{index_name}.json", "w") as f:
        f.write(str(data))


if __name__ == '__main__':
    pass
    monsters_names: List[str] = populate(collection_name='monsters', key_name='results')
    boltac_armors: List[str] = populate(collection_name='armors', key_name='equipment', with_url=True)
    boltac_weapons: List[str] = populate(collection_name='weapons', key_name='equipment', with_url=True)
    races = populate(collection_name='races', key_name='results')
    classes: List[str] = populate(collection_name='classes', key_name='results')
    alignments: List[str] = populate(collection_name='alignments', key_name='results')
    for monster in monsters_names:
        download_data(data_type='monsters', index_name=monster, url=f'/api/monsters/{monster}')
    for armor, url in boltac_armors:
        download_data(data_type='armors', index_name=armor, url=url)
    for weapon, url in boltac_weapons:
        download_data(data_type='weapons', index_name=weapon, url=url)
    for race in races:
        download_data(data_type='races', index_name=race, url=f'/api/monsters/{race}')
    for class_name in classes:
        download_data(data_type='classes', index_name=class_name, url=f'/api/monsters/{class_name}')
    for alignment in alignments:
        download_data(data_type='alignments', index_name=alignment, url=f'/api/alignments/{alignment}')
