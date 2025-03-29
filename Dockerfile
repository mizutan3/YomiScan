FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TESSDATA_PREFIX /usr/share/tesseract-ocr/4.00/tessdata

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    libgl1 \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    file \       # Provides the magic.h header
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "server:app"]
