#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
PLAN_FILE="${1:-PLAN.md}"           # pass a custom plan path as arg1, else PLAN.md
TARGET="${2:-scripting}"            # one of: scripting | fusion | ofx | dctl
OUT_DIR="${3:-resolve-addon}"       # output folder for generated project
MODEL_FLAG="${MODEL_FLAG:-}"        # e.g., MODEL_FLAG="--model gpt-4o-mini" or empty

# --- Checks ---
command -v gh >/dev/null 2>&1 || { echo "❌ GitHub CLI (gh) not found. Install: https://cli.github.com/"; exit 1; }
if ! gh extension list 2>/dev/null | grep -q "github/gh-copilot"; then
  echo "ℹ️ Installing 'gh-copilot' extension..."
  gh extension install github/gh-copilot
fi
[[ -f "$PLAN_FILE" ]] || { echo "❌ Plan file not found: $PLAN_FILE"; exit 1; }

# --- Normalize TARGET ---
case "$TARGET" in
  scripting|fusion|ofx|dctl) ;;
  *) echo "❌ TARGET must be one of: scripting | fusion | ofx | dctl"; exit 1 ;;
esac

# --- Prompt to Copilot ---
read -r -d '' PROMPT <<'P_EOF'
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

P_EOF

# --- PROJECT_NAME by target ---
case "$TARGET" in
  scripting) PROJECT_NAME="resolve-scripting-starter" ;;
  fusion)    PROJECT_NAME="resolve-fusion-fuse-starter" ;;
  ofx)       PROJECT_NAME="resolve-ofx-starter" ;;
  dctl)      PROJECT_NAME="resolve-dctl-starter" ;;
esac

# --- Compose final chat message including the plan ---
PLAN_CONTENT=$(cat "$PLAN_FILE")
FINAL_PROMPT=$(cat <<EOF
$PROMPT

Target: $TARGET
PROJECT_NAME: $PROJECT_NAME

Plan:
---
$PLAN_CONTENT
---
EOF
)

# --- Call Copilot and capture base64 zip ---
echo "🤖 Asking Copilot to generate $PROJECT_NAME from $PLAN_FILE (target: $TARGET)..."
RAW_OUT_FILE="$(mktemp)"
# Note: you can set MODEL_FLAG env var to choose a model, e.g. MODEL_FLAG="--model gpt-4o-mini"
# gh copilot chat -p "<prompt>" prints the assistant reply to stdout.
gh copilot chat -p "$FINAL_PROMPT" $MODEL_FLAG > "$RAW_OUT_FILE"

# --- Extract clean base64 (strip anything non-base64 just in case) ---
# We expect only base64, but sanitize anyway:
BASE64_FILE="$(mktemp)"
# Keep base64 characters only, no spaces; then rewrap lines at 76 chars for base64 -d safety
tr -d '\r\n ' < "$RAW_OUT_FILE" | tr -cd 'A-Za-z0-9+/=' | fold -w 76 > "$BASE64_FILE"

# --- Decode and unzip ---
ZIP_FILE="$(mktemp --suffix=.zip)"
if ! base64 -d "$BASE64_FILE" > "$ZIP_FILE" 2>/dev/null; then
  echo "❌ Could not decode base64. Saving raw response to copilot_raw.txt for inspection."
  cp "$RAW_OUT_FILE" ./copilot_raw.txt
  exit 1
fi

# Prepare output dir
mkdir -p "$OUT_DIR"
unzip -q -o "$ZIP_FILE" -d "$OUT_DIR"

# --- Post-process: ensure project folder is as expected ---
if [[ ! -d "$OUT_DIR/$PROJECT_NAME" ]]; then
  # If Copilot nested differently, try to detect top-level single folder
  TOP=$(find "$OUT_DIR" -mindepth 1 -maxdepth 1 -type d | head -n1 || true)
  if [[ -n "$TOP" && "$TOP" != "$OUT_DIR/$PROJECT_NAME" ]]; then
    mv "$TOP" "$OUT_DIR/$PROJECT_NAME"
  fi
fi

echo "✅ Generated: $OUT_DIR/$PROJECT_NAME"
echo "📄 You can now:  cd \"$OUT_DIR/$PROJECT_NAME\" && cat README.md"