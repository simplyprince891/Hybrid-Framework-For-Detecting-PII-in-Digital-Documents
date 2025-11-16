import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

from .detectors.patterns import build_detectors
from .detectors.validators import normalize_digits
from .extract import extract_text_from_file


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
	from .detectors.patterns import CONTEXT_KEYWORDS

	detectors = build_detectors()
	normalized = normalize_digits(text)
	findings: List[Dict[str, Any]] = []
	replacements: List[Tuple[int, int, str]] = []

	for detector in detectors:
		for match in detector.pattern.finditer(normalized):
			value = match.group(1)
			is_valid = detector.validator(value) if detector.validator else True
			if not is_valid:
				continue
			start, end = match.span(1)
			context_start = max(0, start - 48)
			context_end = min(len(normalized), end + 48)
			context = normalized[context_start:context_end]
			masked_value = detector.mask(value)

			finding: Dict[str, Any] = {
				"type": detector.name,
				"value": value if not mask else None,
				"masked_value": masked_value,
				"span": [start, end],
				"context": context,
				"risk": detector.risk,
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
		for name in files:
			ext = os.path.splitext(name)[1].lower()
			if ext in SUPPORTED_EXTENSIONS:
				paths.append(os.path.join(root, name))
		if not recursive:
			break
	return paths


def scan_path(input_path: str, options: ScanOptions) -> Dict[str, Any]:
	files = _iter_files(input_path, options.recursive)
	results: List[Dict[str, Any]] = []
	for file_path in files:
		try:
			text = extract_text_from_file(file_path, ocr=options.ocr, ocr_lang=options.ocr_lang)
		except Exception as e:
			results.append({
				"file": file_path,
				"error": str(e),
				"findings": [],
			})
			continue

		findings, redacted_text = scan_text(text, mask=options.mask)
		entry: Dict[str, Any] = {
			"file": file_path,
			"num_findings": len(findings),
			"findings": findings,
		}
		results.append(entry)

		if options.redact_output_dir:
			os.makedirs(options.redact_output_dir, exist_ok=True)
			base = os.path.basename(file_path)
			name, _ = os.path.splitext(base)
			out_path = os.path.join(options.redact_output_dir, f"{name}.redacted.txt")
			with open(out_path, "w", encoding="utf-8", errors="ignore") as f:
				f.write(redacted_text)

	summary: Dict[str, int] = {}
	for r in results:
		for f in r.get("findings", []):
			t = f["type"]
			summary[t] = summary.get(t, 0) + 1
	return {"results": results, "summary": summary}


def write_report(report: Dict[str, Any], output_path: str) -> None:
	os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(report, f, ensure_ascii=False, indent=2) 