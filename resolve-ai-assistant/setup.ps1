# Setup Script for Resolve AI Assistant
# Automates initial setup and configuration

Write-Host "DaVinci Resolve AI Assistant - Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Poetry is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$poetryInstalled = Get-Command poetry -ErrorAction SilentlyContinue

if (-not $poetryInstalled) {
    Write-Host "❌ Poetry is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Poetry first:" -ForegroundColor Yellow
    Write-Host "  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ Poetry is installed" -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "✓ $pythonVersion" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies with Poetry..." -ForegroundColor Yellow
poetry install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Setup .env file
Write-Host ""
if (-not (Test-Path ".env")) {
    Write-Host "Setting up environment configuration..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your OpenAI API key" -ForegroundColor Yellow
    Write-Host "   File location: $PWD\.env" -ForegroundColor White
    Write-Host ""
    
    $openEnv = Read-Host "Open .env file now? (y/n)"
    if ($openEnv -eq "y") {
        notepad.exe ".env"
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Check DaVinci Resolve installation
Write-Host ""
Write-Host "Checking DaVinci Resolve installation..." -ForegroundColor Yellow

$resolveScriptPath = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
if (Test-Path $resolveScriptPath) {
    Write-Host "✓ DaVinci Resolve Script API found" -ForegroundColor Green
} else {
    Write-Host "⚠️  DaVinci Resolve Script API not found at default location" -ForegroundColor Yellow
    Write-Host "   If you have Resolve installed elsewhere, update RESOLVE_SCRIPT_API in .env" -ForegroundColor White
}

# Summary
Write-Host ""
Write-Host "Setup Complete! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure your OpenAI API key is set in .env" -ForegroundColor White
Write-Host "2. Open DaVinci Resolve with a project" -ForegroundColor White
Write-Host "3. Run the assistant:" -ForegroundColor White
Write-Host "   poetry run resolve-ai" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or try the examples:" -ForegroundColor Cyan
Write-Host "   poetry run python examples/basic_fusion.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "See QUICKSTART.md for more information" -ForegroundColor White
Write-Host ""
