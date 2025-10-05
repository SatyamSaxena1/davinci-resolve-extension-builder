"""
Task Router - Decides between Fusion nodes and ComfyUI generation
"""

from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass
from resolve_ai.copilot_cli import CopilotCLI, CopilotSuggestion

TaskType = Literal['fusion', 'comfyui', 'hybrid']

@dataclass
class RoutedTask:
    """Task with routing decision"""
    task_type: TaskType
    description: str
    fusion_steps: List[Dict[str, Any]]
    comfyui_prompts: List[str]
    execution_order: List[str]  # ['fusion_1', 'comfyui_1', 'fusion_2', etc.]

class TaskRouter:
    """Routes tasks to Fusion or ComfyUI based on capabilities"""
    
    def __init__(self, copilot_cli: Optional[CopilotCLI] = None):
        self.copilot_cli = copilot_cli or CopilotCLI()
    
    def route(self, user_request: str, context: Optional[str] = None) -> RoutedTask:
        """
        Analyze request and route to appropriate system
        
        Args:
            user_request: Natural language command
            context: Current composition state
        
        Returns:
            RoutedTask with execution plan
        """
        # Get Copilot's analysis
        suggestion = self.copilot_cli.suggest(user_request, context)
        
        # Parse suggestion into concrete steps
        if suggestion.task_type == 'fusion':
            return self._route_fusion_task(user_request, suggestion)
        elif suggestion.task_type == 'comfyui':
            return self._route_comfyui_task(user_request, suggestion)
        else:  # hybrid
            return self._route_hybrid_task(user_request, suggestion)
    
    def _route_fusion_task(self, request: str, suggestion: CopilotSuggestion) -> RoutedTask:
        """Route pure Fusion task"""
        # Extract node types and parameters from suggestion
        fusion_steps = self._extract_fusion_steps(request, suggestion)
        
        return RoutedTask(
            task_type='fusion',
            description=request,
            fusion_steps=fusion_steps,
            comfyui_prompts=[],
            execution_order=[f"fusion_{i}" for i in range(len(fusion_steps))]
        )
    
    def _route_comfyui_task(self, request: str, suggestion: CopilotSuggestion) -> RoutedTask:
        """Route ComfyUI generation task"""
        # Extract prompt from request
        prompts = self._extract_comfyui_prompts(request, suggestion)
        
        # Still need Fusion step to load generated image
        fusion_steps = [{
            'type': 'loader',
            'description': 'Load AI-generated image',
            'params': {'clip': '{generated_image}'}
        }]
        
        return RoutedTask(
            task_type='comfyui',
            description=request,
            fusion_steps=fusion_steps,
            comfyui_prompts=prompts,
            execution_order=['comfyui_0', 'fusion_0']
        )
    
    def _route_hybrid_task(self, request: str, suggestion: CopilotSuggestion) -> RoutedTask:
        """Route hybrid task (ComfyUI + Fusion)"""
        # Break down into ComfyUI and Fusion components
        steps = self.copilot_cli.break_down_task(request)
        
        fusion_steps = []
        comfyui_prompts = []
        execution_order = []
        
        for i, step in enumerate(steps):
            if step.get('type') == 'comfyui':
                comfyui_prompts.append(step.get('details', {}).get('prompt', request))
                execution_order.append(f"comfyui_{len(comfyui_prompts)-1}")
            else:  # fusion
                fusion_steps.append(step)
                execution_order.append(f"fusion_{len(fusion_steps)-1}")
        
        return RoutedTask(
            task_type='hybrid',
            description=request,
            fusion_steps=fusion_steps,
            comfyui_prompts=comfyui_prompts,
            execution_order=execution_order
        )
    
    def _extract_fusion_steps(self, request: str, suggestion: CopilotSuggestion) -> List[Dict]:
        """Extract Fusion node steps from request"""
        # Parse common patterns
        steps = []
        
        request_lower = request.lower()
        
        # Background
        if 'background' in request_lower:
            color = self._extract_color(request_lower)
            steps.append({
                'type': 'background',
                'description': 'Create background',
                'params': {'color': color}
            })
        
        # Text
        if any(word in request_lower for word in ['text', 'title', 'lower-third', 'subtitle']):
            text_content = self._extract_text_content(request)
            steps.append({
                'type': 'text',
                'description': 'Create text',
                'params': {
                    'text': text_content,
                    'size': 0.1
                }
            })
        
        # Effects
        if 'glow' in request_lower:
            steps.append({
                'type': 'glow',
                'description': 'Add glow effect',
                'params': {'intensity': 5.0}
            })
        
        if 'blur' in request_lower:
            steps.append({
                'type': 'blur',
                'description': 'Add blur effect',
                'params': {'blur_size': 5.0}
            })
        
        # Transform
        if any(word in request_lower for word in ['move', 'position', 'transform', 'scale', 'rotate']):
            steps.append({
                'type': 'transform',
                'description': 'Transform element',
                'params': {}
            })
        
        # If no specific steps identified, create generic step
        if not steps:
            steps.append({
                'type': 'generic',
                'description': request,
                'params': {}
            })
        
        return steps
    
    def _extract_comfyui_prompts(self, request: str, suggestion: CopilotSuggestion) -> List[str]:
        """Extract ComfyUI prompts from request"""
        # Clean up request for use as prompt
        prompt = request
        
        # Remove command words
        remove_words = ['create', 'generate', 'make', 'add', 'using ai', 'with ai']
        for word in remove_words:
            prompt = prompt.replace(word, '')
        
        prompt = prompt.strip()
        
        # Enhance prompt for better results
        if 'background' in request.lower():
            prompt = f"cinematic background, {prompt}, high quality, detailed"
        elif 'character' in request.lower():
            prompt = f"character, {prompt}, professional lighting, detailed"
        else:
            prompt = f"{prompt}, high quality, professional"
        
        return [prompt]
    
    def _extract_color(self, text: str) -> tuple:
        """Extract color from text"""
        color_map = {
            'red': (1.0, 0.0, 0.0, 1.0),
            'green': (0.0, 1.0, 0.0, 1.0),
            'blue': (0.0, 0.0, 1.0, 1.0),
            'yellow': (1.0, 1.0, 0.0, 1.0),
            'cyan': (0.0, 1.0, 1.0, 1.0),
            'magenta': (1.0, 0.0, 1.0, 1.0),
            'white': (1.0, 1.0, 1.0, 1.0),
            'black': (0.0, 0.0, 0.0, 1.0),
            'gray': (0.5, 0.5, 0.5, 1.0),
            'grey': (0.5, 0.5, 0.5, 1.0)
        }
        
        for color_name, color_value in color_map.items():
            if color_name in text:
                return color_value
        
        return (0.5, 0.5, 0.5, 1.0)  # Default gray
    
    def _extract_text_content(self, text: str) -> str:
        """Extract text content from quotes or after certain keywords"""
        import re
        
        # Look for quoted text
        quoted = re.search(r'"([^"]+)"', text)
        if quoted:
            return quoted.group(1)
        
        quoted = re.search(r"'([^']+)'", text)
        if quoted:
            return quoted.group(1)
        
        # Look for text after keywords
        for keyword in ['saying', 'text', 'title', 'subtitle']:
            if keyword in text.lower():
                parts = text.lower().split(keyword)
                if len(parts) > 1:
                    return parts[1].strip().strip('"\'')
        
        return "Sample Text"
    
    def can_use_fusion(self, request: str) -> bool:
        """Check if request can be fulfilled with Fusion alone"""
        fusion_capable_keywords = [
            'background', 'gradient', 'text', 'title', 'lower-third',
            'color', 'blur', 'glow', 'transform', 'position', 'scale',
            'rotate', 'merge', 'mask', 'brightness', 'contrast', 'effect'
        ]
        
        request_lower = request.lower()
        
        # Check if any Fusion keywords present
        has_fusion_keywords = any(kw in request_lower for kw in fusion_capable_keywords)
        
        # Check for AI generation keywords (incompatible with Fusion alone)
        ai_keywords = [
            'generate', 'create character', 'create scene', 'fantasy',
            'realistic', 'photo', 'dragon', 'person', 'landscape',
            'painting', 'artistic', 'ai '
        ]
        
        needs_ai = any(kw in request_lower for kw in ai_keywords)
        
        return has_fusion_keywords and not needs_ai
    
    def needs_comfyui(self, request: str) -> bool:
        """Check if request needs ComfyUI generation"""
        ai_keywords = [
            'generate', 'create character', 'create scene', 'fantasy',
            'realistic', 'photorealistic', 'dragon', 'person', 'character',
            'landscape', 'environment', 'painting', 'artistic style',
            'ai-generated', 'using ai', 'with ai'
        ]
        
        request_lower = request.lower()
        return any(kw in request_lower for kw in ai_keywords)


def format_routed_task(task: RoutedTask) -> str:
    """Format routed task for display"""
    output = []
    output.append(f"📋 Task Analysis:")
    output.append(f"   Type: {task.task_type.upper()}")
    output.append(f"   Description: {task.description}")
    
    if task.fusion_steps:
        output.append(f"\n🎨 Fusion Steps ({len(task.fusion_steps)}):")
        for i, step in enumerate(task.fusion_steps):
            output.append(f"   {i+1}. {step.get('description', step.get('type'))}")
    
    if task.comfyui_prompts:
        output.append(f"\n🤖 AI Generation ({len(task.comfyui_prompts)}):")
        for i, prompt in enumerate(task.comfyui_prompts):
            output.append(f"   {i+1}. {prompt[:60]}...")
    
    output.append(f"\n📌 Execution Order:")
    for i, step in enumerate(task.execution_order):
        output.append(f"   {i+1}. {step}")
    
    return "\n".join(output)
