import tika
from tika import parser
from app.pii.ocr import extract_ocr_text
from PIL import Image
import io

def extract_text(file_bytes, filename):
    if filename.lower().endswith(('.txt', '.csv', '.log')):
        return file_bytes.decode(errors='ignore')
    elif filename.lower().endswith(('.pdf', '.docx')):
        # Try using Apache Tika first, but fallback gracefully if Tika fails to start
        try:
            parsed = parser.from_buffer(file_bytes)
            content = parsed.get("content", "") or ""
        except Exception as e:
            # Tika failed (often due to Java not available); fall back to OCR for PDFs
            try:
                import logging
                logging.getLogger("pii_scanner.extract").warning("Tika extraction failed, falling back to OCR: %s", e)
            except Exception:
                pass
            content = ""

        # If Tika produced no content (or failed), and it's a PDF try multiple fallbacks
        if not content and filename.lower().endswith('.pdf'):
            # 1) Try PyMuPDF (fitz) text extraction which doesn't require external Java/Tika
            try:
                import fitz
                pdf = fitz.open(stream=file_bytes, filetype='pdf')
                page_texts = []
                for p in pdf:
                    try:
                        page_texts.append(p.get_text())
                    except Exception:
                        continue
                if page_texts:
                    return "\n".join([t for t in page_texts if t])
            except Exception:
                # ignore and continue to next fallback
                pass

            # 2) Try pdf2image + OCR (if available)
            try:
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(file_bytes)
                ocr_texts = []
                for img in images:
                    try:
                        buf = io.BytesIO()
                        img.save(buf, format='PNG')
                        ocr_texts.append(extract_ocr_text(buf.getvalue()))
                    except Exception:
                        continue
                if ocr_texts:
                    return "\n".join([t for t in ocr_texts if t])
            except Exception:
                pass

            # final fallback: empty string
            return ""
        return content
    elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return extract_ocr_text(file_bytes)
    else:
        return ""
