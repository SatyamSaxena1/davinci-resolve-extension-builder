# Fixing "ModuleNotFoundError" in DaVinci Resolve Console

## The Problem

When you try to run the assistant from DaVinci Resolve's console, you get:

```
ModuleNotFoundError: No module named 'websocket'
```

or similar errors for `rich`, `requests`, or `PIL` (Pillow).

## Why This Happens

DaVinci Resolve has its **own Python interpreter** that's separate from your system Python or Poetry environment. This Python doesn't have the packages we need.

## The Solution

You have **3 options** to fix this:

---

## ✅ Option 1: Install Packages to Resolve's Python (RECOMMENDED)

### Step 1: Run the Setup Script

Open **PowerShell** (not the Resolve console) and run:

```powershell
cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
python setup_resolve_python.py
```

### What it does:
- Finds DaVinci Resolve's Python interpreter
- Installs: `rich`, `requests`, `websocket-client`, `pillow`
- Verifies the installation

### Expected output:
```
============================================================
DaVinci Resolve AI Assistant - Dependency Setup
============================================================
✓ Found DaVinci Resolve Python: C:\Program Files\...

📦 Installing packages...
   Installing rich==13.7.0...
   ✓ rich==13.7.0 installed
   Installing requests==2.31.0...
   ✓ requests==2.31.0 installed
   ...

✅ Setup complete!
```

### Step 2: Launch from Resolve Console

Now open DaVinci Resolve → Workspace → Console and paste:

```python
import sys
sys.path.append("c:/Users/satya/davinci-resolve-extension-builder/resolve-ai-assistant/src")

from resolve_ai.console_ui import launch_console_ui
launch_console_ui()
```

---

## ✅ Option 2: Use Poetry Environment (ALTERNATIVE)

If Option 1 doesn't work, you can launch using Poetry's Python (which has all packages).

### From DaVinci Resolve Console:

```python
exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\launch_with_poetry.py").read())
```

This runs the assistant using Poetry's managed Python environment.

**Note**: This requires Poetry to be installed and dependencies already installed (`poetry install`).

---

## ✅ Option 3: Manual Installation

If you know where DaVinci Resolve's Python is installed:

### Step 1: Find Resolve's Python

Common locations:
- `C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe`
- `C:\Program Files\Blackmagic Design\DaVinci Resolve\Python\python.exe`
- `C:\Program Files\Blackmagic Design\DaVinci Resolve\Python39\python.exe`

### Step 2: Install packages manually

```powershell
# Replace with your actual path
$resolvePython = "C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe"

& $resolvePython -m pip install rich==13.7.0
& $resolvePython -m pip install requests==2.31.0
& $resolvePython -m pip install websocket-client==1.6.0
& $resolvePython -m pip install pillow==10.1.0
```

### Step 3: Verify installation

```powershell
& $resolvePython -c "import rich; print('rich OK')"
& $resolvePython -c "import requests; print('requests OK')"
& $resolvePython -c "import websocket; print('websocket OK')"
& $resolvePython -c "import PIL; print('PIL OK')"
```

All should print "OK" without errors.

---

## Verification

After installing via any method, test in **DaVinci Resolve Console**:

```python
>>> import rich
>>> import requests
>>> import websocket
>>> import PIL
>>> print("✓ All packages available!")
✓ All packages available!
```

If any import fails, the package isn't installed correctly.

---

## Still Having Issues?

### Issue: Can't find Resolve's Python

**Solution**: Use Option 2 (Poetry environment) instead, or install to system Python:
```powershell
pip install rich requests websocket-client pillow
```

### Issue: "Access denied" when installing

**Solution**: Run PowerShell as Administrator:
- Right-click PowerShell → Run as Administrator
- Then run the setup script

### Issue: Multiple Python versions

**Solution**: Make sure you're installing to Resolve's specific Python, not system Python. The setup script finds it automatically.

### Issue: Import works but still crashes

**Solution**: Check Poetry dependencies are up to date:
```powershell
cd resolve-ai-assistant
poetry install
poetry update
```

---

## Quick Reference

| Method | When to Use | Pros | Cons |
|--------|-------------|------|------|
| **Option 1**: Setup script | First time setup | Automatic, permanent | Needs admin rights |
| **Option 2**: Poetry launcher | Quick testing | Uses existing env | Slower startup |
| **Option 3**: Manual install | Setup script fails | Full control | Manual process |

---

## The Root Cause (Technical)

DaVinci Resolve uses an **embedded Python interpreter**:
- Location: `C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe`
- This is **isolated** from system Python
- It has only **built-in modules** + Resolve API
- It does **NOT** see packages installed via `pip` in your system Python or Poetry environments

**Solution**: Install packages directly to Resolve's Python using `python.exe -m pip install`.

That's what `setup_resolve_python.py` does automatically! 🚀

---

## Success! Now What?

Once packages are installed, you can:

1. **Launch the assistant** from Resolve console
2. **Use natural language** to create Fusion compositions
3. **Generate AI images** via ComfyUI
4. **Iterate quickly** with 20-second cycle

See **LAUNCH_GUIDE.md** for usage examples!
