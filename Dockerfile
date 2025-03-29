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

# Install gdown with speed limitation
RUN pip install --no-cache-dir gdown && \
    echo 'import gdown\n\
import os\n\
import sys\n\
\n\
try:\n\
    print("Starting download with speed limit...")\n\
    gdown.download(\n\
        "https://drive.google.com/uc?export=download&id=16XzYxhja-m9zduZPA25QpIZUVt_hwExm",\n\
        "tesseract-files.zip",\n\
        quiet=False,\n\
        speed=2000*1024  # Limit to 2MB/s\n\
    )\n\
    if os.path.exists("tesseract-files.zip"):\n\
        print("Download completed successfully")\n\
        sys.exit(0)\n\
    else:\n\
        print("Download failed - file not found")\n\
        sys.exit(1)\n\
except Exception as e:\n\
    print(f"Download failed: {str(e)}")\n\
    sys.exit(1)' > /tmp/download.py && \
    python /tmp/download.py && \
    unzip tesseract-files.zip -d /usr/local/ && \
    rm tesseract-files.zip /tmp/download.py

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
