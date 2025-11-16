from fastapi import APIRouter, Query, Depends, HTTPException, status
from app.db.database import SessionLocal
from app.db import crud
from fastapi.responses import StreamingResponse, JSONResponse
import io
import csv
from app import config as conf
import logging
from app.core.security import decrypt_value
from app.pii_scanner.detectors.patterns import _mask_keep_last4
import fitz
from app.utils.redaction_utils import find_rects_for_value

logger = logging.getLogger("pii_scanner.api.report")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/report/")
def get_report(document_id: int = Query(...), db=Depends(get_db)):
    detections = crud.get_detections_by_document_id(db, document_id)
    result = [
        {
            "type": d.pii_type,
            # return a masked value for UI display (prefer persisted masked_value)
            "value": (getattr(d, "masked_value", None) or ( _mask_keep_last4(decrypt_value(d.encrypted_value)) if getattr(d, "encrypted_value", None) is not None else None )),
            "score": getattr(d, "score", None),
            "start": d.start,
            "end": d.end,
        }
        for d in detections
    ]
    return {"document_id": document_id, "detections": result}


@router.get("/export/json/")
def export_json(document_id: int = Query(...), db=Depends(get_db)):
    detections = crud.get_detections_by_document_id(db, document_id)
    result = [
        {
            "type": d.pii_type,
            "start": d.start,
            "end": d.end,
            "pii_hash": getattr(d, "pii_hash", None),
        }
        for d in detections
    ]
    # structured log
    logger.info("export_json", extra={"document_id": document_id, "count": len(result)})
    return JSONResponse({"document_id": document_id, "detections": result})


@router.get("/export/csv/")
def export_csv(document_id: int = Query(...), db=Depends(get_db)):
    detections = crud.get_detections_by_document_id(db, document_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["type", "start", "end", "pii_hash"])
    for d in detections:
        writer.writerow([d.pii_type, d.start, d.end, getattr(d, "pii_hash", "")])
    output.seek(0)
    filename = f"detections_{document_id}.csv"
    logger.info("export_csv", extra={"document_id": document_id, "count": len(detections)})
    return StreamingResponse(
        output, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )


@router.get("/export/redacted_pdf/")
def export_redacted_pdf(document_id: int = Query(...), db=Depends(get_db)):
    logger.info("export_redacted_pdf_requested", extra={"document_id": document_id})

    doc = crud.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="document not found")

    # document.filename stores the permanent path for originals when available
    file_path = getattr(doc, "filename", None)
    if not file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="original file not available")

    # Only support PDF redaction for now
    if not str(file_path).lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="redaction supported for PDF files only"
        )

    detections = crud.get_detections_by_document_id(db, document_id)
    if not detections:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no detections to redact")

    try:
        pdf = fitz.open(file_path)
    except Exception:
        logger.exception("failed to open pdf for redaction")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to open original PDF")

    # Add redaction annotations by searching for detected values (decrypted)
    any_annots = False
    # collect rects per page as fallback if apply_redactions() is unavailable
    rects_by_page = {}
    for det in detections:
        try:
            raw = decrypt_value(det.encrypted_value)
        except Exception:
            continue
        if not raw:
            continue
        # search each page for the value; try exact search then fallback to words-based matching
        for page in pdf:
            rects = []
            try:
                rects = page.search_for(raw) or []
            except Exception:
                rects = []

            if not rects:
                rects = find_rects_for_value(page, raw)

            for r in rects:
                # compute a partial rect that covers the value except the last 4 characters
                try:
                    raw_len = len(raw) if isinstance(raw, str) else 0
                    keep = 4 if raw_len >= 4 else 0
                    if raw_len > 0 and keep > 0:
                        # compute fraction of the rect to redact (left-side)
                        frac = max(0.0, (raw_len - keep) / float(raw_len))
                        # create a new rect covering the left portion
                        redact_x1 = r.x0 + (r.x1 - r.x0) * frac
                        mask_rect = fitz.Rect(r.x0, r.y0, redact_x1, r.y1)
                    else:
                        # nothing to keep -> redact full rect
                        mask_rect = r
                except Exception:
                    mask_rect = r

                # try to add redact annot (for PyMuPDF versions that support apply_redactions)
                try:
                    page.add_redact_annot(mask_rect, fill=(0, 0, 0))
                except Exception:
                    # fall back to storing rects for manual drawing
                    rects_by_page.setdefault(page.number, []).append(mask_rect)
                else:
                    any_annots = True

                # always also store mask_rect for fallback drawing to be safe
                rects_by_page.setdefault(page.number, []).append(mask_rect)
                any_annots = True

    if not any_annots:
        # no exact matches found — return 204 to indicate nothing redacted
        pdf.close()
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="no redaction regions found")

    # apply redactions and save to export dir
    try:
        if hasattr(pdf, "apply_redactions"):
            pdf.apply_redactions()
        else:
            # manual fallback: draw filled rectangles over detected rects
            for pnum, rects in rects_by_page.items():
                try:
                    page = pdf[pnum]
                    for r in rects:
                        try:
                            page.draw_rect(r, color=(0, 0, 0), fill=(0, 0, 0))
                        except Exception:
                            # best-effort: ignore drawing errors per rect
                            logger.exception("failed to draw fallback redaction rect")
                except Exception:
                    logger.exception("failed to draw redaction on page %s", pnum)

        export_dir = conf.EXPORT_DIR
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"redacted_{document_id}.pdf"
        pdf.save(str(out_path), garbage=4, deflate=True)
        pdf.close()
    except Exception:
        logger.exception("failed to apply/save redactions")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to generate redacted PDF")

    # stream file back
    f = open(out_path, "rb")
    return StreamingResponse(
        f, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=\"redacted_{document_id}.pdf\""}
    )
