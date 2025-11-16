import os
from io import BytesIO
from typing import Optional

try:
	from PIL import Image
except Exception:  # pragma: no cover
	Image = None

try:
	import pytesseract
except Exception:  # pragma: no cover
	pytesseract = None


_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd and pytesseract is not None:
	pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


def image_to_text(image_bytes: bytes, lang: str = "eng") -> str:
	if pytesseract is None or Image is None:
		raise RuntimeError("OCR dependencies not installed (pytesseract/Pillow)")
	image = Image.open(BytesIO(image_bytes))
	image = image.convert("L")
	try:
		return pytesseract.image_to_string(image, lang=lang) or ""
	except Exception:
		return "" 