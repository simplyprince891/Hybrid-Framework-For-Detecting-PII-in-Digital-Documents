import re
from dataclasses import dataclass
from typing import Callable, Optional, Pattern, Dict, List

from .validators import (
	is_valid_aadhaar,
	is_valid_pan,
	is_valid_passport,
	is_valid_epic,
	is_valid_dl,
	is_valid_ifsc,
	is_valid_gstin,
	is_valid_tan,
	is_valid_email,
	is_valid_indian_mobile,
	is_valid_upi,
	normalize_digits,
)


@dataclass
class Detector:
	name: str
	pattern: Pattern[str]
	validator: Optional[Callable[[str], bool]]
	mask: Callable[[str], str]
	keywords: List[str]
	risk: int  # 1-5


def _mask_keep_last4(value: str) -> str:
	clean = re.sub(r"\s", "", value)
	return "*" * max(0, len(clean) - 4) + clean[-4:]


def _mask_keep_first3_last1(value: str) -> str:
	clean = re.sub(r"\s", "", value)
	if len(clean) <= 4:
		return "*" * len(clean)
	return clean[:3] + "*" * (len(clean) - 4) + clean[-1]


def _mask_email(value: str) -> str:
	local, _, domain = value.partition("@")
	if len(local) <= 2:
		masked_local = "*" * len(local)
	else:
		masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
	return f"{masked_local}@{domain}"


def _mask_generic(value: str) -> str:
	return "*" * len(value)


CONTEXT_KEYWORDS: Dict[str, List[str]] = {
	"AADHAAR": ["aadhaar", "uidai", "uid"],
	"PAN": ["pan", "permanent account"],
	"PASSPORT": ["passport"],
	"EPIC": ["voter", "epic"],
	"DL": ["driver", "driving", "dl"],
	"IFSC": ["ifsc"],
	"GSTIN": ["gstin", "gst"],
	"TAN": ["tan"],
	"PHONE": ["phone", "mobile", "contact"],
	"EMAIL": ["email", "mail"],
	"UPI": ["upi", "vpa"],
}


def build_detectors() -> List[Detector]:
	return [
		Detector(
			name="AADHAAR",
			pattern=re.compile(r"(?<!\d)([2-9][0-9]{3}\s?[0-9]{4}\s?[0-9]{4})(?!\d)"),
			validator=lambda s: is_valid_aadhaar(re.sub(r"\s", "", s)),
			mask=_mask_keep_last4,
			keywords=CONTEXT_KEYWORDS["AADHAAR"],
			risk=5,
		),
		Detector(
			name="PAN",
			pattern=re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b"),
			validator=is_valid_pan,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["PAN"],
			risk=4,
		),
		Detector(
			name="PASSPORT",
			pattern=re.compile(r"\b([A-PR-WY][0-9]{7})\b"),
			validator=is_valid_passport,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["PASSPORT"],
			risk=4,
		),
		Detector(
			name="EPIC",
			pattern=re.compile(r"\b([A-Z]{3}[0-9]{7})\b"),
			validator=is_valid_epic,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["EPIC"],
			risk=3,
		),
		Detector(
			name="DL",
			pattern=re.compile(r"\b([A-Z]{2}-?[0-9]{2}-?[0-9]{11,12})\b"),
			validator=is_valid_dl,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["DL"],
			risk=3,
		),
		Detector(
			name="IFSC",
			pattern=re.compile(r"\b([A-Z]{4}0[A-Z0-9]{6})\b"),
			validator=is_valid_ifsc,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["IFSC"],
			risk=2,
		),
		Detector(
			name="GSTIN",
			pattern=re.compile(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9])\b"),
			validator=is_valid_gstin,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["GSTIN"],
			risk=3,
		),
		Detector(
			name="TAN",
			pattern=re.compile(r"\b([A-Z]{4}[0-9]{5}[A-Z])\b"),
			validator=is_valid_tan,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["TAN"],
			risk=2,
		),
		Detector(
			name="UPI",
			pattern=re.compile(r"\b([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})\b"),
			validator=is_valid_upi,
			mask=_mask_keep_first3_last1,
			keywords=CONTEXT_KEYWORDS["UPI"],
			risk=2,
		),
		Detector(
			name="PHONE",
			pattern=re.compile(r"(?<!\d)((?:\+91[\-\s]?)?[6-9][0-9]{9})(?!\d)"),
			validator=is_valid_indian_mobile,
			mask=_mask_keep_last4,
			keywords=CONTEXT_KEYWORDS["PHONE"],
			risk=2,
		),
		Detector(
			name="EMAIL",
			pattern=re.compile(r"\b([a-zA-Z0-9_.+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-.]+)\b"),
			validator=is_valid_email,
			mask=_mask_email,
			keywords=CONTEXT_KEYWORDS["EMAIL"],
			risk=2,
		),
	] 