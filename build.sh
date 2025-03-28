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
    mecab-ipadic-utf8 \
    mecab-utils \
    wget \
    xz-utils \
    curl

# Create project mecab directory structure
mkdir -p mecab/dic
cd mecab/dic

# Download MeCab IPA dictionary from official source
echo "Downloading MeCab IPA dictionary..."
wget http://downloads.sourceforge.net/project/mecab/mecab-ipadic/2.7.0-20070801/mecab-ipadic-2.7.0-20070801.tar.gz

# Extract dictionary
echo "Extracting dictionary..."
tar -xzf mecab-ipadic-2.7.0-20070801.tar.gz
mv mecab-ipadic-2.7.0-20070801 ipadic
rm mecab-ipadic-2.7.0-20070801.tar.gz

# Set up mecabrc configuration
cd ../..
mkdir -p mecab/etc
echo "dicdir = /opt/render/project/src/mecab/dic/ipadic" > mecab/etc/mecabrc
echo "userdic = /opt/render/project/src/mecab/user.dic" >> mecab/etc/mecabrc

# Create system symlinks
sudo mkdir -p /usr/local/etc/
sudo ln -sf /opt/render/project/src/mecab/etc/mecabrc /usr/local/etc/mecabrc
sudo ln -sf /opt/render/project/src/mecab/dic /usr/local/lib/mecab/dic

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
echo "Verifying MeCab installation..."
mecab --version
echo "Dictionary path:"
mecab-config --dicdir
echo "Configuration:"
cat /usr/local/etc/mecabrc

# Verify Japanese language support
echo "Checking installed Tesseract languages:"
tesseract --list-langs

# If Japanese isn't listed, install it explicitly
sudo apt-get install -y tesseract-ocr-jpn tesseract-ocr-jpn-vert
