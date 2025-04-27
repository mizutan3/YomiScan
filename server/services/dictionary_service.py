import os
import re
import json
import base64
import numpy as np
import cv2
from typing import List, Dict, Set
from fugashi import Tagger
import MeCab
from ..conjugation_rules import CONJUGATION_PATTERNS
from .config_service import load_config, save_config
from ..constants import DICTIONARY_BASE_PATH, USER_DATA_DIR, dictionary_map, active_dictionaries, dictionary_order

# Initialize MeCab
mecab = MeCab.Tagger("-Owakati")
tagger = Tagger('-Owakati')

def process_structured_content(structured_content) -> Dict:
    """Process structured content to extract text only."""
    extracted_text = []

    if isinstance(structured_content, list):
        for item in structured_content:
            if isinstance(item, str):
                extracted_text.append(item.strip())
            elif isinstance(item, dict):
                if "type" in item and item["type"] == "structured-content":
                    for content in item["content"]:
                        if isinstance(content, str):
                            extracted_text.append(content.strip())

    return {
        "text": "\n".join(extracted_text).strip()
    }

def load_dictionary(dict_name: str, device_id: str) -> bool:
    """Improved dictionary loading with per-device memory isolation"""
    dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
    if not os.path.exists(dict_path):
        return False

    index_path = os.path.join(dict_path, 'index.json')
    if not os.path.exists(index_path):
        return False

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
            if not isinstance(index_data, dict):
                return False
    except:
        return False

    term_bank_files = []
    for root, _, files in os.walk(dict_path):
        for file in files:
            if file.startswith("term_bank_") and file.endswith(".json"):
                term_bank_files.append(os.path.join(root, file))
    if not term_bank_files:
        return False

    term_bank_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

    if device_id not in dictionary_map:
        dictionary_map[device_id] = {}

    loaded_entries = 0
    for file_path in term_bank_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    continue

                for entry in data:
                    if isinstance(entry, list) and len(entry) > 5:
                        key = entry[0]
                        reading = entry[1]
                        structured_content = entry[5]

                        content_data = process_structured_content(structured_content)
                        content_data["dict"] = dict_name

                        if key not in dictionary_map[device_id]:
                            dictionary_map[device_id][key] = {}
                        if reading not in dictionary_map[device_id][key]:
                            dictionary_map[device_id][key][reading] = []
                        dictionary_map[device_id][key][reading].append(content_data)
                        loaded_entries += 1
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            continue

    return loaded_entries > 0

def unload_dictionary(dict_name: str, device_id: str) -> bool:
    global active_dictionaries
    print(f"Trying to unload {dict_name} for device {device_id}")
    load_config(device_id)

    if dict_name not in active_dictionaries:
        print(f"❌ {dict_name} not in active_dictionaries: {list(active_dictionaries)}")
        return False

    found_any = False
    device_dict = dictionary_map.get(device_id, {})

    for word in list(device_dict.keys()):
        for reading in list(device_dict[word].keys()):
            original_len = len(device_dict[word][reading])
            device_dict[word][reading] = [
                entry for entry in device_dict[word][reading]
                if entry.get("dict") != dict_name
            ]
            if len(device_dict[word][reading]) < original_len:
                found_any = True

            if not device_dict[word][reading]:
                del device_dict[word][reading]

        if not device_dict[word]:
            del device_dict[word]

    active_dictionaries.remove(dict_name)
    save_config(device_id, dictionary_order, active_dictionaries)

    print(f"Unloaded {dict_name} from dictionary_map[{device_id}]") if found_any else print(
        f"Nothing to unload for {dict_name} on device {device_id}")
    return True

def initialize_dictionaries(device_id: str):
    """Load user-specific dictionaries based on their config"""
    global dictionary_order, active_dictionaries, dictionary_map

    print(f"Initializing dictionaries for device: {device_id}")

    if device_id not in dictionary_map:
        dictionary_map[device_id] = {}

    load_config(device_id)

    available = [d['name'] for d in get_available_dictionaries()]

    # Якщо словники ще не в пам'яті (сервер тільки запустився)
    if not dictionary_map[device_id]:
        print("Server restarted — restoring dictionaries from config")

        for dict_name in dictionary_order:
            if dict_name in available and dict_name in active_dictionaries:
                success = load_dictionary(dict_name, device_id)
                if not success:
                    print(f"⚠Warning: failed to load {dict_name}")

        save_config(device_id, dictionary_order, active_dictionaries)
        return

    # Нормальна ініціалізація
    if not dictionary_order and not active_dictionaries:
        print("First time setup — enabling all available dictionaries")

        dictionary_order = available.copy()
        active_dictionaries = set()

        for dict_name in available:
            load_dictionary(dict_name, device_id)

        save_config(device_id, dictionary_order, active_dictionaries)
        return

    for dict_name in dictionary_order:
        if dict_name in active_dictionaries and dict_name in available:
            load_dictionary(dict_name, device_id)

    save_config(device_id)

def get_available_dictionaries() -> List[Dict]:
    """List all available dictionaries (both loaded and unloaded)"""
    available = []
    if not os.path.exists(DICTIONARY_BASE_PATH):
        return available

    for item in os.listdir(DICTIONARY_BASE_PATH):
        if os.path.isdir(os.path.join(DICTIONARY_BASE_PATH, item)):
            available.append({
                "name": item,
                "loaded": item in active_dictionaries
            })
    return available

def get_dictionary_form(word: str, device_id: str) -> str:
    if not word:
        return word

    device_dict = dictionary_map.get(device_id, {})

    if word in device_dict:
        return word

    try:
        analyzed = tagger.parseToNodeList(word)
        if analyzed:
            lemma = analyzed[0].feature.lemma
            if lemma and lemma != "*" and lemma in device_dict:
                return lemma
    except Exception as e:
        print(f"Error in lemma analysis: {e}")

    for pattern, replacements in CONJUGATION_PATTERNS.items():
        for replacement in replacements:
            base = re.sub(pattern, replacement, word)
            if base in device_dict:
                return base

    return word

def segment_words(text: str) -> List[str]:
    """Segment Japanese text into words using MeCab."""
    if not text.strip():
        return []

    words = mecab.parse(text).strip().split()
    return [w for w in words if w.strip()]
