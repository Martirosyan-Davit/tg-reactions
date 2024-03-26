## Installation

1. **Create a virtual environment:**
   - For macOS/Linux:
     ```sh
     python3 -m venv venv
     source venv/bin/activate
     ```
   - For Windows:
     ```sh
     python -m venv venv
     .\venv\Scripts\activate
     ```

2. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. **Add your Telegram account details:**
   - Create JSON files with your Telegram account details and place them in the `accounts` folder. Each JSON file should contain the account's API ID, API hash, phone number.
   - Add the corresponding `.session` file for each account in the same folder. Ensure that the JSON file name and the `.session` file name match, e.g., `21620723300.json` and `21620723300.session`.

2. **Setup proxies:**
   - Make sure to run the `setup_proxies.py` script to apply proxy settings to your account files.
     ```sh
     python setup_proxies.py
     ```
   - Ensure you have a `proxies.txt` file with proxy details formatted as `host:port:username:password` per line.

3. **React to unread messages:**
   - Run the `main.py` script to start reacting to unread messages in your Telegram channels:
     ```sh
     python main.py
     ```

4. **Join Telegram channels (optional):**
   - Update the `sys-channels.json` file with the names and links of the channels you wish to join.
   - Run the `start_channel_joining.py` script to subscribe your accounts to these channels:
     ```sh
     python start_channel_joining.py
     ```

## Configuration

Modify the script's behavior through variables in `start_reacting.py` such as `batch_size` for processing batch sizes, and `fallback_reactions` for default emoji reactions.

## Logging

Actions and errors are logged to a file in the `logs` folder, providing insights into the script's operation and any issues encountered.

## Project Structure

### `actions/react_actions.py`

Functions for processing Telegram accounts and dialogs, including reacting and marking messages as read.

### `actions/channel_actions.py`

Handles channel subscriptions for Telegram accounts, including joining channels and managing errors.

### `start_channel_joining.py`

Script for subscribing Telegram accounts to channels based on `channels.json`.

### `setup_proxies.py`

Script for applying proxy settings from `proxies.txt` to account JSON files in the `accounts` folder.

### `tiny_db/database.py`

Initializes a TinyDB database (`db.json`) for managing application data, such as reaction records.

### `logger.py`

Configures logging for the application, including file output and log format.

### `main.py`

A wrapper script that schedules and runs start_main.py at specified intervals.

### `start_reacting.py`

The main script that is now executed by main.py to process accounts and react to messages. This script contains the core functionality.

### `sys-channels.json`

Contains channel names and links for interaction.

### `channels-config.txt`

This text file allows for easy configuration of channel names and emojis for reactions. Configure your desired channels and reaction emojis in a simple, line-by-line format for straightforward editing and updating.

### `setup_channels_json.py`

Script responsible for converting the `channels-config.txt` into the `sys-channels.json` format required by the application.

### Updating Channel Configurations

To update your channel reactions and subscriptions:

1. Edit the `channels-config.txt` file with your desired channel names, reaction ranges, and emojis.
2. Run the `main.py` script to validate and transform your configurations into the `sys-channels.json` file.

### `proxies.txt`

Text file with proxy details formatted as `host:port:username:password` per line. Used by `setup_proxies.py` to configure account proxy settings.

This setup ensures a flexible and configurable application for automatically reacting to Telegram messages, by using proxies for account connections and supporting channel subscriptions.