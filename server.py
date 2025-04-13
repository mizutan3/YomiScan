import json
import os
import MeCab
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import pytesseract
import base64
import zipfile
import tempfile
import shutil
from typing import Dict, List, Set
from werkzeug.utils import secure_filename
import magic
import re
import time

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

DICTIONARY_BASE_PATH = os.path.join(os.path.dirname(__file__), "dictionaries")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "app_config.json")
os.makedirs(DICTIONARY_BASE_PATH, exist_ok=True)

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

    extracted_text = pytesseract.image_to_string(
        processed_img,
        lang=lang,
        config=custom_config
    )

    # Segment the extracted text into words
    segmented_text = segment_words(extracted_text)

    return jsonify({
        "text": extracted_text,
        "words": segmented_text
    })


@app.route("/dictionary", methods=["GET"])
def dictionary():
    """Fetch Japanese definition from local JSON dictionary with proper ordering."""
    word = request.args.get("word", "").strip()

    if not word:
        return jsonify({"error": "No word provided"}), 400

    # Get all entries for this word
    all_entries = dictionary_map.get(word, {})

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
                        "dictionary": dict_name  # Optional: include source dictionary
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


@app.route("/dictionaries/upload", methods=["POST"])
def upload_dictionary():
    """Upload a new dictionary zip file with proper Japanese name handling"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Get original filename
    original_filename = file.filename
    if not original_filename.lower().endswith('.zip'):
        return jsonify({"error": "Only .zip files are supported"}), 400

    temp_dir = None
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "temp_upload.zip")
        file.save(zip_path)

        # Verify it's actually a zip file
        if not zipfile.is_zipfile(zip_path):
            return jsonify({"error": "The file is not a valid ZIP archive"}), 400

        # First try to get the dictionary name from index.json
        dict_name = None
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            try:
                with zip_ref.open('index.json') as index_file:
                    index_data = json.load(index_file)
                    if isinstance(index_data, dict):
                        # Try different possible name fields
                        for field in ['title', 'name', 'dictionary']:
                            if field in index_data:
                                dict_name = str(index_data[field])
                                break
            except (KeyError, json.JSONDecodeError):
                pass

        # Fallback to filename without extension if no name found in index.json
        if not dict_name:
            base_name = os.path.splitext(original_filename)[0]
            # Clean up common patterns in filenames but preserve Japanese
            clean_name = re.sub(r'(\[.*?\])|(\(.*?\))', '', base_name)  # Remove brackets and parentheses
            clean_name = clean_name.strip()  # Remove extra whitespace
            dict_name = clean_name

        # Custom sanitization that preserves Japanese characters
        def safe_japanese_filename(name):
            # Keep Japanese characters, letters, numbers, spaces, and basic punctuation
            keep_chars = (' ', '-', '_', '・', '～')
            return ''.join(c for c in name if c.isalnum() or c in keep_chars).strip()

        dict_name = safe_japanese_filename(dict_name) or "dictionary"

        extract_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)

        # Remove existing if present
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        # Extract all files
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        # Verify we have term bank files
        term_bank_files = [
            f for f in os.listdir(extract_path)
            if f.startswith("term_bank_") and f.endswith(".json")
        ]

        if not term_bank_files:
            shutil.rmtree(extract_path)
            return jsonify({"error": "No term bank files found in dictionary"}), 400

        # Add the new dictionary to the order if it's not already there
        if dict_name not in dictionary_order:
            dictionary_order.append(dict_name)
            save_config()

        return jsonify({
            "success": True,
            "message": "Dictionary uploaded successfully",
            "name": dict_name,
            "term_banks": len(term_bank_files)
        })

    except Exception as e:
        # Clean up on error
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        if 'extract_path' in locals() and os.path.exists(extract_path):
            shutil.rmtree(extract_path, ignore_errors=True)

        return jsonify({
            "error": f"Failed to process dictionary: {str(e)}",
            "type": type(e).__name__
        }), 500
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.route("/dictionaries/<dict_name>", methods=["DELETE"])
def delete_dictionary(dict_name):
    """Delete a dictionary directory"""
    dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
    if not os.path.exists(dict_path):
        return jsonify({"error": "Dictionary not found"}), 404

    try:
        import shutil
        if dict_name in active_dictionaries:
            unload_dictionary(dict_name)
        shutil.rmtree(dict_path)

        # Remove from order if present
        if dict_name in dictionary_order:
            dictionary_order.remove(dict_name)
            save_config()

        return jsonify({
            "success": True,
            "message": f"Dictionary {dict_name} deleted"
        })
    except Exception as e:
        return jsonify({
            "error": f"Failed to delete dictionary: {str(e)}"
        }), 500


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


# Initialize dictionaries on startup
initialize_dictionaries()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
