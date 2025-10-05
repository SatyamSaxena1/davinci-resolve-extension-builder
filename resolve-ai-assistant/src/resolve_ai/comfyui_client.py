"""
ComfyUI Client for DaVinci Resolve
Handles AI image generation via ComfyUI + Wan 2.2
"""

import requests
import websocket
import json
import uuid
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class GenerationResult:
    """Result of ComfyUI generation"""
    image_path: str
    prompt: str
    seed: int
    steps: int
    generation_time: float

class ComfyUIClient:
    """Client for ComfyUI API with Wan 2.2 model"""
    
    def __init__(
        self,
        server_url: str = "http://localhost:8188",
        wan22_model: str = "wan2.2.safetensors"
    ):
        self.server_url = server_url.rstrip('/')
        self.wan22_model = wan22_model
        self.client_id = str(uuid.uuid4())
        
        self._check_server_available()
    
    def _check_server_available(self) -> bool:
        """Check if ComfyUI server is running"""
        try:
            response = requests.get(f"{self.server_url}/system_stats", timeout=5)
            if response.status_code == 200:
                return True
            raise RuntimeError("ComfyUI server not responding")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"ComfyUI server not available at {self.server_url}\n"
                "Make sure ComfyUI is running:\n"
                "  python main.py --listen 0.0.0.0 --port 8188"
            ) from e
    
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        width: int = 1920,
        height: int = 1080,
        steps: int = 20,
        cfg: float = 7.0,
        seed: Optional[int] = None
    ) -> GenerationResult:
        """
        Generate image using Wan 2.2
        
        Args:
            prompt: Text description of desired image
            negative_prompt: What to avoid
            width: Image width (default 1080p)
            height: Image height
            steps: Sampling steps (20 for ~10-15s generation)
            cfg: Classifier-free guidance scale
            seed: Random seed (None for random)
        
        Returns:
            GenerationResult with image path and metadata
        """
        if seed is None:
            seed = int(time.time())
        
        # Build workflow
        workflow = self._build_wan22_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg=cfg,
            seed=seed
        )
        
        start_time = time.time()
        
        # Submit workflow
        print(f"🎨 Generating with Wan 2.2...")
        print(f"   Prompt: {prompt}")
        print(f"   Steps: {steps} (~{steps * 0.5:.0f}s estimated)")
        
        response = requests.post(
            f"{self.server_url}/prompt",
            json={"prompt": workflow, "client_id": self.client_id}
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to submit workflow: {response.text}")
        
        prompt_id = response.json()["prompt_id"]
        
        # Monitor progress
        self._monitor_progress(prompt_id)
        
        # Get generated image
        image_data = self._get_image(prompt_id)
        
        # Save to temp directory
        output_path = Path(tempfile.gettempdir()) / f"comfyui_{prompt_id}.png"
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        generation_time = time.time() - start_time
        
        print(f"✅ Generated in {generation_time:.1f}s: {output_path}")
        
        return GenerationResult(
            image_path=str(output_path),
            prompt=prompt,
            seed=seed,
            steps=steps,
            generation_time=generation_time
        )
    
    def _build_wan22_workflow(
        self,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        cfg: float,
        seed: int
    ) -> Dict[str, Any]:
        """Build ComfyUI workflow for Wan 2.2"""
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": self.wan22_model
                }
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": prompt,
                    "clip": ["1", 1]
                }
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1]
                }
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                }
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["6", 0]
                }
            }
        }
    
    def _monitor_progress(self, prompt_id: str) -> None:
        """Monitor generation progress via WebSocket"""
        try:
            ws_url = self.server_url.replace('http://', 'ws://').replace('https://', 'wss://')
            ws = websocket.create_connection(
                f"{ws_url}/ws?clientId={self.client_id}",
                timeout=60
            )
            
            last_node = None
            
            while True:
                try:
                    msg = ws.recv()
                    if not msg:
                        break
                    
                    data = json.loads(msg)
                    
                    if data.get("type") == "progress":
                        # Show progress
                        value = data["data"]["value"]
                        max_val = data["data"]["max"]
                        percentage = (value / max_val * 100) if max_val > 0 else 0
                        print(f"   Progress: {percentage:.0f}%", end='\r')
                    
                    elif data.get("type") == "executing":
                        node = data["data"].get("node")
                        if node != last_node:
                            if node:
                                print(f"   Executing node: {node}")
                            last_node = node
                        
                        # Check if completed
                        if data["data"].get("prompt_id") == prompt_id and node is None:
                            print("   Generation complete!")
                            break
                
                except websocket.WebSocketTimeoutException:
                    break
            
            ws.close()
        
        except Exception as e:
            print(f"   Warning: Could not monitor progress: {e}")
            # Continue anyway - generation may still succeed
            time.sleep(10)  # Estimate wait time
    
    def _get_image(self, prompt_id: str) -> bytes:
        """Get generated image from ComfyUI"""
        # Get history to find output filename
        history_response = requests.get(
            f"{self.server_url}/history/{prompt_id}"
        )
        
        if history_response.status_code != 200:
            raise RuntimeError("Failed to get generation history")
        
        history = history_response.json()
        
        if prompt_id not in history:
            raise RuntimeError("Generation not found in history")
        
        # Extract output filename from history
        outputs = history[prompt_id].get("outputs", {})
        
        # Find SaveImage node output
        image_info = None
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                image_info = node_output["images"][0]
                break
        
        if not image_info:
            raise RuntimeError("No image found in generation output")
        
        filename = image_info["filename"]
        subfolder = image_info.get("subfolder", "")
        folder_type = image_info.get("type", "output")
        
        # Download image
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        
        image_response = requests.get(
            f"{self.server_url}/view",
            params=params
        )
        
        if image_response.status_code != 200:
            raise RuntimeError("Failed to download image")
        
        return image_response.content
    
    def generate_batch(
        self,
        prompts: List[str],
        steps: int = 20,
        **kwargs
    ) -> List[GenerationResult]:
        """Generate multiple images (for variations)"""
        results = []
        for i, prompt in enumerate(prompts):
            print(f"\n🎨 Generating {i+1}/{len(prompts)}...")
            result = self.generate(prompt, steps=steps, **kwargs)
            results.append(result)
        return results
    
    def upscale(
        self,
        image_path: str,
        scale: float = 2.0
    ) -> GenerationResult:
        """Upscale an existing image (for higher quality)"""
        # TODO: Implement upscaling workflow
        # This would use an upscaling model in ComfyUI
        raise NotImplementedError("Upscaling not yet implemented")


# Helper functions for common use cases

def generate_background(
    prompt: str,
    client: Optional[ComfyUIClient] = None
) -> str:
    """Generate a background image"""
    if client is None:
        client = ComfyUIClient()
    
    result = client.generate(
        prompt=prompt,
        steps=15,  # Faster for backgrounds
        width=1920,
        height=1080
    )
    
    return result.image_path

def generate_character(
    description: str,
    client: Optional[ComfyUIClient] = None
) -> str:
    """Generate a character image"""
    if client is None:
        client = ComfyUIClient()
    
    prompt = f"character portrait, {description}, professional lighting, detailed"
    
    result = client.generate(
        prompt=prompt,
        steps=25,  # More steps for quality
        width=1024,
        height=1024
    )
    
    return result.image_path

def generate_scene(
    description: str,
    style: str = "cinematic",
    client: Optional[ComfyUIClient] = None
) -> str:
    """Generate a scene/environment"""
    if client is None:
        client = ComfyUIClient()
    
    prompt = f"{style} scene, {description}, high quality, detailed"
    
    result = client.generate(
        prompt=prompt,
        steps=20,
        width=1920,
        height=1080
    )
    
    return result.image_path
