import logging
import os

# Enhanced logger setup with more detailed formatting
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('run.log')
formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
