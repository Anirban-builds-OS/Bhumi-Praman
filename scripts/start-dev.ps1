# start-dev.ps1
# Starts the Bhumi Praman backend and frontend together for local development.
# Run from the repo root:  .\scripts\start-dev.ps1
#
# Assumes you've already run the one-time setup in README.md (venv created,
# pip install -r requirements.txt, npm install, seed script run at least once).

$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Starting Bhumi Praman backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList `
    "-NoExit", "-Command", `
    "cd '$repoRoot\backend'; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --port 8000"

Start-Sleep -Seconds 2

Write-Host "Starting Bhumi Praman frontend on http://localhost:5173 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList `
    "-NoExit", "-Command", `
    "cd '$repoRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "Two new PowerShell windows have opened -- backend and frontend." -ForegroundColor Green
Write-Host "Once both report 'ready', open http://localhost:5173 in your browser." -ForegroundColor Green
Write-Host "Sample login: OFC-KAM-1102 / Officer@123 (see README.md for all demo accounts)." -ForegroundColor Green
