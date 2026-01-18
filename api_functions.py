import requests

from dao_classes import Monster


# direct api connection not prefered here (use download_json to download json data and json.loads to load data in program memory)
def request_monster_api(index_name: str) -> Monster:
    """
    Send a request to the DnD API for a monster's characteristic
    :param index_name: name of the monster
    :return: Monster object
    """
    # api-endpoint
    url = f"https://www.dnd5eapi.co/api/monsters/{index_name}"
    r = requests.get(url=url)
    # extracting data in json format
    data = r.json()
    return Monster(name=data['name'],
                   armor_class=data['armor_class'],
                   hit_points=data['hit_points'],
                   hit_dice=data['hit_dice'],
                   xp=data['xp'],
                   challenge_rating=data['challenge_rating'])
