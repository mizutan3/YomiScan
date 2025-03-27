#!/bin/bash
set -o errexit

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    libmecab-dev \
    mecab \
    mecab-ipadic-utf8 \
    g++ \
    make \
    cmake \
    git \
    python3-dev

# Install Python dependencies
pip install -r requirements.txt

# Create directories and copy Tesseract data files
mkdir -p /opt/render/.local/share/tesseract-ocr/4.00/tessdata/
cp tessdata/*.traineddata /opt/render/.local/share/tesseract-ocr/4.00/tessdata/
