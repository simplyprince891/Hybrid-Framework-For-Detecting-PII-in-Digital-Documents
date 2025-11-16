import uuid
import threading
import os
import logging
from typing import Dict, Any
from . import config as conf
from app.pii_scanner.extract import extract_text
from app.pii_scanner.scan import scan_text
from app.db.database import SessionLocal
from app.db import crud

logger = logging.getLogger("pii_scanner.tasks")

# simple in-memory job store
_jobs_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def create_job_record(filename: str) -> str:
    job_id = str(uuid.uuid4())
    with _jobs_lock:
        _jobs[job_id] = {
            "status": "pending",
            "filename": filename,
            "result": None,
            "error": None,
        }
    return job_id


def get_job(job_id: str):
    with _jobs_lock:
        return _jobs.get(job_id)


def _update_job(job_id: str, **vals):
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(vals)


def process_upload_background(job_id: str, file_path: str, filename: str):
    logger.info("Starting background processing", extra={"job_id": job_id, "uploaded_filename": filename})
    _update_job(job_id, status="running")
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        text = extract_text(content, filename)
        detections, _ = scan_text(text)


        # store detections in DB and keep original file
        db = SessionLocal()
        try:
            # move saved file to a permanent originals directory
            originals_dir = conf.DATA_DIR / "originals"
            originals_dir.mkdir(parents=True, exist_ok=True)
            dest_path = originals_dir / f"{job_id}_{filename}"
            try:
                # move file
                os.replace(file_path, str(dest_path))
            except Exception:
                # fallback to copy
                import shutil
                shutil.copyfile(file_path, str(dest_path))

            # store the permanent path as the document filename so we can find it later
            document_id = crud.create_document_and_detections(db, str(dest_path), detections)
        finally:
            db.close()

        _update_job(job_id, status="done", result={"document_id": document_id, "detections_count": len(detections), "file_path": str(dest_path)})

        # structured log
        try:
            types_count = {}
            max_score = 0
            for d in detections:
                types_count[d.get("type")] = types_count.get(d.get("type"), 0) + 1
                if isinstance(d.get("score"), (int, float)) and d.get("score") > max_score:
                    max_score = d.get("score")
            logger.info("upload_summary", extra={"job_id": job_id, "document_id": document_id, "uploaded_filename": filename, "num_detections": len(detections), "types": types_count, "max_score": max_score})
        except Exception:
            logger.exception("Failed to emit structured upload summary in background")

    except Exception as e:
        logger.exception("Background processing failed")
        _update_job(job_id, status="error", error=str(e))
    finally:
        # optional: cleanup saved file
        try:
            os.remove(file_path)
        except Exception:
            pass
