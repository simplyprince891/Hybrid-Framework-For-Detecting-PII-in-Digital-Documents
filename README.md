# Hybrid Framework for PII Detection and Redaction

## Overview
A hybrid rule-based + ML framework to detect and redact Personally Identifiable Information (PII) 
such as Aadhaar, PAN, Passport numbers from PDFs and images.

## Motivation
Manual redaction is error-prone and not scalable. This project focuses on automating PII detection 
while complying with DPDP Act requirements.

## Features
- OCR-based text extraction
- Regex + ML hybrid detection
- Irreversible redaction
- PDF and image support

## Tech Stack
- Python
- OCR (Tesseract)
- Regex
- ML models
- FastAPI (if used)

## How to Run
```bash
pip install -r requirements.txt
python main.py
