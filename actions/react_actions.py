import asyncio
import random
import re
from telethon import TelegramClient, errors, functions, types
from telethon.errors import ChannelPrivateError
from logger import logger
from json_helpers import load_account_info
from tinydb import Query
from tiny_db.database import db

async def process_account(api_id, api_hash, phone_number, channels_info, max_retries=3):
    """
    Process actions for a Telegram account.

    Args:
        api_id (int): The API ID for the Telegram account.
        api_hash (str): The API hash for the Telegram account.
        phone_number (str): The phone number associated with the Telegram account.
        channels_info (list): A list of channel names to interact with.
        max_retries (int, optional): Maximum number of retries in case of failures. Defaults to 3.
    """
    retries = 0
    while retries < max_retries:
        try:
            session_file_path = f'accounts/{phone_number.replace("+", "")}.session'
            account_info = load_account_info(phone_number)
            proxy_settings = None
            if account_info and 'proxy_settings' in account_info and account_info['proxy_settings']:
                proxy = account_info['proxy_settings']
                proxy_settings = {
                    'proxy_type': 'socks5',  # (mandatory) protocol to use
                    'addr': proxy[1],              # (mandatory) proxy IP address
                    'port': int(proxy[2]),            # (mandatory) proxy port number
                    'username': proxy[4],    # (optional) username if the proxy requires authentication
                    'password': proxy[5],    # (optional) password if the proxy requires authentication
                    'rdns': True             # (optional) whether to use remote or local resolve, default remote
                }
            else:
                print(f"Skipping account {phone_number} as proxy not found...")
            async with TelegramClient(session_file_path, api_id, api_hash, proxy=proxy_settings) as client:
                await client.start(phone_number)
                dialogs = await client.get_dialogs()
                random.shuffle(dialogs)
                for dialog in dialogs:
                    channel_name = dialog.name
                    react_to_messages = False
                    if channel_name in channels_info:
                        react_to_messages = True
                        emojis = channels_info[channel_name]['emojis']
                    else:
                        emojis = []
                    await process_dialog(client, dialog, emojis, channels_info, react_to_messages)

            return  # Successfully processed the account
        except Exception as e:
            logger.warning(f"Error processing account {phone_number}: {e}")
            retries += 1
            logger.info(f"Retrying processing account {phone_number} (attempt {retries}/{max_retries})")
    logger.error(f"Failed to process account {phone_number} after {max_retries} retries")

async def process_dialog(client, dialog, emojis, channels_info, react_to_messages, max_retries=3):
    """
    Process messages in a Telegram dialog, reacting to unread messages.

    Args:
        client (TelegramClient): The Telegram client instance used for interacting with the API.
        dialog (Dialog): The dialog to process messages from.
        max_retries (int, optional): Maximum number of retries in case of failures. Defaults to 3.

    Returns:
        int: The number of successful reactions.
    """
    retries = 0
    while retries < max_retries:
        try:
            messages = []
            total_unread_count = dialog.unread_count
            offset_id = 0
            while total_unread_count > 0:
                await asyncio.sleep(3) 
                batch = await client.get_messages(dialog.id, limit=min(total_unread_count, 500), offset_id=offset_id)
                if not batch:
                    break
                messages.extend(batch)
                offset_id = batch[-1].id
                total_unread_count -= len(batch)

            unread_message_ids = []
            messages_sent = 0
            random.shuffle(messages)
            channel_name = dialog.name if hasattr(dialog, 'name') else 'default'
            channel_info = channels_info.get(channel_name, {})
            minutes_to_process = channel_info.get('minutes_to_process', 1)  # Default to 3 minutes if not specified
            react_max = channel_info.get('react_max', 1)
            if len(messages) > 0:
                sleep_time = max((minutes_to_process * 60) / (len(messages) * react_max), 3)  # Adjusted sleep time
            else:
                sleep_time = 3
            for message in messages:
                if not message.out:
                    if messages_sent > 99:
                        await asyncio.sleep(10) 
                        messages_sent = 0
                    messages_sent += 1
                    if react_to_messages:
                        success = await react_to_message(client, message, emojis, channels_info, sleep_time)
                    unread_message_ids.append(message.id)
            if unread_message_ids:
                await client.send_read_acknowledge(dialog.id, max_id=max(unread_message_ids))
            return
        except errors.FloodWaitError as e:
            logger.warning(f"Rate limit exceeded. Sleeping for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
            retries += 1
        except ChannelPrivateError:
            logger.info(f"Skipping private channel or no access: {dialog.name}")
            return
        except Exception as e:
            logger.warning(f"Error processing dialog {dialog.id}: {e}")
            retries += 1
            logger.info(f"Retrying processing dialog {dialog.id} (attempt {retries}/{max_retries})")
    logger.error(f"Failed to process dialog {dialog.id} after {max_retries} retries")
    return

async def send_react_to_message_request(client, message, reaction, max_retries=3):
    """
    Send a reaction to a specific message, with retries on failures.
    
    Args:
        client (TelegramClient): The Telegram client instance.
        message (Message): The message object to react to.
        reaction (str): The reaction to be added to the message.
        max_retries (int): Maximum number of retries for sending the reaction.
    """
    retries = 0
    while retries < max_retries:
        try:
            # Check if the reaction is a custom emoji and handle it accordingly
            if isinstance(reaction, types.ReactionCustomEmoji):
                reaction_data = [types.ReactionCustomEmoji(document_id=reaction.document_id)]
            else:
                reaction_data = [types.ReactionEmoji(emoticon=reaction)]
            await client(functions.messages.SendReactionRequest(
                peer=message.chat_id,
                msg_id=message.id,
                reaction=reaction_data 
            ))
            return True  # Reaction sent successfully
        except errors.FloodWaitError as e:
            logger.warning(f"Rate limit exceeded. Sleeping for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
            retries += 1  # Increment the retry counter
        except errors.common.InvalidBufferError as e:
            # Extract the HTTP code from the error message
            match = re.search(r'HTTP code (\d+)', str(e))
            if match and match.group(1) == '429':
                wait_time = 10  # Set a default wait time (in seconds) for rate limiting
                logger.warning(f"Rate limit exceeded. Sleeping for {wait_time} seconds.")
                await asyncio.sleep(wait_time)
                retries += 1  # Increment the retry counter
            else:
                logger.error(f"Unexpected error when sending reaction: {e}")
                return False  # Skip this reaction
        except errors.rpcerrorlist.BadRequestError:
            return False
        except Exception as e:
            logger.exception(f"ERROR to send reaction {e}.")
            return False  # Skip this reaction
    logger.warning(f"Failed to send reaction after {max_retries} retries. Skipping.")
    return False  # Failed to send reaction after retries

async def react_to_message(client, message, emojis, channels_info, sleep_time, max_retries=3):
    """
    Asynchronously attempts to add a reaction to a specific message using a given list of emojis. The function
    ensures that the reaction count does not exceed a pre-defined limit for the channel where the message was posted.
    
    Parameters:
    - client: The Telegram client used to send the reaction.
    - message: The message object to react to. Must contain 'chat' and 'id' attributes.
    - emojis: A list of emoji strings that can be used for reactions.
    - channels_info: A dictionary mapping channel names to their reaction limits. Each entry should
                     contain 'react_min' and 'react_max' keys indicating the minimum and maximum number
                     of reactions allowed.
    - max_retries: The maximum number of attempts to react to a message if initial attempts fail, defaulting to 3.
    
    Returns:
    - True if a reaction was successfully added, False otherwise.
    
    The function maintains a record of reactions in a database to ensure the reaction limits are adhered to.
    If the maximum number of retries is reached or if the message has already received the maximum number of
    reactions allowed, the function will return False.
    """
    channel_name = message.chat.title if hasattr(message.chat, 'title') else 'default'
    message_id_str = f"{channel_name}_{str(message.id)}"  # Create a unique identifier for the message

    MessageQuery = Query()
    message_record = db.search(MessageQuery.message_id == message_id_str)

    # Check if this message_id already has a record
    if not message_record:
        # If not, determine the number of reactions and insert a new record
        react_min, react_max = channels_info.get(channel_name, {}).get('react_min', 1), channels_info.get(channel_name, {}).get('react_max', 1)
        reactions_count = random.randint(react_min, react_max)
        db.insert({'message_id': message_id_str, 'reactions': reactions_count})
    else:
        # If there's a record but no reactions left, return False immediately
        if message_record[0]['reactions'] <= 0:
            return False

    retries = 0
    while retries < max_retries:
        try:
            random.shuffle(emojis)
            await asyncio.sleep(sleep_time)
            for reaction in emojis:
                success = await send_react_to_message_request(client, message, reaction)
                if success:
                    # Decrement the reaction count in the database
                    current_reactions = db.search(MessageQuery.message_id == message_id_str)[0]['reactions']
                    db.update({'reactions': current_reactions - 1}, MessageQuery.message_id == message_id_str)
                    return True
            # If unable to send a reaction, exit the loop
            break
        except errors.FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            retries += 1
        except Exception as e:
            retries += 1

    return False

async def perform_actions(account_batches):
    """
    Asynchronously processes multiple accounts, where each account is configured to react to messages in specific channels
    with predefined emojis. The function distributes the processing load across the accounts, handling each one in parallel.
    
    Parameters:
    - account_batches: A list of tuples, where each tuple represents an account and its configuration.
                       The tuple format is (api_id, api_hash, phone_number, channels_info), where:
                       - api_id and api_hash are credentials for the Telegram API.
                       - phone_number is the account's phone number.
                       - channels_info is a dictionary mapping channel names to their respective reaction configuration,
                         including the emojis to use for reactions in each channel.
    
    Returns:
    - None. The function's primary purpose is to execute side effects (i.e., sending reactions) rather than producing a value.
    
    This function gathers and executes a series of asynchronous tasks, each of which processes an account's
    configuration to perform reactions on messages within specified channels according to the provided emojis.
    """
    tasks = [process_account(api_id, api_hash, phone_number, channels_info) 
             for api_id, api_hash, phone_number, channels_info in account_batches]
    await asyncio.gather(*tasks)