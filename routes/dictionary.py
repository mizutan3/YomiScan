from flask import Blueprint, request, jsonify
from ..services.dictionary_service import (
    initialize_dictionaries,
    load_dictionary,
    unload_dictionary,
    get_available_dictionaries,
    get_dictionary_form,
    segment_words
)
from ..utils.helpers import sanitize_filename
from ..constants import USER_DATA_DIR, DICTIONARY_BASE_PATH, dictionary_map
from ..services.config_service import save_config
import os
import json
import re
import jaconv

dictionary_bp = Blueprint("dictionary", __name__)

@dictionary_bp.route("/dictionaries/init", methods=["POST"])
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

@dictionary_bp.route("/dictionaries/load", methods=["POST"])
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

@dictionary_bp.route("/dictionaries/unload", methods=["POST"])
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

@dictionary_bp.route("/dictionaries", methods=["GET"])
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

@dictionary_bp.route("/dictionaries/order", methods=["GET"])
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

@dictionary_bp.route("/dictionaries/reorder", methods=["POST"])
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

@dictionary_bp.route("/dictionary", methods=["GET"])
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

@dictionary_bp.route("/dictionary/search", methods=["GET"])
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