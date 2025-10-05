"""
Debug launcher for DaVinci Resolve AI Assistant
Provides detailed diagnostics and verbose output
"""

import sys
import os
import traceback

print("=" * 80)
print("DaVinci Resolve AI Assistant - Debug Mode")
print("=" * 80)
print()

# Step 1: Python environment
print("📍 Step 1: Checking Python Environment")
print(f"   Python Version: {sys.version}")
print(f"   Python Executable: {sys.executable}")
print(f"   Current Directory: {os.getcwd()}")
print()

# Step 2: Add source to path
print("📍 Step 2: Setting up Python Path")
src_path = r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\src"
sys.path.insert(0, src_path)
print(f"   Added to sys.path: {src_path}")
print()

# Step 3: Check dependencies
print("📍 Step 3: Checking Dependencies")
dependencies = {
    "rich": "Rich console formatting",
    "requests": "HTTP requests",
    "websocket": "WebSocket client",
    "PIL": "Pillow image processing"
}

for module_name, description in dependencies.items():
    try:
        __import__(module_name)
        print(f"   ✓ {module_name:15} - {description}")
    except ImportError as e:
        print(f"   ✗ {module_name:15} - MISSING ({e})")
print()

# Step 4: Check DaVinci Resolve API
print("📍 Step 4: Checking DaVinci Resolve API")
try:
    # Try direct import
    import DaVinciResolveScript as dvr
    print("   ✓ DaVinciResolveScript imported directly")
except ImportError:
    print("   ⚠ Direct import failed, trying with RESOLVE_SCRIPT_API path...")
    
    resolve_api = os.getenv("RESOLVE_SCRIPT_API")
    if resolve_api:
        print(f"   RESOLVE_SCRIPT_API = {resolve_api}")
        modules_path = os.path.join(resolve_api, "Modules")
        if os.path.exists(modules_path):
            print(f"   Adding to path: {modules_path}")
            sys.path.append(modules_path)
            try:
                import DaVinciResolveScript as dvr
                print("   ✓ DaVinciResolveScript imported via RESOLVE_SCRIPT_API")
            except ImportError as e:
                print(f"   ✗ Still failed: {e}")
        else:
            print(f"   ✗ Modules path doesn't exist: {modules_path}")
    else:
        print("   ✗ RESOLVE_SCRIPT_API environment variable not set")
        
        # Try default path
        default_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
        if os.path.exists(default_path):
            print(f"   Trying default path: {default_path}")
            sys.path.append(default_path)
            try:
                import DaVinciResolveScript as dvr
                print("   ✓ DaVinciResolveScript imported via default path")
            except ImportError as e:
                print(f"   ✗ Failed with default path: {e}")
        else:
            print(f"   ✗ Default path doesn't exist: {default_path}")
print()

# Step 5: Try to connect to Resolve
print("📍 Step 5: Connecting to DaVinci Resolve")
try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if resolve:
        print("   ✓ Connected to DaVinci Resolve")
        pm = resolve.GetProjectManager()
        project = pm.GetCurrentProject()
        if project:
            print(f"   ✓ Project open: {project.GetName()}")
        else:
            print("   ✗ No project is currently open")
    else:
        print("   ✗ Could not connect to DaVinci Resolve")
        print("   Make sure DaVinci Resolve is running")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    traceback.print_exc()
print()

# Step 6: Import assistant modules
print("📍 Step 6: Importing Assistant Modules")
modules_to_check = [
    ("resolve_ai.controller", "DaVinci Resolve Controller"),
    ("resolve_ai.copilot_cli", "GitHub Copilot CLI"),
    ("resolve_ai.fusion_tools", "Fusion Node Builder"),
    ("resolve_ai.comfyui_client", "ComfyUI Client"),
    ("resolve_ai.task_router", "Task Router"),
    ("resolve_ai.console_ui", "Console UI"),
    ("resolve_ai.assistant", "Main Assistant")
]

for module_name, description in modules_to_check:
    try:
        __import__(module_name)
        print(f"   ✓ {module_name:30} - {description}")
    except Exception as e:
        print(f"   ✗ {module_name:30} - FAILED: {e}")
print()

# Step 7: Launch assistant
print("📍 Step 7: Launching Assistant")
print()

try:
    from resolve_ai.console_ui import launch_console_ui
    print("🚀 Starting console UI...")
    print("=" * 80)
    print()
    
    launch_console_ui()
    
except KeyboardInterrupt:
    print("\n\n👋 Interrupted by user")
    sys.exit(0)
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ LAUNCH FAILED")
    print("=" * 80)
    print(f"\nError: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print()
    print("Troubleshooting tips:")
    print("1. Make sure DaVinci Resolve is running")
    print("2. Open a project in DaVinci Resolve")
    print("3. Run this from VS Code terminal or DaVinci Resolve Console")
    print("4. Check if RESOLVE_SCRIPT_API environment variable is set")
    sys.exit(1)
