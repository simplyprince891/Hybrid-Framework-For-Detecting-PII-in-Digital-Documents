"""Debug redaction locally for a given document id.

Usage: python backend/scripts/debug_redact_local.py <document_id>

This script will open the PDF file referenced by the document record, find detections
for that document, attempt to search/add redaction annotations (using the shared
find_rects_for_value), and then call apply_redactions while printing any exceptions
and context to help debug why redaction failed in the smoke test.
"""
import sys
from pathlib import Path
import traceback

# Ensure backend package on sys.path
root = Path(__file__).resolve().parents[1]
import sys
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from app.db.database import SessionLocal
from app.db import crud
from app.core.security import decrypt_value
from app.utils.redaction_utils import find_rects_for_value
import fitz


def main(document_id: int):
    db = SessionLocal()
    try:
        doc = crud.get_document_by_id(db, document_id)
        if not doc:
            print('document not found')
            return
        file_path = getattr(doc, 'filename', None)
        print('file_path=', file_path)
        if not file_path:
            print('no original file available')
            return
        pdf = fitz.open(file_path)
        detections = crud.get_detections_by_document_id(db, document_id)
        print('detections count=', len(detections))
        any_annots = False
        for det in detections:
            try:
                raw = decrypt_value(det.encrypted_value)
            except Exception as e:
                print('decrypt failed for det', det.id, e)
                continue
            if not raw:
                continue
            print('searching for raw value:', raw)
            for pno, page in enumerate(pdf, start=1):
                rects = []
                try:
                    rects = page.search_for(raw) or []
                except Exception as e:
                    print('page.search_for error', e)
                    rects = []
                print(f'page {pno} exact rects:', rects)
                if not rects:
                    try:
                        rects = find_rects_for_value(page, raw)
                    except Exception:
                        print('find_rects_for_value raised:')
                        traceback.print_exc()
                        rects = []
                print(f'page {pno} fallback rects:', rects)
                for r in rects:
                    try:
                        page.add_redact_annot(r, fill=(0, 0, 0))
                        any_annots = True
                    except Exception:
                        print('add_redact_annot failed:')
                        traceback.print_exc()
        print('any_annots:', any_annots)
        try:
            pdf.apply_redactions()
            out = Path(file_path).with_name(f'debug_redacted_{document_id}.pdf')
            pdf.save(str(out), garbage=4, deflate=True)
            pdf.close()
            print('saved redacted to', out)
        except Exception:
            print('apply_redactions/save raised:')
            traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python debug_redact_local.py <document_id>')
        sys.exit(2)
    main(int(sys.argv[1]))
