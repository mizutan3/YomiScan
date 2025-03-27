#!/usr/bin/env bash
# build.sh

set -o errexit

# Install system dependencies
apt-get update
apt-get install -y libmagic1 tesseract-ocr tesseract-ocr-jpn tesseract-ocr-jpn-vert
