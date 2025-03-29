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

# Install gdown for Google Drive downloads
RUN pip install --no-cache-dir gdown

# Download Tesseract using gdown (replace with your actual file ID)
RUN gdown "https://drive.google.com/uc?export=download&id=16XzYxhja-m9zduZPA25QpIZUVt_hwExm" -O tesseract-files.zip \
    && unzip tesseract-files.zip -d /usr/local/ \
    && rm tesseract-files.zip

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
