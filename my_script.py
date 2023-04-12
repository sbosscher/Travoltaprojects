import os
import random
import requests
import shutil
from io import BytesIO
from PIL import Image, ImageSequence, UnidentifiedImageError
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import sys
sys.stdout.flush()

search_url = "https://api.bing.microsoft.com/v7.0/images/search"
key_vault_url = "https://travoltavault.vault.azure.net/"
keyvault_name = "travoltavault"
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=f"https://travoltavault.vault.azure.net/", credential=credential)

# Retrieve the subscription and container key from Key Vault
secret_value = secret_client.get_secret("BingSearchKeyAPI").value
subscription_key = secret_value

def run(entry):
    
############################################################################################################ STILL IMAGE ##############
    # Define the headers for the request
    headers = {
    "Ocp-Apim-Subscription-Key": subscription_key,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Pragma": "no-cache",
    "Accept": "image",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.example.com/",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site"
    }

    # Define the parameters for the request
    params = {
        "q": entry,
        "count": 1,
        "offset": random.randint(0, 100),
        "mkt": "en-US",
        "safeSearch": "Moderate"
    }

    # Send the request and get the response
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    # Parse the JSON response and get the image URL
    json_response = response.json()
    image_url = json_response["value"][0]["contentUrl"]

    # Download the image
    response = requests.get(image_url, stream=True)
    response.raise_for_status()

    # Save the image to a file
    with open("image.jpg", "wb") as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)


############################################################################################################ GIF IMAGE ############################################################################################################
    # Open the Gif Image from local
    image_path = os.path.join(os.getcwd(), 'static', 'gif_image.gif')
    image2 = Image.open(image_path)
############################################################################################################ MERGE ##############    
    # Open the downloaded image
    image1 = Image.open("image.jpg")

    # Define the size of the still image
    image1_size = (800, 600)

    # Resize the still image to the defined size
    image1 = image1.resize(image1_size)

    # Calculate the size of the gif image
    gif_size = (image1_size[0] // 2, image1_size[1] // 2)

    # Resize the gif image to the calculated size
    gif_frames = []
    for frame in ImageSequence.Iterator(image2):
        gif_frames.append(frame.convert("RGBA").resize(gif_size))
        
    # Create a new image with the same size as the still image
    new_image = Image.new("RGB", image1_size)

    # Paste the still image onto the new image
    new_image.paste(image1, (0, 0))

    # Calculate the position to center the gif image at the bottom of the still image
    gif_position = ((image1_size[0] - gif_size[0]) // 2, image1_size[1] - gif_size[1])

    # Paste the gif image onto the new imagee
    new_frames = []
    for frame in gif_frames:
        new_frame = new_image.copy()
        new_frame.paste(frame, gif_position, frame)
        new_frames.append(new_frame)

    # Save the new image as an animated gif
    new_image.save("new_image.gif", save_all=True, append_images=new_frames[1:], duration=50, loop=0)

    # Save the new image to the static folder
    static_folder = os.path.join(os.getcwd(), "static")
    new_image_path = os.path.join(static_folder, "new_image.gif")
    new_image.save(new_image_path, save_all=True, append_images=new_frames[1:], duration=50, loop=0)

    # Return the new image object
    return new_image