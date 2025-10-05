#!/usr/bin/env python3
"""
DaVinci Resolve AI Assistant - Main Entry Point

Launch this script inside DaVinci Resolve's console or as a standalone script.

Usage:
    From DaVinci Resolve Console:
        import sys
        sys.path.append("c:/path/to/resolve-ai-assistant/src")
        exec(open("resolve_ai_assistant.py").read())
    
    Or from terminal (if Resolve API is accessible):
        python resolve_ai_assistant.py
"""

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "resolve-ai-assistant" / "src"
sys.path.insert(0, str(src_path))

from resolve_ai.console_ui import launch_console_ui


def main():
    """Main entry point"""
    # Default ComfyUI URL
    comfyui_url = os.environ.get("COMFYUI_URL", "http://localhost:8188")
    
    # Launch console UI
    launch_console_ui(comfyui_url=comfyui_url)


if __name__ == "__main__":
    main()
