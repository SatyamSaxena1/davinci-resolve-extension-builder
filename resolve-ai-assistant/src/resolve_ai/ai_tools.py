"""
AI Function Tools
OpenAI function calling schemas for DaVinci Resolve control
"""

from typing import Dict, List, Any
import json


# Tool definitions for OpenAI function calling
RESOLVE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_project_status",
            "description": "Get current status and information about the DaVinci Resolve project, including timeline info, resolution, and frame rate",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_fusion_node",
            "description": "Create a new Fusion node in the current composition. Common node types: Background, Transform, Merge, ColorCorrector, Text+, Blur, Glow, Loader",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_type": {
                        "type": "string",
                        "description": "Type of node to create (e.g., 'Background', 'Transform', 'Text+', 'Merge')"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional custom name for the node"
                    },
                    "x_pos": {
                        "type": "integer",
                        "description": "X position in the Fusion flow (default: 0)"
                    },
                    "y_pos": {
                        "type": "integer",
                        "description": "Y position in the Fusion flow (default: 0)"
                    }
                },
                "required": ["node_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "connect_fusion_nodes",
            "description": "Connect two Fusion nodes together",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_node": {
                        "type": "string",
                        "description": "Name of the source node"
                    },
                    "target_node": {
                        "type": "string",
                        "description": "Name of the target node"
                    },
                    "output_name": {
                        "type": "string",
                        "description": "Output socket name (default: 'Output')"
                    },
                    "input_name": {
                        "type": "string",
                        "description": "Input socket name (default: 'Input' or 'Background'/'Foreground' for Merge)"
                    }
                },
                "required": ["source_node", "target_node"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_node_parameters",
            "description": "Set parameters on a Fusion node. Common parameters: Size, Angle, Center, Blend, Color values (Red, Green, Blue), GlowSize, XBlurSize, StyledText",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_name": {
                        "type": "string",
                        "description": "Name of the node to modify"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Dictionary of parameter names and values to set"
                    }
                },
                "required": ["node_name", "parameters"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_text_node",
            "description": "Create a text node with specified content and styling",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text content to display"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional custom name for the node"
                    },
                    "font": {
                        "type": "string",
                        "description": "Font name (default: 'Arial')"
                    },
                    "size": {
                        "type": "number",
                        "description": "Text size as fraction of frame (0.0 to 1.0, default: 0.1)"
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "RGB color values [R, G, B] from 0.0 to 1.0"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_background_node",
            "description": "Create a solid color background node",
            "parameters": {
                "type": "object",
                "properties": {
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "RGBA color values [R, G, B, A] from 0.0 to 1.0"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional custom name for the node"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_lower_third",
            "description": "Create a complete lower-third graphic template with background and text",
            "parameters": {
                "type": "object",
                "properties": {
                    "title_text": {
                        "type": "string",
                        "description": "Main title text"
                    },
                    "subtitle_text": {
                        "type": "string",
                        "description": "Optional subtitle text"
                    },
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Background RGBA color [R, G, B, A] from 0.0 to 1.0"
                    },
                    "text_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Text RGB color [R, G, B] from 0.0 to 1.0"
                    }
                },
                "required": ["title_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_fusion_nodes",
            "description": "List all nodes currently in the Fusion composition",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_fusion_node",
            "description": "Delete a node from the Fusion composition",
            "parameters": {
                "type": "object",
                "properties": {
                    "node_name": {
                        "type": "string",
                        "description": "Name of the node to delete"
                    }
                },
                "required": ["node_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_fusion_composition",
            "description": "Clear all nodes from the Fusion composition",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_timeline_marker",
            "description": "Add a marker to the current timeline at a specific frame",
            "parameters": {
                "type": "object",
                "properties": {
                    "frame_id": {
                        "type": "integer",
                        "description": "Frame number to add marker"
                    },
                    "color": {
                        "type": "string",
                        "description": "Marker color (Blue, Cyan, Green, Yellow, Red, Pink, Purple)",
                        "enum": ["Blue", "Cyan", "Green", "Yellow", "Red", "Pink", "Purple"]
                    },
                    "name": {
                        "type": "string",
                        "description": "Marker name"
                    },
                    "note": {
                        "type": "string",
                        "description": "Marker note/description"
                    }
                },
                "required": ["frame_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_timeline",
            "description": "Create a new timeline with specified settings",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Timeline name"
                    },
                    "frame_rate": {
                        "type": "string",
                        "description": "Frame rate (24, 25, 30, 60, etc.)"
                    },
                    "resolution": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "[width, height] in pixels"
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "import_media_files",
            "description": "Import media files into the media pool",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to import"
                    }
                },
                "required": ["file_paths"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_media_pool_items",
            "description": "List all items currently in the media pool",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


class FunctionExecutor:
    """Execute function calls from LLM"""
    
    def __init__(self, controller, fusion_builder=None):
        """
        Initialize function executor
        
        Args:
            controller: ResolveAIController instance
            fusion_builder: FusionNodeBuilder instance (optional)
        """
        self.controller = controller
        self.fusion_builder = fusion_builder
    
    def execute(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a function call
        
        Args:
            function_name: Name of the function to call
            arguments: Function arguments as dictionary
        
        Returns:
            Result dictionary with success status and data
        """
        try:
            # Project/Timeline functions
            if function_name == "get_project_status":
                return {
                    "success": True,
                    "data": self.controller.get_status()
                }
            
            elif function_name == "create_timeline":
                success = self.controller.create_timeline(
                    name=arguments["name"],
                    frame_rate=arguments.get("frame_rate", "24"),
                    resolution=tuple(arguments.get("resolution", [1920, 1080]))
                )
                return {"success": success, "data": f"Timeline '{arguments['name']}' created"}
            
            elif function_name == "add_timeline_marker":
                success = self.controller.add_marker(
                    frame_id=arguments["frame_id"],
                    color=arguments.get("color", "Blue"),
                    name=arguments.get("name", ""),
                    note=arguments.get("note", "")
                )
                return {"success": success, "data": "Marker added"}
            
            elif function_name == "import_media_files":
                success = self.controller.import_media(arguments["file_paths"])
                return {"success": success, "data": f"Imported {len(arguments['file_paths'])} files"}
            
            elif function_name == "list_media_pool_items":
                items = self.controller.get_media_pool_items()
                return {"success": True, "data": items}
            
            # Fusion functions
            elif function_name == "create_fusion_node":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                node = self.fusion_builder.create_node(
                    node_type=arguments["node_type"],
                    name=arguments.get("name"),
                    x_pos=arguments.get("x_pos", 0),
                    y_pos=arguments.get("y_pos", 0)
                )
                return {
                    "success": node is not None,
                    "data": f"Created {arguments['node_type']} node"
                }
            
            elif function_name == "connect_fusion_nodes":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                success = self.fusion_builder.connect_nodes(
                    source_node=arguments["source_node"],
                    target_node=arguments["target_node"],
                    output_name=arguments.get("output_name", "Output"),
                    input_name=arguments.get("input_name", "Input")
                )
                return {
                    "success": success,
                    "data": f"Connected {arguments['source_node']} to {arguments['target_node']}"
                }
            
            elif function_name == "set_node_parameters":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                success = self.fusion_builder.set_node_params(
                    node=arguments["node_name"],
                    params=arguments["parameters"]
                )
                return {
                    "success": success,
                    "data": f"Set parameters on {arguments['node_name']}"
                }
            
            elif function_name == "create_text_node":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                node = self.fusion_builder.create_text_node(
                    text=arguments["text"],
                    name=arguments.get("name"),
                    font=arguments.get("font", "Arial"),
                    size=arguments.get("size", 0.1),
                    color=tuple(arguments.get("color", [1.0, 1.0, 1.0]))
                )
                return {
                    "success": node is not None,
                    "data": f"Created text node with text: {arguments['text']}"
                }
            
            elif function_name == "create_background_node":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                node = self.fusion_builder.create_background_node(
                    color=tuple(arguments.get("color", [0.0, 0.0, 0.0, 1.0])),
                    name=arguments.get("name")
                )
                return {
                    "success": node is not None,
                    "data": "Created background node"
                }
            
            elif function_name == "create_lower_third":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                nodes = self.fusion_builder.build_lower_third(
                    title_text=arguments["title_text"],
                    subtitle_text=arguments.get("subtitle_text", ""),
                    bg_color=tuple(arguments.get("bg_color", [0.0, 0.3, 0.6, 0.9])),
                    text_color=tuple(arguments.get("text_color", [1.0, 1.0, 1.0]))
                )
                return {
                    "success": len(nodes) > 0,
                    "data": f"Created lower-third with {len(nodes)} nodes"
                }
            
            elif function_name == "list_fusion_nodes":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                nodes = self.fusion_builder.get_node_list()
                return {"success": True, "data": nodes}
            
            elif function_name == "delete_fusion_node":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                success = self.fusion_builder.delete_node(arguments["node_name"])
                return {
                    "success": success,
                    "data": f"Deleted node {arguments['node_name']}"
                }
            
            elif function_name == "clear_fusion_composition":
                if not self.fusion_builder:
                    return {"success": False, "error": "Fusion composition not available"}
                
                success = self.fusion_builder.clear_composition()
                return {
                    "success": success,
                    "data": "Cleared all nodes from composition"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
