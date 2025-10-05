# Quick Start Guide - DaVinci Resolve AI Assistant

## ✅ The Assistant Works in All Terminals!

PowerShell, VS Code Terminal, Command Prompt - they all work!

## 🚀 How to Launch

### Step 1: Make Sure DaVinci Resolve is Running

- ✅ DaVinci Resolve is open
- ✅ A project is loaded
- ⚠️ ComfyUI is optional (for AI generation)

### Step 2: Open Any Terminal

- PowerShell
- VS Code Terminal
- Command Prompt
- Windows Terminal

### Step 3: Run the Launcher

```powershell
cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
python simple_launch.py
```

### Step 4: You'll See This

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ ║
║ ┃                       🎬 DaVinci Resolve AI Assistant                        ┃ ║
║ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛ ║
╚══════════════════════════════════════════════════════════════════════════════════╝

             System Status             
╭────────────────────┬────────────────╮
│ DaVinci Resolve    │ ✓ Connected    │
│ Fusion Composition │ ✓ Available    │
│ ComfyUI Server     │ ✗ Disconnected │ ← Optional!
│ GitHub Copilot CLI │ ✓ Available    │
│ Iteration Limit    │ 20.0s          │
╰────────────────────┴────────────────╯

Type 'help' for commands, 'exit' to quit

What would you like to create? (): █
```

### Step 5: Type a Command (Don't Just Press Enter!)

❌ **WRONG**: Pressing Enter without typing = exits immediately  
✅ **CORRECT**: Type a command first, then press Enter

#### Try These Commands:

```
What would you like to create? (): status
What would you like to create? (): Create a blue background
What would you like to create? (): Add text that says Hello World in white
What would you like to create? (): help
What would you like to create? (): exit
```

## 📋 Available Commands

### Special Commands
- `status` - Show system status
- `help` - Show all commands and examples
- `history` - Show execution history
- `clear` - Clear console
- `exit` or `quit` - Exit assistant

### Natural Language Commands

#### Fusion Tasks (Instant)
```
Create a blue background
Add text that says Welcome to DaVinci Resolve
Add a glow effect to the last node
Create a red gradient background
```

#### ComfyUI Tasks (10-15 seconds - requires ComfyUI running)
```
Generate a fantasy dragon scene
Create a cyberpunk cityscape
Generate a nebula background
Create a character portrait
```

#### Hybrid Tasks (Both systems)
```
Create a title card with AI-generated space background
Generate a dragon and add text overlay
```

## 🔧 Troubleshooting

### "It exits immediately after I run it"

**Problem**: You pressed Enter without typing a command  
**Solution**: Type something before pressing Enter

### "Can't connect to DaVinci Resolve"

**Problem**: Resolve is not running or no project is open  
**Solutions**:
1. Start DaVinci Resolve
2. Open or create a project
3. Try again

### "Want to see detailed diagnostics"

**Solution**: Use debug mode:
```powershell
python debug_launch.py
```

This shows:
- Python version and path
- All dependencies status
- DaVinci Resolve connection details
- Module import verification
- Step-by-step initialization

### "ComfyUI shows as Disconnected"

**Status**: This is normal! ComfyUI is optional.

**What works without ComfyUI**:
- ✅ All Fusion node creation
- ✅ Text, backgrounds, effects
- ✅ Natural language commands
- ✅ GitHub Copilot CLI integration

**What needs ComfyUI**:
- ❌ AI image generation tasks
- ❌ "Generate..." or "Create realistic..." commands

**To enable ComfyUI**:
1. Download from https://github.com/comfyanonymous/ComfyUI
2. Install Wan 2.2 model
3. Run: `python main.py`
4. Restart the assistant

## 🎯 Quick Reference

### Launch Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `simple_launch.py` | Quick start | Normal usage |
| `debug_launch.py` | Diagnostics | Troubleshooting |
| `launch_with_poetry.py` | Poetry env | Using Poetry virtual environment |

### Exit Methods

| Method | How |
|--------|-----|
| Type command | `exit` or `quit` |
| Keyboard | `Ctrl+C` (might need to press twice) |
| Empty input | Just press Enter (exits) |

## 🎬 Example Session

```powershell
PS C:\> cd c:\Users\satya\davinci-resolve-extension-builder\resolve-ai-assistant
PS C:\resolve-ai-assistant> python simple_launch.py

🚀 Starting DaVinci Resolve AI Assistant...
============================================================
📦 Loading modules...
✓ Modules loaded
🔌 Connecting to DaVinci Resolve...

╔══════════════════════════════════════════════════════════════╗
║        🎬 DaVinci Resolve AI Assistant                       ║
╚══════════════════════════════════════════════════════════════╝

System Status
╭────────────────────┬────────────────╮
│ DaVinci Resolve    │ ✓ Connected    │
│ Fusion Composition │ ✓ Available    │
│ GitHub Copilot CLI │ ✓ Available    │
╰────────────────────┴────────────────╯

What would you like to create? (): status
✓ All systems operational

What would you like to create? (): Create a blue background
[Progress bar...]
✓ Success - Created Background node (blue)

What would you like to create? (): Add text saying Hello World
[Progress bar...]
✓ Success - Created Text+ node with "Hello World"

What would you like to create? (): exit
Goodbye! 👋
```

## 📚 More Documentation

- **README.md** - Full project documentation
- **QUICK_REFERENCE.md** - Command reference
- **POWERSHELL_STATUS.md** - PowerShell compatibility details
- **ARCHITECTURE.md** - System architecture
- **examples/** - Python script examples

---

**Status**: ✅ Working in all terminals (PowerShell, VS Code, Command Prompt)  
**Key Point**: Type a command before pressing Enter - empty input exits the assistant!
