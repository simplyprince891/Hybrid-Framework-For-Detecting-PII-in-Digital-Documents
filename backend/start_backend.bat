@echo off
REM Batch launcher to start backend in a new window
cd /d %~dp0
start "Backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
