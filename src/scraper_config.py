import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Telegram configuration
chats_to_follow = ["-1001754252633", "me"]
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
FETCH_INTERVAL = 5
SESSION_NAME = "scraper"
