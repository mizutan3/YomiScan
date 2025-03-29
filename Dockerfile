FROM python:3.12.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Download Tesseract from GitHub Releases (replace with your actual URL)
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata -O /usr/local/share/tessdata/jpn.traineddata \
    && wget https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata -O /usr/local/share/tessdata/jpn_vert.traineddata

# Set environment variables
ENV TESSDATA_PREFIX=/usr/local/Tesseract-OCR/tessdata
ENV PATH="/usr/local/Tesseract-OCR:${PATH}"

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data/dictionaries

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
