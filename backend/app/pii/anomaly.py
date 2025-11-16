def flag_multiple_aadhaar(detections):
    aadhaar_numbers = [d["value"] for d in detections if d["type"] == "aadhaar"]
    if len(set(aadhaar_numbers)) > 1:
        return True  # Suspicious: multiple Aadhaar numbers
    return False
