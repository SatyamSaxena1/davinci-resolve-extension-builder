"""
Alternative launcher using Poetry environment

This script runs the assistant using Poetry's managed Python environment,
which already has all dependencies installed.

Usage from DaVinci Resolve Console:
    exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\launch_with_poetry.py").read())
"""

import subprocess
import sys
import os

# Path to Poetry environment
POETRY_PATH = r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant"

def launch_with_poetry():
    """Launch assistant using Poetry's Python environment"""
    
    print("🚀 Launching DaVinci Resolve AI Assistant...")
    print(f"   Using Poetry environment from: {POETRY_PATH}\n")
    
    # Change to project directory
    os.chdir(POETRY_PATH)
    
    # Run with Poetry
    cmd = [
        "poetry",
        "run",
        "python",
        "-c",
        """
import sys
sys.path.insert(0, "src")
from resolve_ai.console_ui import launch_console_ui
launch_console_ui()
"""
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching assistant: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Poetry is installed: poetry --version")
        print("2. Install dependencies: cd resolve-ai-assistant && poetry install")
        print("3. Check that DaVinci Resolve is running with a project open")
        return 1
    except FileNotFoundError:
        print("\n❌ Poetry not found")
        print("\nInstall Poetry first:")
        print("   pip install poetry")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(launch_with_poetry())
