# How to Access DaVinci Resolve Console

## Step-by-Step Guide

### Method 1: Via Menu Bar (Primary Method)

1. **Launch DaVinci Resolve**
   - Open the application
   - Wait for it to fully load

2. **Open or Create a Project**
   - Click **File → New Project** (or open an existing one)
   - You must have a project open to access scripting features

3. **Navigate to the Console**
   - Look at the top menu bar
   - Click **Workspace** (between View and Playback menus)
   - Look for one of these options:
     - **Console** (DaVinci Resolve 17.x and earlier)
     - **Scripting Console** (DaVinci Resolve 18+)
     - **Scripts** (alternative in some versions)

4. **Console Window Opens**
   - A Python console window should appear
   - You'll see `>>>` prompt
   - This is a live Python interpreter

### Method 2: Enable Console in Preferences (If Not Visible)

If you don't see Console/Scripting Console in the Workspace menu:

1. **Open Preferences**
   - Windows: **DaVinci Resolve → Preferences** or **Edit → Preferences**
   - Mac: **DaVinci Resolve → Preferences**
   - Shortcut: `Ctrl + ,` (Windows) or `Cmd + ,` (Mac)

2. **Navigate to System Settings**
   - Left sidebar: Click **System**
   - Click **General** tab

3. **Enable Scripting**
   - Look for **Scripting** section
   - Check the box: ☑ **Enable Scripting Console**
   - Click **Save**

4. **Restart DaVinci Resolve**
   - Close and reopen the application
   - Now **Workspace → Console** should be visible

### Method 3: Via External Editor (Alternative)

If the built-in console doesn't work, you can run Python scripts externally:

1. **Create a Python file** (e.g., `launch_assistant.py`):
   ```python
   import sys
   sys.path.append("c:/Users/satya/davinci-resolve-extension-builder/resolve-ai-assistant/src")

   from resolve_ai.console_ui import launch_console_ui
   launch_console_ui()
   ```

2. **Set up Resolve API access**:
   ```powershell
   $env:RESOLVE_SCRIPT_API="C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
   $env:RESOLVE_SCRIPT_LIB="C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
   ```

3. **Run the script**:
   ```powershell
   cd resolve-ai-assistant
   poetry run python launch_assistant.py
   ```

## Visual Location Guide

```
DaVinci Resolve Menu Bar:
┌─────────────────────────────────────────────────────────┐
│ File  Edit  View  Workspace ⬅ HERE  Playback  Help     │
└─────────────────────────────────────────────────────────┘
                      ↓
         Click "Workspace" to reveal:
         ┌──────────────────────┐
         │ Dual Timeline        │
         │ Single Viewer        │
         │ ─────────────────    │
         │ ► Console        ⬅ HERE
         │ ► Scripts            │
         │ Reset UI Layout      │
         └──────────────────────┘
```

## Quick Test: Verify Console Works

Once you have the console open, try this simple test:

```python
>>> print("Hello from DaVinci Resolve!")
Hello from DaVinci Resolve!

>>> import DaVinciResolveScript as dvr_script
>>> resolve = dvr_script.scriptapp("Resolve")
>>> print(resolve.GetVersionString())
18.6.0
```

If you see output without errors, the console is working! ✅

## Troubleshooting

### "Console" menu item is grayed out
**Solution**: Make sure you have a project open (File → New Project)

### ImportError: No module named 'DaVinciResolveScript'
**Solution**:
- This is normal in external Python
- The console inside DaVinci Resolve has this module pre-loaded
- Use Method 3 and set environment variables

### Console window doesn't open
**Solution**:
1. Check **Preferences → System → General → Enable Scripting Console**
2. Restart DaVinci Resolve
3. Try accessing via **Workspace → Scripts** instead

### "Permission denied" or access errors
**Solution**:
- Run DaVinci Resolve as Administrator (right-click → Run as administrator)
- Check that scripting hasn't been disabled by IT policies

## Version-Specific Notes

### DaVinci Resolve 18.x and newer:
- Menu path: **Workspace → Console** or **Workspace → Scripting Console**
- Enhanced scripting features
- Better Python 3.x support

### DaVinci Resolve 17.x:
- Menu path: **Workspace → Console**
- Python 3.6+ supported
- May require enabling in Preferences

### DaVinci Resolve 16.x:
- Menu path: **Workspace → Console**
- Python 2.7 or 3.6
- Limited API features

## What the Console Looks Like

When opened, you'll see:

```
┌────────────────────────────────────────────────────────┐
│ DaVinci Resolve - Scripting Console                   │
├────────────────────────────────────────────────────────┤
│                                                        │
│ >>> _                                              ◄── Python prompt
│                                                        │
│                                                        │
│                                                        │
│                                                        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

Type your Python code after the `>>>` prompt.

## Installing Dependencies to Resolve's Python

⚠️ **IMPORTANT**: DaVinci Resolve's built-in Python doesn't have our required packages (rich, requests, websocket-client, pillow).

### Option 1: Install to Resolve's Python (Recommended)

Run this setup script **once** from PowerShell:

```powershell
cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
python setup_resolve_python.py
```

This will find DaVinci Resolve's Python and install the required packages.

### Option 2: Use Poetry Environment (Alternative)

From DaVinci Resolve Console:

```python
exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\launch_with_poetry.py").read())
```

This runs the assistant using Poetry's environment (which has all dependencies).

### Option 3: Manual Installation

If you found Resolve's Python path (e.g., `C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe`):

```powershell
& "C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe" -m pip install rich requests websocket-client pillow
```

## Ready to Launch Assistant

**After installing dependencies**, paste this in the console:

```python
import sys
sys.path.append("c:/Users/satya/davinci-resolve-extension-builder/resolve-ai-assistant/src")

from resolve_ai.console_ui import launch_console_ui
launch_console_ui()
```

Press **Enter** and the Rich-formatted UI will launch! 🚀

## Troubleshooting "ModuleNotFoundError"

### Error: `No module named 'websocket'` or `'rich'` or `'requests'`

**Cause**: DaVinci Resolve's Python doesn't have the required packages.

**Solutions**:
1. Run `setup_resolve_python.py` (Option 1 above)
2. Use `launch_with_poetry.py` (Option 2 above)
3. Manually install with pip (Option 3 above)

### How to verify packages are installed:

From Resolve Console:
```python
>>> import rich
>>> import requests
>>> import websocket
>>> import PIL
>>> print("✓ All packages available!")
```

If any fail, run the setup script again.

## Need Help?

- **Official Docs**: Help → Documentation → Scripting
- **Check version**: Type `resolve.GetVersionString()` in console
- **Test connection**: See "Quick Test" section above
- **Dependencies**: Run `setup_resolve_python.py` if imports fail

---

**Bottom line**: 
1. **Workspace → Console** to open console
2. Run `setup_resolve_python.py` to install dependencies
3. Paste the launch code
