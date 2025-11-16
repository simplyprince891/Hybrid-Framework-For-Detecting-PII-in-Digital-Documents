r"""Smoke test script for the backend API.

Creates a small PDF containing a PII-like string, uploads it via the async upload endpoint,
polls the job until completion, then requests the redacted PDF and writes it to a temp file.

Run from repository root (the script uses the app TestClient so it runs in-process):

python backend\scripts\smoke_test.py

"""
import time
import tempfile
import os
import sys
import io
from pathlib import Path
import fitz
from fastapi.testclient import TestClient

# Import the FastAPI app from the project
from pathlib import Path
import sys

# Ensure backend package dir is on sys.path so `import app` works when running from repo root
backend_dir = str(Path(__file__).resolve().parents[1])
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
# Ensure current working directory is backend so relative resources (like registry.yaml) are found
os.chdir(backend_dir)

from app.main import app

client = TestClient(app)


def make_pdf(path: Path, text: str):
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(72, 72, 540, 720)
    # simple text insert
    page.insert_textbox(rect, text, fontsize=12)
    doc.save(str(path))
    doc.close()


def main():
    tmpdir = Path(tempfile.mkdtemp(prefix="pii_smoke_"))
    pdf_path = tmpdir / "sample_pii.pdf"
    pii_text = "This document contains Aadhaar 1234 5678 9012 and email smoke@example.com"
    make_pdf(pdf_path, pii_text)
    print(f"Created test PDF: {pdf_path}")

    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        resp = client.post("/api/v1/upload_async/", files=files)

    if resp.status_code != 200:
        print("Upload failed", resp.status_code, resp.text)
        sys.exit(2)

    data = resp.json()
    job_id = data.get("job_id")
    if not job_id:
        print("No job_id returned from upload_async", data)
        sys.exit(2)

    print("Upload queued, job_id:", job_id)

    # poll job status
    doc_id = None
    for i in range(60):
        r2 = client.get(f"/api/v1/upload_status/{job_id}")
        if r2.status_code != 200:
            print("Failed to get job status", r2.status_code, r2.text)
            sys.exit(2)
        job = r2.json()
        status = job.get("status")
        print(f"[{i}] job status: {status}")
        if status == "done":
            result = job.get("result") or {}
            doc_id = result.get("document_id")
            print("Job result:", result)
            break
        if status == "error":
            print("Job failed:", job.get("error"))
            sys.exit(2)
        time.sleep(0.5)

    if not doc_id:
        print("Timed out waiting for job to finish")
        sys.exit(2)

    print("Job complete, document_id:", doc_id)

    # request redacted PDF
    r3 = client.get(f"/api/v1/export/redacted_pdf/?document_id={doc_id}")
    if r3.status_code == 204:
        print("No redactions were found (204)")
        sys.exit(0)
    if r3.status_code != 200:
        print("Failed to get redacted PDF", r3.status_code, r3.text)
        sys.exit(2)

    out_path = tmpdir / f"redacted_{doc_id}.pdf"
    with open(out_path, "wb") as out:
        out.write(r3.content)

    print("Saved redacted PDF:", out_path, "size=", out_path.stat().st_size)
    if out_path.stat().st_size > 0:
        print("Smoke test succeeded")
        sys.exit(0)
    else:
        print("Redacted PDF empty")
        sys.exit(2)


if __name__ == "__main__":
    main()
