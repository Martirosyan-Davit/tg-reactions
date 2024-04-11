import json
from asyncio import Lock
from json.decoder import JSONDecodeError

# Initialize a global lock
file_lock = Lock()

def load_account_info(phone):
    """
    Load account information from a JSON file.
    
    Args:
        phone (str): The phone number to load the account info for.
        
    Returns:
        dict: The account information or None if an error occurred.
    """
    try:
        with open(f'accounts/{phone}.json', 'r') as file:
            return json.load(file)
    except JSONDecodeError as e:
        print(f"Error loading JSON for {phone}: {e}")
        return None
    except FileNotFoundError as e:
        print(f"File not found for {phone}: {e}")
        return None

def load_channel_info():
    with open('sys-channels.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['channels_names_to_react'], data['channel_links_to_subscribe']
