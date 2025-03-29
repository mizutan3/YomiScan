FROM python:3.12-slim

# Install system dependencies with non-interactive frontend
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    tesseract-ocr \
    tesseract-ocr-all \  # Installs all languages
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify Tesseract installation
RUN tesseract --version && tesseract --list-langs

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data/dictionaries

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
