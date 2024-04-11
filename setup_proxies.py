import json
import os

# Load proxies from file
with open('proxies.txt', 'r') as file:
    proxy_lines = file.readlines()

proxies = []
for line in proxy_lines:
    parts = line.strip().split(':')
    host = parts[0]  # The host/IP address
    port = parts[1]  # The port
    username = parts[2]  # The username
    password = parts[3]  # The password
    proxies.append([2, host, int(port), True, username, password])

# Path to the accounts folder
accounts_folder = 'accounts/'

# List all json files in the accounts folder
account_files = [f for f in os.listdir(accounts_folder) if f.endswith('.json')]

# Iterate over account files and proxies simultaneously
for account_file, proxy in zip(account_files, proxies):
    try:
        account_path = os.path.join(accounts_folder, account_file)
        
        # Read the existing content of the account json file
        with open(account_path, 'r') as file:
            account_data = json.load(file)
        
        # Update the account data with the proxy settings
        account_data['proxy_settings'] = proxy
        
        # Write the updated account data back to the file
        with open(account_path, 'w') as file:
            json.dump(account_data, file, indent=4)
    except Exception as e:
        continue
print("Updated account files with proxy settings.")
