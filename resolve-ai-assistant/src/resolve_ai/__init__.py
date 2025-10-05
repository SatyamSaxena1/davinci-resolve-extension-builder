"""
DaVinci Resolve AI Assistant
AI-powered automation for DaVinci Resolve with Fusion node control

DaVinci Resolve extension using GitHub Copilot CLI and ComfyUI integration.
"""

__version__ = "0.2.0"

from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder
from resolve_ai.copilot_cli import CopilotCLI
from resolve_ai.comfyui_client import ComfyUIClient
from resolve_ai.task_router import TaskRouter
from resolve_ai.assistant import ResolveAssistant
from resolve_ai.console_ui import ConsoleUI, launch_console_ui

__all__ = [
    "ResolveAIController",
    "FusionNodeBuilder",
    "CopilotCLI",
    "ComfyUIClient",
    "TaskRouter",
    "ResolveAssistant",
    "ConsoleUI",
    "launch_console_ui"
]
