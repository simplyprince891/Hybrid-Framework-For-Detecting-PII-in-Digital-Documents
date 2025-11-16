import os
import io
import time
import tempfile
from fastapi.testclient import TestClient
from app.main import app
from app import config as conf

client = TestClient(app)


def test_upload_async_and_status_cycle(tmp_path):
    # create a small text file to upload
    p = tmp_path / "sample.txt"
    p.write_text("This is a test Aadhaar 1234 5678 9012 and email test@example.com")

    with open(p, "rb") as f:
        files = {"file": ("sample.txt", f, "text/plain")}
        r = client.post("/api/v1/upload_async/", files=files)
    assert r.status_code == 200
    data = r.json()
    assert "job_id" in data
    job_id = data["job_id"]

    # poll until done or timeout
    for _ in range(20):
        r2 = client.get(f"/api/v1/upload_status/{job_id}")
        assert r2.status_code == 200
        job = r2.json()
        if job.get("status") == "done" or job.get("status") == "error":
            break
        time.sleep(0.2)

    assert job.get("status") in ("done", "error")


def test_export_json_csv_no_document():
    # requesting export for non-existent document should return empty lists or 200 with zero items
    r = client.get("/api/v1/export/json/?document_id=999999")
    assert r.status_code in (200, 404)

    r2 = client.get("/api/v1/export/csv/?document_id=999999")
    assert r2.status_code in (200, 404)
