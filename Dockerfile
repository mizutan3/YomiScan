FROM python:3.12.2

# Install system deps
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    && rm -rf /var/lib/apt/lists/*

# Create directories for volume
RUN mkdir -p /app/data/tesseract \
    && mkdir -p /app/data/mecab \
    && mkdir -p /app/data/dictionaries

# Symlink Tesseract data to volume
RUN ln -s /app/data/tesseract /usr/share/tesseract-ocr/4.00/tessdata

# Symlink Mecab dictionary to volume
RUN ln -s /app/data/mecab /usr/lib/x86_64-linux-gnu/mecab/dic

WORKDIR /app
COPY . .

# Install Python deps
RUN pip install -r requirements.txt

COPY preload_assets.py .
RUN python preload_assets.py

CMD ["python", "app.py"]
