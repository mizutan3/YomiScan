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

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Persistent storage paths
VOLUME_BASE = "/app/data"
DICTIONARY_BASE_PATH = os.path.join(VOLUME_BASE, "dictionaries")
CONFIG_FILE = os.path.join(VOLUME_BASE, "config", "app_config.json")
TESSDATA_DIR = "/usr/share/tesseract-ocr/5/tessdata"

# Ensure directories exist
os.makedirs(DICTIONARY_BASE_PATH, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
os.makedirs(TESSDATA_DIR, exist_ok=True)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5"

# Configure MeCab
try:
    mecab = MeCab.Tagger("-Owakati -d /var/lib/mecab/dic/ipadic-utf8")
except Exception as e:
    print(f"MeCab initialization error: {str(e)}")
    mecab = MeCab.Tagger("-Owakati")

# Dictionary management variables
dictionary_map: Dict[str, Dict[str, List[Dict]]] = {}
active_dictionaries: Set[str] = set()
dictionary_order: List[str] = []

def load_config():
    global dictionary_order, active_dictionaries

    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                dictionary_order = config.get('dictionary_order', [])
                active_dictionaries = set(config.get('active_dictionaries', []))
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        dictionary_order = []
        active_dictionaries = set()

def save_config():
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
        save_config()
        return True
    return False

def initialize_dictionaries():
    print("Initializing dictionaries...")
    load_config()

    available = [d['name'] for d in get_available_dictionaries()]

    if not dictionary_order:
        dictionary_order.extend(available)

    for dict_name in dictionary_order:
        if dict_name in active_dictionaries:
            load_dictionary(dict_name)

    save_config()

def unload_dictionary(dict_name: str) -> bool:
    if dict_name not in active_dictionaries:
        return False

    for word in list(dictionary_map.keys()):
        for reading in list(dictionary_map[word].keys()):
            dictionary_map[word][reading] = [
                entry for entry in dictionary_map[word][reading]
                if entry.get("dict") != dict_name
            ]

            if not dictionary_map[word][reading]:
                del dictionary_map[word][reading]

        if not dictionary_map[word]:
            del dictionary_map[word]

    active_dictionaries.remove(dict_name)
    save_config()
    return True

def get_available_dictionaries() -> List[Dict]:
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

def preprocess_image(image_data: str) -> np.ndarray:
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    # Noise reduction with light blur
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # Contrast enhancement
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)

    # Binarization
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphological operations
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.erode(img, kernel, iterations=1)
    img = cv2.dilate(img, kernel, iterations=1)

    return img

def segment_words(text: str) -> List[str]:
    if not text.strip():
        return []

    words = mecab.parse(text).strip().split()
    return [w for w in words if w.strip()]

@app.route("/ocr", methods=["POST"])
def ocr():
    data = request.json
    if "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    orientation = data.get("orientation", "horizontal")

    processed_img = preprocess_image(data["image"])

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

    segmented_text = segment_words(extracted_text)

    return jsonify({
        "text": extracted_text,
        "words": segmented_text
    })

@app.route("/dictionary", methods=["GET"])
def dictionary():
    word = request.args.get("word", "").strip()

    if not word:
        return jsonify({"error": "No word provided"}), 400

    all_entries = dictionary_map.get(word, {})

    results = []

    for dict_name in dictionary_order:
        if dict_name not in active_dictionaries:
            continue

        for reading, entries in all_entries.items():
            for entry in entries:
                if entry.get("dict") == dict_name:
                    results.append({
                        "word": word,
                        "reading": reading,
                        "meanings": [entry["text"]],
                        "dictionary": dict_name
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

    for dict_name in new_order:
        dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
        if not os.path.exists(dict_path):
            return jsonify({
                "success": False,
                "error": "Invalid dictionary in order",
                "details": f"Dictionary '{dict_name}' not found"
            }), 400

    dictionary_order = new_order
    save_config()

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
    data = request.json
    if "name" not in data:
        return jsonify({"error": "Dictionary name not provided"}), 400

    if unload_dictionary(data["name"]):
        return jsonify({"success": True, "message": f"Dictionary {data['name']} unloaded"})
    else:
        return jsonify({"error": f"Dictionary {data['name']} not loaded"}), 400

@app.route("/dictionaries/upload", methods=["POST"])
def upload_dictionary():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    original_filename = file.filename
    if not original_filename.lower().endswith('.zip'):
        return jsonify({"error": "Only .zip files are supported"}), 400

    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "temp_upload.zip")
        file.save(zip_path)

        if not zipfile.is_zipfile(zip_path):
            return jsonify({"error": "The file is not a valid ZIP archive"}), 400

        dict_name = None
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            try:
                with zip_ref.open('index.json') as index_file:
                    index_data = json.load(index_file)
                    if isinstance(index_data, dict):
                        for field in ['title', 'name', 'dictionary']:
                            if field in index_data:
                                dict_name = str(index_data[field])
                                break
            except (KeyError, json.JSONDecodeError):
                pass

        if not dict_name:
            base_name = os.path.splitext(original_filename)[0]
            clean_name = re.sub(r'(\[.*?\])|(\(.*?\))', '', base_name)
            clean_name = clean_name.strip()
            dict_name = clean_name

        def safe_japanese_filename(name):
            keep_chars = (' ', '-', '_', '・', '～')
            return ''.join(c for c in name if c.isalnum() or c in keep_chars).strip()

        dict_name = safe_japanese_filename(dict_name) or "dictionary"

        extract_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

        term_bank_files = [
            f for f in os.listdir(extract_path)
            if f.startswith("term_bank_") and f.endswith(".json")
        ]

        if not term_bank_files:
            shutil.rmtree(extract_path)
            return jsonify({"error": "No term bank files found in dictionary"}), 400

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
    dict_path = os.path.join(DICTIONARY_BASE_PATH, dict_name)
    if not os.path.exists(dict_path):
        return jsonify({"error": "Dictionary not found"}), 404

    try:
        import shutil
        if dict_name in active_dictionaries:
            unload_dictionary(dict_name)
        shutil.rmtree(dict_path)

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

initialize_dictionaries()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
