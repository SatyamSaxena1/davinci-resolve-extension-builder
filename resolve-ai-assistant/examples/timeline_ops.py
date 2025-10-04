"""
Example: Timeline Operations
Demonstrates timeline management, markers, and media import
"""

from resolve_ai.controller import ResolveAIController
from pathlib import Path


def show_project_info():
    """Display current project information"""
    
    print("Fetching project information...")
    controller = ResolveAIController()
    
    status = controller.get_status()
    
    if not status["connected"]:
        print("❌ Not connected to Resolve")
        return
    
    if not status["project_open"]:
        print("❌ No project open")
        return
    
    project_info = status["project_info"]
    
    print("\n📁 Project Information:")
    print(f"  Name: {project_info['project_name']}")
    print(f"  Current Timeline: {project_info['current_timeline'] or 'None'}")
    print(f"  Timeline Count: {project_info['timeline_count']}")
    
    if project_info['frame_rate']:
        print(f"  Frame Rate: {project_info['frame_rate']} fps")
        print(f"  Resolution: {project_info['resolution']['width']}x{project_info['resolution']['height']}")
    
    print(f"  Fusion Available: {'✓' if status['fusion_available'] else '✗'}")


def add_scene_markers():
    """Add color-coded markers for different scene types"""
    
    print("Adding scene markers...")
    controller = ResolveAIController()
    
    # Example markers for a typical video structure
    markers = [
        (0, "Blue", "Intro", "Opening sequence"),
        (240, "Green", "Scene 1", "Main content starts"),
        (720, "Yellow", "B-Roll", "Insert b-roll footage here"),
        (1080, "Green", "Scene 2", "Second part of content"),
        (1440, "Red", "Outro", "End credits and call-to-action"),
    ]
    
    for frame, color, name, note in markers:
        success = controller.add_marker(
            frame_id=frame,
            color=color,
            name=name,
            note=note
        )
        if success:
            print(f"  ✓ Added {color} marker at frame {frame}: {name}")
        else:
            print(f"  ✗ Failed to add marker at frame {frame}")


def create_new_project_timeline():
    """Create a new timeline with custom settings"""
    
    print("Creating new timeline...")
    
    timeline_name = input("Timeline name: ")
    
    print("\nFrame rate options:")
    print("  1. 24 fps (Cinema)")
    print("  2. 25 fps (PAL)")
    print("  3. 30 fps (NTSC)")
    print("  4. 60 fps (High frame rate)")
    
    fps_choice = input("Select frame rate (1-4): ")
    fps_map = {"1": "24", "2": "25", "3": "30", "4": "60"}
    frame_rate = fps_map.get(fps_choice, "24")
    
    print("\nResolution options:")
    print("  1. 1920x1080 (Full HD)")
    print("  2. 3840x2160 (4K UHD)")
    print("  3. 2560x1440 (2K)")
    print("  4. 1280x720 (HD)")
    
    res_choice = input("Select resolution (1-4): ")
    res_map = {
        "1": (1920, 1080),
        "2": (3840, 2160),
        "3": (2560, 1440),
        "4": (1280, 720)
    }
    resolution = res_map.get(res_choice, (1920, 1080))
    
    controller = ResolveAIController()
    success = controller.create_timeline(
        name=timeline_name,
        frame_rate=frame_rate,
        resolution=resolution
    )
    
    if success:
        print(f"\n✓ Timeline '{timeline_name}' created!")
        print(f"  Frame Rate: {frame_rate} fps")
        print(f"  Resolution: {resolution[0]}x{resolution[1]}")
    else:
        print("\n✗ Failed to create timeline")


def import_media_from_folder():
    """Import media files from a folder"""
    
    print("Import Media Files\n")
    
    folder_path = input("Enter folder path: ")
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder not found: {folder_path}")
        return
    
    # Supported video/image formats
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.mxf', '.r3d'}
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.exr', '.dpx'}
    audio_extensions = {'.wav', '.mp3', '.aac', '.aif', '.aiff'}
    
    all_extensions = video_extensions | image_extensions | audio_extensions
    
    # Find all media files
    media_files = []
    for file in folder.rglob('*'):
        if file.suffix.lower() in all_extensions:
            media_files.append(str(file))
    
    if not media_files:
        print(f"❌ No media files found in {folder_path}")
        return
    
    print(f"\nFound {len(media_files)} media files:")
    for i, file in enumerate(media_files[:10], 1):  # Show first 10
        print(f"  {i}. {Path(file).name}")
    
    if len(media_files) > 10:
        print(f"  ... and {len(media_files) - 10} more")
    
    confirm = input(f"\nImport all {len(media_files)} files? (y/n): ")
    
    if confirm.lower() == 'y':
        controller = ResolveAIController()
        success = controller.import_media(media_files)
        
        if success:
            print(f"\n✓ Successfully imported {len(media_files)} files to media pool")
        else:
            print("\n✗ Import failed")


def list_media_pool():
    """List all items in the media pool"""
    
    print("Fetching media pool items...\n")
    
    controller = ResolveAIController()
    items = controller.get_media_pool_items()
    
    if not items:
        print("📭 Media pool is empty")
        return
    
    print(f"📚 Media Pool ({len(items)} items):\n")
    
    for i, item in enumerate(items, 1):
        print(f"{i}. {item['name']}")
        print(f"   Duration: {item['duration']}")
        print(f"   FPS: {item['fps']}")
        print(f"   Resolution: {item['resolution']}")
        print()


def batch_add_chapter_markers():
    """Add markers at regular intervals for chapter points"""
    
    print("Batch Add Chapter Markers\n")
    
    interval = int(input("Interval in seconds (e.g., 300 for 5 minutes): "))
    num_chapters = int(input("Number of chapters: "))
    
    controller = ResolveAIController()
    
    # Get current timeline frame rate
    project_info = controller.get_project_info()
    frame_rate = float(project_info.get('frame_rate', 24))
    
    print(f"\nAdding {num_chapters} chapter markers at {interval}s intervals...")
    
    for i in range(num_chapters):
        frame = int(i * interval * frame_rate)
        success = controller.add_marker(
            frame_id=frame,
            color="Cyan",
            name=f"Chapter {i + 1}",
            note=f"Chapter marker at {i * interval}s"
        )
        
        if success:
            print(f"  ✓ Chapter {i + 1} at frame {frame} ({i * interval}s)")


if __name__ == "__main__":
    print("DaVinci Resolve Timeline Operations\n")
    print("1. Show Project Information")
    print("2. Add Scene Markers (predefined)")
    print("3. Create New Timeline")
    print("4. Import Media from Folder")
    print("5. List Media Pool Items")
    print("6. Batch Add Chapter Markers")
    
    choice = input("\nSelect operation (1-6): ")
    print()
    
    if choice == "1":
        show_project_info()
    elif choice == "2":
        add_scene_markers()
    elif choice == "3":
        create_new_project_timeline()
    elif choice == "4":
        import_media_from_folder()
    elif choice == "5":
        list_media_pool()
    elif choice == "6":
        batch_add_chapter_markers()
    else:
        print("Invalid choice")
