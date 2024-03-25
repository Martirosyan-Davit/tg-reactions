import logging
import os
from datetime import datetime
import glob

# Create a logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Get the current timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Set up the log file name with the timestamp
log_file = f'logs/telegram_reactions_{timestamp}.log'

# Set up logging
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get the logger
logger = logging.getLogger(__name__)

# Function to keep only the last 5 logs
def clean_old_logs(directory, pattern, max_logs):
    log_files = sorted(glob.glob(os.path.join(directory, pattern)), key=os.path.getmtime, reverse=True)
    if len(log_files) > max_logs:
        for old_log in log_files[max_logs:]:
            os.remove(old_log)

# Clean old logs
clean_old_logs('logs', 'telegram_reactions_*.log', 5)
