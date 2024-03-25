import argparse
import asyncio
from db.database import SessionLocal, TGAccount, init_db
from telethon import TelegramClient

async def validate_telegram_credentials(api_id: str, api_hash: str, phone_number: str, proxy: dict):
    """
    Validate the provided Telegram credentials by attempting to create a client and start a session.

    Args:
        api_id (str): The API ID of the Telegram account.
        api_hash (str): The API hash of the Telegram account.
        phone_number (str): The phone number associated with the Telegram account.
        proxy (dict): The proxy server details.

    Returns:
        bool: True if the credentials are valid and a session is created, False otherwise.
    """
    try:
        async with TelegramClient(phone_number.replace('+', ''), api_id, api_hash, proxy=proxy) as client:
            await client.start(phone_number)
        return True
    except Exception as e:
        print(f"Failed to validate credentials for {phone_number}: {e}")
        return False

def add_account(api_id: str, api_hash: str, phone_number: str, ip: str, port: int, username: str, password: str):
    """
    Add a new Telegram account to the database if the credentials are valid.

    Args:
        api_id (str): The API ID of the Telegram account.
        api_hash (str): The API hash of the Telegram account.
        phone_number (str): The phone number associated with the Telegram account.
        ip (str): The IP address of the proxy server.
        port (int): The port of the proxy server.
        username (str): The username for the proxy server authentication.
        password (str): The password for the proxy server authentication.

    Returns:
        None
    """
    proxy = {
        'proxy_type': 'socks5',  # (mandatory) protocol to use
        'addr': ip,              # (mandatory) proxy IP address
        'port': int(port),            # (mandatory) proxy port number
        'username': username,    # (optional) username if the proxy requires authentication
        'password': password,    # (optional) password if the proxy requires authentication
        'rdns': True             # (optional) whether to use remote or local resolve, default remote
    }
    loop = asyncio.get_event_loop()
    if loop.run_until_complete(validate_telegram_credentials(int(api_id), api_hash, phone_number, proxy)):
        init_db()
        db = SessionLocal()
        new_account = TGAccount(api_id=api_id, api_hash=api_hash, phone_number=phone_number, proxy_credentials=proxy)
        db.add(new_account)
        db.commit()
        db.close()
        print(f"Account with phone number {phone_number} added successfully.")
    else:
        print(f"Account with phone number {phone_number} not added due to invalid credentials or proxy settings.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a new Telegram account to the database.")
    parser.add_argument("api_id", type=str, help="The API ID of the Telegram account.")
    parser.add_argument("api_hash", type=str, help="The API hash of the Telegram account.")
    parser.add_argument("phone_number", type=str, help="The phone number associated with the Telegram account.")
    parser.add_argument("ip", type=str, help="The IP address of the proxy server.")
    parser.add_argument("port", type=int, help="The port of the proxy server.")
    parser.add_argument("username", type=str, help="The username for the proxy server authentication.")
    parser.add_argument("password", type=str, help="The password for the proxy server authentication.")
    args = parser.parse_args()

    add_account(args.api_id, args.api_hash, args.phone_number, args.ip, args.port, args.username, args.password)
