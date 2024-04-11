import asyncio
import os
from actions.channel_actions import perform_actions
from json_helpers import load_account_info, load_channel_info

async def main():
    session_files = [f[:-8] for f in os.listdir('accounts') if f.endswith('.session')]
    batch_size = 200
    _, channel_links = load_channel_info()  # Assuming channel links are the second item in the tuple
    for i in range(0, len(session_files), batch_size):
        batch = session_files[i:i + batch_size]
        account_credentials = []
        for phone in batch:
            try:
                account_info = load_account_info(phone)
                account_credentials.append((account_info['app_id'], account_info['app_hash'], phone))
            except Exception as e:
                print(f"Error loading account info for {phone}: {e}")
                continue
        if account_credentials:
            await perform_actions(account_credentials, channel_links)

if __name__ == '__main__':
    asyncio.run(main())
