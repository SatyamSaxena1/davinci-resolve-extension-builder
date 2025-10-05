"""
GitHub Copilot CLI Integration
Uses 'gh copilot' commands for AI assistance in DaVinci Resolve
"""

import subprocess
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class CopilotSuggestion:
    """Represents a suggestion from GitHub Copilot CLI"""
    command: str
    explanation: str
    confidence: float
    task_type: str  # 'fusion', 'comfyui', or 'hybrid'

class CopilotCLI:
    """Interface to GitHub Copilot CLI (gh copilot)"""
    
    def __init__(self):
        self._check_gh_available()
        self._check_copilot_available()
    
    def _check_gh_available(self) -> bool:
        """Check if gh CLI is installed"""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("gh CLI not working")
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(
                "GitHub CLI (gh) not found.\n"
                "Install: winget install --id GitHub.cli\n"
                "Then: gh auth login"
            ) from e
    
    def _check_copilot_available(self) -> bool:
        """Check if GitHub Copilot is available"""
        try:
            result = subprocess.run(
                ["gh", "copilot", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("GitHub Copilot not available")
            return True
        except Exception as e:
            raise RuntimeError(
                "GitHub Copilot CLI not available.\n"
                "Make sure you're authenticated: gh auth login\n"
                "And have Copilot access enabled."
            ) from e
    
    def check_available(self) -> bool:
        """
        Check if GitHub Copilot CLI is available
        
        Returns:
            True if available, False otherwise
        """
        try:
            result = subprocess.run(
                ["gh", "copilot", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def suggest(self, user_request: str, context: Optional[str] = None) -> CopilotSuggestion:
        """
        Get Copilot suggestion for a user request
        
        Args:
            user_request: Natural language command from user
            context: Optional context about current composition state
        
        Returns:
            CopilotSuggestion with command and metadata
        """
        # Build prompt with DaVinci Resolve context
        prompt = self._build_prompt(user_request, context)
        
        # Call gh copilot suggest
        result = subprocess.run(
            [
                'gh', 'copilot', 'suggest',
                '-t', 'shell',  # Treat as shell command
                prompt
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Copilot CLI error: {result.stderr}")
        
        # Parse Copilot's response
        return self._parse_suggestion(result.stdout, user_request)
    
    def explain(self, concept: str) -> str:
        """
        Get Copilot explanation of a Fusion concept
        
        Args:
            concept: Fusion node or concept to explain
        
        Returns:
            Explanation text
        """
        prompt = f"Explain DaVinci Resolve Fusion concept: {concept}"
        
        result = subprocess.run(
            ['gh', 'copilot', 'explain', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return f"Error getting explanation: {result.stderr}"
        
        return result.stdout.strip()
    
    def _build_prompt(self, user_request: str, context: Optional[str]) -> str:
        """Build prompt with DaVinci Resolve context"""
        prompt = f"""
DaVinci Resolve Fusion AI Assistant

User Request: {user_request}

Available Tools:
1. Fusion Nodes (use for basic shapes, text, effects, transforms):
   - Background, Gradient, FastNoise
   - Text+, TextStyler
   - Transform, Merge, Dissolve
   - ColorCorrector, BrightnessContrast, ColorCurves
   - Blur, Glow, DirectionalBlur
   - Loader (for media), Saver (for output)

2. ComfyUI with Wan 2.2 (use for AI-generated content):
   - Character generation
   - Complex scenes
   - Photorealistic images
   - Artistic styles
   - Anything beyond basic shapes/effects

Task: Analyze the request and suggest whether to use Fusion nodes, ComfyUI, or both.
Respond with JSON format:
{{
  "task_type": "fusion" | "comfyui" | "hybrid",
  "explanation": "why this approach",
  "steps": ["step 1", "step 2", ...],
  "fusion_nodes": ["node1", "node2"] (if applicable),
  "comfyui_prompt": "prompt text" (if applicable)
}}
"""
        
        if context:
            prompt += f"\n\nCurrent Composition State:\n{context}"
        
        return prompt
    
    def _parse_suggestion(self, copilot_output: str, original_request: str) -> CopilotSuggestion:
        """Parse Copilot's response"""
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', copilot_output)
        
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                
                return CopilotSuggestion(
                    command=json.dumps(data),
                    explanation=data.get('explanation', ''),
                    confidence=0.9,  # High confidence if JSON parsed
                    task_type=data.get('task_type', 'fusion')
                )
            except json.JSONDecodeError:
                pass
        
        # Fallback: analyze text response
        task_type = self._infer_task_type(copilot_output, original_request)
        
        return CopilotSuggestion(
            command=copilot_output,
            explanation=copilot_output,
            confidence=0.7,  # Lower confidence for text parsing
            task_type=task_type
        )
    
    def _infer_task_type(self, response: str, request: str) -> str:
        """Infer task type from response text"""
        response_lower = response.lower()
        request_lower = request.lower()
        
        # Check for AI generation keywords
        ai_keywords = [
            'comfyui', 'generate', 'create character', 'create scene',
            'photorealistic', 'artistic', 'fantasy', 'dragon', 'person',
            'landscape', 'painting', 'style'
        ]
        
        # Check for Fusion keywords
        fusion_keywords = [
            'fusion', 'node', 'background', 'text', 'transform',
            'merge', 'color', 'blur', 'glow', 'effect'
        ]
        
        ai_score = sum(1 for kw in ai_keywords if kw in response_lower or kw in request_lower)
        fusion_score = sum(1 for kw in fusion_keywords if kw in response_lower or kw in request_lower)
        
        if ai_score > fusion_score:
            return 'comfyui'
        elif ai_score > 0 and fusion_score > 0:
            return 'hybrid'
        else:
            return 'fusion'
    
    def break_down_task(self, user_request: str) -> List[Dict[str, Any]]:
        """
        Break down complex task into steps
        
        Returns:
            List of steps with action details
        """
        prompt = f"""
Break down this DaVinci Resolve task into executable steps:
"{user_request}"

For each step, specify:
1. Description (what to do)
2. Type (fusion, comfyui, or timeline)
3. Details (node types, parameters, or prompts)

Respond with JSON array:
[
  {{
    "id": 1,
    "description": "Create background",
    "type": "fusion",
    "details": {{
      "node": "Background",
      "params": {{"color": [1, 0, 0, 1]}}
    }}
  }},
  ...
]
"""
        
        result = subprocess.run(
            ['gh', 'copilot', 'suggest', '-t', 'shell', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Try to parse JSON array
        json_match = re.search(r'\[[\s\S]*\]', result.stdout)
        if json_match:
            try:
                steps = json.loads(json_match.group(0))
                return steps
            except json.JSONDecodeError:
                pass
        
        # Fallback: create single step
        return [{
            'id': 1,
            'description': user_request,
            'type': 'fusion',
            'details': {}
        }]
    
    def optimize_for_20s(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize task to complete within 20-second limit
        
        For ComfyUI tasks, reduces steps
        For Fusion tasks, simplifies complexity
        """
        if task_details.get('type') == 'comfyui':
            # Reduce ComfyUI steps for faster generation
            if 'comfyui_params' in task_details:
                task_details['comfyui_params']['steps'] = min(
                    task_details['comfyui_params'].get('steps', 20),
                    20  # Max 20 steps for ~10-15s generation
                )
        
        return task_details


def format_copilot_response(suggestion: CopilotSuggestion) -> str:
    """Format Copilot suggestion for display"""
    output = []
    output.append(f"🤖 Copilot Analysis:")
    output.append(f"   Task Type: {suggestion.task_type.upper()}")
    output.append(f"   Confidence: {suggestion.confidence * 100:.0f}%")
    output.append(f"\n📝 Explanation:")
    output.append(f"   {suggestion.explanation}")
    
    return "\n".join(output)
