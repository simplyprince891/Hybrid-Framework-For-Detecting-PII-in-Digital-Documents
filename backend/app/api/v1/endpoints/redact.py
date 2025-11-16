from fastapi import APIRouter, Body
from app.pii.mask import mask_value
from app.pii.detectors import detect_pii
import yaml

router = APIRouter()

with open("app/pii/registry.yaml") as f:
    REGISTRY = yaml.safe_load(f)

@router.post("/redact/")
def redact_text(text: str = Body(...)):
    detections = detect_pii(text)
    redacted = text
    for d in detections:
        mask_rule = REGISTRY[d["type"]]["mask"]
        masked = mask_value(d["value"], mask_rule)
        redacted = redacted.replace(d["value"], masked)
    return {"redacted": redacted, "detections": detections}
