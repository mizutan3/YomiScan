FROM python:3.12.2

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-jpn \
    tesseract-ocr-jpn-vert \
    mecab \
    mecab-ipadic-utf8 \
    libmecab-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Create directories
RUN mkdir -p /app/data/{dictionaries,config} \
    && mkdir -p /usr/share/tesseract-ocr/tessdata

# Install language data
RUN wget -O /usr/share/tesseract-ocr/tessdata/jpn.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/jpn.traineddata \
    && wget -O /usr/share/tesseract-ocr/tessdata/jpn_vert.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/jpn_vert.traineddata

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
