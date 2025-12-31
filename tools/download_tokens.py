import os
from typing import List
from urllib.parse import quote

import requests

# from dao_classes import Monster
from populate_functions import populate, request_monster


def download_image(url, save_folder, monster_name, filename=None) -> int:
    """
        Download an image from a given URL and save it to the specified folder.
    :param filename:
    :param url:
    :param save_folder:
    :param monster_name:
    :param filename:
    :return: HTTP status code
    """
    # Ensure the save folder exists
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Extract the filename from the URL if not provided
    if not filename:
        filename = os.path.basename(url)

    # Define the full path to save the image
    save_path = os.path.join(save_folder, filename)

    # Send a HTTP request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Write the content to a file
        with open(save_path, 'wb') as file:
            file.write(response.content)
        # print(f"Image successfully downloaded and saved to {save_path}")
    else:
        print(f"{monster_name} -> Failed to download image. HTTP Status code: {response.status_code}")

    return response.status_code


if __name__ == "__main__":
    # Define the image URL
    image_url = "https://5e.tools/img/bestiary/tokens/MM/Cult%20Fanatic.webp"
    missing = "https://5e.tools/img/bestiary/tokens/MPMM/Duergar%20Mind%20Master.webp"
    # Define the folder to save the image
    save_folder = "../images/monsters/tokens"

    monster_names: List[str] = populate(collection_name="monsters", key_name="results")
    monsters: List[Monster] = [request_monster(name) for name in monster_names]
    for m in monsters:
        image_url = f"https://5e.tools/img/bestiary/tokens/MM/{quote(m.name, safe='')}.webp"
        download_image(image_url, save_folder, m.name)
    # # Call the download_image function
    # download_image(image_url, save_folder)

"""
    invalid count option for hydra : Bite
    invalid count option for violet-fungus : Rotting Touch
    Giant Rat (Diseased) -> Failed to download image. HTTP Status code: 404
    Succubus/Incubus -> Failed to download image. HTTP Status code: 404
    Werebear, Bear Form -> Failed to download image. HTTP Status code: 404
    Werebear, Human Form -> Failed to download image. HTTP Status code: 404
    Werebear, Hybrid Form -> Failed to download image. HTTP Status code: 404
    Wereboar, Boar Form -> Failed to download image. HTTP Status code: 404
    Wereboar, Human Form -> Failed to download image. HTTP Status code: 404
    Wereboar, Hybrid Form -> Failed to download image. HTTP Status code: 404
    Wererat, Human Form -> Failed to download image. HTTP Status code: 404
    Wererat, Hybrid Form -> Failed to download image. HTTP Status code: 404
    Wererat, Rat Form -> Failed to download image. HTTP Status code: 404
    Weretiger, Human Form -> Failed to download image. HTTP Status code: 404
    Weretiger, Hybrid Form -> Failed to download image. HTTP Status code: 404
    Weretiger, Tiger Form -> Failed to download image. HTTP Status code: 404
    Werewolf, Human Form -> Failed to download image. HTTP Status code: 404
    Werewolf, Hybrid Form -> Failed to download image. HTTP Status code: 404
    Werewolf, Wolf Form -> Failed to download image. HTTP Status code: 404
"""
