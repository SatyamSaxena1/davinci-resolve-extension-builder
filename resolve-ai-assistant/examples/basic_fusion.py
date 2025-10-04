"""
Example: Basic Fusion Node Automation
Demonstrates creating and connecting Fusion nodes programmatically
"""

from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder


def example_basic_composition():
    """Create a simple Fusion composition with background and text"""
    
    print("Connecting to DaVinci Resolve...")
    controller = ResolveAIController()
    
    # Get current Fusion composition
    comp = controller.get_fusion_comp()
    if not comp:
        print("Error: No Fusion composition available")
        print("Please select a clip on the timeline first")
        return
    
    print("Creating Fusion node builder...")
    builder = FusionNodeBuilder(comp)
    
    # Clear existing nodes
    print("Clearing existing composition...")
    builder.clear_composition()
    
    # Create background
    print("Creating background node...")
    background = builder.create_background_node(
        color=(0.1, 0.2, 0.4, 1.0),  # Dark blue
        name="MyBackground",
        x_pos=0,
        y_pos=0
    )
    
    # Create text
    print("Creating text node...")
    text = builder.create_text_node(
        text="Hello from AI!",
        name="MyText",
        font="Arial",
        size=0.12,
        color=(1.0, 1.0, 1.0),  # White
        x_pos=1,
        y_pos=0
    )
    
    # Create merge to composite text onto background
    print("Creating merge node...")
    merge = builder.create_merge_node(
        name="FinalComposite",
        x_pos=2,
        y_pos=0
    )
    
    # Connect nodes
    print("Connecting nodes...")
    builder.connect_nodes(background, merge, input_name="Background")
    builder.connect_nodes(text, merge, input_name="Foreground")
    
    print("\n✓ Composition created successfully!")
    print("\nNodes created:")
    for node_name in builder.get_node_list():
        print(f"  - {node_name}")


def example_animated_text():
    """Create text with transform animation"""
    
    print("Creating animated text composition...")
    controller = ResolveAIController()
    comp = controller.get_fusion_comp()
    
    if not comp:
        print("Error: No Fusion composition available")
        return
    
    builder = FusionNodeBuilder(comp)
    builder.clear_composition()
    
    # Create black background
    bg = builder.create_background_node(
        color=(0.0, 0.0, 0.0, 1.0),
        name="BlackBG"
    )
    
    # Create text
    text = builder.create_text_node(
        text="Animated Title",
        name="AnimatedText",
        size=0.15,
        color=(1.0, 0.5, 0.0),  # Orange
        x_pos=1
    )
    
    # Add transform for animation
    transform = builder.create_transform_node(
        name="TextTransform",
        size=1.0,
        angle=0.0,
        x_pos=2
    )
    
    # Add glow effect
    glow = builder.create_glow_node(
        name="TextGlow",
        glow_size=20.0,
        gain=1.5,
        x_pos=3
    )
    
    # Connect: text → transform → glow
    builder.connect_nodes(text, transform)
    builder.connect_nodes(transform, glow)
    
    # Merge onto background
    merge = builder.create_merge_node(name="FinalMerge", x_pos=4)
    builder.connect_nodes(bg, merge, input_name="Background")
    builder.connect_nodes(glow, merge, input_name="Foreground")
    
    print("✓ Animated text composition created!")


def example_color_correction():
    """Create a color correction node graph"""
    
    print("Creating color correction composition...")
    controller = ResolveAIController()
    comp = controller.get_fusion_comp()
    
    if not comp:
        print("Error: No Fusion composition available")
        return
    
    builder = FusionNodeBuilder(comp)
    
    # Get existing MediaIn node (usually present)
    nodes = builder.get_node_list()
    media_in = None
    for node_name in nodes:
        if "MediaIn" in node_name:
            media_in = builder.get_node_by_name(node_name)
            break
    
    if not media_in:
        print("No MediaIn node found, creating loader instead...")
        media_in = builder.create_node("Loader", name="VideoInput", x_pos=0)
    
    # Create color corrector
    color_correct = builder.create_color_corrector(
        name="ColorGrade",
        gain=(1.2, 1.0, 0.9, 1.0),  # Slight warm tone
        gamma=(1.0, 1.0, 1.0, 1.0),
        x_pos=1
    )
    
    # Create brightness/contrast
    brightness = builder.create_node("BrightnessContrast", name="Brightness", x_pos=2)
    builder.set_node_params(brightness, {
        "Gain": 1.1,
        "Lift": 0.0
    })
    
    # Connect nodes
    builder.connect_nodes(media_in, color_correct)
    builder.connect_nodes(color_correct, brightness)
    
    print("✓ Color correction chain created!")


if __name__ == "__main__":
    print("DaVinci Resolve Fusion Examples\n")
    print("1. Basic Composition (background + text)")
    print("2. Animated Text with Glow")
    print("3. Color Correction Chain")
    
    choice = input("\nSelect example (1-3): ")
    
    if choice == "1":
        example_basic_composition()
    elif choice == "2":
        example_animated_text()
    elif choice == "3":
        example_color_correction()
    else:
        print("Invalid choice")
