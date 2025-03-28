#!/bin/bash
set -e

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    mecab \
    libmecab-dev \
    mecab-ipadic-utf8 \
    mecab-utils \
    python3-dev \
    build-essential

# Create mecabrc configuration
sudo mkdir -p /usr/local/etc/
echo "dicdir = /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-utf8" | sudo tee /usr/local/etc/mecabrc
echo "userdic = /usr/local/etc/mecab-user-dict.dic" | sudo tee -a /usr/local/etc/mecabrc

# Verify installation
echo "MeCab version:"
mecab --version
echo "Dictionary path:"
mecab-config --dicdir
echo "Config file:"
cat /usr/local/etc/mecabrc
