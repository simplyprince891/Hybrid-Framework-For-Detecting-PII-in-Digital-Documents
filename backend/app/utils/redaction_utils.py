from typing import List
import fitz
import pytesseract
from PIL import Image


def _norm(s: str) -> str:
    return ''.join(ch.lower() for ch in s if ch.isalnum())


def find_rects_for_value(page: fitz.Page, value: str) -> List[fitz.Rect]:
    """Return list of fitz.Rect on the page that match the given value.

    Tries exact text search, then word-based matching, and finally OCR fallback for image-only pages.
    """
    rects = []
    try:
        exact = page.search_for(value)
        if exact:
            return exact
    except Exception:
        pass

    try:
        words = page.get_text("words")
    except Exception:
        words = []

    if not words:
        # OCR fallback
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
            mode = "RGB" if pix.n < 4 else "RGBA"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            ocr = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            words = []
            n = len(ocr.get('text', []))
            for i in range(n):
                text = ocr['text'][i]
                if not text or text.strip() == '':
                    continue
                left = ocr['left'][i]
                top = ocr['top'][i]
                width = ocr['width'][i]
                height = ocr['height'][i]
                # map back to PDF coordinates (divide by scale)
                x0 = left / 2.0
                y0 = top / 2.0
                x1 = (left + width) / 2.0
                y1 = (top + height) / 2.0
                words.append((x0, y0, x1, y1, text, 0, 0, 0))
        except Exception:
            return []

    if not words:
        return []

    word_texts = [w[4] for w in words]
    norms = [_norm(w) for w in word_texts]
    target = _norm(value)
    if not target:
        return []

    n = len(norms)
    for i in range(n):
        if not norms[i]:
            continue
        acc = ''
        j = i
        while j < n and len(acc) < len(target) * 3:
            acc += norms[j]
            if acc == target:
                x0 = min(words[k][0] for k in range(i, j + 1))
                y0 = min(words[k][1] for k in range(i, j + 1))
                x1 = max(words[k][2] for k in range(i, j + 1))
                y1 = max(words[k][3] for k in range(i, j + 1))
                rects.append(fitz.Rect(x0, y0, x1, y1))
                break
            j += 1

    # digits-only fallback
    digits = ''.join(ch for ch in value if ch.isdigit())
    if digits and len(digits) >= 6 and not rects:
        norms_digits = [''.join(ch for ch in w if ch.isdigit()) for w in word_texts]
        for i in range(n):
            acc = ''
            j = i
            while j < n and len(acc) < len(digits) * 3:
                acc += norms_digits[j]
                if acc == digits:
                    x0 = min(words[k][0] for k in range(i, j + 1))
                    y0 = min(words[k][1] for k in range(i, j + 1))
                    x1 = max(words[k][2] for k in range(i, j + 1))
                    y1 = max(words[k][3] for k in range(i, j + 1))
                    rects.append(fitz.Rect(x0, y0, x1, y1))
                    break
                j += 1

    return rects
