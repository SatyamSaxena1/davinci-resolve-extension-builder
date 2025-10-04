# DaVinci Resolve AI Assistant - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                                                                 │
│  Natural Language Input: "Create a lower-third for John Doe"   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONVERSATIONAL CLI (cli.py)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ResolveAIAssistant                                     │   │
│  │  - Manages conversation history                         │   │
│  │  - Interfaces with OpenAI GPT-4                        │   │
│  │  - Renders beautiful terminal output                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   OpenAI GPT-4 Function Calling                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Available Tools (14 functions):                        │   │
│  │  • create_fusion_node                                   │   │
│  │  • connect_fusion_nodes                                │   │
│  │  • set_node_parameters                                 │   │
│  │  • create_text_node                                    │   │
│  │  • create_background_node                              │   │
│  │  • create_lower_third                                  │   │
│  │  • list_fusion_nodes                                   │   │
│  │  • delete_fusion_node                                  │   │
│  │  • add_timeline_marker                                 │   │
│  │  • create_timeline                                     │   │
│  │  • import_media_files                                  │   │
│  │  • ... and more                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              FUNCTION EXECUTOR (ai_tools.py)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FunctionExecutor                                       │   │
│  │  - Parses function calls from GPT-4                    │   │
│  │  - Routes to appropriate controller methods            │   │
│  │  - Returns structured results                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────┬────────────────────────┬────────────────────────┘
                │                        │
       ┌────────▼────────┐      ┌───────▼──────────┐
       │                 │      │                  │
┌──────┴─────────────────┴──────┴──────────────────┴──────────────┐
│           CORE CONTROLLERS                                      │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │  ResolveAIController     │  │  FusionNodeBuilder       │    │
│  │  (controller.py)         │  │  (fusion_tools.py)       │    │
│  │                          │  │                          │    │
│  │  • Project management    │  │  • Node creation         │    │
│  │  • Timeline operations   │  │  • Node connection       │    │
│  │  • Marker management     │  │  • Parameter setting     │    │
│  │  • Media pool access     │  │  • Template generation   │    │
│  │  • Fusion comp access    │  │  • Node inspection       │    │
│  └──────────────────────────┘  └──────────────────────────┘    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│             DaVinci Resolve Python API                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  DaVinciResolveScript                                   │   │
│  │  - Resolve object                                       │   │
│  │  - Project Manager                                      │   │
│  │  - Timeline API                                         │   │
│  │  - Fusion composition API                               │   │
│  │  - Media Pool API                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DaVinci Resolve Application                    │
│                                                                 │
│  • Fusion Page (node graph manipulation)                       │
│  • Edit Page (timeline operations)                             │
│  • Media Pool (asset management)                               │
│  • Project (global settings)                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Example: "Create a lower-third"

```
1. User Input
   ↓
   "Create a lower-third with title 'John Doe' and subtitle 'CEO'"

2. CLI → OpenAI
   ↓
   {
     "role": "user",
     "content": "Create a lower-third with title 'John Doe' and subtitle 'CEO'"
   }

3. GPT-4 Function Selection
   ↓
   {
     "function_name": "create_lower_third",
     "arguments": {
       "title_text": "John Doe",
       "subtitle_text": "CEO",
       "bg_color": [0.0, 0.3, 0.6, 0.9],
       "text_color": [1.0, 1.0, 1.0]
     }
   }

4. FunctionExecutor Routing
   ↓
   executor.execute("create_lower_third", {...})

5. FusionNodeBuilder Execution
   ↓
   builder.build_lower_third(...)
   
   Steps:
   a. create_background_node()      → Background node
   b. create_transform_node()       → Position transform
   c. connect_nodes(bg, transform)  → Connect
   d. create_text_node("John Doe")  → Title text
   e. create_text_node("CEO")       → Subtitle text
   f. create_merge_node() × 3       → Composite layers
   g. connect_nodes(...) × 4        → Build graph

6. Resolve API Calls
   ↓
   comp.AddTool("Background")
   tool.SetInput("TopLeftRed", 0.0)
   tool.ConnectInput("Input", source_tool)
   ... (20+ API calls total)

7. Result
   ↓
   {
     "success": true,
     "data": "Created lower-third with 7 nodes"
   }

8. GPT-4 Response Generation
   ↓
   "I've created a professional lower-third for John Doe (CEO) with:
   - Blue background positioned at the lower third
   - Large title text 'John Doe'
   - Smaller subtitle 'CEO'
   - All layers properly composited
   
   The composition is ready in your Fusion page!"

9. CLI Output
   ↓
   [Rich formatted response with colors and formatting]
```

## Module Responsibilities

### cli.py (195 lines)
**Responsibility**: User interaction and conversation management
- Maintains conversation history
- Interfaces with OpenAI API
- Renders terminal output with Rich
- Handles errors gracefully
- Provides example commands

### ai_tools.py (455 lines)
**Responsibility**: AI-to-API translation layer
- Defines 14 function tools for OpenAI
- Parses function calls from GPT-4
- Routes to appropriate controller methods
- Returns structured results
- Error handling and validation

### controller.py (275 lines)
**Responsibility**: DaVinci Resolve project/timeline operations
- Connection to Resolve instance
- Project information retrieval
- Timeline creation and management
- Marker operations
- Media pool access
- Fusion composition access

### fusion_tools.py (485 lines)
**Responsibility**: Fusion node graph manipulation
- Node creation (15+ node types)
- Node connection logic
- Parameter setting
- Template generation (lower-thirds, etc.)
- Node inspection and deletion
- Composition management

## Extension Points

### Adding New Tools

1. **Define tool in ai_tools.py:**
```python
{
    "type": "function",
    "function": {
        "name": "create_custom_effect",
        "description": "Creates a custom visual effect",
        "parameters": {...}
    }
}
```

2. **Implement in FunctionExecutor:**
```python
elif function_name == "create_custom_effect":
    result = self.fusion_builder.create_custom_effect(
        arguments["effect_type"]
    )
    return {"success": True, "data": result}
```

3. **Add method to FusionNodeBuilder:**
```python
def create_custom_effect(self, effect_type: str):
    # Implementation
    pass
```

### Adding New Node Types

```python
# In fusion_tools.py
def create_my_custom_node(
    self,
    name: Optional[str] = None,
    param1: float = 1.0,
    x_pos: int = 0,
    y_pos: int = 0
) -> Optional[object]:
    """Create a custom node type"""
    node = self.create_node("CustomNodeType", name=name, x_pos=x_pos, y_pos=y_pos)
    
    if node:
        self.set_node_params(node, {
            "Parameter1": param1,
            # ... more parameters
        })
    
    return node
```

## Performance Considerations

### Optimization Strategies

1. **Batch Operations**: Group multiple node creations
2. **Connection Caching**: Store node references
3. **Lazy Evaluation**: Only get Fusion comp when needed
4. **Error Recovery**: Graceful degradation on API failures

### Bottlenecks

- **OpenAI API**: 1-3 seconds per request (external)
- **Node Creation**: <100ms per node (good)
- **Connection**: Minimal overhead (<50ms)
- **Parameter Setting**: Near-instant

## Security Considerations

1. **API Key Storage**: Use `.env` file (not committed)
2. **Input Validation**: Sanitize user inputs
3. **Error Messages**: Don't leak sensitive information
4. **Function Sandboxing**: Limited to Resolve API scope

## Future Architecture

### Phase 2: VS Code Extension
```
VS Code Extension
    ↓
Language Server Protocol
    ↓
Python Backend (this system)
    ↓
DaVinci Resolve
```

### Phase 3: Template Library
```
User → Template Browser → Template System → FusionNodeBuilder → Resolve
```

### Phase 4: ComfyUI Integration
```
User → AI Assistant → ComfyUI API → Image Generation
                    → FusionNodeBuilder → Import to Resolve
```
