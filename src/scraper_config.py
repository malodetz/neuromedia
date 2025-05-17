import os
from pathlib import Path
import logging

from dotenv import load_dotenv

load_dotenv()

# Telegram configuration
chats_to_follow = ["-1001754252633", "me"]
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
FETCH_INTERVAL = 5
SESSION_NAME = "scraper"

# Simple logger setup
logger = logging.getLogger('scraper')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('scraper_logs.txt')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
