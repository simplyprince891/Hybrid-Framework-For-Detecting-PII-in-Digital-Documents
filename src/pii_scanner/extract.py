import os
from typing import Optional

from .ocr import image_to_text

try:
	import fitz  # pymupdf
except Exception:  # pragma: no cover
	fitz = None

try:
	from docx import Document
except Exception:  # pragma: no cover
	Document = None


def read_text_file(path: str) -> str:
	with open(path, "r", encoding="utf-8", errors="ignore") as f:
		return f.read()


def extract_text_from_pdf(path: str, ocr: bool = False, ocr_lang: str = "eng") -> str:
	if fitz is None:
		raise RuntimeError("pymupdf is not installed")
	text_parts = []
	with fitz.open(path) as doc:
		for page in doc:
			text = page.get_text("text")
			if text.strip():
				text_parts.append(text)
			elif ocr:
				pix = page.get_pixmap(dpi=300)
				img_bytes = pix.tobytes("png")
				text_parts.append(image_to_text(img_bytes, ocr_lang))
	return "\n".join(text_parts)


def extract_text_from_docx(path: str) -> str:
	if Document is None:
		raise RuntimeError("python-docx is not installed")
	doc = Document(path)
	paras = [p.text for p in doc.paragraphs]
	return "\n".join(paras)


def extract_text_from_image(path: str, ocr_lang: str = "eng") -> str:
	with open(path, "rb") as f:
		data = f.read()
	return image_to_text(data, ocr_lang)


def extract_text_from_file(path: str, ocr: bool = False, ocr_lang: str = "eng") -> str:
	ext = os.path.splitext(path)[1].lower()
	if ext in {".txt", ".csv", ".log", ".json"}:
		return read_text_file(path)
	if ext in {".pdf"}:
		return extract_text_from_pdf(path, ocr=ocr, ocr_lang=ocr_lang)
	if ext in {".docx"}:
		return extract_text_from_docx(path)
	if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
		return extract_text_from_image(path, ocr_lang=ocr_lang)
	return ""  # unsupported 