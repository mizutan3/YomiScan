# Use Python 3.11 slim image
FROM python:3.11-slim

# Install Tesseract and Japanese language packs with suppressed warnings
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files (improves build caching)
COPY requirements.txt .
COPY server.py .
COPY tessdata/ ./tessdata/
COPY dictionaries/ ./dictionaries/

# Install Python dependencies as non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "server:app"]
