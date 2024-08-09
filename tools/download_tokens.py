import os
import requests


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

    # Call the download_image function
    download_image(image_url, save_folder)
