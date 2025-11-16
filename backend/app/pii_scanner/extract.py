

import tika
from tika import parser
from .ocr import extract_ocr_text
from PIL import Image
import io
import logging
from .. import config as conf

logger = logging.getLogger("pii_scanner.extract")
logging.basicConfig(level=logging.INFO)

def extract_text(file_bytes, filename):
    try:
        if filename.lower().endswith(('.txt', '.csv', '.log')):
            text = file_bytes.decode(errors='ignore')
            logger.info(f"Extracted text from TXT: {len(text)} chars")
            return text
        elif filename.lower().endswith(('.pdf', '.docx')):
            parsed = parser.from_buffer(file_bytes)
            content = parsed.get("content", "")
            logger.info(f"Tika extracted from {filename}: {len(content or '')} chars")
            # If Tika fails to extract, or text is too short, try OCR on each page image
            if (not content or len(content.strip()) < 50) and filename.lower().endswith('.pdf'):
                try:
                    from pdf2image import convert_from_bytes
                    poppler_path = conf.POPPLER_PATH
                    import pytesseract
                    import cv2
                    import numpy as np
                    from PIL import Image
                    # render at higher DPI for better OCR
                    images = convert_from_bytes(file_bytes, poppler_path=poppler_path, dpi=300)
                    logger.info(f"PDF2Image produced {len(images)} images for OCR")
                    ocr_texts = []
                    for i, img in enumerate(images):
                        # Preprocess image for OCR
                        img_np = np.array(img)
                        if img_np.ndim == 3:
                            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                        else:
                            gray = img_np
                        # denoise and enhance
                        gray = cv2.bilateralFilter(gray, 9, 75, 75)
                        gray = cv2.GaussianBlur(gray, (3, 3), 0)
                        # Adaptive thresholding
                        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                      cv2.THRESH_BINARY, 11, 2)
                        # morphological opening to remove small noise
                        kernel = np.ones((1, 1), np.uint8)
                        processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
                        pil_img = Image.fromarray(processed)
                        # ensure tesseract command is known
                        try:
                            pytesseract.pytesseract.tesseract_cmd = conf.TESSERACT_CMD
                        except Exception:
                            pass
                        # general OCR (captures emails, text)
                        try:
                            ocr_general = pytesseract.image_to_string(pil_img, config=r'--oem 3 --psm 3')
                        except Exception:
                            ocr_general = ""
                        # digits-only OCR (helps numeric PII like Aadhaar)
                        try:
                            ocr_digits = pytesseract.image_to_string(pil_img, config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789')
                        except Exception:
                            ocr_digits = ""
                        ocr_result = (ocr_general or "") + "\n" + (ocr_digits or "")
                        logger.info(f"Raw OCR output (page {i+1}): {repr(ocr_result)}")
                        ocr_texts.append(ocr_result)
                    ocr_text = "\n".join(ocr_texts)
                    logger.info(f"Total OCR text: {len(ocr_text or '')} chars")
                    return ocr_text or ""
                except Exception as e:
                    logger.error(f"OCR extraction failed: {e}")
                    return ""
            return content or ""
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Image preprocessing for better OCR
            import cv2
            import numpy as np
            from PIL import Image
            import io
            import pytesseract
            # Convert bytes to numpy array
            img_array = np.frombuffer(file_bytes, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # denoise and enhance
            gray = cv2.bilateralFilter(gray, 9, 75, 75)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            # Adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            pil_img = Image.fromarray(processed)
            # Ensure tesseract command is known
            try:
                pytesseract.pytesseract.tesseract_cmd = conf.TESSERACT_CMD
            except Exception:
                pass
            # general OCR
            try:
                ocr_general = pytesseract.image_to_string(pil_img, config=r'--oem 3 --psm 3')
            except Exception:
                ocr_general = ""
            # digits-only OCR
            try:
                ocr_digits = pytesseract.image_to_string(pil_img, config=r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789')
            except Exception:
                ocr_digits = ""
            ocr_result = (ocr_general or "") + "\n" + (ocr_digits or "")
            logger.info(f"Raw OCR output: {repr(ocr_result)}")
            return ocr_result
        else:
            logger.info(f"Unsupported file type: {filename}")
            return ""
    except Exception as e:
        logger.error(f"extract_text failed: {e}")
        return ""
