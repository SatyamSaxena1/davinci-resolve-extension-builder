"""
Setup script to install required packages into DaVinci Resolve's Python environment

This script finds DaVinci Resolve's Python interpreter and installs the required
packages so they're available when running scripts from the Resolve console.
"""

import subprocess
import sys
import os
from pathlib import Path


def find_resolve_python():
    """Find DaVinci Resolve's Python interpreter"""
    
    # Common paths for Windows
    possible_paths = [
        r"C:\Program Files\Blackmagic Design\DaVinci Resolve\python.exe",
        r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Python\python.exe",
        r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Python39\python.exe",
        r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Python311\python.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Found DaVinci Resolve Python: {path}")
            return path
    
    print("⚠️  Could not find DaVinci Resolve's Python interpreter")
    print("    Will use system Python instead")
    return sys.executable


def install_packages(python_exe):
    """Install required packages"""
    
    packages = [
        "rich==13.7.0",
        "requests==2.31.0",
        "websocket-client==1.6.0",
        "pillow==10.1.0",
    ]
    
    print("\n📦 Installing packages...")
    print(f"   Using Python: {python_exe}\n")
    
    for package in packages:
        print(f"   Installing {package}...")
        try:
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"   ✓ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"   ✗ Failed to install {package}")
            print(f"   Error: {e.stderr}")
            return False
    
    return True


def verify_installation(python_exe):
    """Verify packages are installed"""
    
    print("\n✓ Verifying installation...\n")
    
    modules = ["rich", "requests", "websocket", "PIL"]
    
    for module in modules:
        try:
            result = subprocess.run(
                [python_exe, "-c", f"import {module}; print('{module}:', {module}.__version__ if hasattr({module}, '__version__') else 'OK')"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"   ✓ {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print(f"   ✗ {module} not available")
            return False
    
    return True


def main():
    """Main setup function"""
    
    print("=" * 60)
    print("DaVinci Resolve AI Assistant - Dependency Setup")
    print("=" * 60)
    
    # Find Python interpreter
    python_exe = find_resolve_python()
    
    # Install packages
    if install_packages(python_exe):
        # Verify installation
        if verify_installation(python_exe):
            print("\n" + "=" * 60)
            print("✅ Setup complete!")
            print("=" * 60)
            print("\nYou can now run the assistant from DaVinci Resolve console:")
            print("\n>>> import sys")
            print('>>> sys.path.append("c:/Users/satya/davinci-resolve-extension-builder/resolve-ai-assistant/src")')
            print(">>> from resolve_ai.console_ui import launch_console_ui")
            print(">>> launch_console_ui()")
            print()
            return 0
        else:
            print("\n⚠️  Some packages failed verification")
            return 1
    else:
        print("\n❌ Setup failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
