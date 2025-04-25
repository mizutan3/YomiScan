from flask import Blueprint, request, jsonify
import os
import json
from ..utils.helpers import sanitize_filename
from ..constants import USER_DATA_DIR

sync_bp = Blueprint("sync", __name__)

@sync_bp.route("/sync/dictionaries", methods=["GET"])
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

@sync_bp.route("/sync/dictionaries", methods=["POST"])
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