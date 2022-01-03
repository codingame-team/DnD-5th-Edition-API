import requests


def download_monster(index_name: str):
    """
    Downloads a monster's characteristic to a local .json file
    :param index_name: name of the monster
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/monsters/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"monsters/{index_name}.json", "w") as f:
        f.write(str(data))


def download_weapon(index_name: str, url: str):
    """
    Downloads a weapon's characteristic to a local .json file
    :param index_name: name of the weapon
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co{url}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"weapons/{index_name}.json", "w") as f:
        f.write(str(data))


def download_armor(index_name: str, url: str):
    """
    Downloads a armors's characteristic to a local .json file
    :param index_name: name of the armors
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co{url}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"data/armors/{index_name}.json", "w") as f:
        f.write(str(data))


def download_race(index_name: str):
    """
    Downloads a race's characteristic to a local .json file
    :param index_name: name of the race
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/races/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"data/races/{index_name}.json", "w") as f:
        f.write(str(data))


def download_class(index_name: str):
    """
    Downloads a class' characteristic to a local .json file
    :param index_name: name of the class
    :return:
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/classes/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    with open(f"data/classes/{index_name}.json", "w") as f:
        f.write(str(data))


if __name__ == '__main__':
    pass
    # monsters_names: List[str] = populate_dungeon()
    # for monster in monsters_names:
    #     download_monster(monster)
    # boltac_armors = populate_boltac_armors()
    # for armor_name, url in boltac_armors:
    #     download_armor(armor_name, url)
    # boltac_weapons = populate_boltac_weapons()
    # for weapon_name, url in boltac_weapons:
    #     download_weapon(weapon_name, url)
    # races = populate_races()
    # for race_name in races:
    #     download_race(race_name)
    # classes = populate_classes()
    # for class_name in classes:
    #     download_class(class_name)
