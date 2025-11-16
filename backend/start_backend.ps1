<#
PowerShell launcher to start the backend server in a new cmd window.

Usage:
- Right-click -> Run with PowerShell, or
- From PowerShell: powershell -ExecutionPolicy Bypass -File .\start_backend.ps1

This script opens a new cmd.exe window and runs uvicorn so the server stays running.
#>

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

$cmd = "/k cd /d \"$scriptDir\" && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Process -FilePath "cmd.exe" -ArgumentList $cmd -WorkingDirectory $scriptDir -WindowStyle Normal
Write-Output "Launched backend server in a new window (if python/uvicorn are on PATH)."
