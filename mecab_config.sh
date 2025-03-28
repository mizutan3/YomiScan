#!/bin/bash
# Ensure config directory exists
sudo mkdir -p /usr/local/etc/

# Create mecabrc if missing
if [ ! -f /usr/local/etc/mecabrc ]; then
    echo "dicdir = /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-utf8" | sudo tee /usr/local/etc/mecabrc
    echo "userdic = /usr/local/etc/mecab-user-dict.dic" | sudo tee -a /usr/local/etc/mecabrc
fi

# Verify paths
echo "MeCab configuration:"
cat /usr/local/etc/mecabrc
echo "Dictionary path:"
mecab-config --dicdir
