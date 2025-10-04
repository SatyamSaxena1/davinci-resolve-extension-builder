# DaVinci Resolve AI Assistant

AI-powered automation assistant for DaVinci Resolve 18.6+ with natural language control of Fusion node systems, timeline editing, and project management.

## Features

🎯 **Natural Language Control**: Control DaVinci Resolve using conversational commands  
🎨 **Fusion Node Automation**: Create and manipulate Fusion compositions programmatically  
🤖 **AI-Powered Workflows**: Multi-step automation with GPT-4  
📝 **Timeline Management**: Markers, imports, timeline creation  
🎬 **Template Generation**: Lower-thirds, effects, compositions on demand  

## What Can It Do?

- **Create Fusion node graphs** from natural language descriptions
- **Build visual effects templates** (lower-thirds, titles, overlays)
- **Automate timeline operations** (markers, imports, rendering)
- **Manage media pool** (import, organize)
- **Execute multi-step workflows** conversationally

## Installation

### Prerequisites

1. **DaVinci Resolve 18.6+** installed and running
2. **Python 3.11+**
3. **Poetry** for dependency management
4. **OpenAI API key**

### Setup

```powershell
# Navigate to project directory
cd resolve-ai-assistant

# Install dependencies with Poetry
poetry install

# Copy environment template
copy .env.example .env

# Edit .env and add your OpenAI API key
notepad .env
```

### Configure DaVinci Resolve Script API

The assistant needs access to DaVinci Resolve's Python API:

**Windows:**
```powershell
# Set environment variable (adjust path if needed)
$env:RESOLVE_SCRIPT_API = "C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
```

**Alternative**: The paths are auto-detected on Windows, but you can set them in `.env` if needed.

## Usage

### Start the AI Assistant

```powershell
# Activate Poetry environment
poetry shell

# Run the assistant
resolve-ai

# Or directly with Poetry
poetry run resolve-ai
```

### Example Commands

Once running, you can use natural language commands:

```
You: Create a lower-third with title "John Doe" and subtitle "CEO"
AI: [Creates complete Fusion composition with background, text, and animations]

You: Add a blue marker at frame 100 with note "Start of interview"
AI: [Adds marker to timeline]

You: Create a text node that says "Subscribe" in red color
AI: [Creates and configures Text+ node]

You: Show me what nodes are currently in the Fusion composition
AI: [Lists all nodes with details]

You: Create a background node with blue color and connect it to a transform
AI: [Creates nodes and connects them]

You: Clear the composition and start fresh
AI: [Removes all nodes]
```

## Architecture

### Core Components

```
resolve-ai-assistant/
├── src/resolve_ai/
│   ├── __init__.py
│   ├── controller.py       # Main Resolve API wrapper
│   ├── fusion_tools.py     # Fusion node manipulation
│   ├── ai_tools.py         # OpenAI function schemas
│   └── cli.py              # Conversational interface
├── examples/
│   ├── basic_fusion.py     # Example: Basic Fusion automation
│   ├── lower_third.py      # Example: Lower-third template
│   └── timeline_ops.py     # Example: Timeline operations
├── pyproject.toml          # Poetry configuration
└── .env                    # Environment variables
```

### How It Works

1. **User Input** → Natural language command
2. **LLM Processing** → GPT-4 interprets intent and selects tools
3. **Function Calling** → AI executes Resolve API functions
4. **Feedback Loop** → Results returned to LLM for next steps
5. **User Response** → Confirmation and explanation

### Available Tools

The AI has access to these function tools:

**Fusion Node Tools:**
- `create_fusion_node` - Create any Fusion node type
- `connect_fusion_nodes` - Connect nodes together
- `set_node_parameters` - Modify node parameters
- `create_text_node` - Create styled text
- `create_background_node` - Create solid backgrounds
- `create_lower_third` - Complete lower-third template
- `list_fusion_nodes` - Show all nodes
- `delete_fusion_node` - Remove nodes
- `clear_fusion_composition` - Clear all nodes

**Timeline Tools:**
- `get_project_status` - Get project information
- `create_timeline` - Create new timeline
- `add_timeline_marker` - Add markers
- `import_media_files` - Import media
- `list_media_pool_items` - Show media pool

## Advanced Usage

### Programmatic API

You can also use the assistant programmatically:

```python
from resolve_ai import ResolveAIController, FusionNodeBuilder

# Initialize controller
controller = ResolveAIController()

# Get Fusion composition
comp = controller.get_fusion_comp()

# Build nodes
builder = FusionNodeBuilder(comp)

# Create a lower-third
nodes = builder.build_lower_third(
    title_text="John Doe",
    subtitle_text="CEO",
    bg_color=(0.0, 0.3, 0.6, 0.9),  # Blue background
    text_color=(1.0, 1.0, 1.0)      # White text
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
4. Verify Python API paths in `.env`

### Fusion Composition Not Available

**Problem**: `Fusion composition not available`

**Solution**: Select a video clip on the timeline before using Fusion tools

### API Key Issues

**Problem**: `OPENAI_API_KEY not found`

**Solution**: 
1. Create `.env` file from `.env.example`
2. Add your OpenAI API key: `OPENAI_API_KEY=sk-...`

### Module Import Errors

**Problem**: `Failed to import DaVinciResolveScript`

**Solutions**:
1. Verify DaVinci Resolve installation
2. Check `RESOLVE_SCRIPT_API` path in `.env`
3. On Windows, default path is auto-detected

## Limitations

- Requires DaVinci Resolve Studio or Free version with scripting enabled
- Fusion API has limitations compared to manual UI manipulation
- Some advanced Fusion features require manual configuration
- OpenFX plugins cannot be generated at runtime (requires compilation)

## Future Enhancements (Phase 2+)

- 🔮 VS Code extension with inline suggestions
- 🎨 ComfyUI integration for AI-generated assets
- 🎬 Template library with pre-built effects
- 📊 Analytics and workflow optimization
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
