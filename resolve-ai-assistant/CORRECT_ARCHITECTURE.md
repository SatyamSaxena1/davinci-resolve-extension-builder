# DaVinci Resolve AI Assistant - Correct Architecture

## What This Actually Is

This is a **DaVinci Resolve Extension/Script** that:
1. Runs **inside DaVinci Resolve** (not VS Code)
2. Uses **GitHub Copilot CLI** (`gh copilot`) for AI assistance
3. Controls **Fusion nodes** via DaVinci Resolve Python API
4. Delegates to **ComfyUI + Wan 2.2** for AI-generated graphics/VFX
5. Provides natural language control of video editing workflow

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  DaVinci Resolve                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Resolve AI Assistant Script                   │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Natural Language Interface (Console/UI Panel)  │  │  │
│  │  └────────────────┬────────────────────────────────┘  │  │
│  │                   │                                    │  │
│  │         ┌─────────▼──────────┐                        │  │
│  │         │  GitHub Copilot CLI │                       │  │
│  │         │  (gh copilot)       │                       │  │
│  │         └─────────┬──────────┘                        │  │
│  │                   │                                    │  │
│  │         ┌─────────▼──────────┐                        │  │
│  │         │   Intent Parser     │                       │  │
│  │         │  & Task Router      │                       │  │
│  │         └─────────┬──────────┘                        │  │
│  │                   │                                    │  │
│  │         ┌─────────┴──────────┐                        │  │
│  │         │                    │                        │  │
│  │    ┌────▼─────┐      ┌──────▼────────┐               │  │
│  │    │ Fusion   │      │   ComfyUI     │               │  │
│  │    │ Tools    │      │   Client      │               │  │
│  │    └────┬─────┘      └──────┬────────┘               │  │
│  │         │                    │                        │  │
│  │    ┌────▼─────┐      ┌──────▼────────┐               │  │
│  │    │ Resolve  │      │   ComfyUI     │               │  │
│  │    │ API      │      │   Server      │               │  │
│  │    └──────────┘      │  (Wan 2.2)    │               │  │
│  │                      └───────────────┘               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Natural Language Interface
**Location**: Runs inside DaVinci Resolve console or custom UI panel

**What it does**:
- Accept natural language commands from user
- Display AI responses and execution status
- Show preview of operations before execution
- 20-second render limit enforcement

**Example Commands**:
```
> Create a lower-third with red text saying "John Doe"
> Add glow effect to the title
> Generate a sci-fi background using AI
> Animate the text from left to right
```

### 2. GitHub Copilot CLI Integration
**Command**: `gh copilot suggest` and `gh copilot explain`

**What it does**:
- Parse natural language into structured commands
- Provide context-aware suggestions
- Help explain Fusion concepts
- No OpenAI API key needed (uses gh auth)

**Usage Pattern**:
```python
import subprocess
import json

# Get suggestion from Copilot CLI
result = subprocess.run(
    ['gh', 'copilot', 'suggest', '-t', 'shell', 'create red background in fusion'],
    capture_output=True,
    text=True
)

# Parse Copilot's response
suggestion = parse_copilot_output(result.stdout)

# Execute in Resolve
execute_fusion_command(suggestion)
```

### 3. Intent Parser & Task Router
**What it does**:
- Analyze user request
- Determine if task can be done with Fusion nodes OR needs AI generation
- Route to appropriate handler

**Decision Logic**:
```python
def route_task(user_request: str, copilot_suggestion: dict):
    """
    Determine where to execute the task
    """
    # Tasks Fusion CAN do:
    # - Basic shapes (backgrounds, gradients, text)
    # - Color correction, blur, glow effects
    # - Transformations, merges, masks
    # - Node graph manipulation
    
    # Tasks for ComfyUI + Wan 2.2:
    # - AI-generated images (characters, scenes, objects)
    # - Complex visual effects beyond Fusion's capabilities
    # - Style transfers, AI upscaling
    # - Photorealistic rendering
    
    if is_fusion_capable(user_request):
        return 'fusion'
    else:
        return 'comfyui'
```

### 4. Fusion Tools (Existing)
**Files**: `fusion_tools.py`, `controller.py`

**What it does**:
- Create and manipulate Fusion nodes
- Build effects compositions
- 15+ node types (Background, Text, Transform, Merge, Glow, etc.)
- Connect nodes, set parameters

**Example**:
```python
from resolve_ai.fusion_tools import FusionNodeBuilder

builder = FusionNodeBuilder(comp)

# Create lower-third
bg = builder.create_background(color=(1, 0, 0, 1))  # Red
text = builder.create_text(text="John Doe", size=0.1)
transform = builder.create_transform(center=(0.2, 0.8))

builder.connect_nodes(bg, text)
builder.connect_nodes(text, transform)
builder.connect_to_output(transform)
```

### 5. ComfyUI Client (NEW)
**What it does**:
- Connect to ComfyUI server API
- Submit Wan 2.2 generation workflows
- Monitor generation progress
- Download generated images
- Import into Resolve media pool
- Create Loader nodes pointing to generated assets

**Example**:
```python
from resolve_ai.comfyui_client import ComfyUIClient

client = ComfyUIClient(server_url="http://localhost:8188")

# Generate sci-fi background
image_path = client.generate(
    prompt="cinematic sci-fi background, neon lights, cyberpunk city",
    model="wan2.2",
    width=1920,
    height=1080,
    steps=20  # Quick generation for 20s preview limit
)

# Import to Resolve
media_item = resolve.import_media(image_path)

# Create Loader node in Fusion
loader = builder.create_loader(clip=media_item)
```

## Workflow Examples

### Example 1: Pure Fusion Task
```
User: "Create a lower-third with red text"

Flow:
1. User types command in Resolve console
2. gh copilot suggest → "Create fusion nodes: background(red), text, transform"
3. Intent parser → "This is Fusion-capable"
4. Route to fusion_tools.py
5. Execute: create nodes, connect, preview
6. Result: Composition ready in 20s
```

### Example 2: AI Generation Task
```
User: "Generate a fantasy dragon flying over mountains"

Flow:
1. User types command in Resolve console
2. gh copilot suggest → "Use AI generation for complex scene"
3. Intent parser → "This needs ComfyUI"
4. Route to ComfyUI client
5. Submit to ComfyUI server with Wan 2.2
6. Generate image (respecting 20s limit → low steps)
7. Import to media pool
8. Create Loader node in Fusion
9. Result: AI-generated background ready
```

### Example 3: Hybrid Task
```
User: "Create title with AI-generated nebula background"

Flow:
1. gh copilot suggest → "AI background + Fusion text"
2. Intent parser → "Hybrid: ComfyUI + Fusion"
3. Execute:
   a. ComfyUI generates nebula image
   b. Import to Resolve
   c. Create Loader node for nebula
   d. Create Text node with title
   e. Create Merge node
   f. Connect: nebula → merge, text → merge
   g. Connect merge to output
4. Result: AI background + Fusion text composition
```

## Technology Stack

### Core
- **Python 3.11+**: Main language
- **DaVinci Resolve Python API**: Fusion/timeline control
- **GitHub Copilot CLI**: AI assistance (no OpenAI API)
- **ComfyUI API**: AI generation backend

### Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"  # ComfyUI API calls
websocket-client = "^1.6.0"  # ComfyUI progress monitoring
pillow = "^10.1.0"  # Image handling
rich = "^13.7.0"  # Console UI
```

### External Services
- **GitHub Copilot CLI**: `gh copilot` (requires `gh auth login`)
- **ComfyUI Server**: Running locally or remote
- **Wan 2.2 Model**: Loaded in ComfyUI

## GitHub Copilot CLI Integration

### Installation
```bash
# Install GitHub CLI
winget install --id GitHub.cli

# Authenticate
gh auth login

# Verify Copilot access
gh copilot --help
```

### Usage Patterns

#### Pattern 1: Command Suggestion
```python
def get_copilot_suggestion(user_query: str) -> dict:
    """Get Copilot's suggestion for a command"""
    result = subprocess.run(
        [
            'gh', 'copilot', 'suggest',
            '-t', 'shell',
            user_query
        ],
        capture_output=True,
        text=True
    )
    return parse_copilot_response(result.stdout)
```

#### Pattern 2: Code Explanation
```python
def explain_fusion_concept(concept: str) -> str:
    """Get Copilot's explanation"""
    result = subprocess.run(
        [
            'gh', 'copilot', 'explain',
            f'Fusion node system: {concept}'
        ],
        capture_output=True,
        text=True
    )
    return result.stdout
```

#### Pattern 3: Task Breakdown
```python
def break_down_task(user_request: str) -> list:
    """Use Copilot to break complex task into steps"""
    prompt = f"""
    Break this video editing task into steps:
    "{user_request}"
    
    Available tools:
    - Fusion nodes (backgrounds, text, effects, transforms)
    - ComfyUI AI generation (images, scenes, characters)
    """
    
    result = subprocess.run(
        ['gh', 'copilot', 'suggest', '-t', 'shell', prompt],
        capture_output=True,
        text=True
    )
    
    return parse_steps(result.stdout)
```

## ComfyUI + Wan 2.2 Integration

### ComfyUI Server Setup
```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI

# Install dependencies
pip install -r requirements.txt

# Download Wan 2.2 model
# Place in: models/checkpoints/wan2.2.safetensors

# Start server
python main.py --listen 0.0.0.0 --port 8188
```

### Workflow JSON for Wan 2.2
```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "wan2.2.safetensors"
    }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "{prompt}",
      "clip": ["1", 1]
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 42,
      "steps": 20,
      "cfg": 7.0,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["5", 0],
      "latent_image": ["6", 0]
    }
  }
}
```

### Python Client
```python
import requests
import websocket
import json

class ComfyUIClient:
    def __init__(self, server_url="http://localhost:8188"):
        self.server_url = server_url
        self.client_id = str(uuid.uuid4())
    
    def generate(self, prompt: str, steps: int = 20) -> str:
        """Generate image and return path"""
        workflow = self.load_workflow_template()
        workflow = self.customize_workflow(workflow, prompt, steps)
        
        # Submit workflow
        response = requests.post(
            f"{self.server_url}/prompt",
            json={"prompt": workflow, "client_id": self.client_id}
        )
        
        prompt_id = response.json()["prompt_id"]
        
        # Monitor progress via WebSocket
        ws = websocket.create_connection(
            f"ws://{self.server_url}/ws?clientId={self.client_id}"
        )
        
        while True:
            msg = json.loads(ws.recv())
            if msg["type"] == "executing" and msg["data"]["prompt_id"] == prompt_id:
                if msg["data"]["node"] is None:
                    # Generation complete
                    break
        
        # Download image
        image_data = self.get_image(prompt_id)
        
        # Save to temp directory
        output_path = Path(tempfile.gettempdir()) / f"comfyui_{prompt_id}.png"
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        return str(output_path)
```

## Decision Logic

### Task Classification
```python
def classify_task(user_request: str, copilot_analysis: dict) -> str:
    """
    Classify task as 'fusion', 'comfyui', or 'hybrid'
    """
    
    # Keywords for Fusion-capable tasks
    fusion_keywords = [
        'background', 'gradient', 'text', 'title', 'lower-third',
        'color', 'blur', 'glow', 'transform', 'position', 'scale',
        'rotate', 'merge', 'mask', 'brightness', 'contrast'
    ]
    
    # Keywords for AI generation tasks
    ai_keywords = [
        'generate', 'create character', 'create scene', 'fantasy',
        'realistic', 'photo', 'painting', 'style', 'artistic',
        'dragon', 'landscape', 'person', 'object', 'complex'
    ]
    
    request_lower = user_request.lower()
    
    fusion_score = sum(1 for kw in fusion_keywords if kw in request_lower)
    ai_score = sum(1 for kw in ai_keywords if kw in request_lower)
    
    if ai_score > fusion_score:
        return 'comfyui'
    elif fusion_score > 0 and ai_score > 0:
        return 'hybrid'
    else:
        return 'fusion'
```

## 20-Second Iteration Principle

### Why 20 Seconds?
- Wan 2.2 can generate images in ~10-20 seconds with low steps
- Fusion node operations are instant
- Preview playback is 20 seconds
- Keeps workflow fast and iterative

### Implementation
```python
class ResolveAIAssistant:
    MAX_RENDER_SECONDS = 20
    MAX_COMFYUI_STEPS = 20  # Fast generation
    
    def execute_task(self, task: dict):
        """Execute with 20s limit"""
        
        # Set render range
        timeline = self.controller.get_current_timeline()
        frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24")
        end_frame = int(self.MAX_RENDER_SECONDS * frame_rate)
        
        timeline.SetSetting("useInOutRange", "1")
        timeline.SetSetting("inFrame", "0")
        timeline.SetSetting("outFrame", str(end_frame))
        
        # Execute
        if task['type'] == 'comfyui':
            # Use low steps for speed
            image = self.comfyui_client.generate(
                prompt=task['prompt'],
                steps=self.MAX_COMFYUI_STEPS
            )
        
        # Preview
        timeline.Play()
```

## User Interface Options

### Option 1: Console/REPL
```python
# Simple console interface
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def run_console():
    console.print("[bold green]DaVinci Resolve AI Assistant[/bold green]")
    console.print("Control Fusion with natural language\n")
    
    while True:
        user_input = Prompt.ask("[blue]>[/blue]")
        
        if user_input.lower() in ['exit', 'quit']:
            break
        
        # Process command
        response = process_command(user_input)
        console.print(response)
```

### Option 2: Custom UI Panel (Advanced)
```python
# DaVinci Resolve UI Manager
from python.DaVinciResolveScript import scriptapp

ui = fusion.UIManager
dispatcher = bmd.UIDispatcher(ui)

# Create dialog window
win = dispatcher.AddWindow({
    'ID': 'ResolveAI',
    'WindowTitle': 'AI Assistant',
    'Geometry': [100, 100, 600, 400],
}, [
    ui.VGroup([
        ui.Label({'Text': 'Enter command:'}),
        ui.TextEdit({'ID': 'CommandInput'}),
        ui.Button({'ID': 'ExecuteBtn', 'Text': 'Execute'}),
        ui.TextEdit({'ID': 'OutputText', 'ReadOnly': True})
    ])
])

def on_execute_clicked(ev):
    command = win.Find('CommandInput').PlainText
    result = process_command(command)
    win.Find('OutputText').PlainText = result

win.On.ExecuteBtn.Clicked = on_execute_clicked
win.Show()
dispatcher.RunLoop()
```

## Next Steps

1. **Remove VS Code extension code** (`resolve-copilot-extension/`)
2. **Create ComfyUI client** (`comfyui_client.py`)
3. **Integrate gh copilot CLI** (`copilot_cli.py`)
4. **Build task router** (`task_router.py`)
5. **Create console UI** (`console_ui.py`)
6. **Update documentation** (reflect new architecture)
7. **Test workflow**: Natural language → Copilot CLI → Fusion/ComfyUI → Preview

## File Structure (Revised)

```
resolve-ai-assistant/
├── src/
│   └── resolve_ai/
│       ├── controller.py          # ✅ Keep (Resolve API)
│       ├── fusion_tools.py        # ✅ Keep (Fusion nodes)
│       ├── copilot_cli.py         # 🆕 NEW (gh copilot integration)
│       ├── comfyui_client.py      # 🆕 NEW (ComfyUI + Wan 2.2)
│       ├── task_router.py         # 🆕 NEW (Fusion vs ComfyUI decision)
│       ├── console_ui.py          # 🆕 NEW (User interface)
│       └── assistant.py           # 🆕 NEW (Main orchestrator)
├── examples/
│   ├── fusion_examples.py         # ✅ Keep
│   ├── comfyui_examples.py        # 🆕 NEW
│   └── hybrid_workflows.py        # 🆕 NEW
├── docs/
│   ├── ARCHITECTURE.md            # 🆕 This file
│   ├── COPILOT_CLI_GUIDE.md       # 🆕 NEW
│   ├── COMFYUI_SETUP.md           # 🆕 NEW
│   └── USER_GUIDE.md              # 🆕 NEW
├── pyproject.toml                 # Update dependencies
└── README.md                      # Update description
```

## Conclusion

This is a **DaVinci Resolve extension**, not a VS Code extension. It:
- Runs inside DaVinci Resolve
- Uses gh copilot CLI for AI (no OpenAI API)
- Controls Fusion nodes directly
- Delegates to ComfyUI + Wan 2.2 for AI-generated content
- Maintains 20-second iteration cycle
- Provides natural language interface within Resolve

The architecture is now correctly aligned with your vision! 🎬🤖
