import asyncio
import json
import sys
from actions.react_actions import perform_actions
import os

async def process_batch(file_path):
    # Read the batch data from the file
    with open(file_path, 'r') as file:
        account_batches = json.load(file)

    # Process the batch
    await perform_actions(account_batches)

    # Clean up: Delete the temporary file
    os.remove(file_path)

if __name__ == '__main__':
    batch_file_path = sys.argv[1]
    asyncio.run(process_batch(batch_file_path))
