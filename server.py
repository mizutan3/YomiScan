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

def load_config():
    """Load configuration from file including dictionary order and loaded state"""
    global dictionary_order, active_dictionaries

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                dictionary_order = config.get('dictionary_order', [])
                active_dictionaries = set(config.get('active_dictionaries', []))
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        # Reset to defaults if config is corrupted
        dictionary_order = []
        active_dictionaries = set()


def save_config():
    """Save current configuration to file"""
    config = {
        'dictionary_order': dictionary_order,
        'active_dictionaries': list(active_dictionaries)
    }

    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving config: {str(e)}")


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


def load_dictionary(dict_name):
    """Improved dictionary loading with validation and dictionary tracking"""
    dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
    if not os.path.exists(dict_path):
        return False

    # Validate dictionary structure first
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

    # Find all term bank files in the dictionary
    term_bank_files = []
    for root, _, files in os.walk(dict_path):
        for file in files:
            if file.startswith("term_bank_") and file.endswith(".json"):
                term_bank_files.append(os.path.join(root, file))

    if not term_bank_files:
        return False  # Not a valid dictionary

    # Sort files numerically
    term_bank_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))

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
                        content_data["dict"] = dict_name  # Track which dictionary this came from

                        if key not in dictionary_map:
                            dictionary_map[key] = {}
                        if reading not in dictionary_map[key]:
                            dictionary_map[key][reading] = []
                        dictionary_map[key][reading].append(content_data)
                        loaded_entries += 1
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            continue

    if loaded_entries > 0:
        active_dictionaries.add(dict_name)
        save_config()  # Save the updated active dictionaries
        return True
    return False

def initialize_dictionaries():
    """Load initial dictionaries on startup"""
    print("Initializing dictionaries...")
    load_config()  # Load saved configuration
    print(f"📁 Using dictionary base path: {DICTIONARY_BASE_PATH}")

    # Get all available dictionaries
    available = [d['name'] for d in get_available_dictionaries()]

    # If we have a saved order, use that, otherwise initialize with all available
    if not dictionary_order:
        dictionary_order.extend(available)

    # Load dictionaries that were active in the last session
    for dict_name in dictionary_order:
        if dict_name in active_dictionaries:
            load_dictionary(dict_name)

    save_config()  # Ensure config is saved after initialization

def download_default_dictionary():
    """Download dictionary from GitHub if none exists"""
    if not os.path.exists(DICTIONARY_BASE_PATH):
        os.makedirs(DICTIONARY_BASE_PATH)

    jmdict_path = os.path.join(DICTIONARY_BASE_PATH, "JMDict English", "term_bank_1.json")
    if not os.path.exists(jmdict_path):
        print("📦 No dictionary found. Downloading from GitHub...")

        os.makedirs(os.path.dirname(jmdict_path), exist_ok=True)

        import requests
        url = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/dictionaries/JMDict%20English/term_bank_1.json"
        try:
            r = requests.get(url)
            if r.status_code == 200:
                with open(jmdict_path, "w", encoding="utf-8") as f:
                    f.write(r.text)
                print("✅ Dictionary downloaded successfully.")
            else:
                print(f"❌ Failed to download dictionary (status {r.status_code})")
        except Exception as e:
            print("❌ Error downloading dictionary:", e)

def unload_dictionary(dict_name: str) -> bool:
    """Unload a dictionary by removing its entries"""
    if dict_name not in active_dictionaries:
        return False

    # Remove all entries from this dictionary
    for word in list(dictionary_map.keys()):
        for reading in list(dictionary_map[word].keys()):
            # Filter out entries from this dictionary
            dictionary_map[word][reading] = [
                entry for entry in dictionary_map[word][reading]
                if entry.get("dict") != dict_name
            ]

            # Remove reading if empty
            if not dictionary_map[word][reading]:
                del dictionary_map[word][reading]

        # Remove word if empty
        if not dictionary_map[word]:
            del dictionary_map[word]

    active_dictionaries.remove(dict_name)
    save_config()  # Save the updated active dictionaries
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

    full_config = f"{custom_config} {tessdata_dir_config}"

    extracted_text = pytesseract.image_to_string(
        processed_img,
        lang=lang,
        config=full_config
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


def get_dictionary_form(word: str) -> str:
    """Convert conjugated forms to dictionary form"""
    if not word:
        return word

    # Try to find exact match first
    if word in dictionary_map:
        return word

    # Analyze the word to get possible lemmas
    analyzed = tagger.parseToNodeList(word)
    if analyzed:
        # Get the first node's lemma (dictionary form)
        lemma = analyzed[0].feature.lemma
        if lemma and lemma != "*":
            return lemma

    # Common conjugation patterns (add more as needed)
    conjugations = {
        'った$': 'る',  # past tense (走った -> 走る)
        'んだ$': 'ぬ',  # past tense (死んだ -> 死ぬ)
        'いだ$': 'ぐ',  # past tense (泳いだ -> 泳ぐ)
        'んだ$': 'ぶ',  # past tense (飛んだ -> 飛ぶ)
        'んだ$': 'む',  # past tense (読んだ -> 読む)
        'った$': 'う',  # past tense (買った -> 買う)
        'いた$': 'く',  # past tense (書いた -> 書く)
        'した$': 'す',  # past tense (話した -> 話す)
        'て$': '',  # te-form (食べて -> 食べる)
        'た$': '',  # ta-form (食べた -> 食べる)
        'ない$': '',  # negative (食べない -> 食べる)
        'ます$': '',  # polite form (食べます -> 食べる)
        'ましょう$': '',  # volitional polite (食べましょう -> 食べる)
    }

    for pattern, replacement in conjugations.items():
        base = re.sub(pattern, replacement, word)
        if base in dictionary_map:
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
    """Fetch Japanese definition from local JSON dictionary with proper ordering."""
    word = request.args.get("word", "").strip()

    if not word:
        return jsonify({"error": "No word provided"}), 400

    # Get dictionary form of the word
    dict_form = get_dictionary_form(word)

    # Get all entries for both the original word and dictionary form
    all_entries = {}

    # First try the exact word
    if word in dictionary_map:
        all_entries.update(dictionary_map[word])

    # Then try the dictionary form
    if dict_form != word and dict_form in dictionary_map:
        all_entries.update(dictionary_map[dict_form])

    # If we found nothing, try some common variations
    if not all_entries:
        # Try katakana/hiragana conversion
        hiragana = jaconv.kata2hira(word)
        katakana = jaconv.hira2kata(word)

        if hiragana != word and hiragana in dictionary_map:
            all_entries.update(dictionary_map[hiragana])
        if katakana != word and katakana in dictionary_map:
            all_entries.update(dictionary_map[katakana])

    # We'll build results in dictionary order
    results = []

    # Process dictionaries in the specified order
    for dict_name in dictionary_order:
        if dict_name not in active_dictionaries:
            continue

        # Find all entries from this dictionary
        for reading, entries in all_entries.items():
            for entry in entries:
                if entry.get("dict") == dict_name:
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
    print("Listing dictionaries in:", DICTIONARY_BASE_PATH)
    available = []
    if not os.path.exists(DICTIONARY_BASE_PATH):
        print("Dictionaries directory doesn't exist!")
        return jsonify(available)

    # Get all dictionary folders
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

    # Create response maintaining the saved order
    result = []

    # First add dictionaries in the saved order
    for dict_name in dictionary_order:
        if dict_name in all_dicts:
            result.append({
                "name": dict_name,
                "loaded": dict_name in active_dictionaries,
                "position": dictionary_order.index(dict_name)
            })
            all_dicts.remove(dict_name)

    # Then add any remaining dictionaries that weren't in the order
    for dict_name in all_dicts:
        result.append({
            "name": dict_name,
            "loaded": dict_name in active_dictionaries,
            "position": len(dictionary_order)  # Add at the end
        })

    return jsonify(result)


@app.route("/dictionaries/load", methods=["POST"])
def load_dictionary_route():
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Dictionary name not provided"}), 400

    dict_path = os.path.join(DICTIONARY_BASE_PATH, data["name"])
    if not os.path.exists(dict_path):
        return jsonify({"error": "Dictionary not found"}), 404

    try:
        if load_dictionary(data["name"]):
            # Add to order if not already present
            if data["name"] not in dictionary_order:
                dictionary_order.append(data["name"])
                save_config()  # Save the new order
            return jsonify({
                "success": True,
                "message": f"Dictionary {data['name']} loaded",
                "order": dictionary_order
            })
        else:
            return jsonify({
                "error": f"Dictionary {data['name']} has no valid term_bank files"
            }), 400
    except Exception as e:
        return jsonify({
            "error": f"Failed to load dictionary: {str(e)}"
        }), 500


@app.route("/dictionaries/reorder", methods=["POST"])
def reorder_dictionaries():
    """Change the order of dictionaries"""
    data = request.json
    if "order" not in data:
        return jsonify({
            "success": False,
            "error": "New order not provided",
            "details": "The 'order' field is required in the request body"
        }), 400

    global dictionary_order
    new_order = data["order"]

    if not isinstance(new_order, list):
        return jsonify({
            "success": False,
            "error": "Invalid order format",
            "details": "Order must be a list of dictionary names"
        }), 400

    # Validate all dictionaries in the new order exist
    for dict_name in new_order:
        dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
        if not os.path.exists(dict_path):
            return jsonify({
                "success": False,
                "error": "Invalid dictionary in order",
                "details": f"Dictionary '{dict_name}' not found"
            }), 400

    # Update the order
    dictionary_order = new_order
    save_config()  # Save the new order

    return jsonify({
        "success": True,
        "message": "Dictionary order updated",
        "order": dictionary_order
    })


@app.route("/dictionaries/order", methods=["GET"])
def get_dictionary_order():
    return jsonify({
        "order": dictionary_order
    })


@app.route("/dictionaries/unload", methods=["POST"])
def unload_dictionary_route():
    """Unload a specific dictionary"""
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Dictionary name not provided"}), 400

    if unload_dictionary(data["name"]):
        return jsonify({"success": True, "message": f"Dictionary {data['name']} unloaded"})
    else:
        return jsonify({"error": f"Dictionary {data['name']} not loaded"}), 400

@app.route("/dictionary/search", methods=["GET"])
def search_dictionary_words():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    # Check if query is kana (hiragana or katakana)
    is_kana_query = re.fullmatch(r'[\u3040-\u309F\u30A0-\u30FF]+', query) is not None

    exact_word_matches = []
    exact_reading_matches = []
    partial_matches = []

    query_lower = query.lower()

    for word in dictionary_map.keys():
        lower_word = word.lower()

        # 1. Exact word matches
        if lower_word == query_lower:
            exact_word_matches.append(word)
            continue

        # For kana queries only
        if is_kana_query:
            # 2. Exact reading matches
            exact_reading_match = False
            for reading in dictionary_map[word].keys():
                if query_lower == reading.lower():
                    exact_reading_matches.append(word)
                    exact_reading_match = True
                    break

            if not exact_reading_match:
                # 3. Partial matches (word contains query)
                if query_lower in lower_word:
                    partial_matches.append(word)
        else:
            # For kanji queries, only exact matches
            if lower_word.startswith(query_lower):
                partial_matches.append(word)

    # Combine results in priority order
    results = exact_word_matches + exact_reading_matches + partial_matches

    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for word in results:
        if word not in seen:
            seen.add(word)
            unique_results.append(word)

    return jsonify(unique_results[:50])  # Return up to 50 matches


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
            "active_dictionaries": dictionaries,
            "dictionary_order": order
        }

        os.makedirs(USER_DATA_DIR, exist_ok=True)
        config_file = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"Saved dictionary config for {safe_device_id}")
        return jsonify({"success": True})
    except Exception as e:
        print("Dictionary sync error:", e)
        return jsonify({"error": str(e)}), 500

# Initialize dictionaries on startup
download_default_dictionary()
initialize_dictionaries()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
