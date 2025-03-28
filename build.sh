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
    libmecab-dev \
    mecab-utils

# Create symlinks to our bundled dictionary
sudo mkdir -p /usr/local/etc/
sudo ln -sf /opt/render/project/src/mecab/mecabrc /usr/local/etc/mecabrc
sudo ln -sf /opt/render/project/src/mecab/dic /usr/local/lib/mecab/dic

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
echo "MeCab configuration:"
mecab-config --dicdir
cat /usr/local/etc/mecabrc
