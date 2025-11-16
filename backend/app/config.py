import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database
SQLITE_PATH = os.environ.get("PII_SQLITE_PATH", str(DATA_DIR / "pii.db"))

# OCR / Poppler
POPPLER_PATH = os.environ.get("POPPLER_PATH", r"C:\\Program Files\\poppler-25.07.0\\Library\\bin")
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe")

# Detection
CONTEXT_WINDOW = int(os.environ.get("CONTEXT_WINDOW", 48))
SCORE_THRESHOLD = int(os.environ.get("SCORE_THRESHOLD", 2))

# Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_JSON = os.environ.get("LOG_JSON", "true").lower() in ("1","true","yes")

# Export
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# Limits
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 20 * 1024 * 1024))  # 20 MB
