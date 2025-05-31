import os

from dotenv import load_dotenv

load_dotenv()

# Telegram configuration
chats_to_follow = ["me", "-1001754252633", "-1001513669961", "-1001006869491"]
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
FETCH_INTERVAL = 5
SESSION_NAME = "scraper"

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

PROMETHEUS_PORT = 8000
