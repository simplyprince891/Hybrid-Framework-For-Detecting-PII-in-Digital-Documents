# moved from src/pii_scanner/ocr.py
import pytesseract
from PIL import Image
import io

def extract_ocr_text(file_bytes, lang='eng+hin'):
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image, lang=lang)
