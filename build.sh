#!/bin/bash
set -o errexit

# Install Tesseract and Japanese language data
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev tesseract-ocr-jpn tesseract-ocr-script-jpan-vert

# Install Python dependencies
pip install -r requirements.txt
