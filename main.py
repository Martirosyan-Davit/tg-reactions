import subprocess
import time

def run_script():
    # Adjust the command if necessary, e.g., if you need to specify the full path to `python` or to your script
    command = ['python', 'start_reacting.py']
    while True:
        print("Starting the main script...")
        # Run your main script as a subprocess
        subprocess.run(command)

        print("Main script finished. Waiting for 1 minute before restarting...")
        # Wait for 60 seconds before restarting the script
        time.sleep(60)

if __name__ == '__main__':
    run_script()
