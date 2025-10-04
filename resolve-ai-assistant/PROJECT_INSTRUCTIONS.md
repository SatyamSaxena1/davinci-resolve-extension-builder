# Project Instructions: AI-Assisted DaVinci Resolve Editing

## Core Philosophy

This system is designed to work like a **well-trained assistant** that:
- **Never acts without permission**
- **Always shows you the result before moving forward**
- **Maintains context throughout the conversation**
- **Breaks down complex tasks into simple, approvable steps**

Think of it as a dog bringing you a stick: it fetches what you ask for, brings it back to show you, and waits for your next command.

---

## Key Requirements

### 1. No OpenAI API - Use GitHub Copilot Instead
- Leverage VS Code's built-in GitHub Copilot Chat
- Create `@resolve` chat participant
- No separate API keys needed
- Uses your existing GitHub Copilot subscription

### 2. Permission-Based Execution ("Dog Behavior")
- AI proposes action
- Waits for approval
- Executes only after "yes"
- Shows result
- Waits for next command

### 3. Video Preview Feedback Loop
- After each action, automatically play preview on DaVinci's video output
- Let user see the result in real-time
- Get feedback before next step

### 4. 20-Second Render Limit
- Enforce maximum 20-second render range
- Reason: Rapid iteration for AI video generation (Wan 2.2)
- Fast feedback loop
- Force focused edits

### 5. Merge Node Context Maintenance
- Keep track of current Fusion composition structure
- Understand what's connected to what
- Provide context to AI for intelligent suggestions
- Enable iterative refinement

---

## Workflow Pattern

```
User Request
    ↓
AI Breaks Down into Steps
    ↓
AI Shows Plan
    ↓
AI Asks: "Proceed with Step 1?"
    ↓
User: "yes"
    ↓
AI Executes Step 1
    ↓
AI Sets 20s Render Range
    ↓
AI Plays Preview on Video Output
    ↓
AI Asks: "Continue to Step 2?"
    ↓
User: "yes, but make it blue"
    ↓
AI Updates Plan
    ↓
AI Asks: "Proceed with modified step?"
    ↓
[LOOP]
```

---

## Technical Architecture

### Three-Tier System

```
┌──────────────────────────────────────┐
│  VS Code + GitHub Copilot Chat       │ ← User interacts here
│  (@resolve chat participant)         │
└───────────────┬──────────────────────┘
                │
                ↓ (JSON commands)
┌──────────────────────────────────────┐
│  Python Backend                       │ ← Permission logic
│  (CopilotExecutor + PreviewControl)   │    Step execution
└───────────────┬──────────────────────┘
                │
                ↓ (DaVinci API calls)
┌──────────────────────────────────────┐
│  DaVinci Resolve 18.6                 │ ← Actual execution
│  (Fusion Nodes + Video Output)        │    Preview display
└──────────────────────────────────────┘
```

### Components

1. **VS Code Extension** (`resolve-copilot-extension/`)
   - Chat participant for `@resolve` commands
   - Parses natural language
   - Sends commands to Python backend
   - Displays results in chat

2. **Python Backend** (`resolve-ai-assistant/`)
   - `CopilotExecutor`: Permission-based execution
   - `PreviewController`: Video output control
   - `FusionNodeBuilder`: Node graph manipulation
   - `MergeNodeContext`: Context maintenance

3. **DaVinci Resolve Integration**
   - Python API for scripting
   - Fusion API for node control
   - Video output for preview

---

## Iteration Pattern (Like Copilot Chat Debug Log)

### Step 1: Break Down Task

```
User: "Create a professional title sequence"

AI Analysis:
This requires:
1. Background creation
2. Text node setup
3. Animation
4. Positioning
5. Preview

Breaking into steps...

□ Step 1: Create black background
□ Step 2: Add main title text
□ Step 3: Add subtitle text
□ Step 4: Position elements
□ Step 5: Add fade in/out
□ Step 6: Set 20s render + preview

❓ Shall I proceed with Step 1?
```

### Step 2: Execute with Permission

```
User: "yes"

AI: Executing Step 1...
✓ Created black background node
✓ Render range set: 0-480 frames (20s @ 24fps)
📺 Playing preview on video output...

[User sees black screen for 20 seconds]

Current state: Black background active

❓ Continue to Step 2 (add main title)?
```

### Step 3: Handle Modifications

```
User: "actually make it blue"

AI: Modifying Step 1...
✓ Updated background color to blue
📺 Playing updated preview...

[User sees blue screen for 20 seconds]

✓ Step 1 complete with modifications

❓ Now continue to Step 2?
```

### Step 4: Continue Iteration

```
User: "yes"

AI: Executing Step 2...
✓ Created Text+ node
✓ Text: "Your Title Here"
✓ Color: White
✓ Size: 0.1
✓ Position: Center
✓ Connected Background → Text
📺 Playing preview...

[User sees white text on blue background]

Current composition:
- Background (blue)
- Text+ ("Your Title Here")
- Merge (connecting both)

❓ Continue to Step 3 (subtitle)?
```

---

## Example Commands

### In VS Code Copilot Chat:

```
@resolve create a lower-third
@resolve add glow effect to the text
@resolve change background color to orange
@resolve show me what's in the composition
@resolve play preview
@resolve set render range to 10 seconds
@resolve clear composition and start over
```

### Expected Responses:

```
You: @resolve create a lower-third

AI: I'll create a lower-third graphic. Here's my plan:

1. Create background rectangle (blue, semi-transparent)
2. Add title text (position: lower-third)
3. Add subtitle text (smaller, below title)
4. Animate entrance (slide in from left)
5. Set 20-second render range
6. Preview

❓ Shall I proceed with Step 1?

---

You: yes

AI: ✓ Background rectangle created
    Color: Blue (0.2, 0.4, 0.8, 0.7)
    Size: 1920x200
    Position: Bottom of frame
    
    📺 Preview updated (20s render)
    
    ❓ Continue to Step 2 (title text)?

---

You: make it orange instead

AI: ✓ Background color updated
    New color: Orange (1.0, 0.6, 0.0, 0.7)
    
    📺 Preview updated
    
    ❓ Ready for Step 2?

---

You: yes

AI: ✓ Title text added
    Text: "Title Here"
    Font: Arial
    Size: 0.08
    Color: White
    Position: X=0.5, Y=0.85
    
    📺 Preview updated
    
    Current composition:
    - Background (orange rectangle)
    - Text+ (white title)
    - Merge (connected)
    
    ❓ Continue to Step 3 (subtitle)?
```

---

## 20-Second Render Range Enforcement

### Why 20 Seconds?

1. **Fast Iteration**: Quick preview cycles
2. **AI Video Generation**: Compatible with Wan 2.2 constraints
3. **Focus**: Forces tight, focused edits
4. **Resource Efficient**: Faster renders = more iterations

### Implementation

```python
class PreviewController:
    MAX_DURATION = 20  # seconds
    
    def set_render_range(self, duration=20):
        """Always enforce 20-second limit"""
        if duration > self.MAX_DURATION:
            duration = self.MAX_DURATION
            print(f"⚠️  Limited to {self.MAX_DURATION}s")
        
        # Set in/out points
        timeline = self.timeline
        fps = float(timeline.GetSetting("timelineFrameRate"))
        end_frame = int(duration * fps)
        
        timeline.SetSetting("inFrame", "0")
        timeline.SetSetting("outFrame", str(end_frame))
        
        print(f"⏱️  Render: 0-{end_frame} frames ({duration}s @ {fps}fps)")
```

---

## Merge Node Context Management

### Purpose
- Track current Fusion composition structure
- Understand node connections
- Provide AI with context for decisions
- Enable intelligent suggestions

### Implementation

```python
class MergeNodeContext:
    def __init__(self, fusion_builder):
        self.builder = fusion_builder
        self.history = []
    
    def get_context_summary(self):
        """Provide context for AI"""
        nodes = self.builder.get_node_list()
        merges = [n for n in nodes if 'Merge' in n]
        
        return f"""
Current Fusion Composition:
- Total nodes: {len(nodes)}
- Merge nodes: {len(merges)}
- Last modified: {datetime.now()}
- Ready for render: {self._check_ready()}

Node tree:
{self._build_tree_diagram()}
"""
    
    def maintain_conversation_context(self):
        """Keep history of changes for AI"""
        self.history.append({
            'timestamp': datetime.now(),
            'nodes': self.builder.get_node_list(),
            'connections': self._get_connections()
        })
```

---

## Configuration

### Project Settings

```toml
# pyproject.toml
[tool.resolve-ai]
use_github_copilot = true
use_openai_api = false
max_render_seconds = 20
preview_auto_play = true
wait_for_approval = true
show_progress = true
permission_required = true
```

### VS Code Settings

```json
{
  "resolve.pythonPath": ".venv/Scripts/python.exe",
  "resolve.maxRenderSeconds": 20,
  "resolve.autoPreview": true,
  "resolve.requirePermission": true,
  "resolve.showProgress": true
}
```

---

## Development Roadmap

### Phase 1: Core Permission Loop ✅
- [x] Python backend with DaVinci API integration
- [x] Permission-based executor
- [x] Context maintenance
- [x] 20-second render enforcement

### Phase 2: VS Code Extension 🎯 (NEXT)
- [ ] Create extension skeleton
- [ ] Implement @resolve chat participant
- [ ] Build Python bridge
- [ ] Test iteration workflow

### Phase 3: Preview Control 📺
- [ ] Automatic preview playback
- [ ] Video output control
- [ ] Render range UI feedback

### Phase 4: Advanced Features 🚀
- [ ] Undo/redo for iterations
- [ ] Save iteration checkpoints
- [ ] Branch different approaches
- [ ] Template library

---

## Remember: The "Dog" Principle

Every interaction follows this pattern:

1. **Fetch**: AI understands what you want
2. **Bring Back**: AI shows you a plan
3. **Wait**: AI asks for permission
4. **Execute**: AI makes the change
5. **Show**: AI displays the result (20s preview)
6. **Wait**: AI asks for next command

**Never** execute without approval.
**Always** show the result.
**Maintain** context throughout.

This is **your creative vision**, and the AI is **your assistant** - not the other way around.

---

## Quick Reference

### Commands

| Command | Action |
|---------|--------|
| `@resolve create [effect]` | Create new Fusion composition |
| `@resolve modify [parameter]` | Change existing parameters |
| `@resolve preview` | Play 20s preview |
| `@resolve context` | Show current composition state |
| `@resolve clear` | Clear all nodes |
| `@resolve undo` | Undo last action |

### Responses

| User Says | AI Action |
|-----------|-----------|
| "yes" | Execute current step |
| "no" | Cancel and ask for alternative |
| "make it [color]" | Modify current step |
| "show me" | Display context/preview |
| "start over" | Clear and begin fresh |

---

## Success Criteria

The system is working correctly when:

- ✅ AI **never** acts without permission
- ✅ User **always** sees preview after changes
- ✅ Render range **never** exceeds 20 seconds
- ✅ AI **maintains** context between messages
- ✅ User feels **in control** of the creative process

---

This document serves as the **master specification** for how the AI assistant should behave. All implementation decisions should align with these principles.
