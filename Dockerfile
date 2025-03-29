FROM python:3.12.2

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

# Verify Tesseract installation and explicitly copy language files
RUN mkdir -p /usr/share/tesseract-ocr/tessdata && \
    tesseract --version && \
    # Ensure language files are in the correct location
    cp /usr/share/tesseract-ocr/4.00/tessdata/jpn.traineddata /usr/share/tesseract-ocr/tessdata/ && \
    cp /usr/share/tesseract-ocr/4.00/tessdata/jpn_vert.traineddata /usr/share/tesseract-ocr/tessdata/ && \
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
