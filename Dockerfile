FROM python:3.12.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create directory structure
RUN mkdir -p /app/data/{tesseract,mecab,dictionaries,config}

# Correct Tesseract symlink (Debian 12 uses /usr/share/tesseract-ocr/5/)
RUN ln -s /app/data/tesseract /usr/share/tesseract-ocr/5/tessdata

# Correct MeCab symlink (Debian uses /var/lib/mecab/dic/)
RUN ln -s /app/data/mecab /var/lib/mecab/dic/ipadic-utf8

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload assets
COPY preload_assets.py .
RUN python preload_assets.py

RUN ls -la /usr/share/tesseract-ocr/5/tessdata/ && \
    echo "TESSDATA_PREFIX=$TESSDATA_PREFIX" && \
    tesseract --list-langs

# Copy application code
COPY . .

CMD ["python", "server.py"]
