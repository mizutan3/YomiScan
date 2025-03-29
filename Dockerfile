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

# Create tessdata directory and download language files
RUN mkdir -p /usr/share/tesseract-ocr/tessdata \
    && wget https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata -O /usr/share/tesseract-ocr/tessdata/jpn.traineddata \
    && wget https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata -O /usr/share/tesseract-ocr/tessdata/jpn_vert.traineddata

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data/dictionaries

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
