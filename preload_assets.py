import os
import shutil
import requests
import tarfile
from urllib.parse import urlparse

def download_file(url, destination):
    """Download a file from URL to destination"""
    print(f"Downloading {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(destination, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Saved to {destination}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")
        return False

def setup_tesseract():
    """Download and setup Tesseract language data"""
    tessdata_dir = "/usr/share/tesseract-ocr/5/tessdata"
    os.makedirs(tessdata_dir, exist_ok=True)
    
    # Download Japanese language files
    base_url = "https://github.com/tesseract-ocr/tessdata/raw/main/"
    files = [
        "jpn.traineddata",
        "jpn_vert.traineddata",
        "eng.traineddata"  # Optional
    ]
    
    for file in files:
        dest = os.path.join(tessdata_dir, file)
        if not os.path.exists(dest):
            download_file(base_url + file, dest)
    
    # Verify installation
    if not os.path.exists(os.path.join(tessdata_dir, "jpn.traineddata")):
        raise Exception("Japanese Tesseract data not installed!")

def setup_mecab():
    """Download and setup MeCab dictionary"""
    mecab_dir = "/var/lib/mecab/dic/ipadic-utf8"
    if os.path.exists(mecab_dir):
        return
        
    os.makedirs(mecab_dir, exist_ok=True)
    
    # Download IPADIC dictionary from direct source
    print("Downloading MeCab IPADIC...")
    url = "https://jaist.dl.sourceforge.net/project/mecab/mecab-ipadic/2.7.0-20070801/mecab-ipadic-2.7.0-20070801.tar.gz"
    tar_path = "/tmp/ipadic.tar.gz"
    
    if download_file(url, tar_path):
        try:
            # Extract
            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(path="/var/lib/mecab/dic/")
            
            # Move to correct location
            extracted_dir = "/var/lib/mecab/dic/mecab-ipadic-2.7.0-20070801"
            if os.path.exists(extracted_dir):
                for item in os.listdir(extracted_dir):
                    shutil.move(os.path.join(extracted_dir, item), mecab_dir)
                os.rmdir(extracted_dir)
            
            print("MeCab IPADIC installed")
        except Exception as e:
            print(f"Failed to extract MeCab dictionary: {str(e)}")
        finally:
            if os.path.exists(tar_path):
                os.remove(tar_path)

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
