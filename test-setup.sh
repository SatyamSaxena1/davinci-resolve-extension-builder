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

# Check if GitHub CLI is available
echo ""
echo "🔧 Checking dependencies..."
if command -v gh >/dev/null 2>&1; then
  echo "✅ GitHub CLI found"
  
  # Check if user is authenticated
  if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub CLI authenticated"
  else
    echo "⚠️  GitHub CLI not authenticated. Run 'gh auth login'"
  fi
  
  # Check if copilot extension is available
  if gh extension list 2>/dev/null | grep -q "github/gh-copilot"; then
    echo "✅ GitHub Copilot extension installed"
  else
    echo "⚠️  GitHub Copilot extension not installed. Run 'gh extension install github/gh-copilot'"
  fi
else
  echo "❌ GitHub CLI not found. Install from https://cli.github.com/"
  exit 1
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