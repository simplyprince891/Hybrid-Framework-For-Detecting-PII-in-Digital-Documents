from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.v1.endpoints import document, redact, feedback, report, anomaly

# initialize structured logging
from app import logging_config
logging_config.configure_logging()

app = FastAPI()
app.include_router(document.router, prefix="/api/v1")
app.include_router(redact.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(report.router, prefix="/api/v1")
app.include_router(anomaly.router, prefix="/api/v1")

# If a built frontend is present, serve it at the root so the UI and API are on the same origin.
frontend_build = Path(__file__).resolve().parents[2] / "frontend" / "build"
if frontend_build.exists():
	app.mount("/", StaticFiles(directory=str(frontend_build), html=True), name="frontend")

# Ensure DB schema is up-to-date for local/dev runs (best-effort)
try:
	from app.db.init_db import ensure_schema
	ensure_schema()
except Exception:
	pass

# To run: uvicorn app.main:app --reload
