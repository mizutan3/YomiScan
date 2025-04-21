import json
import os
import MeCab
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import pytesseract
import base64
import zipfile
import tempfile
from typing import Dict, List, Set
from werkzeug.utils import secure_filename
import re
import time
import jaconv
from fugashi import Tagger
from gtts import gTTS
from io import BytesIO
import shutil
import magic
from playsound import playsound
from conjugation_rules import CONJUGATION_PATTERNS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    tessdata_dir_config = r'--tessdata-dir "C:\Program Files\Tesseract-OCR\tessdata"'
else:  # Linux (Railway uses Ubuntu)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    # Point to your tessdata directory in the project
    tessdata_dir_config = '--tessdata-dir ./tessdata'

mecab = MeCab.Tagger("-Owakati")
tagger = Tagger('-Owakati')


DICTIONARY_BASE_PATH = os.environ.get("DICTIONARY_PATH", "./dictionaries")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "app_config.json")
os.makedirs(DICTIONARY_BASE_PATH, exist_ok=True)
USER_DATA_DIR = os.environ.get("USER_DATA_PATH", "./user_data")

dictionary_map: Dict[str, Dict[str, List[Dict]]] = {}
active_dictionaries: Set[str] = set()
dictionary_order: List[str] = []

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

def load_config(device_id: str):
    global dictionary_order, active_dictionaries

    safe_device_id = sanitize_filename(device_id)
    config_file = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                dictionary_order = config.get('dictionary_order', [])
                active_dictionaries = set(config.get('active_dictionaries', []))
                print(f"Loaded config for device {safe_device_id}")
        else:
            print(f"No config found for device {safe_device_id}, using defaults")
            dictionary_order = []
            active_dictionaries = set()
    except Exception as e:
        print(f"Error loading config for {safe_device_id}: {str(e)}")
        dictionary_order = []
        active_dictionaries = set()


def save_config(device_id: str, order=None, active=None):
    safe_device_id = sanitize_filename(device_id)
    config_file = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    config = {
        'dictionary_order': order if order is not None else dictionary_order,
        'active_dictionaries': list(active if active is not None else active_dictionaries)
    }

    try:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved config for device {safe_device_id}")
    except Exception as e:
        print(f"❌ Error saving config for {safe_device_id}: {str(e)}")


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


@app.route("/dictionaries/init", methods=["POST"])
def initialize_dictionaries_route():
    data = request.get_json()
    device_id = data.get("device_id")

    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    try:
        initialize_dictionaries(device_id)
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Failed to initialize dictionaries: {str(e)}")
        return jsonify({"error": str(e)}), 500


def initialize_dictionaries(device_id: str):
    """Load user-specific dictionaries based on their config"""
    global dictionary_order, active_dictionaries

    print(f"Initializing dictionaries for device: {device_id}")
    load_config(device_id)

    available = [d['name'] for d in get_available_dictionaries()]

    # Якщо конфіг порожній — перший запуск
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


def unload_dictionary(dict_name: str, device_id: str) -> bool:
    global active_dictionaries
    print(f"🔄 Trying to unload {dict_name} for device {device_id}")
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

    print(f"✅ Unloaded {dict_name} from dictionary_map[{device_id}]") if found_any else print(
        f"⚠️ Nothing to unload for {dict_name} on device {device_id}")
    return True


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


def adjust_gamma(image, gamma=1.0):
    """Gamma correction for brightness adjustment"""
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)


def remove_shadows(image):
    """Remove shadows from an image"""
    if len(image.shape) == 2:  # Grayscale
        rgb_planes = [image]
    else:  # Color
        rgb_planes = cv2.split(image)

    result_planes = []
    for plane in rgb_planes:
        # Estimate background using morphological closing
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        # Subtract background from original
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        result_planes.append(diff_img)

    if len(result_planes) == 1:
        return result_planes[0]
    return cv2.merge(result_planes)


def preprocess_image(image_data: str, fast_mode: bool = False) -> np.ndarray:
    # Start timer for whole processing
    start_time = time.time()

    # Process the image
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if fast_mode:
        # Simplified processing for screenshots
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Original full processing pipeline
        shadow_removed = remove_shadows(img)
        gray = cv2.cvtColor(shadow_removed, cv2.COLOR_BGR2GRAY)
        gamma_corrected = adjust_gamma(gray, gamma=2.0)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gamma_corrected)
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((1, 1), np.uint8)
        binary = cv2.erode(binary, kernel, iterations=1)
        binary = cv2.dilate(binary, kernel, iterations=1)

    # Calculate and print total time
    total_time = time.time() - start_time
    print(f"Total image processing time: {total_time:.4f} seconds (fast mode: {fast_mode})")

    return binary


def segment_words(text: str) -> List[str]:
    """Segment Japanese text into words using MeCab."""
    if not text.strip():
        return []

    words = mecab.parse(text).strip().split()
    return [w for w in words if w.strip()]


@app.route("/ocr", methods=["POST"])
def ocr():
    """Perform OCR on the uploaded image with optional vertical text recognition and cropping."""
    data = request.json
    if "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    # Get the text orientation from the request
    orientation = data.get("orientation", "horizontal")
    fast_mode = data.get("fast_mode", False)
    crop_data = data.get("crop", None)

    # Preprocess image and extract text
    processed_img = preprocess_image(data["image"], fast_mode=fast_mode)

    # Apply cropping if specified
    if crop_data:
        try:
            height, width = processed_img.shape[:2]
            left = int(crop_data["left"] * width)
            top = int(crop_data["top"] * height)
            right = left + int(crop_data["width"] * width)
            bottom = top + int(crop_data["height"] * height)

            # Ensure coordinates are within image bounds
            left = max(0, left)
            top = max(0, top)
            right = min(width, right)
            bottom = min(height, bottom)

            if right > left and bottom > top:  # Only crop if valid dimensions
                processed_img = processed_img[top:bottom, left:right]
        except Exception as e:
            print(f"Error applying crop: {str(e)}")

    # Configure Tesseract based on text orientation
    if orientation == "vertical":
        custom_config = "--psm 5 -c preserve_interword_spaces=1"
        lang = "jpn_vert"
    else:
        custom_config = "--psm 6 -c preserve_interword_spaces=1"
        lang = "jpn"

    extracted_text = pytesseract.image_to_string(
        processed_img,
        lang=lang,
        config=custom_config
    )

    # Process the extracted text to join lines while preserving punctuation-newline cases
    lines = extracted_text.split('\n')
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:  # Skip empty lines
            i += 1
            continue

        # Check if current line ends with punctuation and next line is not empty
        if (i < len(lines) - 1 and
                len(line) > 0 and
                line[-1] in ('。', '、', '！', '？', '…', '」', '』', '》', ')', '）', '.', ',', '!', '?') and
                lines[i + 1].strip()):
            # Keep this line as is and move to next
            processed_lines.append(line)
            i += 1
        else:
            # Join with next lines until we hit punctuation+newline or end
            joined_line = line
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue

                # Check if we should stop joining
                if (len(joined_line) > 0 and
                        joined_line[-1] in ('。', '、', '！', '？', '…', '」', '』', '》', ')', '）', '.', ',', '!', '?')):
                    break

                joined_line += next_line
                i += 1
            processed_lines.append(joined_line)

    # Reconstruct the text with our processed lines
    processed_text = '\n'.join(processed_lines)

    # Segment the processed text into words
    segmented_text = segment_words(processed_text)

    return jsonify({
        "text": processed_text,
        "words": segmented_text
    })


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


@app.route("/synthesize_speech", methods=["POST"])
def synthesise_speech():
    """Synthesize speech from Japanese text"""
    data = request.json
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Create a temporary in-memory file
        tts = gTTS(text=data["text"], lang='ja')

        # Use BytesIO to store the audio in memory
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        # Convert to base64 for sending to frontend
        audio_base64 = base64.b64encode(audio_bytes.read()).decode('utf-8')

        return jsonify({
            "success": True,
            "audio": audio_base64
        })
    except Exception as e:
        return jsonify({
            "error": f"Failed to synthesize speech: {str(e)}"
        }), 500


@app.route("/dictionary", methods=["GET"])
def dictionary():
    """Fetch Japanese definition from local JSON dictionary for a specific device."""
    word = request.args.get("word", "").strip()
    device_id = request.args.get("device_id")

    if not word:
        return jsonify({"error": "No word provided"}), 400
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    safe_device_id = sanitize_filename(device_id)
    config_path = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                dictionary_order = config.get("dictionary_order", [])
                active_dictionaries = set(config.get("active_dictionaries", []))
        else:
            dictionary_order = []
            active_dictionaries = set()
    except Exception as e:
        return jsonify({"error": f"Failed to load user config: {str(e)}"}), 500

    device_dict = dictionary_map.get(device_id, {})
    dict_form = get_dictionary_form(word, device_id)

    all_entries = {}

    def merge_entries(source_word):
        if source_word in device_dict:
            for reading, entries in device_dict[source_word].items():
                if reading not in all_entries:
                    all_entries[reading] = []
                all_entries[reading].extend(entries)

    merge_entries(word)
    if dict_form != word:
        merge_entries(dict_form)

    # Try kana variants if still empty
    if not all_entries:
        hiragana = jaconv.kata2hira(word)
        katakana = jaconv.hira2kata(word)
        if hiragana != word:
            merge_entries(hiragana)
        if katakana != word:
            merge_entries(katakana)

    # Deduplicate results
    results = []
    seen = set()

    for dict_name in dictionary_order:
        if dict_name not in active_dictionaries:
            continue

        for reading, entries in all_entries.items():
            for entry in entries:
                key = (dict_name, reading, entry.get("text"))
                if entry.get("dict") == dict_name and key not in seen:
                    seen.add(key)
                    results.append({
                        "word": word,
                        "reading": reading,
                        "meanings": [entry["text"]],
                        "dictionary": dict_name,
                        "original_form": word if word != dict_form else None,
                        "dictionary_form": dict_form if word != dict_form else None
                    })

    if results:
        return jsonify(results)
    else:
        return jsonify({
            "word": word,
            "meanings": ["Definition not found."]
        })


@app.route("/dictionaries", methods=["GET"])
def list_dictionaries():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    print("Listing dictionaries in:", DICTIONARY_BASE_PATH)

    safe_device_id = sanitize_filename(device_id)
    config_path = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                dictionary_order = config.get("dictionary_order", [])
                active_dictionaries = set(config.get("active_dictionaries", []))
        else:
            dictionary_order = []
            active_dictionaries = set()
    except Exception as e:
        print("❌ Failed to load config:", e)
        dictionary_order = []
        active_dictionaries = set()

    all_dicts = []
    for item in os.listdir(DICTIONARY_BASE_PATH):
        dict_path = os.path.join(DICTIONARY_BASE_PATH, item)
        if os.path.isdir(dict_path):
            term_bank_files = [
                f for f in os.listdir(dict_path)
                if f.startswith("term_bank_") and f.endswith(".json")
            ]
            if term_bank_files:
                all_dicts.append(item)

    result = []

    for dict_name in dictionary_order:
        if dict_name in all_dicts:
            result.append({
                "name": dict_name,
                "loaded": dict_name in active_dictionaries,
                "position": dictionary_order.index(dict_name)
            })
            all_dicts.remove(dict_name)

    for dict_name in all_dicts:
        result.append({
            "name": dict_name,
            "loaded": dict_name in active_dictionaries,
            "position": len(dictionary_order)
        })

    return jsonify(result)



@app.route("/dictionaries/load", methods=["POST"])
def load_dictionary_route():
    data = request.json
    dict_name = data.get("name")
    device_id = data.get("device_id")

    if not dict_name or not device_id:
        return jsonify({"error": "Missing dictionary name or device_id"}), 400

    if not os.path.exists(os.path.join(DICTIONARY_BASE_PATH, dict_name)):
        return jsonify({"error": "Dictionary not found"}), 404

    if load_dictionary(dict_name, device_id):
        # Load existing config
        safe_device_id = sanitize_filename(device_id)
        config_path = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print("❌ Failed to read config for load:", e)

        active = set(config.get("active_dictionaries", []))
        order = config.get("dictionary_order", [])

        active.add(dict_name)
        if dict_name not in order:
            order.append(dict_name)

        config["active_dictionaries"] = list(active)
        config["dictionary_order"] = order

        # Save updated config
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"✅ Saved updated config (load) for {safe_device_id}")
        except Exception as e:
            print("❌ Failed to save config after load:", e)

        return jsonify({"success": True, "order": order})
    else:
        return jsonify({"error": f"Failed to load dictionary: {dict_name}"}), 400


@app.route("/dictionaries/reorder", methods=["POST"])
def reorder_dictionaries():
    """Change the order of dictionaries for a specific device"""
    data = request.get_json()
    new_order = data.get("order")
    device_id = data.get("device_id")

    if not new_order or not device_id:
        return jsonify({
            "success": False,
            "error": "Missing required fields"
        }), 400

    if not isinstance(new_order, list):
        return jsonify({
            "success": False,
            "error": "'order' must be a list"
        }), 400

    # Validate dictionary existence
    for dict_name in new_order:
        dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
        if not os.path.exists(dict_path):
            return jsonify({
                "success": False,
                "error": f"Dictionary '{dict_name}' not found"
            }), 400

    safe_device_id = sanitize_filename(device_id)
    config_path = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            current_active = set(config.get("active_dictionaries", []))
    except:
        current_active = set()

    global dictionary_order
    dictionary_order = new_order

    save_config(device_id, dictionary_order, current_active)

    print(f"✅ Saved reordered config for {safe_device_id}")
    return jsonify({"success": True})


@app.route("/dictionaries/order", methods=["GET"])
def get_dictionary_order():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    safe_device_id = sanitize_filename(device_id)
    config_path = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return jsonify({
                    "order": config.get("dictionary_order", [])
                })
        else:
            return jsonify({"order": []})
    except Exception as e:
        return jsonify({"error": "Failed to read order"}), 500


@app.route("/dictionaries/unload", methods=["POST"])
def unload_dictionary_route():
    data = request.json
    dict_name = data.get("name")
    device_id = data.get("device_id")

    if not dict_name or not device_id:
        return jsonify({"error": "Missing dictionary name or device_id"}), 400

    if unload_dictionary(dict_name, device_id):
        return jsonify({"success": True})
    else:
        return jsonify({"error": f"Dictionary {dict_name} not loaded"}), 400

@app.route("/dictionary/search", methods=["GET"])
def search_dictionary_words():
    query = request.args.get("query", "").strip()
    device_id = request.args.get("device_id")

    if not query or not device_id:
        return jsonify([])

    config_path = os.path.join(USER_DATA_DIR, f"{sanitize_filename(device_id)}_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                active_dictionaries = set(config.get("active_dictionaries", []))
        else:
            active_dictionaries = set()
    except:
        active_dictionaries = set()

    device_dict = dictionary_map.get(device_id, {})
    if not active_dictionaries or not device_dict:
        return jsonify([])

    is_kana_query = re.fullmatch(r'[\u3040-\u309F\u30A0-\u30FF]+', query) is not None
    exact_word_matches = []
    exact_reading_matches = []
    partial_matches = []

    query_lower = query.lower()
    normalized_form = get_dictionary_form(query, device_id)
    normalized_lower = normalized_form.lower() if normalized_form else None

    for word in device_dict.keys():
        lower_word = word.lower()
        matched = False

        # Exact word match
        if lower_word == query_lower or lower_word == normalized_lower:
            if any(entry["dict"] in active_dictionaries
                   for entries in device_dict[word].values()
                   for entry in entries):
                exact_word_matches.append(word)
                continue

        # Reading match (kana)
        if is_kana_query:
            for reading, entries in device_dict[word].items():
                if query_lower == reading.lower() and any(entry["dict"] in active_dictionaries for entry in entries):
                    exact_reading_matches.append(word)
                    matched = True
                    break
            if matched:
                continue

        # Partial match
        if lower_word.startswith(query_lower) or (normalized_lower and lower_word.startswith(normalized_lower)):
            if any(entry["dict"] in active_dictionaries
                   for entries in device_dict[word].values()
                   for entry in entries):
                partial_matches.append(word)

    seen = set()
    unique_results = []
    for word in exact_word_matches + exact_reading_matches + partial_matches:
        if word not in seen:
            seen.add(word)
            unique_results.append(word)

    return jsonify(unique_results[:50])


def sanitize_filename(name: str) -> str:
    # Залишає тільки літери, цифри, підкреслення і дефіси
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

@app.route("/sync/dictionaries", methods=["GET"])
def get_dictionaries_state():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    safe_device_id = sanitize_filename(device_id)
    config_file = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            return jsonify({
                "dictionaries": config.get("active_dictionaries", []),
                "order": config.get("dictionary_order", [])
            })
    except FileNotFoundError:
        return jsonify({"dictionaries": [], "order": []})

@app.route("/sync/dictionaries", methods=["POST"])
def save_dictionaries_state():
    try:
        data = request.get_json(force=True)
        device_id = data.get("device_id")
        if not device_id:
            return jsonify({"error": "Missing device_id"}), 400

        safe_device_id = sanitize_filename(device_id)

        dictionaries = data.get("dictionaries", [])
        order = data.get("order", [])

        if not isinstance(dictionaries, list) or not isinstance(order, list):
            return jsonify({"error": "Invalid format"}), 400

        config = {
            "dictionary_order": order,
            "active_dictionaries": dictionaries,
        }

        os.makedirs(USER_DATA_DIR, exist_ok=True)
        config_file = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"✅ Saved dictionary config for {safe_device_id}")
        return jsonify({"success": True})
    except Exception as e:
        print("❌ Dictionary sync error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
