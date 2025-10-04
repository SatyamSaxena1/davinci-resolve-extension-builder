param(
  [string]$PlanFile = "PLAN.md",
  [ValidateSet("scripting","fusion","ofx","dctl")]
  [string]$Target = "scripting",
  [string]$OutDir = "resolve-addon"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $PlanFile)) {
  Write-Error "Plan file not found: $PlanFile"
}

switch ($Target) {
  "scripting" { $ProjectName = "resolve-scripting-starter" }
  "fusion"    { $ProjectName = "resolve-fusion-fuse-starter" }
  "ofx"       { $ProjectName = "resolve-ofx-starter" }
  "dctl"      { $ProjectName = "resolve-dctl-starter" }
}

Write-Host "🚀 Generating $ProjectName from $PlanFile (target: $Target)..." -ForegroundColor Cyan

# Create output directory structure
$ProjectPath = Join-Path $OutDir $ProjectName
New-Item -ItemType Directory -Force -Path $ProjectPath | Out-Null
Set-Location $ProjectPath

# Generate project based on target
switch ($Target) {
  "scripting" {
    # Create Python scripting project
    New-Item -ItemType Directory -Force -Path "scripts", "examples", "docs" | Out-Null
    
    # Main Python script
    @'
#!/usr/bin/env python3
"""
Basic DaVinci Resolve Scripting Example
This script demonstrates basic DaVinciResolveScript API usage.
"""

import sys
import os

def get_resolve():
    """Get DaVinci Resolve instance"""
    try:
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        return resolve
    except ImportError:
        print("❌ DaVinciResolveScript module not found")
        print("Make sure DaVinci Resolve is installed and Python API is available")
        return None
    except Exception as e:
        print(f"❌ Failed to connect to DaVinci Resolve: {e}")
        return None

def main():
    # Connect to DaVinci Resolve
    resolve = get_resolve()
    if not resolve:
        return False
    
    # Get project manager and current project
    project_manager = resolve.GetProjectManager()
    project = project_manager.GetCurrentProject()
    
    if not project:
        print("❌ No project open in DaVinci Resolve")
        return False
    
    print(f"✅ Connected to project: {project.GetName()}")
    
    # Get current timeline
    timeline = project.GetCurrentTimeline()
    if timeline:
        print(f"📽️  Current timeline: {timeline.GetName()}")
        
        # Add a marker at the playhead position
        current_frame = timeline.GetCurrentTimecode()
        marker_added = timeline.AddMarker(
            frameId=current_frame,
            color="Blue",
            name="Script Generated Marker",
            note="Added by DaVinci Resolve scripting example",
            duration=1
        )
        
        if marker_added:
            print(f"✅ Added marker at {current_frame}")
        else:
            print("⚠️  Could not add marker")
    else:
        print("⚠️  No timeline open")
    
    # Get media pool
    media_pool = project.GetMediaPool()
    print(f"📁 Media pool has {len(media_pool.GetRootFolder().GetClipList())} clips")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'@ | Out-File -FilePath "examples\basic_workflow.py" -Encoding UTF8
    
    # Build script (PowerShell version)
    @'
Write-Host "🔧 Setting up Python environment for DaVinci Resolve scripting..." -ForegroundColor Cyan

# Check Python version
python --version

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

Write-Host "✅ Environment ready!" -ForegroundColor Green
Write-Host "To run examples: python examples\basic_workflow.py" -ForegroundColor White
'@ | Out-File -FilePath "scripts\build.ps1" -Encoding UTF8
  }
  
  "fusion" {
    # Create Fusion Fuse project
    New-Item -ItemType Directory -Force -Path "Fuses", "scripts", "docs" | Out-Null
    
    # Basic Fuse template
    @'
--[[
BrightnessAdjust.fuse
A simple brightness adjustment Fuse for DaVinci Resolve Fusion

Copyright (c) 2025 - MIT License
]]--

FuRegisterClass("BrightnessAdjust", CT_Tool, {
    REGS_Name = "Brightness Adjust",
    REGS_Category = "Color",
    REGS_OpIconString = "BrA",
    REGS_OpDescription = "Simple brightness adjustment tool",
    REG_NoObjMatCtrls = true,
    REG_NoMotionBlurCtrls = true,
    REG_OpNoMask = true,
})

function Create()
    -- Input
    InImage = self:AddInput("Input", "Input", {
        LINKID_DataType = "Image",
        LINK_Main = 1,
    })
    
    -- Brightness control
    InBrightness = self:AddInput("Brightness", "Brightness", {
        LINKID_DataType = "Number",
        INPID_InputControl = "SliderControl",
        INP_Default = 1.0,
        INP_MinScale = 0.0,
        INP_MaxScale = 2.0,
    })
    
    -- Output
    OutImage = self:AddOutput("Output", "Output", {
        LINKID_DataType = "Image",
        LINK_Main = 1,
    })
end

function Process(req)
    local img = InImage:GetValue(req)
    local brightness = InBrightness:GetValue(req).Value
    
    if not img then
        return nil
    end
    
    -- Create output image
    local out = Image({IMG_Like = img})
    
    -- Simple brightness adjustment
    out:Fill(Pixel({R = brightness, G = brightness, B = brightness, A = 1.0}))
    out:MultiplyOf(img)
    
    OutImage:Set(req, out)
end
'@ | Out-File -FilePath "Fuses\BrightnessAdjust.fuse" -Encoding UTF8
    
    # Install script (PowerShell version)
    @'
Write-Host "🔧 Installing Fusion Fuse..." -ForegroundColor Cyan

# Detect platform and set Fuse directory
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $FuseDir = "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\Fuses"
} elseif ($IsMacOS) {
    $FuseDir = "$env:HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fuses"
} else {
    $FuseDir = "$env:HOME/.local/share/DaVinciResolve/Fuses"
}

# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $FuseDir | Out-Null

# Copy Fuse files
Copy-Item "Fuses\*.fuse" -Destination $FuseDir

Write-Host "✅ Fuse installed to: $FuseDir" -ForegroundColor Green
Write-Host "Restart DaVinci Resolve to see the new Fuse in the Effects Library" -ForegroundColor Yellow
'@ | Out-File -FilePath "scripts\install.ps1" -Encoding UTF8
  }
  
  "ofx" {
    # Create OpenFX plugin project
    New-Item -ItemType Directory -Force -Path "src", "include", "scripts", "docs" | Out-Null
    
    # CMakeLists.txt
    @'
cmake_minimum_required(VERSION 3.10)
project(ResolveOFXPlugin)

set(CMAKE_CXX_STANDARD 11)

# Find OpenFX headers (you'll need to download these separately)
find_path(OFX_INCLUDE_DIR ofxCore.h
    PATHS
    ${CMAKE_SOURCE_DIR}/OpenFX/include
    /usr/local/include/OpenFX
    /opt/OpenFX/include
)

if(NOT OFX_INCLUDE_DIR)
    message(FATAL_ERROR "OpenFX headers not found. Please download from https://github.com/ofxa/openFX")
endif()

include_directories(${OFX_INCLUDE_DIR})
include_directories(include)

# Plugin source
add_library(BasicColorCorrect SHARED
    src/BasicColorCorrect.cpp
)

# Platform-specific settings
if(WIN32)
    set_target_properties(BasicColorCorrect PROPERTIES SUFFIX ".ofx")
elseif(APPLE)
    set_target_properties(BasicColorCorrect PROPERTIES SUFFIX ".ofx")
    set_target_properties(BasicColorCorrect PROPERTIES BUNDLE TRUE)
else()
    set_target_properties(BasicColorCorrect PROPERTIES SUFFIX ".ofx")
endif()
'@ | Out-File -FilePath "CMakeLists.txt" -Encoding UTF8
    
    # Build script (PowerShell version)
    @'
Write-Host "🔧 Building OpenFX plugin..." -ForegroundColor Cyan

# Create build directory
New-Item -ItemType Directory -Force -Path "build" | Out-Null
Set-Location "build"

# Configure with CMake
cmake ..

# Build
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    cmake --build . --config Release
} else {
    make -j4
}

Write-Host "✅ Plugin built successfully!" -ForegroundColor Green
Write-Host "Install the .ofx file to your DaVinci Resolve OFX plugins directory" -ForegroundColor Yellow
'@ | Out-File -FilePath "scripts\build.ps1" -Encoding UTF8
  }
  
  "dctl" {
    # Create DCTL project
    New-Item -ItemType Directory -Force -Path "dctl", "scripts", "docs" | Out-Null
    
    # DCTL file
    @'
// ContrastAdjust.dctl
// Simple contrast adjustment DCTL for DaVinci Resolve
// Copyright (c) 2025 - MIT License

DEFINE_UI_PARAMS(contrast, Contrast, DCTLUI_SLIDER_FLOAT, 1.0, 0.0, 2.0, 0.01)
DEFINE_UI_PARAMS(pivot, Pivot, DCTLUI_SLIDER_FLOAT, 0.18, 0.0, 1.0, 0.01)

__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)
{
    // Apply contrast adjustment around pivot point
    float3 rgb = make_float3(p_R, p_G, p_B);
    
    // Subtract pivot, apply contrast, add pivot back
    rgb.x = (rgb.x - pivot) * contrast + pivot;
    rgb.y = (rgb.y - pivot) * contrast + pivot;
    rgb.z = (rgb.z - pivot) * contrast + pivot;
    
    // Clamp to valid range
    rgb.x = _clampf(rgb.x, 0.0f, 1.0f);
    rgb.y = _clampf(rgb.y, 0.0f, 1.0f);
    rgb.z = _clampf(rgb.z, 0.0f, 1.0f);
    
    return rgb;
}
'@ | Out-File -FilePath "dctl\ContrastAdjust.dctl" -Encoding UTF8
    
    # Install script (PowerShell version)
    @'
Write-Host "🔧 Installing DCTL..." -ForegroundColor Cyan

# Detect platform and set DCTL directory
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    $DctlDir = "$env:APPDATA\Blackmagic Design\DaVinci Resolve\Support\LUT"
} elseif ($IsMacOS) {
    $DctlDir = "$env:HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
} else {
    $DctlDir = "$env:HOME/.local/share/DaVinciResolve/LUT"
}

# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $DctlDir | Out-Null

# Copy DCTL files
Copy-Item "dctl\*.dctl" -Destination $DctlDir

Write-Host "✅ DCTL installed to: $DctlDir" -ForegroundColor Green
Write-Host "The DCTL will appear in the OpenFX panel in DaVinci Resolve" -ForegroundColor Yellow
'@ | Out-File -FilePath "scripts\install.ps1" -Encoding UTF8
  }
}

# Create common files for all project types
$readmeContent = @"
# $ProjectName

A starter project for DaVinci Resolve $Target development.

## Quick Start

### Prerequisites
- DaVinci Resolve installed
- Development tools for your platform

### Installation
1. Clone or download this project
2. Follow the setup instructions for your platform below
3. Run the build/install scripts
4. Test in DaVinci Resolve

### Platform Setup

#### Windows
- Visual Studio 2019 or later (for C++ projects)
- Python 3.7+ (for scripting projects)

#### macOS
- Xcode command line tools
- Python 3.7+ (for scripting projects)

#### Linux
- GCC 7+ or Clang 6+
- Python 3.7+ (for scripting projects)

### Building and Installing

#### Build (PowerShell)
``````powershell
cd scripts
.\build.ps1
``````

#### Install (PowerShell)
``````powershell
cd scripts
.\install.ps1
``````

#### Build (Bash)
``````bash
cd scripts
./build.sh
``````

## Project Structure
- ``examples/`` - Example code and usage
- ``scripts/`` - Build and installation scripts
- ``docs/`` - Documentation

## Development

### Customization
Modify the source files to implement your specific functionality.

### Testing
1. Build the project
2. Install to DaVinci Resolve
3. Test functionality in DaVinci Resolve

## Resources
- [DaVinci Resolve Scripting Documentation](https://documents.blackmagicdesign.com/DeveloperManuals/DaVinci_Resolve_18_Developer_Documentation.zip)
- [OpenFX Documentation](http://openeffects.org/)
- [DaVinci Resolve Training](https://www.blackmagicdesign.com/training)

## License
MIT License - see LICENSE file for details.
"@

$readmeContent | Out-File -FilePath "README.md" -Encoding UTF8

# Create .gitignore
@'
# Build artifacts
build/
dist/
*.o
*.obj
*.exe
*.dll
*.so
*.dylib
*.a
*.lib

# IDE files
.vscode/
.idea/
*.sublime-*

# OS files
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
*.pyo
venv/
env/

# Logs
*.log
'@ | Out-File -FilePath ".gitignore" -Encoding UTF8

# Create LICENSE
@'
MIT License

Copyright (c) 2025 DaVinci Resolve Extension

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'@ | Out-File -FilePath "LICENSE" -Encoding UTF8

Set-Location ..

Write-Host "✅ Generated: $ProjectPath" -ForegroundColor Green
Write-Host "📄 Next: cd `"$ProjectPath`" ; Get-Content README.md" -ForegroundColor White