# Test script for DaVinci Resolve Extension Builder (PowerShell)

Write-Host "🧪 Testing DaVinci Resolve Extension Builder" -ForegroundColor Cyan
Write-Host "==============================================`n" -ForegroundColor Cyan

# Check if required files exist
Write-Host "📁 Checking project files..." -ForegroundColor Yellow
$files = @("generate-resolve-addon.sh", "generate-resolve-addon.ps1", "PLAN.md", "README.md", "LICENSE")
$allFilesExist = $true

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    exit 1
}

# Check if GitHub CLI is available
Write-Host "`n🔧 Checking dependencies..." -ForegroundColor Yellow
if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "✅ GitHub CLI found" -ForegroundColor Green
    
    # Check if user is authenticated
    try {
        gh auth status 2>$null | Out-Null
        Write-Host "✅ GitHub CLI authenticated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  GitHub CLI not authenticated. Run 'gh auth login'" -ForegroundColor Yellow
    }
    
    # Check if copilot extension is available
    $extensions = gh extension list 2>$null
    if ($extensions -match "github/gh-copilot") {
        Write-Host "✅ GitHub Copilot extension installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  GitHub Copilot extension not installed. Run 'gh extension install github/gh-copilot'" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ GitHub CLI not found. Install from https://cli.github.com/" -ForegroundColor Red
    exit 1
}

Write-Host "`n📋 Available extension types:" -ForegroundColor Cyan
Write-Host "  - scripting  (Python DaVinciResolveScript API)" -ForegroundColor White
Write-Host "  - fusion     (Lua Fusion effects)" -ForegroundColor White
Write-Host "  - ofx        (C++ OpenFX plugins)" -ForegroundColor White
Write-Host "  - dctl       (DCTL color transforms)" -ForegroundColor White

Write-Host "`n🎯 Example usage:" -ForegroundColor Cyan
Write-Host "  PowerShell:    .\generate-resolve-addon.ps1 -Target scripting -OutDir my-project" -ForegroundColor White
Write-Host "  Bash:          ./generate-resolve-addon.sh PLAN.md scripting my-project" -ForegroundColor White

Write-Host "`n✅ Setup test completed!" -ForegroundColor Green