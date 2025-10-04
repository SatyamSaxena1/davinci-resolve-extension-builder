"""
Core DaVinci Resolve AI Controller
Provides high-level interface for AI to control Resolve and Fusion
"""

import sys
import os
from typing import Optional, Dict, List, Any
from pathlib import Path
import json


class ResolveAIController:
    """Main controller for AI-driven DaVinci Resolve automation"""

    def __init__(self):
        """Initialize connection to DaVinci Resolve"""
        self.resolve = None
        self.project_manager = None
        self.project = None
        self.fusion = None
        
        # Import DaVinci Resolve Script module
        self._import_resolve_module()
        
        # Connect to Resolve
        self._connect_to_resolve()

    def _import_resolve_module(self):
        """Import DaVinciResolveScript module"""
        try:
            # Try standard import first
            import DaVinciResolveScript as dvr
            self.dvr_module = dvr
        except ImportError:
            # Add Resolve script paths for Windows
            resolve_script_api = os.getenv(
                "RESOLVE_SCRIPT_API",
                r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
            )
            
            # Add Modules folder to path
            modules_path = Path(resolve_script_api) / "Modules"
            if modules_path.exists():
                sys.path.append(str(modules_path))
            
            try:
                import DaVinciResolveScript as dvr
                self.dvr_module = dvr
            except ImportError as e:
                raise RuntimeError(
                    f"Failed to import DaVinciResolveScript module. "
                    f"Make sure DaVinci Resolve is installed and RESOLVE_SCRIPT_API is set correctly. "
                    f"Error: {e}"
                )

    def _connect_to_resolve(self):
        """Establish connection to running DaVinci Resolve instance"""
        try:
            self.resolve = self.dvr_module.scriptapp("Resolve")
            if not self.resolve:
                raise RuntimeError("Could not connect to DaVinci Resolve")
            
            self.project_manager = self.resolve.GetProjectManager()
            self.project = self.project_manager.GetCurrentProject()
            self.fusion = self.resolve.Fusion()
            
            if not self.project:
                raise RuntimeError("No project is currently open in DaVinci Resolve")
                
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to DaVinci Resolve. "
                f"Make sure Resolve is running with a project open. Error: {e}"
            )

    def get_project_info(self) -> Dict[str, Any]:
        """Get information about current project"""
        if not self.project:
            return {"error": "No project open"}
        
        timeline = self.project.GetCurrentTimeline()
        
        return {
            "project_name": self.project.GetName(),
            "current_timeline": timeline.GetName() if timeline else None,
            "timeline_count": self.project.GetTimelineCount(),
            "frame_rate": timeline.GetSetting("timelineFrameRate") if timeline else None,
            "resolution": {
                "width": timeline.GetSetting("timelineResolutionWidth") if timeline else None,
                "height": timeline.GetSetting("timelineResolutionHeight") if timeline else None,
            }
        }

    def get_current_timeline(self):
        """Get current timeline object"""
        if not self.project:
            return None
        return self.project.GetCurrentTimeline()

    def get_fusion_comp(self) -> Optional[object]:
        """
        Get current Fusion composition
        Returns Fusion comp from current timeline's selected clip
        """
        timeline = self.get_current_timeline()
        if not timeline:
            return None
        
        # Get currently selected clip
        current_video_item = timeline.GetCurrentVideoItem()
        if not current_video_item:
            return None
        
        # Get Fusion composition from clip
        fusion_comp = current_video_item.GetFusionCompByIndex(1)
        return fusion_comp

    def list_timeline_items(self) -> List[Dict[str, Any]]:
        """List all items in current timeline"""
        timeline = self.get_current_timeline()
        if not timeline:
            return []
        
        items = []
        item_count = timeline.GetItemListInTrack("video", 1)
        
        for item in item_count:
            items.append({
                "name": item.GetName(),
                "duration": item.GetDuration(),
                "start": item.GetStart(),
                "end": item.GetEnd(),
            })
        
        return items

    def add_marker(
        self,
        frame_id: int,
        color: str = "Blue",
        name: str = "",
        note: str = "",
        duration: int = 1
    ) -> bool:
        """
        Add marker to current timeline
        
        Args:
            frame_id: Frame number to add marker
            color: Marker color (Blue, Cyan, Green, Yellow, Red, Pink, Purple, etc.)
            name: Marker name
            note: Marker note/description
            duration: Marker duration in frames
        """
        timeline = self.get_current_timeline()
        if not timeline:
            return False
        
        return timeline.AddMarker(
            frame_id,
            color,
            name,
            note,
            duration
        )

    def create_timeline(
        self,
        name: str,
        frame_rate: str = "24",
        resolution: tuple = (1920, 1080)
    ) -> bool:
        """
        Create new timeline
        
        Args:
            name: Timeline name
            frame_rate: Frame rate (24, 25, 30, etc.)
            resolution: (width, height) tuple
        """
        media_pool = self.project.GetMediaPool()
        
        timeline_settings = {
            "name": name,
            "timelineResolutionWidth": str(resolution[0]),
            "timelineResolutionHeight": str(resolution[1]),
            "timelineFrameRate": frame_rate,
        }
        
        timeline = media_pool.CreateEmptyTimeline(name)
        if timeline:
            # Apply settings
            for key, value in timeline_settings.items():
                if key != "name":
                    timeline.SetSetting(key, value)
            return True
        
        return False

    def set_current_timeline(self, timeline_name: str) -> bool:
        """Set timeline as current by name"""
        timeline_count = self.project.GetTimelineCount()
        
        for i in range(1, timeline_count + 1):
            timeline = self.project.GetTimelineByIndex(i)
            if timeline and timeline.GetName() == timeline_name:
                self.project.SetCurrentTimeline(timeline)
                return True
        
        return False

    def export_timeline(
        self,
        output_path: str,
        preset_name: str = "H.264 Master"
    ) -> bool:
        """
        Export current timeline
        
        Args:
            output_path: Full path for output file
            preset_name: Render preset name
        """
        timeline = self.get_current_timeline()
        if not timeline:
            return False
        
        self.project.SetCurrentTimeline(timeline)
        
        # Load render preset
        self.project.LoadRenderPreset(preset_name)
        
        # Set output path
        self.project.SetRenderSettings({
            "TargetDir": str(Path(output_path).parent),
            "CustomName": Path(output_path).stem
        })
        
        # Add to render queue
        render_job_id = self.project.AddRenderJob()
        
        if render_job_id:
            # Start rendering
            self.project.StartRendering(render_job_id)
            return True
        
        return False

    def get_media_pool_items(self) -> List[Dict[str, Any]]:
        """Get all items in media pool"""
        media_pool = self.project.GetMediaPool()
        root_folder = media_pool.GetRootFolder()
        
        items = []
        clips = root_folder.GetClipList()
        
        for clip in clips:
            items.append({
                "name": clip.GetName(),
                "duration": clip.GetClipProperty("Duration"),
                "fps": clip.GetClipProperty("FPS"),
                "resolution": f"{clip.GetClipProperty('Resolution Width')}x{clip.GetClipProperty('Resolution Height')}",
            })
        
        return items

    def import_media(self, file_paths: List[str]) -> bool:
        """
        Import media files into media pool
        
        Args:
            file_paths: List of file paths to import
        """
        media_pool = self.project.GetMediaPool()
        media_storage = self.resolve.GetMediaStorage()
        
        # Add clips to media pool
        result = media_storage.AddItemListToMediaPool(file_paths)
        return bool(result)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of Resolve connection"""
        return {
            "connected": self.resolve is not None,
            "project_open": self.project is not None,
            "project_info": self.get_project_info() if self.project else None,
            "fusion_available": self.fusion is not None,
        }
