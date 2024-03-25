import os
import json

from asyncio import Lock

# Initialize a global lock
file_lock = Lock()

def load_account_info(phone_number):
    file_path = f'accounts/{phone_number}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return None

def load_channel_info():
    with open('channels.json', 'r') as file:
        data = json.load(file)
    return data['channels_names_to_react'], data['channel_links_to_subscribe']
