from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException, status
from app.pii_scanner.extract import extract_text
from app.pii_scanner.scan import scan_text
from app.db.database import SessionLocal
from app.db import crud
import logging

logger = logging.getLogger("pii_scanner.api.document")
from app import config as conf
from app.tasks import create_job_record, process_upload_background, get_job
import os

router = APIRouter()

# allowed upload extensions
ALLOWED_EXT = {'.pdf', '.docx', '.png', '.jpg', '.jpeg', '.txt', '.csv'}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload/")
async def upload_document(file: UploadFile = File(...), db=Depends(get_db)):
    # validate file extension and size
    filename = file.filename or "unnamed"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > conf.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Uploaded file is too large")

    try:
        text = extract_text(content, filename)
        detections, _ = scan_text(text)
        document_id = crud.create_document_and_detections(db, filename, detections)
    except Exception as e:
        logger.exception("Failed processing upload")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    # structured summary log for this upload
    try:
        types_count = {}
        max_score = 0
        for d in detections:
            types_count[d.get("type")] = types_count.get(d.get("type"), 0) + 1
            if isinstance(d.get("score"), (int, float)) and d.get("score") > max_score:
                max_score = d.get("score")

        logger.info(
            f"upload_summary",
            extra={
                "document_id": document_id,
                "uploaded_filename": file.filename,
                "num_detections": len(detections),
                "types": types_count,
                "max_score": max_score,
            },
        )
    except Exception:
        logger.exception("Failed to emit structured upload summary")

    return {"document_id": document_id, "detections": detections}


@router.post("/upload_async/")
async def upload_document_async(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    filename = file.filename or "unnamed"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > conf.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Uploaded file is too large")

    # save file to uploads dir and create a job
    uploads_dir = conf.DATA_DIR / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    job_id = create_job_record(filename)
    saved_path = uploads_dir / f"{job_id}_{filename}"
    try:
        with open(saved_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.exception("Failed to save uploaded file")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save file")

    # schedule background processing
    background_tasks.add_task(process_upload_background, job_id, str(saved_path), filename)
    return {"job_id": job_id}


@router.get("/upload_status/{job_id}")
async def upload_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return {"error": "job not found"}
    return job
