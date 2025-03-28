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
    libmecab-dev \
    git \
    make \
    curl \
    xz-utils \
    file

# Install MeCab IPA dictionary (more reliable)
sudo mkdir -p /usr/local/etc/
curl -s https://raw.githubusercontent.com/neologd/mecab-ipadic-neologd/master/seed/mecab-user-dict-seed.20200910.csv.xz | xz -dc | iconv -f utf8 -t eucjp | /usr/lib/mecab/mecab-dict-index -d /usr/share/mecab/dic/ipadic -u /usr/local/etc/mecab-user-dict.dic -f eucjp -t eucjp
echo "dicdir = /usr/share/mecab/dic/ipadic" | sudo tee /usr/local/etc/mecabrc
echo "userdic = /usr/local/etc/mecab-user-dict.dic" | sudo tee -a /usr/local/etc/mecabrc

# Verify installation
mecab --version
mecab-config --dicdir

# Install Python dependencies
pip install -r requirements.txt
