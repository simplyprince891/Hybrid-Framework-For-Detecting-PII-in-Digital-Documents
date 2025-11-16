from fastapi import APIRouter, Body
from app.pii.anomaly import flag_multiple_aadhaar

router = APIRouter()

@router.post("/anomaly/")
def check_anomaly(detections: list = Body(...)):
    suspicious = flag_multiple_aadhaar(detections)
    return {"anomaly": suspicious}
