import os
import requests
import re
from tqdm import tqdm
from urllib.parse import urlparse

def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    with open(destination, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()

def parse_and_download(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_season = None
        current_episode_number = 1  # Assuming the episode number starts from 1

        for line in lines:
            # Remove leading and trailing whitespaces from the line
            line = line.strip()

            # Skip lines without any content
            if not line:
                continue

            # Using a simple regular expression to find URLs in each line
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)

            # If the line doesn't contain a link, check for season or episode information
            if not urls:
                season_match = re.search(r'^SEZON (\d+)$', line)
                if season_match:
                    current_season = season_match.group(1)
                    print(f"Current Season: {current_season}")
                    
                    # Create a folder for the current season if it doesn't exist
                    season_folder = f"Season_{current_season}"
                    os.makedirs(season_folder, exist_ok=True)

                else:
                    episode_match = re.search(r'^(\d+)$.', line)
                    if episode_match:
                        current_episode_number = int(episode_match.group(1))
                        print(f"Current Episode: {current_episode_number}")

            # If the line contains a link, download the file if it doesn't exist
            else:
                # Extract the file extension from the URL
                parsed_url = urlparse(urls[0])
                file_extension = os.path.splitext(parsed_url.path)[1]

                # Assuming the filename is present in the URL, you can modify this logic based on your needs
                filename = f"episode_{current_episode_number}_SEASON_{current_season}{file_extension}"

                # Check if the file already exists in the season folder
                episode_path = os.path.join(season_folder, filename)
                if os.path.exists(episode_path):
                    print(f"File {filename} already exists. Skipping download.")
                    continue

                print(f"Downloading {filename} from {urls[0]}")
                download_file(urls[0], episode_path)
                print(f"{filename} downloaded successfully.")

                # Increment episode number for the next episode
                current_episode_number += 1

# Replace 'td.txt' with the path to your text document
parse_and_download('td.txt')
