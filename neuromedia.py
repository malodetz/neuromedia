from prometheus_client import start_http_server

from src.config import DB_NAME, DB_PASSWORD, DB_USER, PROMETHEUS_PORT
from src.core import Core
from src.db import PostgreStorage
from src.ml_client import MLClient
from src.scraper import get_scraper

if __name__ == "__main__":
    start_http_server(PROMETHEUS_PORT)

    storage = PostgreStorage(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    ml_client = MLClient(db=storage)
    core = Core(db=storage, ml_client=ml_client)
    scraper = get_scraper(core=core)
