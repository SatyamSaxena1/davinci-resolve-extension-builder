# DaVinci Resolve AI Assistant - VS Code Extension

AI-powered GitHub Copilot integration for DaVinci Resolve automation with permission-based execution and 20-second rapid iteration cycles.

## Features

🤖 **@resolve Chat Participant** - Natural language control through GitHub Copilot Chat  
✋ **Permission-Based Execution** - AI asks before every action ("dog behavior")  
📺 **Automatic Preview** - 20-second video output after each step  
🎬 **Fusion Node Control** - Create and manipulate Fusion compositions  
⏱️ **Rapid Iteration** - 20-second render limit for fast feedback  
🎯 **Context-Aware** - Maintains conversation context across steps  

## Requirements

- **VS Code 1.85+** with GitHub Copilot enabled
- **DaVinci Resolve 18.6+** installed and running
- **Python 3.11+** with Poetry
- **resolve-ai-assistant** Python package (included in workspace)

## Installation

### 1. Install Dependencies

```powershell
# Navigate to resolve-ai-assistant
cd resolve-ai-assistant

# Install Python dependencies
poetry install

# Verify installation
poetry run python -c "import resolve_ai; print('✓ Ready')"
```

### 2. Install VS Code Extension

#### From Source (Development)

```powershell
# Navigate to extension directory
cd resolve-copilot-extension

# Install npm dependencies
npm install

# Compile TypeScript
npm run compile

# Package extension
npm run package

# Install the .vsix file
code --install-extension resolve-copilot-assistant-0.1.0.vsix
```

#### From VSIX (Release)

1. Download `resolve-copilot-assistant-0.1.0.vsix`
2. In VS Code: Extensions → `...` → Install from VSIX
3. Select the downloaded file

### 3. Configure Extension

Open VS Code settings (`Ctrl+,`) and search for "resolve":

```json
{
  "resolve.pythonPath": "C:\\Users\\satya\\davinci-resolve-extension-builder\\resolve-ai-assistant\\.venv\\Scripts\\python.exe",
  "resolve.projectPath": "${workspaceFolder}/resolve-ai-assistant",
  "resolve.maxRenderSeconds": 20,
  "resolve.autoPreview": true,
  "resolve.requirePermission": true
}
```

**Or** use the `.vscode/settings.json` template:

```powershell
# Copy template
copy .vscode\settings.json.example .vscode\settings.json

# Edit paths if needed
code .vscode\settings.json
```

## Usage

### Start DaVinci Resolve

1. Open DaVinci Resolve
2. Create or open a project
3. Optionally: Select a video clip on timeline (for Fusion operations)

### Open Copilot Chat

- Press `Ctrl+Shift+I` or click Chat icon
- Type `@resolve` to invoke the assistant

### Example Commands

```
@resolve create a lower-third with title "John Doe"

@resolve add blue background

@resolve create text that says "Subscribe" in red

@resolve show me what's in the composition

@resolve clear composition and start over
```

### Permission-Based Workflow

```
You: @resolve create a lower-third

AI: ## 📋 Plan

    → Step 1: Create blue background rectangle
    □ Step 2: Add title text "Title"
    □ Step 3: Position at lower-third
    
    ⏱️ Render range will be set to 20 seconds
    
    ❓ Shall I proceed with Step 1?

You: yes

AI: ✓ Create blue background rectangle
    📺 Playing preview...
    
    [■□□] 1/3 steps complete
    
    ❓ Continue with Step 2: Add title text?

You: yes but make it orange

AI: ✓ Plan updated:
    - Changed background color to orange
    
    ❓ Proceed with modified step?

You: yes

AI: ✓ Create orange background rectangle
    📺 Playing preview...
    
    [■■□] 2/3 steps complete
    
    ❓ Continue with Step 2: Add title text?
```

## Commands

Access from Command Palette (`Ctrl+Shift+P`):

| Command | Description |
|---------|-------------|
| `Resolve: Play Preview (20s)` | Play 20-second preview in DaVinci |
| `Resolve: Get Composition Context` | Show current Fusion composition state |
| `Resolve: Set Render Range` | Change max render duration |
| `Resolve: Clear Fusion Composition` | Remove all nodes |
| `Resolve: Open AI Assistant Chat` | Open Copilot Chat with @resolve |

## Configuration

### Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `resolve.pythonPath` | (auto) | Path to Python with resolve-ai installed |
| `resolve.projectPath` | `${workspaceFolder}/resolve-ai-assistant` | Path to Python backend |
| `resolve.maxRenderSeconds` | `20` | Maximum render duration (1-120s) |
| `resolve.autoPreview` | `true` | Auto-play preview after changes |
| `resolve.requirePermission` | `true` | Ask before executing actions |
| `resolve.showProgress` | `true` | Show progress indicators |
| `resolve.verboseLogging` | `false` | Enable debug logging |

### Recommended Workspace Settings

```json
{
  "resolve.maxRenderSeconds": 20,
  "resolve.autoPreview": true,
  "resolve.requirePermission": true,
  "files.associations": {
    "*.fuse": "lua",
    "*.dctl": "c"
  }
}
```

## How It Works

### Architecture

```
┌─────────────────────────────────────┐
│  VS Code + GitHub Copilot Chat      │  ← User types @resolve commands
│  (@resolve chat participant)        │
└──────────────┬──────────────────────┘
               │
               ↓ (JSON over stdio)
┌─────────────────────────────────────┐
│  Python Backend (vscode_bridge.py)  │  ← Permission logic & execution
│  - CopilotExecutor                  │
│  - FusionNodeBuilder                │
└──────────────┬──────────────────────┘
               │
               ↓ (DaVinci Resolve API)
┌─────────────────────────────────────┐
│  DaVinci Resolve 18.6               │  ← Actual Fusion node manipulation
│  - Fusion Composition               │    & video preview
└─────────────────────────────────────┘
```

### Execution Flow

1. **User Message** → Natural language in @resolve chat
2. **Intent Parsing** → Python backend understands request
3. **Task Breakdown** → Split into approachable steps
4. **Permission Check** → Show plan, ask for approval
5. **Step Execution** → Execute approved action
6. **Preview** → Set 20s range, play on video output
7. **Next Step** → Ask permission for next action
8. **Repeat** → Continue until complete

## Troubleshooting

### Extension Not Activating

**Problem**: `@resolve` not available in Copilot Chat

**Solutions**:
1. Ensure GitHub Copilot extension is installed and enabled
2. Check VS Code version (must be 1.85+)
3. Reload window: `Ctrl+Shift+P` → "Reload Window"
4. Check Output panel: View → Output → "DaVinci Resolve AI"

### Python Backend Connection Failed

**Problem**: `Failed to connect to DaVinci Resolve`

**Solutions**:
1. Verify DaVinci Resolve is running
2. Open a project in Resolve
3. Check Python path in settings
4. Test Python backend manually:
   ```powershell
   cd resolve-ai-assistant
   poetry run python -c "from resolve_ai import ResolveAIController; ResolveAIController()"
   ```

### No Fusion Composition

**Problem**: `No Fusion composition available`

**Solution**: Select a video clip on the timeline before using Fusion commands

### Preview Not Playing

**Problem**: Preview command succeeds but nothing happens

**Possible causes**:
- DaVinci Resolve window minimized (must be visible)
- Timeline playhead not at correct position
- Render range not set correctly

**Solutions**:
1. Ensure Resolve window is visible
2. Use `@resolve show context` to check status
3. Manually verify render range (in/out points)

### Permission Mode Stuck

**Problem**: AI keeps asking permission, won't execute

**Solution**: Reply with exact approval words: "yes", "go", "proceed", "continue", or "ok"

### Modification Not Applied

**Problem**: Said "make it blue" but color didn't change

**Solution**: Use clear modification phrases:
- "change color to blue"
- "make it blue instead"
- "update background to blue"

## Examples

### Create Lower-Third

```
@resolve create a lower-third with "John Doe" as title and "CEO" as subtitle
```

Creates professional lower-third graphic with background, title, and subtitle.

### Simple Text

```
@resolve add text that says "Subscribe Now" in red color
```

Creates single text node with specified content and color.

### Background

```
@resolve create a blue background
```

Creates solid color background node.

### Check Status

```
@resolve what's currently in the composition?
```

Shows all nodes and composition state.

### Clear and Start Over

```
@resolve clear the composition
```

Removes all nodes to start fresh.

## Development

### Build from Source

```powershell
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Package extension
npm run package
```

### Testing

1. Open extension project in VS Code
2. Press `F5` to launch Extension Development Host
3. Test @resolve commands in new window

### Debugging

Enable verbose logging in settings:

```json
{
  "resolve.verboseLogging": true
}
```

Check logs:
- **TypeScript**: VS Code Output → "Extension Host"
- **Python**: VS Code Output → "DaVinci Resolve AI"

## Keyboard Shortcuts

No default shortcuts, but you can add:

```json
{
  "key": "ctrl+alt+r",
  "command": "resolve.openChat",
  "when": "editorTextFocus"
},
{
  "key": "ctrl+alt+p",
  "command": "resolve.preview",
  "when": "editorTextFocus"
}
```

## Known Limitations

- Requires GitHub Copilot subscription
- DaVinci Resolve must be running and visible
- Some Fusion nodes not yet supported (limited by API)
- Preview playback may not work if Resolve is minimized
- Animation keyframes require manual adjustment

## Roadmap

- [ ] More Fusion node types (Glow, Blur, Color Corrector)
- [ ] Animation and keyframe control
- [ ] Template library with pre-built effects
- [ ] Undo/redo for iterations
- [ ] Save iteration checkpoints
- [ ] ComfyUI integration (Phase 4)
- [ ] Voice control interface

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../../LICENSE)

## Credits

Part of the [DaVinci Resolve Extension Builder](https://github.com/SatyamSaxena1/davinci-resolve-extension-builder) toolkit.

Built with:
- GitHub Copilot Chat API
- DaVinci Resolve Python API
- TypeScript + Node.js
- Python + Poetry

---

**Remember**: This assistant is your creative partner. It asks before acting, shows you the result, and waits for your feedback. You're always in control! 🎬
