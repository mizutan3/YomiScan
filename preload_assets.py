import os
import shutil
import requests
import tarfile

def download_file(url, destination):
    """Download a file from URL to destination"""
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    with open(destination, 'wb') as f:
        shutil.copyfileobj(response.raw, f)
    print(f"Saved to {destination}")

def setup_tesseract():
    """Download and setup Tesseract language data"""
    tessdata_dir = "/app/data/tesseract"
    os.makedirs(tessdata_dir, exist_ok=True)
    
    # Download Japanese language files
    base_url = "https://github.com/tesseract-ocr/tessdata/raw/main/"
    files = [
        "jpn.traineddata",
        "jpn_vert.traineddata",
    ]
    
    for file in files:
        dest = os.path.join(tessdata_dir, file)
        if not os.path.exists(dest):
            download_file(base_url + file, dest)

def setup_mecab():
    """Download and setup MeCab dictionary"""
    mecab_dir = "/app/data/mecab/ipadic"
    if os.path.exists(mecab_dir):
        return
        
    os.makedirs(mecab_dir, exist_ok=True)
    
    # Download IPADIC dictionary
    print("Downloading MeCab IPADIC...")
    url = "https://drive.google.com/uc?export=download&id=0B4y35FiV1wh7MWVlSDBCSXZMTXM"
    tar_path = "/tmp/ipadic.tar.gz"
    download_file(url, tar_path)
    
    # Extract
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(path="/app/data/mecab")
    
    # Cleanup
    os.remove(tar_path)
    print("MeCab IPADIC installed")

def setup_directories():
    """Ensure required directories exist"""
    os.makedirs("/app/data/dictionaries", exist_ok=True)
    os.makedirs("/app/data/config", exist_ok=True)

if __name__ == "__main__":
    print("=== Setting up Tesseract/MeCab assets ===")
    setup_directories()
    setup_tesseract()
    setup_mecab()
    print("=== Setup complete ===")
