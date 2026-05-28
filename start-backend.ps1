# Start Backend Server
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🚀 Starting ArchAItect Backend Server" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location $PSScriptRoot\backend

# Check if virtual environment exists
if (-not (Test-Path ".\venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    
    Write-Host "📥 Downloading spaCy language model..." -ForegroundColor Cyan
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
    
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔵 Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Start the server
Write-Host "🚀 Starting server..." -ForegroundColor Green
Write-Host ""
python app.py
