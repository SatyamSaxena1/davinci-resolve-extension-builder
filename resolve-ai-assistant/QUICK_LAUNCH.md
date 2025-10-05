# Quick Launch Guide - Updated for Your Setup

## ✅ Good News!

Your **system Python (3.11.7)** now has all the required packages:
- ✓ rich
- ✓ requests  
- ✓ websocket-client
- ✓ pillow

## 🚀 How to Launch (3 Easy Methods)

### **Method 1: Simple One-Liner** (Easiest!)

From **DaVinci Resolve Console** (Workspace → Console), paste this:

```python
exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\simple_launch.py").read())
```

That's it! The assistant will launch.

---

### **Method 2: Direct Import** (If Method 1 doesn't work)

From **DaVinci Resolve Console**:

```python
import sys
sys.path.insert(0, r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\src")

from resolve_ai.console_ui import launch_console_ui
launch_console_ui()
```

---

### **Method 3: External Terminal** (For testing)

From **PowerShell** (while Resolve is running):

```powershell
cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
python -c "import sys; sys.path.insert(0, 'src'); from resolve_ai.console_ui import launch_console_ui; launch_console_ui()"
```

Or simpler:

```powershell
python simple_launch.py
```

---

## 📋 Pre-Launch Checklist

Before launching, make sure:

- [ ] **DaVinci Resolve is running**
- [ ] **A project is open** (File → New Project)
- [ ] **Console is accessible** (Workspace → Console)
- [ ] **ComfyUI server is running** (optional, for AI generation):
  ```powershell
  cd path\to\ComfyUI
  python main.py
  ```
- [ ] **GitHub Copilot CLI installed**:
  ```powershell
  gh copilot --version
  ```

---

## 🎯 Quick Test

To verify everything works, try this in Resolve Console first:

```python
# Test 1: Check DaVinci Resolve connection
import DaVinciResolveScript as dvr_script
resolve = dvr_script.scriptapp("Resolve")
print(f"✓ Connected to Resolve {resolve.GetVersionString()}")

# Test 2: Check packages
import rich
import requests
import websocket
import PIL
print("✓ All packages available!")

# Test 3: Launch assistant
exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\simple_launch.py").read())
```

---

## ⚠️ Important Notes

### About Resolve's Python vs System Python

Your setup script couldn't find DaVinci Resolve's embedded Python, which is fine! There are two scenarios:

**Scenario A**: Resolve uses system Python (your pyenv 3.11.7)
- ✅ Dependencies already installed
- ✅ Just launch with Method 1 or 2

**Scenario B**: Resolve has its own Python
- If imports fail, Resolve is using its own isolated Python
- Use Method 1 (`simple_launch.py`) which handles this
- Or manually install to Resolve's Python (see FIXING_DEPENDENCIES.md)

---

## 🎬 Example Session

Here's what a successful launch looks like:

```python
Py3> exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\simple_launch.py").read())

🚀 Launching DaVinci Resolve AI Assistant...

╔══════════════════════════════════════════════════╗
║     🎬 DaVinci Resolve AI Assistant              ║
║  Natural Language Control • Fusion Automation    ║
╚══════════════════════════════════════════════════╝

System Status
┌─────────────────────┬────────────────┐
│ DaVinci Resolve     │ ✓ Connected    │
│ Fusion Composition  │ ✓ Available    │
│ ComfyUI Server      │ ✓ Connected    │
│ GitHub Copilot CLI  │ ✓ Available    │
│ Iteration Limit     │ 20s            │
└─────────────────────┴────────────────┘

What would you like to create? _
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError" still appears

This means Resolve is using its own Python. Try:

1. **Use simple_launch.py** (Method 1) - it's designed for this
2. **Or manually find Resolve's Python**:
   - Check: `C:\Program Files\Blackmagic Design\DaVinci Resolve\`
   - Look for `python.exe` or `Python\python.exe`
   - Install packages to that Python:
     ```powershell
     & "path\to\resolve\python.exe" -m pip install rich requests websocket-client pillow
     ```

### "Cannot connect to DaVinci Resolve"

- Make sure Resolve is running
- Open a project (File → New Project)
- Try switching to Fusion page

### ComfyUI not available

This is OK! You can still use Fusion tasks. ComfyUI is only needed for AI-generated images.

To start ComfyUI:
```powershell
cd path\to\ComfyUI
python main.py
```

---

## 📚 Additional Resources

- **FIXING_DEPENDENCIES.md** - Detailed dependency troubleshooting
- **HOW_TO_ACCESS_CONSOLE.md** - How to open Resolve console
- **LAUNCH_GUIDE.md** - Usage examples and commands
- **README.md** - Full documentation

---

## 🎉 You're Ready!

**TL;DR**: Copy this into Resolve Console and press Enter:

```python
exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\simple_launch.py").read())
```

That's it! 🚀
