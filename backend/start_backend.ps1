# Start Backend Server with correct Virtual Environment check
$VenvPath = "d:\Deepway\.venv\Scripts\python.exe"
$MainModule = "app.main:app"

Write-Host "🚀 Starting Deepway Backend..." -ForegroundColor Cyan

if (Test-Path $VenvPath) {
    Write-Host "✅ Found Virtual Environment at: $VenvPath" -ForegroundColor Green
    # Use the venv python directly to avoid 'py' global interpretation issues
    & $VenvPath -m uvicorn $MainModule --reload --port 8000
} else {
    Write-Host "❌ Virtual Environment not found at $VenvPath" -ForegroundColor Red
    Write-Host "Attempting global python (May fail if dependencies missing)..." -ForegroundColor Yellow
    python -m uvicorn $MainModule --reload --port 8000
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Server crashed. Press any key to exit..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
