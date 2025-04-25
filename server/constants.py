import os
from typing import Dict, List, Set

TEMP_IMAGE_PATH = "./temp_image.jpg"

DICTIONARY_BASE_PATH = os.environ.get("DICTIONARY_PATH", "./dictionaries")
USER_DATA_DIR = os.environ.get("USER_DATA_PATH", "./user_data")

#DICTIONARY_BASE_PATH = os.path.join(os.path.dirname(__file__), "dictionaries")
#USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "user_data")

os.makedirs(DICTIONARY_BASE_PATH, exist_ok=True)
os.makedirs(USER_DATA_DIR, exist_ok=True)

dictionary_map: Dict[str, Dict[str, Dict[str, List[Dict]]]] = {}
active_dictionaries: Set[str] = set()
dictionary_order: List[str] = []
