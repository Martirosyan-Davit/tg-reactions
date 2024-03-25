from telethon import TelegramClient, errors
from telethon.errors import ChannelPrivateError
from logger import logger
from json_helpers import load_account_info
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
import asyncio
import random

async def subscribe_to_channels(api_id, api_hash, phone_number, channel_links, max_retries=3):
    """
    Subscribe to a list of channels for a Telegram account.

    Args:
        api_id (int): The API ID for the Telegram account.
        api_hash (str): The API hash for the Telegram account.
        phone_number (str): The phone number associated with the Telegram account.
        channel_links (list): A list of channel links to subscribe to.
        max_retries (int, optional): Maximum number of retries in case of failures. Defaults to 3.
    """
    print(f"Started subscribing account with phone number: {phone_number} to channels")
    random.shuffle(channel_links)
    retries = 0
    while retries < max_retries:
        try:
            session_file_path = f'accounts/{phone_number.replace("+", "")}.session'
            account_info = load_account_info(phone_number)
            proxy_settings = None
            if account_info and 'proxy_settings' in account_info:
                proxy = account_info['proxy_settings']
                try:
                    proxy_settings = {
                        'proxy_type': 'socks5',
                        'addr': proxy[1],
                        'port': int(proxy[2]),
                        'username': proxy[4],
                        'password': proxy[5],
                        'rdns': True
                    }
                except Exception as e:
                    print(f"Skipping account {phone_number} as proxy is not valid.")
            else:
                print(f"Skipping account {phone_number} as proxy not found...")
            async with TelegramClient(session_file_path, api_id, api_hash, proxy=proxy_settings) as client:
                await client.start(phone_number)
                for channel in channel_links:
                    try:
                        if channel.startswith('https://t.me/+'):
                            # Join private channel using invitation link
                            invite_hash = channel.split('/+')[-1]
                            try:
                                await client(ImportChatInviteRequest(invite_hash))
                            except errors.UserAlreadyParticipantError:
                                continue
                        else:
                            # Join public channel using username
                            await client(JoinChannelRequest(channel))
                    except errors.FloodWaitError as e:
                        logger.warning(f"Rate limit exceeded. Sleeping for {e.seconds} seconds.")
                        await asyncio.sleep(e.seconds)
                    except ChannelPrivateError:
                        logger.info(f"Skipping private channel or no access: {channel}")
                    except Exception as e:
                        logger.warning(f"Error subscribing to channel {channel} phone: {phone_number}: {e}")
                        print(f"Error subscribing to channel {channel} phone: {phone_number}: {e}")
            logger.info(f"Account {phone_number} successfully subscribed to channels")
            return  # Successfully subscribed to channels
        except Exception as e:
            logger.warning(f"Error subscribing account {phone_number} to channels: {e}")
            retries += 1
            logger.info(f"Retrying subscribing account {phone_number} to channels (attempt {retries}/{max_retries})")
    logger.error(f"Failed to subscribe account {phone_number} to channels after {max_retries} retries")

async def perform_actions(account_credentials, channel_links):
    """
    Subscribe multiple Telegram accounts to channels concurrently.

    Args:
        account_credentials (list): A list of tuples containing credentials for Telegram accounts.
            Each tuple should contain (api_id, api_hash, phone_number).
        channel_links (list): A list of channel links to subscribe to.
    """
    tasks = [subscribe_to_channels(*creds, channel_links) for creds in account_credentials]
    await asyncio.gather(*tasks)
