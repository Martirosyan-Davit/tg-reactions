import argparse
from db.database import SessionLocal, TGAccount
from telethon import TelegramClient
import asyncio

async def validate_proxy(api_id: int, api_hash: str, phone_number: str, proxy: dict, max_attempts=3):
    """
    Validate the provided proxy by attempting to create a client and start a session.

    Args:
        api_id (int): The API ID of the Telegram account.
        api_hash (str): The API hash of the Telegram account.
        phone_number (str): The phone number associated with the Telegram account.
        proxy (dict): The proxy server details.
        max_attempts (int): The maximum number of attempts to validate the proxy.

    Returns:
        bool: True if the proxy is valid, False otherwise.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            async with TelegramClient(f'session_{phone_number}', api_id, api_hash, timeout=20, proxy=proxy) as client:
                await client.start(phone_number)
            return True
        except Exception as e:
            print(f"Attempt {attempt}/{max_attempts} failed to validate proxy for {phone_number}: {e}")
    
    print(f"Failed to validate proxy for {phone_number} after {max_attempts} attempts.")
    return False

def update_account(phone_number: str, new_proxy: dict):
    """
    Update the proxy configuration of a Telegram account in the database.

    Args:
        phone_number (str): The phone number of the account to update.
        new_proxy (dict): The new proxy configuration.

    Returns:
        None
    """
    db = SessionLocal()
    account = db.query(TGAccount).filter_by(phone_number=phone_number).first()

    if account:
        loop = asyncio.get_event_loop()
        if loop.run_until_complete(validate_proxy(account.api_id, account.api_hash, phone_number, new_proxy)):
            account.proxy_credentials = new_proxy
            db.commit()
            print(f"Updated proxy for account with phone number {phone_number}.")
        else:
            print(f"Proxy validation failed for {phone_number}.")
    else:
        print(f"No account found with phone number {phone_number}.")

    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the proxy configuration of a Telegram account.")
    parser.add_argument("phone_number", type=str, help="The phone number of the account to update.")
    parser.add_argument("ip", type=str, help="The IP address of the new proxy server.")
    parser.add_argument("port", type=int, help="The port of the new proxy server.")
    parser.add_argument("username", type=str, help="The username for the new proxy server authentication.")
    parser.add_argument("password", type=str, help="The password for the new proxy server authentication.")

    args = parser.parse_args()

    new_proxy = {
        'proxy_type': 'socks5',
        'addr': args.ip,
        'port': args.port,
        'username': args.username,
        'password': args.password
    }

    update_account(args.phone_number, new_proxy)
