#!/bin/bash
mkdir -p /app/data/tessdata
cd /app/data/tessdata
wget https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata
