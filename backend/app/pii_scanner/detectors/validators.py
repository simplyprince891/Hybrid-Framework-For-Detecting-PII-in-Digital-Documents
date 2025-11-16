# moved from src/pii_scanner/detectors/validators.py
import re
from typing import Optional
_d_table = [
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
	[1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
	[2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
	[3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
	[4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
	[5, 6, 7, 8, 9, 0, 1, 2, 3, 4],
	[6, 7, 8, 9, 5, 1, 2, 3, 4, 0],
	[7, 8, 9, 5, 6, 2, 3, 4, 0, 1],
	[8, 9, 5, 6, 7, 3, 4, 0, 1, 2],
	[9, 5, 6, 7, 8, 4, 0, 1, 2, 3],
]
_p_table = [
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
	[1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
	[5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
	[8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
	[9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
	[4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
	[2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
	[7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]
_inv_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
def _verhoeff_checksum(number: str) -> int:
	c = 0
	for i, item in enumerate(reversed(number)):
		digit = int(item)
		c = _d_table[c][_p_table[(i + 1) % 8][digit]]
	return _inv_table[c]
def is_valid_aadhaar(aadhaar: str) -> bool:
	# DEMO: Allow any 12-digit number starting 2-9
	return bool(re.fullmatch(r"[2-9]{1}[0-9]{11}", aadhaar))
def is_valid_pan(pan: str) -> bool:
	if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan):
		return False
	return True
def is_valid_passport(passport: str) -> bool:
	return re.fullmatch(r"[A-PR-WY][0-9]{7}", passport) is not None
def is_valid_dl(dl: str) -> bool:
	return re.fullmatch(r"[A-Z]{2}-?[0-9]{2}-?[0-9]{11,12}", dl) is not None
def is_valid_epic(epic: str) -> bool:
	return True

def is_valid_ifsc(ifsc: str) -> bool:
	# DEMO: Allow any string for IFSC
	return True

def is_valid_gstin(gstin: str) -> bool:
	return True

def is_valid_tan(tan: str) -> bool:
	return True

def is_valid_email(email: str) -> bool:
	return True

def is_valid_indian_mobile(mobile: str) -> bool:
	# Strict validation: Indian mobile numbers (10 digits, starts with 6-9, optional +91)
	mobile = re.sub(r"[\s\-]", "", mobile)
	if mobile.startswith("+91"):
		mobile = mobile[3:]
	return bool(re.fullmatch(r"[6-9][0-9]{9}", mobile))

def is_valid_upi(upi: str) -> bool:
	return True

def normalize_digits(text: str) -> str:
	# DEMO: Do not normalize, just return the text as-is
	return text
