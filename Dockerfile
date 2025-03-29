FROM python:3.12-slim

# Install system dependencies with explicit versions
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    tesseract-ocr=5.3.0-2 \
    tesseract-ocr-jpn=1:5.3.0-2 \
    tesseract-ocr-jpn-vert=1:5.3.0-2 \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Manually verify and fix language file locations
RUN mkdir -p /usr/share/tesseract-ocr/tessdata && \
    cp /usr/share/tesseract-ocr/5/tessdata/* /usr/share/tesseract-ocr/tessdata/ && \
    tesseract --list-langs

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data/dictionaries

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
