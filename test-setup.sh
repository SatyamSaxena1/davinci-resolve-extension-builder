#!/usr/bin/env bash

# Test script for DaVinci Resolve Extension Builder

echo "🧪 Testing DaVinci Resolve Extension Builder"
echo "=============================================="

# Check if required files exist
echo "📁 Checking project files..."
files=("generate-resolve-addon.sh" "generate-resolve-addon.ps1" "PLAN.md" "README.md" "LICENSE")
for file in "${files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "✅ $file exists"
  else
    echo "❌ $file missing"
    exit 1
  fi
done

# Check if bash is available
echo ""
echo "🔧 Checking shell compatibility..."
if command -v bash >/dev/null 2>&1; then
  echo "✅ Bash shell found"
else
  echo "⚠️  Bash shell not found (Linux/macOS compatibility may be limited)"
fi

# Check if PowerShell is available
if command -v pwsh >/dev/null 2>&1 || command -v powershell >/dev/null 2>&1; then
  echo "✅ PowerShell found"
else
  echo "⚠️  PowerShell not found (Windows compatibility may be limited)"
fi

echo ""
echo "📋 Available extension types:"
echo "  - scripting  (Python DaVinciResolveScript API)"
echo "  - fusion     (Lua Fusion effects)"
echo "  - ofx        (C++ OpenFX plugins)"
echo "  - dctl       (DCTL color transforms)"

echo ""
echo "🎯 Example usage:"
echo "  Linux/macOS:   ./generate-resolve-addon.sh PLAN.md scripting my-project"
echo "  Windows:       .\\generate-resolve-addon.ps1 -Target scripting -OutDir my-project"

echo ""
echo "✅ Setup test completed!"