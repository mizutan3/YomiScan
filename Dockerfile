FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create directory structure
RUN mkdir -p /app/data/{tesseract,mecab,dictionaries,config}

# For Tesseract 5.x on Debian
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata \
    && ln -s /app/data/tesseract /usr/share/tesseract-ocr/5/tessdata/persisted

# For MeCab
RUN ln -s /app/data/mecab /var/lib/mecab/dic/custom

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload assets
COPY preload_assets.py .
RUN python preload_assets.py

# Copy application code
COPY . .

CMD ["python", "server.py"]
