# server/services/ocr_service.py
import cv2
import numpy as np
import base64
import time
import pytesseract
from flask import jsonify, request
from ..constants import TEMP_IMAGE_PATH
from ..services.dictionary_service import segment_words
import os

if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    tessdata_dir_config = r'--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'
else:  # Linux (Railway)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    tessdata_dir_config = '--tessdata-dir /app/tessdata'

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
