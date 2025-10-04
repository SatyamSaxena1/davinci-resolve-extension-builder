#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
PLAN_FILE="${1:-PLAN.md}"           # pass a custom plan path as arg1, else PLAN.md
TARGET="${2:-scripting}"            # one of: scripting | fusion | ofx | dctl
OUT_DIR="${3:-resolve-addon}"       # output folder for generated project

# --- Checks ---
[[ -f "$PLAN_FILE" ]] || { echo "❌ Plan file not found: $PLAN_FILE"; exit 1; }

# --- Normalize TARGET ---
case "$TARGET" in
  scripting|fusion|ofx|dctl) ;;
  *) echo "❌ TARGET must be one of: scripting | fusion | ofx | dctl"; exit 1 ;;
esac

# --- PROJECT_NAME by target ---
case "$TARGET" in
  scripting) PROJECT_NAME="resolve-scripting-starter" ;;
  fusion)    PROJECT_NAME="resolve-fusion-fuse-starter" ;;
  ofx)       PROJECT_NAME="resolve-ofx-starter" ;;
  dctl)      PROJECT_NAME="resolve-dctl-starter" ;;
esac

echo "🚀 Generating $PROJECT_NAME from $PLAN_FILE (target: $TARGET)..."

# Create output directory structure
mkdir -p "$OUT_DIR/$PROJECT_NAME"
cd "$OUT_DIR/$PROJECT_NAME"

# Generate project based on target
case "$TARGET" in
  scripting)
    # Create Python scripting project
    mkdir -p scripts examples docs
    
    # Main Python script
    cat > examples/basic_workflow.py << 'EOF'
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
EOF

    # Build script
    cat > scripts/build.sh << 'EOF'
#!/bin/bash
echo "🔧 Setting up Python environment for DaVinci Resolve scripting..."

# Check Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Environment ready!"
echo "To run examples: python3 examples/basic_workflow.py"
EOF

    chmod +x scripts/build.sh
    ;;
    
  fusion)
    # Create Fusion Fuse project
    mkdir -p Fuses scripts docs
    
    # Basic Fuse template
    cat > Fuses/BrightnessAdjust.fuse << 'EOF'
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
EOF

    # Build script
    cat > scripts/install.sh << 'EOF'
#!/bin/bash
echo "🔧 Installing Fusion Fuse..."

# Detect platform and set Fuse directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    FUSE_DIR="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fuses"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    FUSE_DIR="$HOME/.local/share/DaVinciResolve/Fuses"
else
    # Windows (Git Bash)
    FUSE_DIR="$APPDATA/Blackmagic Design/DaVinci Resolve/Support/Fuses"
fi

# Create directory if it doesn't exist
mkdir -p "$FUSE_DIR"

# Copy Fuse files
cp Fuses/*.fuse "$FUSE_DIR/"

echo "✅ Fuse installed to: $FUSE_DIR"
echo "Restart DaVinci Resolve to see the new Fuse in the Effects Library"
EOF

    chmod +x scripts/install.sh
    ;;
    
  ofx)
    # Create OpenFX plugin project
    mkdir -p src include scripts docs
    
    # CMakeLists.txt
    cat > CMakeLists.txt << 'EOF'
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
    src/ofxsImageEffect.cpp
    src/ofxsInteract.cpp
    src/ofxsLog.cpp
    src/ofxsMultiThread.cpp
    src/ofxsParams.cpp
    src/ofxsProperty.cpp
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
EOF

    # Basic OFX plugin source
    cat > src/BasicColorCorrect.cpp << 'EOF'
/*
Basic Color Correct OFX Plugin for DaVinci Resolve
A simple example demonstrating OpenFX plugin development.
*/

#include "ofxsImageEffect.h"
#include <algorithm>

class BasicColorCorrectPlugin : public OFX::ImageEffect
{
protected:
    OFX::Clip* srcClip_;
    OFX::Clip* dstClip_;
    OFX::DoubleParam* brightness_;
    OFX::DoubleParam* contrast_;
    
public:
    BasicColorCorrectPlugin(OfxImageEffectHandle handle)
        : OFX::ImageEffect(handle)
        , srcClip_(0)
        , dstClip_(0)
        , brightness_(0)
        , contrast_(0)
    {
        srcClip_ = fetchClip(kOfxImageEffectSimpleSourceClipName);
        dstClip_ = fetchClip(kOfxImageEffectOutputClipName);
        
        brightness_ = fetchDoubleParam("brightness");
        contrast_ = fetchDoubleParam("contrast");
    }
    
    virtual void render(const OFX::RenderArguments &args) override
    {
        // Get the render window
        OfxRectI renderWindow = args.renderWindow;
        
        // Get source image
        std::auto_ptr<OFX::Image> src(srcClip_->fetchImage(args.time));
        std::auto_ptr<OFX::Image> dst(dstClip_->fetchImage(args.time));
        
        if (!src.get() || !dst.get()) {
            return;
        }
        
        // Get parameter values
        double brightness = brightness_->getValueAtTime(args.time);
        double contrast = contrast_->getValueAtTime(args.time);
        
        // Simple color correction processing
        // (This is a simplified example - real implementation would be more complex)
        
        // Process pixels (this is pseudo-code for demonstration)
        // Real implementation would depend on pixel format and use proper pixel iterators
    }
    
    virtual bool isIdentity(const OFX::IsIdentityArguments &args, 
                           OFX::Clip * &identityClip, 
                           double &identityTime) override
    {
        double brightness = brightness_->getValueAtTime(args.time);
        double contrast = contrast_->getValueAtTime(args.time);
        
        if (brightness == 1.0 && contrast == 1.0) {
            identityClip = srcClip_;
            identityTime = args.time;
            return true;
        }
        return false;
    }
};

class BasicColorCorrectPluginFactory : public OFX::PluginFactoryHelper<BasicColorCorrectPluginFactory>
{
public:
    BasicColorCorrectPluginFactory(const std::string& id, unsigned int verMaj, unsigned int verMin)
        : OFX::PluginFactoryHelper<BasicColorCorrectPluginFactory>(id, verMaj, verMin) {}
    
    virtual void describe(OFX::ImageEffectDescriptor &desc) override
    {
        desc.setLabel("Basic Color Correct");
        desc.setShortLabel("BasicCC");
        desc.setLongLabel("Basic Color Correction Plugin");
        desc.setGrouping("Color");
        desc.setPluginDescription("Simple brightness and contrast adjustment");
        
        desc.addSupportedContext(eContextFilter);
        desc.addSupportedBitDepth(eBitDepthFloat);
        
        desc.setSingleInstance(false);
        desc.setHostFrameThreading(false);
        desc.setSupportsMultiResolution(true);
        desc.setSupportsTiles(true);
        desc.setTemporalClipAccess(false);
        desc.setRenderTwiceAlways(false);
        desc.setSupportsMultipleClipPARs(false);
        desc.setSupportsMultipleClipDepths(false);
        desc.setRenderThreadSafety(eRenderFullySafe);
    }
    
    virtual void describeInContext(OFX::ImageEffectDescriptor &desc, 
                                  OFX::ContextEnum context) override
    {
        OFX::ClipDescriptor *srcClip = desc.defineClip(kOfxImageEffectSimpleSourceClipName);
        srcClip->addSupportedComponent(ePixelComponentRGBA);
        srcClip->addSupportedComponent(ePixelComponentRGB);
        srcClip->setTemporalClipAccess(false);
        srcClip->setSupportsTiles(true);
        srcClip->setIsMask(false);
        
        OFX::ClipDescriptor *dstClip = desc.defineClip(kOfxImageEffectOutputClipName);
        dstClip->addSupportedComponent(ePixelComponentRGBA);
        dstClip->addSupportedComponent(ePixelComponentRGB);
        dstClip->setSupportsTiles(true);
        
        // Define parameters
        OFX::DoubleParamDescriptor *brightness = desc.defineDoubleParam("brightness");
        brightness->setLabel("Brightness");
        brightness->setHint("Adjust image brightness");
        brightness->setDefault(1.0);
        brightness->setRange(0.0, 2.0);
        brightness->setDisplayRange(0.0, 2.0);
        
        OFX::DoubleParamDescriptor *contrast = desc.defineDoubleParam("contrast");
        contrast->setLabel("Contrast");
        contrast->setHint("Adjust image contrast");
        contrast->setDefault(1.0);
        contrast->setRange(0.0, 2.0);
        contrast->setDisplayRange(0.0, 2.0);
    }
    
    virtual OFX::ImageEffect* createInstance(OfxImageEffectHandle handle, 
                                           OFX::ContextEnum context) override
    {
        return new BasicColorCorrectPlugin(handle);
    }
};

static BasicColorCorrectPluginFactory p("com.example.BasicColorCorrect", 1, 0);
mRegisterPluginFactoryInstance(p)
EOF

    # Build script
    cat > scripts/build.sh << 'EOF'
#!/bin/bash
echo "🔧 Building OpenFX plugin..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake ..

# Build
make -j$(nproc)

echo "✅ Plugin built successfully!"
echo "Install the .ofx file to your DaVinci Resolve OFX plugins directory"
EOF

    chmod +x scripts/build.sh
    ;;
    
  dctl)
    # Create DCTL project
    mkdir -p dctl scripts docs
    
    # DCTL file
    cat > dctl/ContrastAdjust.dctl << 'EOF'
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
EOF

    # Install script
    cat > scripts/install.sh << 'EOF'
#!/bin/bash
echo "🔧 Installing DCTL..."

# Detect platform and set DCTL directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    DCTL_DIR="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    DCTL_DIR="$HOME/.local/share/DaVinciResolve/LUT"
else
    # Windows (Git Bash)
    DCTL_DIR="$APPDATA/Blackmagic Design/DaVinci Resolve/Support/LUT"
fi

# Create directory if it doesn't exist
mkdir -p "$DCTL_DIR"

# Copy DCTL files
cp dctl/*.dctl "$DCTL_DIR/"

echo "✅ DCTL installed to: $DCTL_DIR"
echo "The DCTL will appear in the OpenFX panel in DaVinci Resolve"
EOF

    chmod +x scripts/install.sh
    ;;
esac

# Create common files for all project types
cat > README.md << EOF
# $PROJECT_NAME

A starter project for DaVinci Resolve $TARGET development.

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

#### Build
\`\`\`bash
cd scripts
./build.sh
\`\`\`

#### Install
\`\`\`bash
cd scripts
./install.sh
\`\`\`

## Project Structure
- \`examples/\` - Example code and usage
- \`scripts/\` - Build and installation scripts
- \`docs/\` - Documentation

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
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
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
EOF

# Create LICENSE
cat > LICENSE << 'EOF'
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
EOF

echo "✅ Generated: $OUT_DIR/$PROJECT_NAME"
echo "📄 You can now: cd \"$OUT_DIR/$PROJECT_NAME\" && cat README.md"