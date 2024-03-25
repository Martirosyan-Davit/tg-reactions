import asyncio
import os
import time
from actions.react_actions import perform_actions
from json_helpers import load_account_info, load_channel_info
import random
from tiny_db.database import db

async def assign_and_react():
    session_files = [f[:-5] for f in os.listdir('accounts') if f.endswith('.json')]
    random.shuffle(session_files)
    batch_size = 10
    channels_info, _ = load_channel_info()

    for i in range(0, len(session_files), batch_size):
        batch = session_files[i:i + batch_size]
        account_batches = []

        for phone in batch:
            account_info = load_account_info(phone)
            if account_info:
                account_channels = {name: details for name, details in channels_info.items()}
                if account_channels:
                    account_batches.append((account_info['app_id'], account_info['app_hash'], phone, account_channels))
        
        if account_batches:
            await perform_actions(account_batches)

async def main():
    while True:
        db.truncate()
        await assign_and_react()
        print("Waiting for 1 minute before the next run...")
        time.sleep(60)  # Wait for 1 minute before the next run

if __name__ == '__main__':
    asyncio.run(main())
