# 🎬 DaVinci Resolve AI Assistant - Cheat Sheet

## 🚀 Launch Commands

| Method | Command |
|--------|---------|
| **PowerShell** | `cd resolve-ai-assistant; python simple_launch.py` |
| **Debug Mode** | `python debug_launch.py` |
| **Batch File** | Double-click `launch.bat` |
| **Resolve Console** | `exec(open(r"path\to\simple_launch.py").read())` |

## 💡 Pro Tips

### ⚠️ Most Important Rules

1. **TYPE before pressing Enter** - Empty input exits the assistant!
2. **Make sure Resolve is running** - Open a project first
3. **ComfyUI is optional** - Everything works without it

## 🎯 Quick Commands

### System Commands
```
status    - Show system status
help      - Show all commands
history   - Show execution history
clear     - Clear console
exit      - Exit assistant
```

### Instant Fusion Commands (< 1 second)
```
Create a blue background
Create a red gradient background
Add text that says Hello World
Add text that says Title in white size 72
Add a glow effect to the last node
Add blur to the current node
Create a black background
```

### AI Generation Commands (10-15 seconds, needs ComfyUI)
```
Generate a fantasy dragon scene
Create a cyberpunk cityscape
Generate a nebula background
Create a character portrait
Generate a sunset landscape
Create a fantasy forest
```

### Hybrid Commands (Combined)
```
Create a title card with AI-generated space background
Generate a dragon and add text overlay saying Dragon Master
Create AI fantasy scene with white text title
```

## 📊 System Status Indicators

| Symbol | Meaning |
|--------|---------|
| ✓ Connected | System is working |
| ✗ Disconnected | System not available (may be optional) |
| ⚠️ Warning | Non-critical issue |
| ❌ Error | Critical issue |

## 🔧 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| "Exits immediately" | Type a command before pressing Enter |
| "Can't connect to Resolve" | Start DaVinci Resolve and open a project |
| "ComfyUI Disconnected" | Normal! It's optional. AI generation disabled. |
| "Module not found" | Run `pip install rich requests websocket-client pillow` |
| "Want detailed info" | Use `python debug_launch.py` |
| "Copilot not available" | Install: `gh extension install github/gh-copilot` |

## 📁 File Reference

| File | Purpose |
|------|---------|
| `simple_launch.py` | Quick launcher |
| `debug_launch.py` | Diagnostic launcher |
| `launch.bat` | Windows batch launcher |
| `QUICK_START.md` | Detailed guide |
| `README.md` | Full documentation |
| `QUICK_REFERENCE.md` | Command reference |

## 🎨 Fusion Node Types Available

| Category | Nodes |
|----------|-------|
| **Basics** | Background, Text+, Transform, Merge |
| **Effects** | Glow, Blur, Brightness, Contrast |
| **Color** | ColorCorrector, ColorCurves |
| **I/O** | Loader (import), Saver (export) |
| **Shapes** | Rectangle, Ellipse, Polygon |
| **Advanced** | Mask, Filter, Custom effects |

## 🖼️ ComfyUI Generation Types (when enabled)

| Type | Examples |
|------|----------|
| **Backgrounds** | Nebula, sunset, cityscape, forest |
| **Characters** | Fantasy, cyberpunk, realistic portraits |
| **Scenes** | Dragons, spaceships, landscapes |
| **Styles** | Photorealistic, artistic, stylized |
| **Speed** | ~10-15 seconds per generation |

## ⚡ Performance Tips

| Tip | Benefit |
|-----|---------|
| Use Fusion for simple tasks | Instant results |
| Use ComfyUI for complex art | High quality AI |
| Combine both for best results | Fusion speed + AI quality |
| Keep iterations under 20s | Fast workflow |

## 📝 Example Session

```powershell
# Start assistant
PS> python simple_launch.py

# Check status
What would you like to create? (): status
✓ All systems operational

# Create simple background
What would you like to create? (): Create a blue background
✓ Success - Created Background node

# Add text
What would you like to create? (): Add text saying Welcome
✓ Success - Created Text+ node

# Exit
What would you like to create? (): exit
Goodbye! 👋
```

## 🎯 Common Workflows

### 1. Simple Title Card (2 seconds)
```
1. Create a black background
2. Add text that says Movie Title in white size 96
3. Add glow effect to the text
```

### 2. AI Background + Text (15 seconds)
```
1. Generate a fantasy space scene
2. Add text that says Starship in white size 72
```

### 3. Lower Third (3 seconds)
```
1. Create a gradient background from blue to transparent
2. Add text that says John Doe
3. Position text at bottom left
```

## 🎓 Learning Path

### Beginner
1. Start with `status` command
2. Try simple backgrounds
3. Add basic text
4. Use `help` to explore

### Intermediate
1. Combine multiple nodes
2. Add effects (glow, blur)
3. Try transformations
4. Create compositions

### Advanced
1. Use AI generation (ComfyUI)
2. Hybrid workflows
3. Complex compositions
4. Custom node graphs

## 📞 Support Resources

| Resource | Location |
|----------|----------|
| Quick Start | `QUICK_START.md` |
| Full Docs | `README.md` |
| Architecture | `ARCHITECTURE.md` |
| Examples | `examples/` folder |
| Troubleshooting | `RESOLUTION_SUMMARY.md` |

## 🎬 Remember

1. **Type before Enter** - Don't press Enter on empty prompt
2. **Resolve must be running** - Open a project first
3. **ComfyUI is optional** - Everything works without it
4. **Use status often** - Check system health
5. **Read QUICK_START.md** - Your friend for first time

---

**Quick Test Command**: `python simple_launch.py` → type `status` → type `exit`

**Most Common Mistake**: Pressing Enter without typing → Exits assistant

**Most Helpful Command**: `help` - Shows all available commands and examples
