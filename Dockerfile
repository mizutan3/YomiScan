FROM python:3.11-slim

# 1. Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Create appuser and setup environment
RUN useradd -m appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

WORKDIR /app
USER appuser

# 3. Set PATH before installing packages
ENV PATH="/home/appuser/.local/bin:${PATH}"

# 4. Copy and install requirements
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 5. Copy application files
COPY --chown=appuser:appuser . .

# 6. Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
ENV FLASK_APP=server.py
ENV PORT=10000

# 7. Ensure dictionaries directory exists
RUN mkdir -p dictionaries && chown appuser:appuser dictionaries

# 8. Fix for $PORT variable in CMD
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} server:app"]
