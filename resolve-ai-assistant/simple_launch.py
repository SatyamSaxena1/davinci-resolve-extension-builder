"""
Simple launcher for DaVinci Resolve Console

Since DaVinci Resolve's Python wasn't found, this uses your system Python
which already has all the dependencies installed.

Usage from DaVinci Resolve Console:
    exec(open(r"c:\\Users\\satya\\davinci-resolve-extension-builder\\resolve-ai-assistant\\simple_launch.py").read())

Or from PowerShell:
    python simple_launch.py
"""

import sys
import os
import traceback

# Add our source to path
sys.path.insert(0, r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\src")

print("🚀 Starting DaVinci Resolve AI Assistant...")
print("=" * 60)

# Now import and launch
try:
    print("📦 Loading modules...")
    from resolve_ai.console_ui import launch_console_ui
    
    print("✓ Modules loaded")
    print("🔌 Connecting to DaVinci Resolve...")
    print()
    
    launch_console_ui()
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure dependencies are installed:")
    print("   pip install rich requests websocket-client pillow")
    print("\n2. Or use Poetry environment:")
    print("   cd resolve-ai-assistant && poetry install")
    traceback.print_exc()
    
except KeyboardInterrupt:
    print("\n\n👋 Interrupted by user")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFull error details:")
    traceback.print_exc()
    print("\nMake sure:")
    print("- DaVinci Resolve is running")
    print("- A project is open in DaVinci Resolve")
    print("- ComfyUI server is running (optional)")
    sys.exit(1)
