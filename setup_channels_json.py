import re
import json

def is_valid_link(link):
    """Validate if a link is a valid Telegram link or channel name."""
    return link.startswith('https://t.me/') or link.startswith('@')

def validate_reactions(reactions_str):
    """Validate the reactions format: 'min-max: emoji1,emoji2,...: minutes'"""
    reaction_pattern = r'^(\d+)-(\d+): (.+): (\d+)$'
    match = re.match(reaction_pattern, reactions_str)
    if not match:
        return False, "Invalid reactions format. Expected 'min-max: emoji1,emoji2,...: minutes'"
    react_min, react_max, emojis_str, minutes_to_process = match.groups()
    if int(react_min) > int(react_max):
        return False, "Minimum reactions should not exceed maximum reactions."
    emojis = [emoji.strip() for emoji in emojis_str.split(',')]
    if not all(emojis):
        return False, "Empty emoji found."
    return True, {"react_min": int(react_min), "react_max": int(react_max), "emojis": emojis, "minutes_to_process": int(minutes_to_process)}

def parse_txt_to_json(filepath):
    channels = {}
    valid_links = []
    section = None
    errors = []

    with open(filepath, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if line == '[Channels]':
                section = 'channels'
            elif line == '[Links]':
                section = 'links'
            elif section == 'channels' and line:
                parts = line.split(': ', 1)
                if len(parts) != 2:
                    errors.append(f"Line {line_number}: Invalid channel format.")
                    continue
                channel_name, reactions_str = parts
                valid, reactions = validate_reactions(reactions_str)
                if not valid:
                    errors.append(f"Line {line_number}: {reactions}")
                    continue
                channels[channel_name] = reactions
            elif section == 'links' and line:
                if not is_valid_link(line):
                    errors.append(f"Line {line_number}: Invalid link: {line}")
                    continue
                valid_links.append(line)

    return {"channels_names_to_react": channels, "channel_links_to_subscribe": valid_links}, errors

def create_json_file(data, filename='sys-channels.json'):
    """Writes data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

async def setup_channels():
    filepath = 'channels-config.txt'  # Update this with the path to your TXT file
    json_data, errors = parse_txt_to_json(filepath)

    if not errors and json_data["channels_names_to_react"] and json_data["channel_links_to_subscribe"]:
        create_json_file(json_data)
        print("sys-channels.json has been successfully created with validated data.")
    else:
        print("Validation failed. Issues found:")
        for error in errors:
            print(error)
        print("sys-channels.json was not created.")
