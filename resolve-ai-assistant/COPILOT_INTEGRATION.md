# GitHub Copilot CLI Integration Guide

## Overview

This system uses **GitHub Copilot Chat** (built into VS Code) instead of OpenAI API for AI-powered DaVinci Resolve control. This means:

- ✅ **No API keys required** - Uses your GitHub Copilot subscription
- ✅ **Integrated with VS Code** - Seamless workflow
- ✅ **Context-aware** - Copilot understands your project
- ✅ **Permission-based** - Always asks before executing

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  VS Code with GitHub Copilot Chat                               │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  User: "@resolve create lower-third"                      │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
│                        │                                         │
│                        ▼                                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Copilot Chat Participant (@resolve)                      │  │
│  │  - Parses intent                                           │  │
│  │  - Breaks into steps                                       │  │
│  │  - Asks for permission                                     │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Python Backend (resolve-ai-assistant)                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  CopilotExecutor                                           │  │
│  │  - Executes approved actions                              │  │
│  │  - Maintains conversation context                         │  │
│  │  - Controls render range (20s limit)                      │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
└────────────────────────┼─────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  DaVinci Resolve 18.6                                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Fusion Composition                                        │  │
│  │  - Node graph manipulation                                │  │
│  │  - Video output preview                                   │  │
│  │  - 20-second render range                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## VS Code Extension Setup

### 1. Extension Structure

```
resolve-copilot-extension/
├── package.json
├── src/
│   ├── extension.ts          # Main extension entry
│   ├── chatParticipant.ts    # @resolve chat participant
│   ├── pythonBridge.ts       # Bridge to Python backend
│   └── commands.ts           # VS Code commands
├── tsconfig.json
└── README.md
```

### 2. Package.json Configuration

```json
{
  "name": "resolve-copilot-assistant",
  "displayName": "DaVinci Resolve AI Assistant",
  "description": "GitHub Copilot integration for DaVinci Resolve automation",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["AI", "Other"],
  "activationEvents": [
    "onStartupFinished"
  ],
  "contributes": {
    "commands": [
      {
        "command": "resolve.preview",
        "title": "Resolve: Play Preview"
      },
      {
        "command": "resolve.getContext",
        "title": "Resolve: Get Composition Context"
      },
      {
        "command": "resolve.setRenderRange",
        "title": "Resolve: Set 20s Render Range"
      }
    ],
    "configuration": {
      "title": "Resolve AI Assistant",
      "properties": {
        "resolve.pythonPath": {
          "type": "string",
          "default": "",
          "description": "Path to Python executable with resolve-ai installed"
        },
        "resolve.maxRenderSeconds": {
          "type": "number",
          "default": 20,
          "description": "Maximum render duration in seconds"
        },
        "resolve.autoPreview": {
          "type": "boolean",
          "default": true,
          "description": "Automatically play preview after changes"
        },
        "resolve.requirePermission": {
          "type": "boolean",
          "default": true,
          "description": "Ask for permission before executing actions"
        }
      }
    }
  },
  "dependencies": {
    "@types/vscode": "^1.85.0",
    "typescript": "^5.3.0"
  }
}
```

### 3. Chat Participant Implementation

```typescript
// src/chatParticipant.ts
import * as vscode from 'vscode';
import { PythonBridge } from './pythonBridge';

export class ResolveChatParticipant {
    private bridge: PythonBridge;
    private currentPlan: Step[] = [];
    private currentStep: number = 0;
    
    constructor(context: vscode.ExtensionContext) {
        this.bridge = new PythonBridge();
        this.registerParticipant(context);
    }
    
    private registerParticipant(context: vscode.ExtensionContext) {
        const participant = vscode.chat.createChatParticipant(
            'resolve.assistant',
            this.handleChat.bind(this)
        );
        
        participant.iconPath = vscode.Uri.file(
            context.asAbsolutePath('resources/resolve-icon.png')
        );
        
        context.subscriptions.push(participant);
    }
    
    private async handleChat(
        request: vscode.ChatRequest,
        context: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ): Promise<void> {
        const prompt = request.prompt;
        
        // Check if this is a continuation or new request
        if (this.isApproval(prompt)) {
            await this.executeCurrentStep(stream);
        } else if (this.isModification(prompt)) {
            await this.modifyCurrentStep(prompt, stream);
        } else {
            await this.createNewPlan(prompt, stream);
        }
    }
    
    private async createNewPlan(
        prompt: string,
        stream: vscode.ChatResponseStream
    ): Promise<void> {
        // Parse user intent
        const intent = await this.bridge.parseIntent(prompt);
        
        // Break into steps
        this.currentPlan = await this.bridge.breakDownTask(intent);
        this.currentStep = 0;
        
        // Show plan
        stream.markdown(`## Plan:\n\n`);
        this.currentPlan.forEach((step, i) => {
            const status = i === 0 ? '→' : '□';
            stream.markdown(`${status} **Step ${i + 1}**: ${step.description}\n`);
        });
        
        stream.markdown(`\n\n❓ Shall I proceed with Step 1?\n`);
        stream.markdown(`*Reply with "yes", "no", or suggest modifications*\n`);
    }
    
    private async executeCurrentStep(
        stream: vscode.ChatResponseStream
    ): Promise<void> {
        if (this.currentStep >= this.currentPlan.length) {
            stream.markdown('✅ All steps complete!\n');
            return;
        }
        
        const step = this.currentPlan[this.currentStep];
        
        stream.progress(`Executing: ${step.description}...`);
        
        try {
            // Execute via Python backend
            const result = await this.bridge.executeStep(step);
            
            stream.markdown(`✓ ${step.description}\n`);
            stream.markdown(`📺 Preview updated\n\n`);
            
            // Play preview if auto-preview enabled
            const config = vscode.workspace.getConfiguration('resolve');
            if (config.get('autoPreview')) {
                await this.bridge.playPreview();
            }
            
            // Move to next step
            this.currentStep++;
            
            if (this.currentStep < this.currentPlan.length) {
                const nextStep = this.currentPlan[this.currentStep];
                stream.markdown(`\n❓ Continue with Step ${this.currentStep + 1}: ${nextStep.description}?\n`);
            } else {
                stream.markdown('\n✅ All steps complete! Would you like to make any changes?\n');
            }
            
        } catch (error) {
            stream.markdown(`❌ Error: ${error.message}\n`);
            stream.markdown(`\nWhat would you like to do?\n`);
        }
    }
    
    private async modifyCurrentStep(
        modification: string,
        stream: vscode.ChatResponseStream
    ): Promise<void> {
        // Parse modification
        const modifiedStep = await this.bridge.modifyStep(
            this.currentPlan[this.currentStep],
            modification
        );
        
        this.currentPlan[this.currentStep] = modifiedStep;
        
        stream.markdown(`✓ Plan updated:\n`);
        stream.markdown(`- ${modifiedStep.description}\n\n`);
        stream.markdown(`❓ Proceed with modified step?\n`);
    }
    
    private isApproval(prompt: string): boolean {
        const approvalWords = ['yes', 'go', 'proceed', 'continue', 'ok', 'yeah'];
        return approvalWords.some(word => 
            prompt.toLowerCase().includes(word)
        );
    }
    
    private isModification(prompt: string): boolean {
        const modWords = ['change', 'modify', 'update', 'instead', 'but'];
        return modWords.some(word => 
            prompt.toLowerCase().includes(word)
        );
    }
}

interface Step {
    description: string;
    actions: Action[];
    parameters: Record<string, any>;
}

interface Action {
    type: string;
    target: string;
    params: Record<string, any>;
}
```

### 4. Python Bridge

```typescript
// src/pythonBridge.ts
import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';

export class PythonBridge {
    private pythonPath: string;
    
    constructor() {
        const config = vscode.workspace.getConfiguration('resolve');
        this.pythonPath = config.get('pythonPath') || 'python';
    }
    
    async executeStep(step: any): Promise<any> {
        const command = {
            action: 'execute_step',
            step: step
        };
        
        return this.callPython(command);
    }
    
    async playPreview(): Promise<void> {
        const command = {
            action: 'play_preview'
        };
        
        await this.callPython(command);
    }
    
    async getContext(): Promise<string> {
        const command = {
            action: 'get_context'
        };
        
        return this.callPython(command);
    }
    
    async parseIntent(prompt: string): Promise<any> {
        const command = {
            action: 'parse_intent',
            prompt: prompt
        };
        
        return this.callPython(command);
    }
    
    async breakDownTask(intent: any): Promise<any[]> {
        const command = {
            action: 'break_down_task',
            intent: intent
        };
        
        return this.callPython(command);
    }
    
    async modifyStep(step: any, modification: string): Promise<any> {
        const command = {
            action: 'modify_step',
            step: step,
            modification: modification
        };
        
        return this.callPython(command);
    }
    
    private async callPython(command: any): Promise<any> {
        return new Promise((resolve, reject) => {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            const scriptPath = path.join(
                workspaceFolder.uri.fsPath,
                'resolve-ai-assistant',
                'src',
                'resolve_ai',
                'vscode_bridge.py'
            );
            
            const proc = child_process.spawn(this.pythonPath, [
                scriptPath,
                JSON.stringify(command)
            ]);
            
            let stdout = '';
            let stderr = '';
            
            proc.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            proc.stderr.on('data', (data) => {
                stderr += data.toString();
            });
            
            proc.on('close', (code) => {
                if (code !== 0) {
                    reject(new Error(stderr));
                } else {
                    try {
                        const result = JSON.parse(stdout);
                        resolve(result);
                    } catch (e) {
                        reject(new Error(`Failed to parse response: ${stdout}`));
                    }
                }
            });
        });
    }
}
```

---

## Python Backend Updates

### VS Code Bridge Script

```python
# src/resolve_ai/vscode_bridge.py
"""
Bridge between VS Code extension and Python backend
Handles commands from VS Code Copilot Chat
"""

import sys
import json
from typing import Dict, List, Any
from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder
from resolve_ai.preview_controller import PreviewController
from resolve_ai.copilot_executor import CopilotExecutor

class VSCodeBridge:
    """Handles commands from VS Code extension"""
    
    def __init__(self):
        self.controller = ResolveAIController()
        self.fusion_builder = None
        self.preview = PreviewController(self.controller)
        self.executor = CopilotExecutor(self.controller, self.preview)
    
    def handle_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Route command to appropriate handler"""
        action = command.get('action')
        
        handlers = {
            'execute_step': self.execute_step,
            'play_preview': self.play_preview,
            'get_context': self.get_context,
            'parse_intent': self.parse_intent,
            'break_down_task': self.break_down_task,
            'modify_step': self.modify_step
        }
        
        handler = handlers.get(action)
        if not handler:
            return {'error': f'Unknown action: {action}'}
        
        try:
            result = handler(command)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_step(self, command: Dict) -> Dict:
        """Execute a single step"""
        step = command['step']
        result = self.executor.execute_step(step)
        return result
    
    def play_preview(self, command: Dict) -> Dict:
        """Play 20-second preview"""
        self.preview.set_render_range(20)
        self.preview.play_preview()
        return {'status': 'playing'}
    
    def get_context(self, command: Dict) -> str:
        """Get current composition context"""
        return self.executor.get_context_summary()
    
    def parse_intent(self, command: Dict) -> Dict:
        """Parse user intent from natural language"""
        prompt = command['prompt']
        # Simple intent parsing (can be enhanced with local LLM)
        intent = self._simple_intent_parser(prompt)
        return intent
    
    def break_down_task(self, command: Dict) -> List[Dict]:
        """Break task into executable steps"""
        intent = command['intent']
        steps = self.executor.create_execution_plan(intent)
        return steps
    
    def modify_step(self, command: Dict) -> Dict:
        """Modify a step based on user feedback"""
        step = command['step']
        modification = command['modification']
        modified = self.executor.modify_step(step, modification)
        return modified
    
    def _simple_intent_parser(self, prompt: str) -> Dict:
        """Simple rule-based intent parser"""
        prompt_lower = prompt.lower()
        
        intent = {
            'type': 'unknown',
            'parameters': {}
        }
        
        # Detect common patterns
        if 'lower-third' in prompt_lower or 'lower third' in prompt_lower:
            intent['type'] = 'create_lower_third'
            # Extract title/subtitle if present
            if '"' in prompt:
                texts = [t.strip() for t in prompt.split('"') if t.strip()]
                if len(texts) >= 1:
                    intent['parameters']['title'] = texts[0]
                if len(texts) >= 2:
                    intent['parameters']['subtitle'] = texts[1]
        
        elif 'text' in prompt_lower:
            intent['type'] = 'create_text'
            if '"' in prompt:
                intent['parameters']['text'] = prompt.split('"')[1]
        
        elif 'background' in prompt_lower:
            intent['type'] = 'create_background'
            # Extract color if present
            colors = ['red', 'blue', 'green', 'black', 'white', 'orange']
            for color in colors:
                if color in prompt_lower:
                    intent['parameters']['color'] = color
                    break
        
        elif 'preview' in prompt_lower or 'play' in prompt_lower:
            intent['type'] = 'play_preview'
        
        elif 'context' in prompt_lower or 'what' in prompt_lower:
            intent['type'] = 'get_context'
        
        return intent

def main():
    """Main entry point for VS Code bridge"""
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No command provided'}))
        sys.exit(1)
    
    try:
        command = json.loads(sys.argv[1])
        bridge = VSCodeBridge()
        result = bridge.handle_command(command)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## Usage Examples

### In VS Code Copilot Chat

```
You: @resolve create a lower-third with title "John Doe"

Copilot: ## Plan:

→ **Step 1**: Create blue background rectangle
□ **Step 2**: Add title text "John Doe"
□ **Step 3**: Position at lower-third (bottom 25%)
□ **Step 4**: Add subtle animation
□ **Step 5**: Set 20-second render range

❓ Shall I proceed with Step 1?

---

You: yes

Copilot: ✓ Create blue background rectangle
📺 Preview updated

❓ Continue with Step 2: Add title text "John Doe"?

---

You: yes but make it orange

Copilot: ✓ Plan updated:
- Changed background color to orange

❓ Proceed with modified step?

---

You: yes

Copilot: ✓ Create orange background rectangle
📺 Preview updated

❓ Continue with Step 2: Add title text "John Doe"?
```

---

## Configuration

### .vscode/settings.json

```json
{
  "resolve.pythonPath": "C:\\Users\\satya\\davinci-resolve-extension-builder\\resolve-ai-assistant\\.venv\\Scripts\\python.exe",
  "resolve.maxRenderSeconds": 20,
  "resolve.autoPreview": true,
  "resolve.requirePermission": true,
  "github.copilot.enable": {
    "*": true,
    "resolve": true
  }
}
```

---

## Benefits Over OpenAI API

1. **No API costs** - Uses existing GitHub Copilot subscription
2. **Better VS Code integration** - Native chat interface
3. **Context awareness** - Copilot knows your project structure
4. **Offline-capable** - Can work with local models
5. **Permission-based** - Natural conversation flow with approvals

---

## Next Steps

1. Create VS Code extension skeleton
2. Implement chat participant
3. Build Python bridge
4. Test iteration workflow
5. Add command palette commands
6. Package and distribute

This approach gives you **full control** while leveraging **GitHub Copilot's AI** without needing separate API keys!
