# Start the API with the repo virtualenv (repo root is the parent of backend/).
$Root = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $Root ".venv\Scripts\python.exe"
$MainModule = "app.main:app"

Write-Host "Starting Deepway backend..." -ForegroundColor Cyan

Set-Location $PSScriptRoot

if (Test-Path $VenvPath) {
    Write-Host "Using virtualenv: $VenvPath" -ForegroundColor Green
    & $VenvPath -m uvicorn $MainModule --host 127.0.0.1 --port 8000
} else {
    Write-Host "Virtualenv not found at $VenvPath" -ForegroundColor Red
    python -m uvicorn $MainModule --host 127.0.0.1 --port 8000
}
