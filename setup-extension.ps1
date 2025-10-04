# VS Code Extension Setup Script

Write-Host "🎬 DaVinci Resolve AI Assistant - Extension Setup" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# Check Node.js
Write-Host "Checking Node.js..." -NoNewline
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host " ✓ Found: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ from https://nodejs.org"
    exit 1
}

# Check npm
Write-Host "Checking npm..." -NoNewline
if (Get-Command npm -ErrorAction SilentlyContinue) {
    $npmVersion = npm --version
    Write-Host " ✓ Found: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host " ✗ Not found" -ForegroundColor Red
    exit 1
}

# Navigate to extension directory
$extensionDir = Join-Path $PSScriptRoot "resolve-copilot-extension"
if (!(Test-Path $extensionDir)) {
    Write-Host "✗ Extension directory not found: $extensionDir" -ForegroundColor Red
    exit 1
}

Set-Location $extensionDir
Write-Host "📁 Working directory: $extensionDir" -ForegroundColor Cyan
Write-Host ""

# Install npm dependencies
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ npm install failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Compile TypeScript
Write-Host "Compiling TypeScript..." -ForegroundColor Yellow
npm run compile
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Compilation failed" -ForegroundColor Red
    exit 1
}
Write-Host "✓ TypeScript compiled" -ForegroundColor Green
Write-Host ""

# Check if Python backend is set up
$pythonBackend = Join-Path $PSScriptRoot "resolve-ai-assistant"
Write-Host "Checking Python backend..." -NoNewline
if (Test-Path $pythonBackend) {
    Write-Host " ✓ Found" -ForegroundColor Green
    
    # Check if Poetry is installed
    $poetryVenv = Join-Path $pythonBackend ".venv"
    if (Test-Path $poetryVenv) {
        Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Virtual environment not found. Run setup.ps1 in resolve-ai-assistant/" -ForegroundColor Yellow
    }
} else {
    Write-Host " ✗ Not found" -ForegroundColor Red
    Write-Host "  Run setup.ps1 in resolve-ai-assistant/ first" -ForegroundColor Yellow
}
Write-Host ""

# Create icon placeholder
$resourcesDir = Join-Path $extensionDir "resources"
$iconPath = Join-Path $resourcesDir "resolve-icon.png"
if (!(Test-Path $iconPath)) {
    Write-Host "⚠ Icon not found. Extension will use default icon." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ Extension Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Press F5 in VS Code to launch Extension Development Host"
Write-Host "  2. Or package the extension:"
Write-Host "       npm run package"
Write-Host "  3. Install the generated .vsix file:"
Write-Host "       code --install-extension resolve-copilot-assistant-0.1.0.vsix"
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  - Open Copilot Chat (Ctrl+Shift+I)"
Write-Host "  - Type: @resolve create a lower-third"
Write-Host "  - Make sure DaVinci Resolve is running!"
Write-Host ""
Write-Host "Documentation: README.md in resolve-copilot-extension/" -ForegroundColor Gray
