"""
Fusion Node Builder
Provides tools for creating and manipulating Fusion nodes programmatically
"""

from typing import Dict, List, Any, Optional, Tuple
import json


class FusionNodeBuilder:
    """Builder for creating and connecting Fusion nodes"""

    def __init__(self, comp):
        """
        Initialize with Fusion composition
        
        Args:
            comp: Fusion composition object from timeline clip
        """
        self.comp = comp
        self.created_nodes = {}  # Track created nodes by name

    def get_node_list(self) -> List[str]:
        """Get list of all nodes in composition"""
        if not self.comp:
            return []
        
        tools = self.comp.GetToolList()
        return [tool.GetAttrs()["TOOLS_Name"] for tool in tools.values()]

    def get_node_by_name(self, name: str):
        """Find node by name"""
        if not self.comp:
            return None
        
        tools = self.comp.GetToolList()
        for tool in tools.values():
            if tool.GetAttrs()["TOOLS_Name"] == name:
                return tool
        
        return None

    def create_node(
        self,
        node_type: str,
        name: Optional[str] = None,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """
        Create a new Fusion node
        
        Common node types:
        - Background: Solid color background
        - Transform: 2D transform (position, rotation, scale)
        - Merge: Composite two inputs
        - ColorCorrector: Color correction
        - BrightnessContrast: Brightness and contrast adjustment
        - Text+: Text generator
        - FastNoise: Noise generator
        - Blur: Blur effect
        - Glow: Glow effect
        - Loader: Load media file
        - Saver: Save output
        
        Args:
            node_type: Type of node to create
            name: Optional custom name
            x_pos: X position in flow
            y_pos: Y position in flow
        """
        if not self.comp:
            return None
        
        try:
            tool = self.comp.AddTool(node_type)
            
            if tool:
                # Set position
                tool.SetAttrs({"TOOLB_XPos": x_pos, "TOOLB_YPos": y_pos})
                
                # Set custom name if provided
                if name:
                    tool.SetAttrs({"TOOLS_Name": name})
                    self.created_nodes[name] = tool
                else:
                    default_name = tool.GetAttrs()["TOOLS_Name"]
                    self.created_nodes[default_name] = tool
                
                return tool
            
        except Exception as e:
            print(f"Error creating node {node_type}: {e}")
        
        return None

    def connect_nodes(
        self,
        source_node,
        target_node,
        output_name: str = "Output",
        input_name: str = "Input"
    ) -> bool:
        """
        Connect two nodes
        
        Args:
            source_node: Source node object or name
            target_node: Target node object or name
            output_name: Output socket name (default: "Output")
            input_name: Input socket name (default: "Input")
        """
        if not self.comp:
            return False
        
        # Resolve node names to objects
        if isinstance(source_node, str):
            source_node = self.get_node_by_name(source_node) or self.created_nodes.get(source_node)
        
        if isinstance(target_node, str):
            target_node = self.get_node_by_name(target_node) or self.created_nodes.get(target_node)
        
        if not source_node or not target_node:
            return False
        
        try:
            target_node.ConnectInput(input_name, source_node)
            return True
        except Exception as e:
            print(f"Error connecting nodes: {e}")
            return False

    def set_node_params(self, node, params: Dict[str, Any]) -> bool:
        """
        Set parameters on a node
        
        Args:
            node: Node object or name
            params: Dictionary of parameter names and values
        """
        if isinstance(node, str):
            node = self.get_node_by_name(node) or self.created_nodes.get(node)
        
        if not node:
            return False
        
        try:
            for param_name, value in params.items():
                node.SetInput(param_name, value)
            return True
        except Exception as e:
            print(f"Error setting node params: {e}")
            return False

    def create_text_node(
        self,
        text: str,
        name: Optional[str] = None,
        font: str = "Arial",
        size: float = 0.1,
        color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a text node with specified parameters"""
        node = self.create_node("Text+", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "StyledText": text,
                "Font": font,
                "Size": size,
                "Red": color[0],
                "Green": color[1],
                "Blue": color[2],
            })
        
        return node

    def create_background_node(
        self,
        color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0),
        name: Optional[str] = None,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a background node with specified color"""
        node = self.create_node("Background", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "TopLeftRed": color[0],
                "TopLeftGreen": color[1],
                "TopLeftBlue": color[2],
                "TopLeftAlpha": color[3],
            })
        
        return node

    def create_transform_node(
        self,
        name: Optional[str] = None,
        center: Tuple[float, float] = (0.5, 0.5),
        size: float = 1.0,
        angle: float = 0.0,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a transform node"""
        node = self.create_node("Transform", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "Center": center,
                "Size": size,
                "Angle": angle,
            })
        
        return node

    def create_merge_node(
        self,
        name: Optional[str] = None,
        blend_mode: str = "Normal",
        opacity: float = 1.0,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a merge node for compositing"""
        node = self.create_node("Merge", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "Blend": opacity,
            })
        
        return node

    def create_color_corrector(
        self,
        name: Optional[str] = None,
        gain: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        gamma: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        lift: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a color corrector node"""
        node = self.create_node("ColorCorrector", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "GainRed": gain[0],
                "GainGreen": gain[1],
                "GainBlue": gain[2],
                "GainAlpha": gain[3],
                "GammaRed": gamma[0],
                "GammaGreen": gamma[1],
                "GammaBlue": gamma[2],
                "GammaAlpha": gamma[3],
            })
        
        return node

    def create_blur_node(
        self,
        name: Optional[str] = None,
        blur_size: float = 10.0,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a blur node"""
        node = self.create_node("Blur", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "XBlurSize": blur_size,
            })
        
        return node

    def create_glow_node(
        self,
        name: Optional[str] = None,
        glow_size: float = 10.0,
        gain: float = 1.0,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a glow node"""
        node = self.create_node("Glow", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "GlowSize": glow_size,
                "Gain": gain,
            })
        
        return node

    def create_loader_node(
        self,
        file_path: str,
        name: Optional[str] = None,
        x_pos: int = 0,
        y_pos: int = 0
    ) -> Optional[object]:
        """Create a loader node to import media"""
        node = self.create_node("Loader", name=name, x_pos=x_pos, y_pos=y_pos)
        
        if node:
            self.set_node_params(node, {
                "Clip": file_path,
            })
        
        return node

    def build_lower_third(
        self,
        title_text: str,
        subtitle_text: str = "",
        bg_color: Tuple[float, float, float, float] = (0.0, 0.3, 0.6, 0.9),
        text_color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    ) -> Dict[str, object]:
        """
        Build a complete lower-third template
        
        Returns dictionary of created nodes
        """
        nodes = {}
        
        # Create background
        nodes["background"] = self.create_background_node(
            color=bg_color,
            name="LowerThird_BG",
            x_pos=0,
            y_pos=0
        )
        
        # Transform background to lower third position
        nodes["bg_transform"] = self.create_transform_node(
            name="LowerThird_Transform",
            center=(0.5, 0.15),
            size=0.4,
            x_pos=1,
            y_pos=0
        )
        
        # Connect background to transform
        self.connect_nodes(nodes["background"], nodes["bg_transform"])
        
        # Create title text
        nodes["title"] = self.create_text_node(
            text=title_text,
            name="LowerThird_Title",
            size=0.08,
            color=text_color,
            x_pos=2,
            y_pos=0
        )
        
        # Merge title onto background
        nodes["title_merge"] = self.create_merge_node(
            name="LowerThird_TitleMerge",
            x_pos=3,
            y_pos=0
        )
        
        self.connect_nodes(nodes["bg_transform"], nodes["title_merge"], input_name="Background")
        self.connect_nodes(nodes["title"], nodes["title_merge"], input_name="Foreground")
        
        # Add subtitle if provided
        if subtitle_text:
            nodes["subtitle"] = self.create_text_node(
                text=subtitle_text,
                name="LowerThird_Subtitle",
                size=0.05,
                color=text_color,
                x_pos=4,
                y_pos=0
            )
            
            nodes["subtitle_merge"] = self.create_merge_node(
                name="LowerThird_SubtitleMerge",
                x_pos=5,
                y_pos=0
            )
            
            self.connect_nodes(nodes["title_merge"], nodes["subtitle_merge"], input_name="Background")
            self.connect_nodes(nodes["subtitle"], nodes["subtitle_merge"], input_name="Foreground")
        
        return nodes

    def get_node_info(self, node) -> Dict[str, Any]:
        """Get information about a node"""
        if isinstance(node, str):
            node = self.get_node_by_name(node) or self.created_nodes.get(node)
        
        if not node:
            return {}
        
        attrs = node.GetAttrs()
        
        return {
            "name": attrs.get("TOOLS_Name", "Unknown"),
            "type": attrs.get("TOOLS_RegID", "Unknown"),
            "position": (attrs.get("TOOLB_XPos", 0), attrs.get("TOOLB_YPos", 0)),
        }

    def delete_node(self, node) -> bool:
        """Delete a node"""
        if isinstance(node, str):
            node = self.get_node_by_name(node) or self.created_nodes.get(node)
        
        if not node:
            return False
        
        try:
            node.Delete()
            # Remove from tracking
            node_name = node.GetAttrs()["TOOLS_Name"]
            if node_name in self.created_nodes:
                del self.created_nodes[node_name]
            return True
        except Exception as e:
            print(f"Error deleting node: {e}")
            return False

    def clear_composition(self) -> bool:
        """Clear all nodes from composition"""
        if not self.comp:
            return False
        
        try:
            tools = self.comp.GetToolList()
            for tool in tools.values():
                tool.Delete()
            
            self.created_nodes.clear()
            return True
        except Exception as e:
            print(f"Error clearing composition: {e}")
            return False
