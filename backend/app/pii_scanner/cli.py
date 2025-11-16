# moved from src/pii_scanner/cli.py
import argparse
from typing import Optional
from .scan import scan_path, write_report, ScanOptions

def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(prog="pii-scanner", description="Detect Indian PII in documents")
	sub = parser.add_subparsers(dest="command", required=True)

	scan = sub.add_parser("scan", help="Scan files or directories for PII")
	scan.add_argument("--input", required=True, help="File or directory to scan")
	scan.add_argument("--recursive", action="store_true", help="Recurse into subdirectories")
	scan.add_argument("--ocr", action="store_true", help="Enable OCR for images and scanned PDFs")
	scan.add_argument("--ocr-lang", default="eng", help="Tesseract languages, e.g., 'eng+hin'")
	scan.add_argument("--mask", action="store_true", help="Mask PII values in outputs")
	scan.add_argument("--output", default="report.json", help="Path to JSON report output")
	scan.add_argument("--redact-output-dir", default="", help="Directory to write redacted text files")
	return parser.parse_args()


def main() -> None:
	args = _parse_args()
	if args.command == "scan":
		options = ScanOptions(
			ocr=args.ocr,
			ocr_lang=args.ocr_lang,
			mask=args.mask,
			redact_output_dir=args.redact_output_dir,
			recursive=args.recursive,
		)
		report = scan_path(args.input, options)
		write_report(report, args.output)


if __name__ == "__main__":
	main()
