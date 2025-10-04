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

# Check platform compatibility
Write-Host "`n🔧 Checking platform compatibility..." -ForegroundColor Yellow
Write-Host "✅ PowerShell available" -ForegroundColor Green

if (Get-Command bash -ErrorAction SilentlyContinue) {
    Write-Host "✅ Bash shell found (cross-platform compatibility)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Bash shell not found (Linux/macOS scripts may not work)" -ForegroundColor Yellow
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