FROM python:3.12.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create directory structure
RUN mkdir -p /app/data/{tesseract,mecab,dictionaries,config}

# Symlink Tesseract data to our persistent volume
RUN ln -s /app/data/tesseract /usr/share/tesseract-ocr/4.00/tessdata

# Symlink MeCab dictionary
RUN ln -s /app/data/mecab /usr/lib/x86_64-linux-gnu/mecab/dic

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload assets
COPY preload_assets.py .
RUN python preload_assets.py

# Copy application code
COPY . .

CMD ["python", "server.py"]
