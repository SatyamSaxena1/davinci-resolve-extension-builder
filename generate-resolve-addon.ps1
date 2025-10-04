param(
  [string]$PlanFile = "PLAN.md",
  [ValidateSet("scripting","fusion","ofx","dctl")]
  [string]$Target = "scripting",
  [string]$OutDir = "resolve-addon",
  [string]$ModelFlag = ""  # e.g. '--model gpt-4o-mini'
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  Write-Error "GitHub CLI (gh) not found. Install: https://cli.github.com/"
}

# Install gh-copilot if missing
$ext = gh extension list 2>$null
if ($ext -notmatch "github/gh-copilot") {
  Write-Host "Installing gh-copilot extension..."
  gh extension install github/gh-copilot
}

if (-not (Test-Path $PlanFile)) {
  Write-Error "Plan file not found: $PlanFile"
}

switch ($Target) {
  "scripting" { $ProjectName = "resolve-scripting-starter" }
  "fusion"    { $ProjectName = "resolve-fusion-fuse-starter" }
  "ofx"       { $ProjectName = "resolve-ofx-starter" }
  "dctl"      { $ProjectName = "resolve-dctl-starter" }
}

$Prompt = @'
You are a precise code generator. Read the plan below and create a production-ready starter
project for the specified DaVinci Resolve development path. Return ONLY a base64-encoded ZIP
(no prose, no backticks). The ZIP must contain a minimal, runnable scaffold with README and
clear instructions.

Requirements:
1) Include a top-level README.md with quickstart steps.
2) Provide a simple but real "Hello" example for the chosen path:
   - scripting: Python script using DaVinciResolveScript to add a marker, import a clip, and render.
   - fusion: a Fuse (Lua) with parameters and a pass-through/brightness tweak; plus install notes.
   - ofx: C++ OFX skeleton with build files (CMake) + stub render callback; platform notes.
   - dctl: .dctl with parameter block (eg. contrast) and README showing install paths.
3) Add a scripts/ or tools/ folder with helper scripts to build/run/install.
4) Use portable paths and provide Windows/macOS/Linux notes where relevant.
5) Include .gitignore and a LICENSE (MIT).
6) Keep dependencies minimal; where needed, document them in README.
7) Project should be in a single folder named PROJECT_NAME.

Output protocol (critical):
- Respond with ONLY raw base64 data of a zip file (no markdown, no explanation).
- The zip root must be named PROJECT_NAME.
'@

$PlanContent = Get-Content -Raw -Path $PlanFile
$FinalPrompt = @"
$Prompt

Target: $Target
PROJECT_NAME: $ProjectName

Plan:
---
$PlanContent
---
"@

Write-Host "🤖 Asking Copilot to generate $ProjectName from $PlanFile (target: $Target)..."
$rawOutFile = New-TemporaryFile

# Compose args
$argsList = @("copilot","chat","-p",$FinalPrompt)
if ($ModelFlag -ne "") { $argsList += $ModelFlag.Split(" ") }

# Invoke Copilot
& gh @argsList | Out-File -Encoding ascii $rawOutFile

# Clean to base64 (remove spaces/newlines, keep base64 chars)
$raw = Get-Content -Raw $rawOutFile
$clean = ($raw -replace '\s','') -replace '[^A-Za-z0-9+/=]',''

# Decode and unzip
$zipPath = Join-Path $env:TEMP ("scaffold_{0}.zip" -f ([guid]::NewGuid().ToString("N")))
try {
  [IO.File]::WriteAllBytes($zipPath, [Convert]::FromBase64String($clean))
} catch {
  Copy-Item $rawOutFile -Destination ".\copilot_raw.txt"
  throw "Could not decode base64. Raw saved to copilot_raw.txt"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Expand-Archive -Path $zipPath -DestinationPath $OutDir -Force

# Normalize folder name if needed
$expected = Join-Path $OutDir $ProjectName
if (-not (Test-Path $expected)) {
  $dirs = Get-ChildItem -Directory $OutDir
  if ($dirs.Count -eq 1) {
    Rename-Item -Path $dirs[0].FullName -NewName $ProjectName -Force
  }
}

Write-Host "✅ Generated: $expected"
Write-Host "📄 Next: cd `"$expected`" ; type README.md"