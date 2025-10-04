# AI-Assisted Iteration Workflow for DaVinci Resolve

## Core Philosophy: "Dog-like" Permission-Based Iteration

The AI assistant acts as a collaborative partner that:
1. **Proposes** actions based on your goals
2. **Waits** for your approval before executing
3. **Shows** you the visual result via DaVinci's video output
4. **Asks** for feedback and iterates

Think of it like a well-trained dog: it fetches what you ask for, brings it back to show you, and waits for your next command.

---

## Workflow Pattern

```
┌─────────────────────────────────────────────────────────────┐
│  USER: "Create a lower-third animation"                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  AI COPILOT: Breaking down the task...                     │
│  1. Create background node (blue, semi-transparent)         │
│  2. Add title text node ("Your Name")                      │
│  3. Position at lower-third                                │
│  4. Connect nodes in Merge composition                     │
│  5. Set render range to 20 seconds                         │
│                                                             │
│  ❓ Shall I proceed with step 1?                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  USER: "Yes, go ahead"                                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  AI: ✓ Created background node                             │
│  📺 Playing preview on video output...                      │
│  ⏱️  Render range: 0-480 frames (20 seconds @ 24fps)       │
│                                                             │
│  Current state: Blue background visible                    │
│  Next step: Add title text                                 │
│                                                             │
│  ❓ Continue with step 2?                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  USER: "Yes, but make it orange instead"                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  AI: ✓ Updated plan:                                       │
│  - Changed background color to orange                      │
│  - Updating node parameters...                             │
│  📺 Playing updated preview...                              │
│                                                             │
│  ❓ Looks good? Ready for step 2?                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Implementation

### 1. GitHub Copilot CLI Integration

Instead of OpenAI API, use **VS Code's built-in Copilot Chat API**:

```typescript
// VS Code Extension: resolve-copilot-assistant/src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // Register chat participant
    const participant = vscode.chat.createChatParticipant(
        'resolve.assistant',
        async (request, context, stream, token) => {
            // Parse user intent
            const intent = parseUserIntent(request.prompt);
            
            // Break down into steps
            const steps = breakDownTask(intent);
            
            // Show plan
            stream.markdown(`## Plan:\n`);
            steps.forEach((step, i) => {
                stream.markdown(`${i + 1}. ${step.description}\n`);
            });
            
            // Ask for permission
            stream.markdown(`\n❓ Shall I proceed with step 1?`);
            
            // Wait for user confirmation in next message
            return;
        }
    );
    
    context.subscriptions.push(participant);
}
```

### 2. Permission-Based Execution

```python
# src/resolve_ai/copilot_executor.py
class CopilotExecutor:
    """Executes DaVinci Resolve operations with permission checks"""
    
    def __init__(self):
        self.current_step = 0
        self.plan = []
        self.waiting_for_approval = False
    
    async def execute_with_permission(self, step):
        """Execute a step only after getting user approval"""
        
        # Show what we're about to do
        print(f"📋 Step {self.current_step + 1}: {step.description}")
        print(f"   Actions: {step.actions}")
        print(f"\n❓ Proceed? (yes/no/modify): ")
        
        # Wait for user input
        response = await self.get_user_response()
        
        if response.lower() == 'yes':
            # Execute the step
            result = self.execute_step(step)
            
            # Show preview
            self.show_preview()
            
            # Ask for next step
            self.current_step += 1
            if self.current_step < len(self.plan):
                print(f"\n✓ Step {self.current_step} complete")
                print(f"📺 Preview updated on video output")
                print(f"\n❓ Continue to step {self.current_step + 1}?")
            else:
                print("\n✅ All steps complete!")
            
        elif response.lower() == 'modify':
            # User wants to change something
            print("What would you like to modify?")
            modification = await self.get_user_response()
            step = self.modify_step(step, modification)
            await self.execute_with_permission(step)  # Retry with changes
        
        else:
            print("❌ Step cancelled. What would you like to do instead?")
```

### 3. Video Preview Integration

```python
# src/resolve_ai/preview_controller.py
class PreviewController:
    """Controls DaVinci Resolve video output preview"""
    
    def __init__(self, controller):
        self.controller = controller
        self.timeline = controller.get_current_timeline()
    
    def set_render_range(self, duration_seconds=20):
        """Set render range to 20 seconds from current position"""
        timeline = self.timeline
        current_frame = timeline.GetCurrentTimecode()
        frame_rate = float(timeline.GetSetting("timelineFrameRate"))
        
        # Calculate frame range (20 seconds)
        end_frame = int(duration_seconds * frame_rate)
        
        # Set in/out points
        timeline.SetSetting("useInOutRange", "1")
        timeline.SetSetting("inFrame", "0")
        timeline.SetSetting("outFrame", str(end_frame))
        
        print(f"⏱️  Render range set: 0-{end_frame} frames ({duration_seconds}s @ {frame_rate}fps)")
    
    def play_preview(self):
        """Play the current composition in DaVinci's video output"""
        timeline = self.timeline
        
        # Go to start of render range
        timeline.SetCurrentTimecode("00:00:00:00")
        
        # Play
        self.controller.project.Play()
        
        print("📺 Playing preview on video output...")
        print("   (Press ESC in DaVinci to stop)")
    
    def stop_preview(self):
        """Stop playback"""
        self.controller.project.Stop()
```

### 4. Context-Aware Merge Node Control

```python
# src/resolve_ai/merge_context.py
class MergeNodeContext:
    """Maintains context about the current Merge node composition"""
    
    def __init__(self, fusion_builder):
        self.builder = fusion_builder
        self.conversation_history = []
        self.current_merge_tree = {}
    
    def maintain_context(self):
        """Keep track of the current Merge node structure"""
        nodes = self.builder.get_node_list()
        
        # Analyze Merge node connections
        merge_nodes = [n for n in nodes if 'Merge' in n]
        
        context = {
            "total_nodes": len(nodes),
            "merge_nodes": merge_nodes,
            "last_modification": datetime.now(),
            "render_ready": self.check_render_ready()
        }
        
        self.conversation_history.append(context)
        return context
    
    def check_render_ready(self):
        """Check if composition is ready for preview"""
        # Must have at least one output node
        nodes = self.builder.get_node_list()
        has_output = any('MediaOut' in n or 'Saver' in n for n in nodes)
        
        return has_output
    
    def get_context_summary(self):
        """Provide context for the AI to understand current state"""
        context = self.maintain_context()
        
        return f"""
Current Fusion Composition State:
- Total nodes: {context['total_nodes']}
- Merge nodes: {len(context['merge_nodes'])}
- Ready for preview: {'✓' if context['render_ready'] else '✗'}
- Last modified: {context['last_modification'].strftime('%H:%M:%S')}
"""
```

---

## VS Code Copilot Chat Commands

### Command Pattern

```
@resolve create lower-third with blue background
@resolve show preview
@resolve modify color to orange
@resolve add glow effect
@resolve render 20 seconds
@resolve what's in the composition?
```

### Implementation

```typescript
// Commands for VS Code Copilot Chat
vscode.commands.registerCommand('resolve.createEffect', async (effect) => {
    const chatResponse = await vscode.commands.executeCommand(
        'workbench.action.chat.open',
        { message: `@resolve create ${effect}` }
    );
});

vscode.commands.registerCommand('resolve.showPreview', async () => {
    // Call Python backend
    const result = await executePythonCommand('preview.play()');
    vscode.window.showInformationMessage('📺 Preview playing in DaVinci Resolve');
});

vscode.commands.registerCommand('resolve.getContext', async () => {
    const context = await executePythonCommand('get_context_summary()');
    return context; // Returns to Copilot Chat
});
```

---

## 20-Second Render Limit Rationale

### Why 20 Seconds?

1. **Rapid Iteration**: Quick feedback loop for AI-assisted editing
2. **AI Video Generation**: Wan 2.2 and similar AI models work best with short clips
3. **Preview Speed**: Faster render times = faster iteration
4. **Focus**: Forces tight, focused edits instead of long sequences

### Enforcement

```python
# Automatically set on every operation
class RenderLimitEnforcer:
    MAX_DURATION_SECONDS = 20
    
    def enforce_limit(self, timeline):
        """Ensure render range never exceeds 20 seconds"""
        frame_rate = float(timeline.GetSetting("timelineFrameRate"))
        max_frames = int(self.MAX_DURATION_SECONDS * frame_rate)
        
        current_out = int(timeline.GetSetting("outFrame"))
        current_in = int(timeline.GetSetting("inFrame"))
        
        if (current_out - current_in) > max_frames:
            # Adjust to max duration
            timeline.SetSetting("outFrame", str(current_in + max_frames))
            print(f"⚠️  Render range limited to {self.MAX_DURATION_SECONDS} seconds")
```

---

## Conversation Pattern Examples

### Example 1: Creating Effect with Iterations

```
You: @resolve create a title sequence with my name

AI: I'll create a title sequence. Here's my plan:
    1. Black background
    2. Animated text with your name
    3. Glow effect
    4. Fade in/out
    
    Render range: 0-20 seconds
    
    ❓ Proceed with step 1 (background)?

You: yes

AI: ✓ Created black background
    📺 Preview updated
    
    ❓ Continue with step 2 (text)?

You: yes, but use orange text

AI: ✓ Plan updated: orange text
    ✓ Created text node with "Satyam"
    📺 Preview updated
    
    ❓ Continue with step 3 (glow)?

You: yes

AI: ✓ Added glow effect
    📺 Preview updated
    
    ❓ Continue with step 4 (animation)?

You: actually, let's make the glow bigger

AI: ✓ Increased glow size from 10 to 20
    📺 Preview updated
    
    ❓ Now add animation?

You: yes

AI: ✓ Added fade in/out animation
    📺 Final preview playing
    
    ✅ Title sequence complete!
```

### Example 2: Getting Context

```
You: @resolve what's in the composition?

AI: Current Fusion Composition:
    - 5 total nodes
    - Background (black)
    - Text+ ("Satyam", orange)
    - Glow (size: 20)
    - Merge x2
    - Ready for render: ✓
    
    Render range: 0-480 frames (20s @ 24fps)
    
    What would you like to modify?
```

---

## Integration with Copilot Chat Debug Pattern

Following the debug log pattern you referenced, the AI should:

### 1. Break Down Complex Tasks

```
User request: "Create a professional lower-third"

AI breakdown:
□ Step 1: Create background shape
□ Step 2: Add primary text
□ Step 3: Add secondary text  
□ Step 4: Position elements
□ Step 5: Add animation
□ Step 6: Preview with 20s render

❓ Start with Step 1?
```

### 2. Maintain Progress State

```
Progress: [■■■□□□] 3/6 steps complete

Completed:
✓ Background created
✓ Primary text added
✓ Secondary text added

Current:
→ Positioning elements

Remaining:
□ Add animation
□ Preview
```

### 3. Allow Modifications Mid-Stream

```
AI: ✓ Step 3 complete - secondary text added
    
    ❓ Continue to Step 4 (positioning)?

You: wait, change the text color to blue

AI: ✓ Modified Step 3 result
    ✓ Text color changed to blue
    📺 Updated preview
    
    ❓ Now continue to Step 4?
```

---

## Implementation Priority

### Phase 1: Core Loop ✅ (Current)
- [x] Permission-based execution
- [x] Step-by-step breakdown
- [x] Context maintenance

### Phase 2: VS Code Integration 🎯 (Next)
- [ ] Copilot Chat participant
- [ ] @resolve commands
- [ ] Context sharing with Copilot

### Phase 3: Preview Control 📺
- [ ] 20-second render enforcement
- [ ] Automatic preview playback
- [ ] Video output control

### Phase 4: Advanced Iteration 🔄
- [ ] Undo/redo for iterations
- [ ] Save iteration checkpoints
- [ ] Branch different approaches

---

## Configuration

```toml
# pyproject.toml additions
[tool.resolve-ai]
use_github_copilot = true
use_openai_api = false
max_render_seconds = 20
preview_auto_play = true
wait_for_approval = true
show_progress = true
```

```json
// .vscode/settings.json
{
  "resolve-ai.copilotIntegration": true,
  "resolve-ai.maxRenderDuration": 20,
  "resolve-ai.autoPreview": true,
  "resolve-ai.permissionRequired": true,
  "github.copilot.enable": {
    "*": true,
    "resolve": true
  }
}
```

---

## Summary: The "Dog" Behavior Model

Think of the AI as a well-trained assistant that:

1. **Listens** 👂 - Understands your creative intent
2. **Plans** 📋 - Breaks it into achievable steps  
3. **Asks** ❓ - Gets permission before acting
4. **Executes** ⚡ - Makes the changes in Fusion
5. **Shows** 📺 - Plays 20-second preview
6. **Waits** ⏸️ - Stops for your feedback
7. **Iterates** 🔄 - Refines based on your input

**Never** acts without permission.
**Always** shows you the result.
**Maintains** context throughout the conversation.

This creates a collaborative, **iterative creative workflow** where you stay in control while the AI handles the technical execution.
