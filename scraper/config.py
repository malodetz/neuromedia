import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

chats_to_follow = ["-1001754252633", "me", "-1002050218130", "-4755682534", "-1002514867149"]
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
FETCH_INTERVAL = 5
SESSION_NAME = "scraper"