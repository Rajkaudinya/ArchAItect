# Start Frontend Development Server
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host "🎨 Starting ArchAItect Frontend Development Server" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 69) -ForegroundColor Cyan
Write-Host ""

# Navigate to frontend directory
Set-Location $PSScriptRoot\frontend

# Check if node_modules exists
if (-not (Test-Path ".\node_modules")) {
    Write-Host "⚠️  Node modules not found. Installing..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

# Start the development server
Write-Host "🚀 Starting Vite development server..." -ForegroundColor Green
Write-Host ""
npm run dev
