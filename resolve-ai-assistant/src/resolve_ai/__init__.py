"""
DaVinci Resolve AI Assistant
AI-powered automation for DaVinci Resolve with Fusion node control
"""

__version__ = "0.1.0"

from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder

__all__ = ["ResolveAIController", "FusionNodeBuilder"]
