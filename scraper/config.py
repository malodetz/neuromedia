import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

chats_to_follow = ["-1001215996279", "me"]
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
client_name = "scraper"