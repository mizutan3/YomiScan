#!/bin/bash
set -o errexit

# Install MeCab first
chmod +x install_mecab.sh
./install_mecab.sh

# Then install OCR tools
sudo apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-jpn \
    tesseract-ocr-script-jpan-vert

# Install Python dependencies
pip install -r requirements.txt

# Copy unidic-lite dictionary to expected location
UNIDIC_PATH=$(python -c "import unidic_lite; print(unidic_lite.__path__[0])")
sudo cp -r $UNIDIC_PATH/dicdir /usr/local/lib/mecab/dic/unidic-lite
