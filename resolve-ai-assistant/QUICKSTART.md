# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```powershell
# Navigate to the project
cd resolve-ai-assistant

# Install with Poetry
poetry install
```

### 2. Configure Environment

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file
notepad .env
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the Assistant

```powershell
# Activate Poetry environment
poetry shell

# Start the AI assistant
resolve-ai
```

## First Steps

### Before Running
1. **Open DaVinci Resolve**
2. **Open or create a project**
3. **(Optional) Select a video clip** for Fusion tools

### Example Workflow

```
You: What's the current project status?
AI: Shows project info, timeline details, resolution

You: Create a new timeline called "My Video" at 24fps
AI: Creates the timeline

You: Add a blue marker at frame 100 with note "Important scene"
AI: Adds the marker

You: Create a lower-third with title "John Smith" and subtitle "Director"
AI: Builds complete Fusion composition
```

## Common Commands

### Project & Timeline
- "Show me the current project information"
- "Create a new timeline called 'X' at 30fps in 4K"
- "Add a red marker at frame 500 with note 'cut here'"
- "List all items in the media pool"

### Fusion Nodes
- "Create a text node that says 'Hello World' in blue"
- "Create a background with red color"
- "Show me all nodes in the composition"
- "Clear the composition"
- "Create a lower-third for 'Jane Doe'"

### Advanced
- "Create a text node with glow effect"
- "Build a title sequence with background, text, and blur"
- "Connect the background to a transform node"

## Running Examples

### Basic Fusion Automation
```powershell
poetry run python examples/basic_fusion.py
```

### Lower-Third Templates
```powershell
poetry run python examples/lower_third.py
```

### Timeline Operations
```powershell
poetry run python examples/timeline_ops.py
```

## Troubleshooting

### Can't connect to Resolve?
- Make sure DaVinci Resolve is running
- Open a project (it won't work without an open project)

### Fusion composition not available?
- Select a video clip on the timeline
- Or add a Fusion composition clip to the timeline

### API key not working?
- Check that `.env` file has `OPENAI_API_KEY=sk-...`
- Verify the key is valid at platform.openai.com

## Tips

1. **Be specific**: "Create a blue text node" works better than "make text"
2. **Step by step**: Complex compositions work better when broken into steps
3. **Use names**: Referring to nodes by name helps the AI track them
4. **Check the Fusion page**: After creation, switch to Fusion to see the node graph

## What's Next?

- Try the example scripts to see what's possible
- Experiment with different node combinations
- Build your own workflow automation scripts
- Explore the API documentation in README.md

---

**Need help?** Check the full README.md for detailed documentation.
