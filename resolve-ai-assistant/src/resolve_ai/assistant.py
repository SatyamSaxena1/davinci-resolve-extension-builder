"""
DaVinci Resolve AI Assistant - Main Orchestrator

This module combines all components (Copilot CLI, Task Router, Fusion Tools, ComfyUI)
into a cohesive assistant that runs inside DaVinci Resolve.

Architecture:
    User Input → Copilot CLI Analysis → Task Router → Execute (Fusion/ComfyUI) → Preview
    All within 20-second iteration cycle
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from .controller import ResolveAIController
from .fusion_tools import FusionNodeBuilder
from .copilot_cli import CopilotCLI, CopilotSuggestion
from .comfyui_client import ComfyUIClient, GenerationResult
from .task_router import TaskRouter, RoutedTask, TaskType


class AssistantState(Enum):
    """Current state of the assistant"""
    IDLE = "idle"
    ANALYZING = "analyzing"
    ROUTING = "routing"
    EXECUTING_FUSION = "executing_fusion"
    EXECUTING_COMFYUI = "executing_comfyui"
    EXECUTING_HYBRID = "executing_hybrid"
    PREVIEWING = "previewing"
    ERROR = "error"
    COMPLETE = "complete"


@dataclass
class IterationResult:
    """Result of a single assistant iteration"""
    success: bool
    duration: float
    state: AssistantState
    message: str
    nodes_created: List[str] = None
    images_generated: List[str] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.nodes_created is None:
            self.nodes_created = []
        if self.images_generated is None:
            self.images_generated = []


class ResolveAssistant:
    """
    Main AI Assistant for DaVinci Resolve
    
    Orchestrates the complete workflow:
    1. Receive natural language input
    2. Analyze with GitHub Copilot CLI
    3. Route to appropriate system (Fusion/ComfyUI/Hybrid)
    4. Execute task within 20-second limit
    5. Preview results
    """
    
    def __init__(
        self,
        comfyui_url: str = "http://localhost:8188",
        iteration_limit: float = 20.0
    ):
        """
        Initialize the assistant
        
        Args:
            comfyui_url: URL of ComfyUI server
            iteration_limit: Maximum seconds per iteration (default 20)
        """
        self.iteration_limit = iteration_limit
        self.state = AssistantState.IDLE
        
        # Initialize components
        self.controller = ResolveAIController()
        self.copilot = CopilotCLI()
        
        # Try to initialize ComfyUI (optional)
        try:
            self.comfyui = ComfyUIClient(comfyui_url)
            if not self.comfyui.check_connection():
                print(f"⚠️  ComfyUI server not available at {comfyui_url}")
                print("   AI image generation will be disabled")
                self.comfyui = None
        except Exception as e:
            print(f"⚠️  ComfyUI initialization failed: {e}")
            print("   AI image generation will be disabled")
            self.comfyui = None
        
        self.router = TaskRouter(self.copilot)
        
        # Get Fusion composition
        self.comp = self.controller.get_fusion_comp()
        self.builder = FusionNodeBuilder(self.comp) if self.comp else None
    
    def process_request(self, user_input: str) -> IterationResult:
        """
        Process a single user request with 20-second limit
        
        Args:
            user_input: Natural language command from user
            
        Returns:
            IterationResult with execution details
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze with Copilot CLI
            self.state = AssistantState.ANALYZING
            suggestion = self._analyze_input(user_input)
            
            # Step 2: Route to appropriate system
            self.state = AssistantState.ROUTING
            routed_task = self._route_task(user_input, suggestion)
            
            # Step 3: Execute based on task type
            if routed_task.task_type == TaskType.FUSION_ONLY:
                result = self._execute_fusion_task(routed_task)
            elif routed_task.task_type == TaskType.COMFYUI_ONLY:
                result = self._execute_comfyui_task(routed_task)
            else:  # HYBRID
                result = self._execute_hybrid_task(routed_task)
            
            # Calculate duration
            duration = time.time() - start_time
            result.duration = duration
            
            # Check 20-second limit
            if duration > self.iteration_limit:
                result.message += f" ⚠️ Exceeded {self.iteration_limit}s limit ({duration:.1f}s)"
            
            self.state = AssistantState.COMPLETE
            return result
            
        except Exception as e:
            self.state = AssistantState.ERROR
            duration = time.time() - start_time
            return IterationResult(
                success=False,
                duration=duration,
                state=AssistantState.ERROR,
                message=f"Error processing request",
                error=str(e)
            )
    
    def _analyze_input(self, user_input: str) -> CopilotSuggestion:
        """
        Analyze user input with GitHub Copilot CLI
        
        Args:
            user_input: User's natural language command
            
        Returns:
            CopilotSuggestion with analysis
        """
        # Optimize for 20-second limit
        prompt = f"""DaVinci Resolve Fusion task: {user_input}
        
        Provide a brief, actionable plan (max 3 steps) for:
        - Fusion nodes needed, OR
        - AI generation requirements, OR
        - Combination of both
        
        Keep it concise for 20-second execution."""
        
        return self.copilot.suggest(prompt)
    
    def _route_task(self, user_input: str, suggestion: CopilotSuggestion) -> RoutedTask:
        """
        Route task to Fusion, ComfyUI, or both
        
        Args:
            user_input: Original user input
            suggestion: Copilot analysis
            
        Returns:
            RoutedTask with execution plan
        """
        return self.router.route(user_input)
    
    def _execute_fusion_task(self, task: RoutedTask) -> IterationResult:
        """
        Execute a Fusion-only task
        
        Args:
            task: Routed task with Fusion steps
            
        Returns:
            IterationResult with created nodes
        """
        self.state = AssistantState.EXECUTING_FUSION
        
        if not self.builder:
            return IterationResult(
                success=False,
                duration=0,
                state=AssistantState.ERROR,
                message="Fusion composition not available",
                error="No active Fusion composition"
            )
        
        nodes_created = []
        
        try:
            for step in task.fusion_steps:
                node = self._create_fusion_node(step)
                if node:
                    nodes_created.append(step.get('name', 'Unknown'))
            
            return IterationResult(
                success=True,
                duration=0,  # Will be set by caller
                state=AssistantState.COMPLETE,
                message=f"✓ Created {len(nodes_created)} Fusion nodes",
                nodes_created=nodes_created
            )
            
        except Exception as e:
            return IterationResult(
                success=False,
                duration=0,
                state=AssistantState.ERROR,
                message="Failed to create Fusion nodes",
                error=str(e)
            )
    
    def _execute_comfyui_task(self, task: RoutedTask) -> IterationResult:
        """
        Execute a ComfyUI-only task
        
        Args:
            task: Routed task with ComfyUI prompts
            
        Returns:
            IterationResult with generated images
        """
        self.state = AssistantState.EXECUTING_COMFYUI
        
        # Check if ComfyUI is available
        if not self.comfyui:
            return IterationResult(
                success=False,
                duration=0,
                state=AssistantState.ERROR,
                message="ComfyUI not available - AI image generation disabled",
                error="ComfyUI server not connected. Start ComfyUI or use Fusion-only tasks."
            )
        
        images_generated = []
        
        try:
            for prompt_data in task.comfyui_prompts:
                prompt = prompt_data.get('prompt', '')
                style = prompt_data.get('style', 'photorealistic')
                
                # Generate with fast settings for 20s limit
                result = self.comfyui.generate(
                    prompt=prompt,
                    width=512,  # Smaller for speed
                    height=512,
                    steps=15,   # Fewer steps for speed
                    cfg_scale=7.0,
                    style=style
                )
                
                if result.success:
                    images_generated.append(result.image_path)
                    
                    # Import to Fusion if available
                    if self.builder:
                        loader = self.builder.create_loader_node(
                            file_path=result.image_path,
                            name=f"AI_{prompt_data.get('name', 'Generated')}"
                        )
            
            return IterationResult(
                success=True,
                duration=0,
                state=AssistantState.COMPLETE,
                message=f"✓ Generated {len(images_generated)} AI images",
                images_generated=images_generated
            )
            
        except Exception as e:
            return IterationResult(
                success=False,
                duration=0,
                state=AssistantState.ERROR,
                message="Failed to generate AI images",
                error=str(e)
            )
    
    def _execute_hybrid_task(self, task: RoutedTask) -> IterationResult:
        """
        Execute a hybrid task (ComfyUI + Fusion)
        
        Args:
            task: Routed task with both ComfyUI and Fusion steps
            
        Returns:
            IterationResult with both images and nodes
        """
        self.state = AssistantState.EXECUTING_HYBRID
        
        # Check if ComfyUI is available for hybrid tasks
        if not self.comfyui:
            return IterationResult(
                success=False,
                duration=0,
                state=AssistantState.ERROR,
                message="ComfyUI not available - cannot execute hybrid task",
                error="Hybrid tasks require ComfyUI. Try a Fusion-only task or start ComfyUI server."
            )
        
        images_generated = []
        nodes_created = []
        
        try:
            # Step 1: Generate AI images
            for prompt_data in task.comfyui_prompts:
                prompt = prompt_data.get('prompt', '')
                style = prompt_data.get('style', 'photorealistic')
                
                result = self.comfyui.generate(
                    prompt=prompt,
                    width=512,
                    height=512,
                    steps=15,
                    cfg_scale=7.0,
                    style=style
                )
                
                if result.success:
                    images_generated.append(result.image_path)
            
            # Step 2: Create Fusion composition
            if self.builder:
                for step in task.fusion_steps:
                    node = self._create_fusion_node(step)
                    if node:
                        nodes_created.append(step.get('name', 'Unknown'))
            
            return IterationResult(
                success=True,
                duration=0,
                state=AssistantState.COMPLETE,
                message=f"✓ Generated {len(images_generated)} images + {len(nodes_created)} nodes",
                images_generated=images_generated,
                nodes_created=nodes_created
            )
            
        except Exception as e:
            return IterationResult(
                success=False,
                duration=0,
                state=AssistantState.ERROR,
                message="Failed to execute hybrid task",
                error=str(e)
            )
    
    def _create_fusion_node(self, step: Dict[str, Any]) -> Optional[Any]:
        """
        Create a Fusion node based on step specification
        
        Args:
            step: Dictionary with node type and parameters
            
        Returns:
            Created node or None
        """
        node_type = step.get('type', '').lower()
        name = step.get('name', f"{node_type}_1")
        
        try:
            if node_type == 'background':
                color = step.get('color', (0.0, 0.0, 0.0, 1.0))
                return self.builder.create_background_node(color=color, name=name)
            
            elif node_type == 'text':
                text = step.get('text', 'Text')
                color = step.get('color', (1.0, 1.0, 1.0))
                size = step.get('size', 0.1)
                return self.builder.create_text_node(
                    text=text,
                    color=color,
                    size=size,
                    name=name
                )
            
            elif node_type == 'merge':
                return self.builder.create_merge_node(name=name)
            
            elif node_type == 'transform':
                return self.builder.create_transform_node(name=name)
            
            elif node_type == 'glow':
                return self.builder.create_glow_node(name=name)
            
            elif node_type == 'blur':
                return self.builder.create_blur_node(name=name)
            
            else:
                print(f"Unknown node type: {node_type}")
                return None
                
        except Exception as e:
            print(f"Failed to create {node_type} node: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current assistant status
        
        Returns:
            Dictionary with status information
        """
        return {
            'state': self.state.value,
            'resolve_connected': self.controller.is_connected(),
            'fusion_available': self.builder is not None,
            'comfyui_available': self.comfyui.check_connection() if self.comfyui else False,
            'copilot_available': self.copilot.check_available(),
            'iteration_limit': self.iteration_limit
        }
    
    def clear_composition(self) -> bool:
        """
        Clear all nodes from Fusion composition
        
        Returns:
            True if successful
        """
        if self.builder:
            return self.builder.clear_composition()
        return False


def create_assistant(comfyui_url: str = "http://localhost:8188") -> ResolveAssistant:
    """
    Factory function to create a ResolveAssistant instance
    
    Args:
        comfyui_url: URL of ComfyUI server
        
    Returns:
        Initialized ResolveAssistant
    """
    return ResolveAssistant(comfyui_url=comfyui_url)
