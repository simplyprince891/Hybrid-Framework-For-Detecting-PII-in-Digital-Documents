# moved from src/pii_scanner/scan.py
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

from .detectors.patterns import build_detectors
from .detectors.validators import normalize_digits
from .extract import extract_text

SUPPORTED_EXTENSIONS = {
	".txt", ".csv", ".log", ".json", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"
}

@dataclass
class ScanOptions:
	ocr: bool = False
	ocr_lang: str = "eng"
	mask: bool = True
	redact_output_dir: str = ""
	recursive: bool = True

def _apply_redactions(text: str, replacements: List[Tuple[int, int, str]]) -> str:
	if not replacements:
		return text
	replacements.sort(key=lambda x: x[0])
	result_parts = []
	cursor = 0
	for start, end, masked in replacements:
		result_parts.append(text[cursor:start])
		result_parts.append(masked)
		cursor = end
	result_parts.append(text[cursor:])
	return "".join(result_parts)

def scan_text(text: str, mask: bool = True) -> Tuple[List[Dict[str, Any]], str]:
	import logging
	logger = logging.getLogger("pii_scanner.scan")
	logging.basicConfig(level=logging.INFO)
	from .detectors.patterns import CONTEXT_KEYWORDS
	detectors = build_detectors()
	normalized = normalize_digits(text or "")
	if normalized is None:
		normalized = ""
	logger.info(f"Normalized text: {repr(normalized)}")
	findings: List[Dict[str, Any]] = []
	replacements: List[Tuple[int, int, str]] = []

	for detector in detectors:
		if not isinstance(normalized, str):
			normalized = str(normalized) if normalized is not None else ""
		matches = list(detector.pattern.finditer(normalized))
		logger.info(f"Detector {detector.name}: {len(matches)} matches")
		for match in matches:
			value = match.group(1)
			is_valid = detector.validator(value) if detector.validator else True
			logger.info(f"  Match: {value}, valid={is_valid}")
			start, end = match.span(1)
			context_start = max(0, start - 48)
			context_end = min(len(normalized), end + 48)
			context = normalized[context_start:context_end]
			masked_value = detector.mask(value)

			# Scoring system
			score = 1  # base score for regex match
			# Check for context keyword
			context_text = context.lower()
			if any(kw.lower() in context_text for kw in detector.keywords):
				score += 2
			if is_valid:
				score += 2

			finding: Dict[str, Any] = {
				"type": detector.name,
				"value": value,
				"masked_value": masked_value,
				"span": [start, end],
				"context": context,
				"risk": detector.risk,
				"score": score,
			}
			findings.append(finding)
			replacements.append((start, end, masked_value))

	redacted_text = _apply_redactions(normalized, replacements) if mask else normalized
	return findings, redacted_text

def _iter_files(input_path: str, recursive: bool) -> List[str]:
	paths: List[str] = []
	if os.path.isfile(input_path):
		ext = os.path.splitext(input_path)[1].lower()
		if ext in SUPPORTED_EXTENSIONS:
			paths.append(input_path)
		return paths
	for root, dirs, files in os.walk(input_path):
		for file in files:
			if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
				paths.append(os.path.join(root, file))
	return paths

def scan_path(input_path: str, options: ScanOptions) -> Dict[str, Any]:
	files = _iter_files(input_path, options.recursive)
	all_findings = []
	for file_path in files:
		with open(file_path, "rb") as f:
			text = extract_text(f.read(), file_path)
			findings, _ = scan_text(text, mask=options.mask)
			all_findings.extend(findings)
	return {"findings": all_findings}

def write_report(report: Dict[str, Any], output_path: str):
	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(report, f, ensure_ascii=False, indent=2)
