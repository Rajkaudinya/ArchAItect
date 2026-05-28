# ArchAItect Setup Script
# This script installs all dependencies and initializes NLP models

Write-Host "🏛️ ArchAItect - Microservice Architecture AI System" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Check Python version
Write-Host "🐍 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found! Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}
Write-Host "   $pythonVersion" -ForegroundColor Green
Write-Host ""

# Navigate to backend
Set-Location -Path "$PSScriptRoot\backend"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host ""
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "   This may take several minutes on first run..." -ForegroundColor Gray
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Download spaCy model
Write-Host ""
Write-Host "🧠 Downloading NLP models (spaCy)..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  SpaCy model download failed, but continuing..." -ForegroundColor Yellow
}

# Download NLTK data
Write-Host ""
Write-Host "📖 Downloading NLTK data..." -ForegroundColor Yellow
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"

# Test imports
Write-Host ""
Write-Host "✅ Testing imports..." -ForegroundColor Yellow
python -c @"
import fastapi
import uvicorn
import spacy
from sentence_transformers import SentenceTransformer
import torch
print('   All core dependencies imported successfully!')
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some imports failed. The system will use fallback modes." -ForegroundColor Yellow
} else {
    Write-Host "   ✅ All systems operational!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 60
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the backend server:" -ForegroundColor Cyan
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   python run.py" -ForegroundColor White
Write-Host ""
Write-Host "To start the frontend:" -ForegroundColor Cyan
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm install" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
