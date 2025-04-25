from flask import Blueprint, request
from ..services.ocr_service import ocr

ocr_bp = Blueprint("ocr", __name__)

@ocr_bp.route("/ocr", methods=["POST"])
def ocr_route():
    return ocr()