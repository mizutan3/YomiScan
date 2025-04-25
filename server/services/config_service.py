# server/services/config_service.py
from ..constants import USER_DATA_DIR, dictionary_order, active_dictionaries
from ..utils.helpers import sanitize_filename
import os
import json

def load_config(device_id: str):
    safe_device_id = sanitize_filename(device_id)
    config_file = os.path.join(USER_DATA_DIR, f"{safe_device_id}_config.json")

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

                # Clear existing and update in place
                dictionary_order.clear()
                dictionary_order.extend(config.get('dictionary_order', []))

                active_dictionaries.clear()
                active_dictionaries.update(config.get('active_dictionaries', []))

                print(f"✅ Loaded config for device {safe_device_id}")
        else:
            print(f"No config found for device {safe_device_id}, using defaults")
            dictionary_order.clear()
            active_dictionaries.clear()
    except Exception as e:
        print(f"❌ Error loading config for {safe_device_id}: {str(e)}")
        dictionary_order.clear()
        active_dictionaries.clear()

def save_config(device_id: str, order=None, active=None):
    from ..constants import dictionary_order, active_dictionaries  # safe repeat in function scope

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