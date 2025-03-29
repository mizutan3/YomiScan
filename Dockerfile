FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Verify and configure Tesseract
RUN mkdir -p /usr/share/tesseract-ocr/tessdata && \
    if [ -d /usr/share/tesseract-ocr/5/tessdata ]; then \
        cp -r /usr/share/tesseract-ocr/5/tessdata/* /usr/share/tesseract-ocr/tessdata/; \
    fi && \
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
ENV FLASK_APP=server.py

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
