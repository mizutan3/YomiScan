#!/bin/bash
set -o errexit

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-jpn \
    tesseract-ocr-script-jpan-vert \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev

# Install Python dependencies
pip install -r requirements.txt
