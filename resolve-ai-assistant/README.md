# DaVinci Resolve AI Assistant

**A DaVinci Resolve Extension** that runs inside Resolve, using GitHub Copilot CLI for AI assistance, controlling Fusion nodes directly, and delegating AI-generated graphics to ComfyUI + Wan 2.2.

## Architecture

This is **NOT a VS Code extension**. It's a **DaVinci Resolve Python script** that:
1. 🎬 **Runs inside DaVinci Resolve** (console or UI panel)
2. 🤖 **Uses GitHub Copilot CLI** (`gh copilot`) for natural language understanding
3. 🎨 **Controls Fusion nodes** via DaVinci Resolve Python API
4. 🖼️ **Delegates to ComfyUI + Wan 2.2** for AI-generated graphics/VFX
5. ⚡ **20-second iteration cycle** for rapid workflow

## Features

🎯 **Natural Language Control**: Use conversational commands inside DaVinci Resolve  
🎨 **Fusion Node Automation**: Create and manipulate Fusion compositions programmatically  
🤖 **GitHub Copilot CLI Integration**: AI assistance without OpenAI API  
🖼️ **ComfyUI Integration**: AI-generated backgrounds, characters, scenes via Wan 2.2  
� **Intelligent Routing**: Automatically decides Fusion vs ComfyUI based on task  
⚡ **20-Second Limit**: Fast iteration with optimized generation  

## What Can It Do?

### DaVinci Resolve Control
- **Create Fusion node graphs** from natural language descriptions
- **Build visual effects templates** (lower-thirds, titles, overlays)
- **Automate timeline operations** (markers, imports, rendering)
- **Manage media pool** (import, organize)
- **Execute multi-step workflows** conversationally

## Installation

### Prerequisites

1. **DaVinci Resolve 18.6+** - installed and running
2. **Python 3.11+** - for Resolve scripting
3. **Poetry** - dependency management (`pip install poetry`)
4. **GitHub Copilot CLI** - install `gh` CLI and authenticate:
   ```powershell
   # Install GitHub CLI (Windows)
   winget install GitHub.cli
   
   # Authenticate and enable Copilot
   gh auth login
   gh extension install github/gh-copilot
   ```
5. **ComfyUI Server** - for AI image generation:
   - Install from https://github.com/comfyanonymous/ComfyUI
   - Download **Wan 2.2 model** to `ComfyUI/models/checkpoints/`
   - Start server: `python main.py` (runs on http://localhost:8188)

### Setup

```powershell
# Navigate to project directory
cd resolve-ai-assistant

# Install dependencies with Poetry
poetry install

# Verify GitHub Copilot CLI is working
gh copilot suggest "create a red background"

# Start ComfyUI server (separate terminal)
cd path\to\ComfyUI
python main.py
```

### Configure DaVinci Resolve Script API

The assistant needs access to DaVinci Resolve's Python API:

**Windows:**
```powershell
# Set environment variable (adjust path if needed)
$env:RESOLVE_SCRIPT_API = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
```

**Alternative**: The paths are auto-detected on Windows.

## Usage

### Quick Start

#### Method 1: Simple Launcher (Recommended)

1. **Launch DaVinci Resolve** and open a project
2. **Open PowerShell or Terminal**
3. **Run:**
   ```powershell
   cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
   python simple_launch.py
   ```
4. **Type commands** at the prompt and press Enter:
   ```
   What would you like to create? (): Create a blue background
   What would you like to create? (): Add text that says Hello World
   What would you like to create? (): exit
   ```

**Important**: Make sure to TYPE a command before pressing Enter. Pressing Enter without typing will exit the assistant.

#### Method 2: Debug Mode (Troubleshooting)

If you have issues, use the debug launcher to see detailed diagnostics:

```powershell
cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
python debug_launch.py
```

This shows:
- ✓ Python environment details
- ✓ Dependency check (rich, requests, websocket, PIL)
- ✓ DaVinci Resolve API connection status
- ✓ Module import verification
- ✓ System status before launch

#### Method 3: Inside DaVinci Resolve Console

For running directly in Resolve's console:

```python
# DaVinci Resolve Console
exec(open(r"c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant\simple_launch.py").read())
```

Then type commands at the prompt.

### Example Workflows

#### Fusion Tasks (Pure Fusion Nodes)
```
You: Create a red background with white text saying "Welcome"
Assistant: [Analyzes with Copilot CLI → Routes to Fusion → Creates Background + Text+ nodes]

You: Add a blue glow effect to the text
Assistant: [Routes to Fusion → Adds Glow node, connects to text]
```

#### ComfyUI Tasks (AI-Generated Graphics)
```
You: Generate a fantasy dragon scene as background
Assistant: [Analyzes with Copilot CLI → Routes to ComfyUI → Generates with Wan 2.2 → Imports to Fusion]

You: Create a cyberpunk character portrait
Assistant: [Routes to ComfyUI → Generates image → Imports as Loader node]
```

#### Hybrid Tasks (Both Systems)
```
You: Create a title card with AI-generated nebula background
Assistant: 
  Step 1: [ComfyUI generates nebula image]
  Step 2: [Fusion creates Loader + Text+ + Merge composition]
  Result: [Complete title card in 18 seconds]
```

## Architecture

### Core Components

```
resolve-ai-assistant/
├── src/resolve_ai/
│   ├── __init__.py
│   ├── controller.py       # DaVinci Resolve API wrapper
│   ├── fusion_tools.py     # Fusion node creation (15+ node types)
│   ├── copilot_cli.py      # GitHub Copilot CLI integration
│   ├── comfyui_client.py   # ComfyUI + Wan 2.2 client
│   ├── task_router.py      # Intelligent Fusion vs ComfyUI routing
│   ├── assistant.py        # Main orchestrator (TODO)
│   └── console_ui.py       # Rich console interface (TODO)
├── examples/
│   ├── basic_fusion.py     # Example: Basic Fusion automation
│   ├── lower_third.py      # Example: Lower-third template
│   └── timeline_ops.py     # Example: Timeline operations
├── CORRECT_ARCHITECTURE.md # Full architecture documentation
├── pyproject.toml          # Poetry configuration
└── .env                    # Environment variables (optional)
```

### How It Works

1. **User Input** → Natural language command (inside Resolve)
2. **Copilot CLI Analysis** → `gh copilot suggest` understands intent
3. **Task Routing** → Decides Fusion vs ComfyUI vs Hybrid
4. **Execution** → 
   - **Fusion**: Create nodes via Resolve Python API
   - **ComfyUI**: Generate image via Wan 2.2 → Import to Fusion
5. **Preview** → Shows result in Fusion viewer (20-second cycle)
6. **Iteration** → User refines or moves to next task

### Task Routing Decision Logic

**Routes to Fusion when:**
- Simple shapes (backgrounds, gradients, masks)
- Text overlays (Text+, TextPlus)
- Basic effects (glow, blur, transform)
- Node connections and compositions

**Routes to ComfyUI when:**
- "generate", "create realistic", "AI"
- Complex scenes (fantasy, landscapes, characters)
- Photorealistic content
- Artistic styles beyond Fusion's capabilities

**Hybrid workflow when:**
- Compositing AI backgrounds with Fusion text/effects
- Multiple AI elements combined in Fusion
- AI-generated elements with Fusion animation

### Available Capabilities

**Fusion Node Creation (15+ node types):**
- Background (solid colors, gradients)
- Text+ (styled text with fonts, colors, sizing)
- Transform (position, rotation, scale)
- Merge (compositing multiple elements)
- Glow, Blur, ColorCorrector, Brightness/Contrast
- Loader (import images/video)
- Saver (export compositions)
- Shapes (Rectangle, Ellipse, Polygon)
- Masks, Filters, Effects

**ComfyUI Generation (via Wan 2.2):**
- AI-generated backgrounds (landscapes, abstract, textures)
- Character portraits (realistic, stylized, fantasy)
- Scene generation (environments, locations)
- Custom prompts with styles and quality settings
- Batch generation for multiple variations

**Timeline Operations:**
- Project/timeline creation and management
- Marker insertion with notes
- Media import and organization
- Clip manipulation

## Advanced Usage

### Programmatic API

You can use the components directly in Python scripts:

```python
from resolve_ai import ResolveAIController, FusionNodeBuilder
from resolve_ai.copilot_cli import CopilotCLI
from resolve_ai.comfyui_client import ComfyUIClient

# Initialize controller
controller = ResolveAIController()
comp = controller.get_fusion_comp()

# Create Fusion nodes directly
builder = FusionNodeBuilder(comp)
bg_node = builder.create_background(color=(1.0, 0.0, 0.0, 1.0))  # Red
text_node = builder.create_text(text="Hello", color=(1.0, 1.0, 1.0))
merge_node = builder.create_merge(foreground=text_node, background=bg_node)

# Use GitHub Copilot CLI for suggestions
copilot = CopilotCLI()
suggestion = copilot.suggest("How do I animate text in Fusion?")
print(suggestion.suggestion)

# Generate AI images with ComfyUI
comfy = ComfyUIClient("http://localhost:8188")
result = comfy.generate_background(
    description="fantasy nebula with purple and blue swirls",
    style="cinematic"
)

# Create custom node graph
bg = builder.create_background_node(color=(0.2, 0.2, 0.2, 1.0))
transform = builder.create_transform_node(size=1.5, angle=45)
builder.connect_nodes(bg, transform)
```

### Custom Workflows

Create Python scripts for repeatable workflows:

```python
from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder

def create_youtube_intro(title: str):
    """Create a YouTube intro composition"""
    controller = ResolveAIController()
    comp = controller.get_fusion_comp()
    builder = FusionNodeBuilder(comp)
    
    # Clear existing nodes
    builder.clear_composition()
    
    # Create background
    bg = builder.create_background_node(
        color=(0.1, 0.1, 0.1, 1.0),
        name="IntroBG",
        x_pos=0, y_pos=0
    )
    
    # Create title text
    title_node = builder.create_text_node(
        text=title,
        name="IntroTitle",
        size=0.15,
        color=(1.0, 0.3, 0.0),  # Orange
        x_pos=1, y_pos=0
    )
    
    # Add glow effect
    glow = builder.create_glow_node(
        name="TitleGlow",
        glow_size=15.0,
        gain=2.0,
        x_pos=2, y_pos=0
    )
    
    # Connect nodes
    builder.connect_nodes(title_node, glow)
    
    # Merge onto background
    merge = builder.create_merge_node(name="FinalMerge", x_pos=3, y_pos=0)
    builder.connect_nodes(bg, merge, input_name="Background")
    builder.connect_nodes(glow, merge, input_name="Foreground")
    
    print(f"✓ YouTube intro created with title: {title}")

# Usage
create_youtube_intro("My Awesome Channel")
```

## Troubleshooting

### Connection Issues

**Problem**: `Failed to connect to DaVinci Resolve`

**Solutions**:
1. Make sure DaVinci Resolve is running
2. Open a project (File → New Project or open existing)
3. Check that Scripting API is enabled in Preferences → System → General
4. Verify Python paths are correct in Resolve console

### GitHub Copilot CLI Issues

**Problem**: `gh copilot command not found`

**Solution**: 
1. Install GitHub CLI: `winget install GitHub.cli`
2. Authenticate: `gh auth login`
3. Install Copilot extension: `gh extension install github/gh-copilot`
4. Verify: `gh copilot --version`

### ComfyUI Connection Issues

**Problem**: `Cannot connect to ComfyUI server`

**Solutions**:
1. Start ComfyUI server: `cd ComfyUI && python main.py`
2. Verify server is running: open http://localhost:8188 in browser
3. Check firewall settings allow localhost:8188
4. Make sure Wan 2.2 model is in `ComfyUI/models/checkpoints/`

### Fusion Composition Not Available

**Problem**: `Fusion composition not available`

**Solution**: 
- Switch to **Fusion page** in DaVinci Resolve, OR
- Select a video clip on the timeline first

### Performance Issues

**Problem**: Generation takes too long (>20 seconds)

**Solutions**:
1. **ComfyUI**: Reduce steps (default 20), lower resolution
2. **Copilot CLI**: Use `optimize_for_20s()` to get faster suggestions
3. **Fusion**: Simplify node graphs, avoid complex effects

### Module Import Errors

**Problem**: `Failed to import DaVinciResolveScript`

**Solutions**:
1. Verify DaVinci Resolve installation
2. Check `RESOLVE_SCRIPT_API` path
3. On Windows, default path is auto-detected

## Limitations

- Requires DaVinci Resolve Studio or Free version (scripting enabled by default)
- Fusion API has limitations compared to manual UI manipulation
- ComfyUI requires GPU for fast generation (CPU mode is very slow)
- Wan 2.2 model is large (~5GB download)
- GitHub Copilot CLI requires active GitHub Copilot subscription
- 20-second limit means complex multi-step workflows need iteration

## Technical Details

### Why GitHub Copilot CLI?
- **No API keys needed**: Uses `gh auth` authentication
- **Free for Copilot subscribers**: No per-token costs
- **Terminal-based**: Works in any environment
- **Context-aware**: Understands DaVinci Resolve/Fusion context

### Why ComfyUI + Wan 2.2?
- **Local execution**: No cloud API dependency
- **High quality**: Wan 2.2 produces excellent results
- **Workflow control**: Full control over generation pipeline
- **Cost-effective**: One-time model download, no per-image costs

### Why Fusion for simple tasks?
- **Instant execution**: No generation time
- **Deterministic**: Same parameters = same result
- **Animatable**: All parameters keyframe-able
- **Lightweight**: No GPU overhead for simple shapes/text

## Future Enhancements

- ✅ ComfyUI integration (COMPLETE)
- ✅ GitHub Copilot CLI integration (COMPLETE)
- ✅ Intelligent task routing (COMPLETE)
- 🚧 Console UI with Rich formatting (IN PROGRESS)
- 🚧 Main assistant orchestrator (IN PROGRESS)
- ⏳ Custom Resolve UI panel integration
- ⏳ Template library with preset compositions
- ⏳ Batch processing workflows
- ⏳ Animation timeline integration
- ⏳ Multi-model support (SDXL, Flux, etc.)
- 🔄 Batch processing capabilities
- 🎯 Voice control interface

## Contributing

Contributions welcome! This is part of the larger `davinci-resolve-extension-builder` project.

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- OpenAI GPT-4 for natural language processing
- DaVinci Resolve Python API
- Poetry for dependency management
- Rich for beautiful CLI output

---

**Part of the DaVinci Resolve Extension Builder toolkit**
