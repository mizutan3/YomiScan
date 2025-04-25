from flask import Blueprint, request, send_file, jsonify
from gtts import gTTS
import os
import base64
from io import BytesIO

system_bp = Blueprint("system", __name__)

@system_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@system_bp.route("/synthesize_speech", methods=["POST"])
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
        }), 50