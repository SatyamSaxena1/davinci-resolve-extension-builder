"""
Example: Lower-Third Template Generator
Demonstrates building complete lower-third graphics
"""

from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder


def create_simple_lower_third(title: str, subtitle: str = ""):
    """Create a simple lower-third with default styling"""
    
    print(f"Creating lower-third for: {title}")
    
    controller = ResolveAIController()
    comp = controller.get_fusion_comp()
    
    if not comp:
        print("Error: No Fusion composition available")
        return
    
    builder = FusionNodeBuilder(comp)
    builder.clear_composition()
    
    # Use built-in template
    nodes = builder.build_lower_third(
        title_text=title,
        subtitle_text=subtitle,
        bg_color=(0.0, 0.3, 0.6, 0.9),  # Blue
        text_color=(1.0, 1.0, 1.0)      # White
    )
    
    print(f"✓ Lower-third created with {len(nodes)} nodes")


def create_custom_lower_third(title: str, subtitle: str, style: str = "corporate"):
    """Create a custom-styled lower-third"""
    
    print(f"Creating {style} lower-third...")
    
    controller = ResolveAIController()
    comp = controller.get_fusion_comp()
    
    if not comp:
        print("Error: No Fusion composition available")
        return
    
    builder = FusionNodeBuilder(comp)
    builder.clear_composition()
    
    # Different styles
    styles = {
        "corporate": {
            "bg_color": (0.0, 0.2, 0.4, 0.95),
            "text_color": (1.0, 1.0, 1.0),
            "accent_color": (0.0, 0.8, 1.0)
        },
        "modern": {
            "bg_color": (0.1, 0.1, 0.1, 0.9),
            "text_color": (1.0, 1.0, 1.0),
            "accent_color": (1.0, 0.3, 0.0)
        },
        "elegant": {
            "bg_color": (0.2, 0.15, 0.25, 0.85),
            "text_color": (0.95, 0.9, 0.85),
            "accent_color": (0.8, 0.6, 0.9)
        }
    }
    
    style_config = styles.get(style, styles["corporate"])
    
    # Create background
    bg = builder.create_background_node(
        color=style_config["bg_color"],
        name="LT_Background",
        x_pos=0, y_pos=0
    )
    
    # Transform background to lower-third position
    bg_transform = builder.create_transform_node(
        name="LT_Position",
        center=(0.5, 0.15),  # Lower third position
        size=0.45,
        x_pos=1, y_pos=0
    )
    builder.connect_nodes(bg, bg_transform)
    
    # Add accent bar
    accent = builder.create_background_node(
        color=(*style_config["accent_color"], 1.0),
        name="LT_Accent",
        x_pos=0, y_pos=1
    )
    
    accent_transform = builder.create_transform_node(
        name="LT_AccentPos",
        center=(0.5, 0.12),
        size=0.1,
        x_pos=1, y_pos=1
    )
    builder.connect_nodes(accent, accent_transform)
    
    # Merge accent onto background
    merge1 = builder.create_merge_node(name="LT_BG_Merge", x_pos=2, y_pos=0)
    builder.connect_nodes(bg_transform, merge1, input_name="Background")
    builder.connect_nodes(accent_transform, merge1, input_name="Foreground")
    
    # Create title text
    title_node = builder.create_text_node(
        text=title,
        name="LT_Title",
        font="Arial",
        size=0.08,
        color=style_config["text_color"],
        x_pos=3, y_pos=0
    )
    
    # Merge title
    merge2 = builder.create_merge_node(name="LT_Title_Merge", x_pos=4, y_pos=0)
    builder.connect_nodes(merge1, merge2, input_name="Background")
    builder.connect_nodes(title_node, merge2, input_name="Foreground")
    
    # Create subtitle if provided
    if subtitle:
        subtitle_node = builder.create_text_node(
            text=subtitle,
            name="LT_Subtitle",
            font="Arial",
            size=0.05,
            color=style_config["text_color"],
            x_pos=5, y_pos=0
        )
        
        # Merge subtitle
        merge3 = builder.create_merge_node(name="LT_Final_Merge", x_pos=6, y_pos=0)
        builder.connect_nodes(merge2, merge3, input_name="Background")
        builder.connect_nodes(subtitle_node, merge3, input_name="Foreground")
    
    print(f"✓ {style.capitalize()} lower-third created!")


def create_broadcast_lower_third(
    name: str,
    role: str,
    show_logo: bool = False
):
    """Create a broadcast-style lower-third"""
    
    print(f"Creating broadcast lower-third for {name}...")
    
    controller = ResolveAIController()
    comp = controller.get_fusion_comp()
    
    if not comp:
        print("Error: No Fusion composition available")
        return
    
    builder = FusionNodeBuilder(comp)
    builder.clear_composition()
    
    # Dark semi-transparent background
    bg = builder.create_background_node(
        color=(0.05, 0.05, 0.1, 0.85),
        name="Broadcast_BG",
        x_pos=0
    )
    
    bg_transform = builder.create_transform_node(
        name="Broadcast_Position",
        center=(0.5, 0.14),
        size=0.5,
        x_pos=1
    )
    builder.connect_nodes(bg, bg_transform)
    
    # Name text (larger)
    name_text = builder.create_text_node(
        text=name,
        name="Broadcast_Name",
        size=0.09,
        color=(1.0, 1.0, 1.0),
        x_pos=2
    )
    
    # Add subtle glow to name
    name_glow = builder.create_glow_node(
        name="Name_Glow",
        glow_size=5.0,
        gain=0.8,
        x_pos=3
    )
    builder.connect_nodes(name_text, name_glow)
    
    # Merge name
    merge1 = builder.create_merge_node(name="Broadcast_Name_Merge", x_pos=4)
    builder.connect_nodes(bg_transform, merge1, input_name="Background")
    builder.connect_nodes(name_glow, merge1, input_name="Foreground")
    
    # Role text (smaller, below name)
    role_text = builder.create_text_node(
        text=role,
        name="Broadcast_Role",
        size=0.05,
        color=(0.9, 0.9, 1.0),
        x_pos=5
    )
    
    # Merge role
    merge2 = builder.create_merge_node(name="Broadcast_Final", x_pos=6)
    builder.connect_nodes(merge1, merge2, input_name="Background")
    builder.connect_nodes(role_text, merge2, input_name="Foreground")
    
    print("✓ Broadcast lower-third created!")
    print("\nNote: Text positions may need manual adjustment in Fusion UI")


if __name__ == "__main__":
    print("Lower-Third Template Generator\n")
    print("1. Simple Lower-Third")
    print("2. Corporate Style")
    print("3. Modern Style")
    print("4. Elegant Style")
    print("5. Broadcast Style")
    
    choice = input("\nSelect template (1-5): ")
    
    if choice == "1":
        title = input("Enter title: ")
        subtitle = input("Enter subtitle (optional): ")
        create_simple_lower_third(title, subtitle)
    
    elif choice in ["2", "3", "4"]:
        title = input("Enter title: ")
        subtitle = input("Enter subtitle: ")
        style = {"2": "corporate", "3": "modern", "4": "elegant"}[choice]
        create_custom_lower_third(title, subtitle, style)
    
    elif choice == "5":
        name = input("Enter name: ")
        role = input("Enter role: ")
        create_broadcast_lower_third(name, role)
    
    else:
        print("Invalid choice")
