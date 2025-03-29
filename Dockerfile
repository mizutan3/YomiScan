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

# Install gdown for Google Drive downloads
RUN pip install --no-cache-dir gdown

# Download Tesseract from Google Drive using gdown
# Replace FILE_ID with your actual Google Drive file ID
ARG TESSERACT_FILE_ID="16XzYxhja-m9zduZPA25QpIZUVt_hwExm"
RUN gdown ${TESSERACT_FILE_ID} -O /tmp/tesseract-files.zip \
    && unzip /tmp/tesseract-files.zip -d /usr/local/ \
    && rm /tmp/tesseract-files.zip

# Verify Tesseract installation
RUN ls -la /usr/local/Tesseract-OCR && \
    /usr/local/Tesseract-OCR/tesseract --version

# Set environment variables
ENV TESSDATA_PREFIX=/usr/local/Tesseract-OCR/tessdata
ENV PATH="/usr/local/Tesseract-OCR:${PATH}"

# Create application directory structure
RUN mkdir -p /app/data/dictionaries \
    && mkdir -p /app/data/config

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Verify Python packages can access Tesseract
RUN python -c "import pytesseract; print(f'Tesseract path: {pytesseract.pytesseract.tesseract_cmd}'); print(f'Languages: {pytesseract.get_languages()}')"

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Runtime configuration
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
