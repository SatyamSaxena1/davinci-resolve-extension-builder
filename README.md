# DaVinci Resolve Extension Builder

A powerful toolkit for generating starter projects for DaVinci Resolve extension development across multiple platforms and development paths.

## Overview

This project provides automated scaffolding tools to kickstart development of:
- **Scripting Extensions** (Python) - Automate workflows using DaVinciResolveScript API
- **Fusion Effects** (Lua) - Create custom visual effects and tools for Fusion
- **OpenFX Plugins** (C++) - Develop industry-standard visual effects plugins
- **DCTL Color Transforms** - Build custom color grading and transformation effects

## Prerequisites

- Bash shell (Linux/macOS) or PowerShell (Windows)
- DaVinci Resolve (for testing generated extensions)
- Development tools for your platform (Python, C++ compiler, etc.)

## Quick Start

### Linux/macOS

```bash
# Generate a Python scripting extension
./generate-resolve-addon.sh PLAN.md scripting my-scripting-project

# Generate a Fusion effect
./generate-resolve-addon.sh PLAN.md fusion my-fusion-effect

# Generate an OpenFX plugin
./generate-resolve-addon.sh PLAN.md ofx my-ofx-plugin

# Generate a DCTL color transform
./generate-resolve-addon.sh PLAN.md dctl my-dctl-transform
```

### Windows (PowerShell)

```powershell
# Generate a Python scripting extension
.\generate-resolve-addon.ps1 -PlanFile "PLAN.md" -Target "scripting" -OutDir "my-scripting-project"

# Generate a Fusion effect
.\generate-resolve-addon.ps1 -Target "fusion" -OutDir "my-fusion-effect"

# Generate an OpenFX plugin
.\generate-resolve-addon.ps1 -Target "ofx" -OutDir "my-ofx-plugin"

# Generate a DCTL color transform
.\generate-resolve-addon.ps1 -Target "dctl" -OutDir "my-dctl-transform"
```

## Script Parameters

### Linux/macOS Script (`generate-resolve-addon.sh`)

```bash
./generate-resolve-addon.sh [PLAN_FILE] [TARGET] [OUT_DIR]
```

- `PLAN_FILE`: Path to plan markdown file (default: `PLAN.md`)
- `TARGET`: Extension type - `scripting`, `fusion`, `ofx`, or `dctl` (default: `scripting`)
- `OUT_DIR`: Output directory for generated project (default: `resolve-addon`)

### Windows Script (`generate-resolve-addon.ps1`)

```powershell
.\generate-resolve-addon.ps1 [-PlanFile <path>] [-Target <type>] [-OutDir <dir>]
```

- `-PlanFile`: Path to plan markdown file (default: `PLAN.md`)
- `-Target`: Extension type - `scripting`, `fusion`, `ofx`, or `dctl` (default: `scripting`)
- `-OutDir`: Output directory for generated project (default: `resolve-addon`)

## Extension Types

### Scripting Extensions (Python)
- Uses DaVinciResolveScript API
- Perfect for workflow automation, batch processing, and project management
- Generated projects include examples for timeline manipulation, media import, and rendering

### Fusion Effects (Lua)
- Create custom Fusion nodes and effects
- Includes parameter controls and GPU acceleration support
- Examples cover filters, generators, and modifiers

### OpenFX Plugins (C++)
- Industry-standard plugin format
- Cross-platform compatibility
- Includes CMake build system and basic effect templates

### DCTL Color Transforms
- GPU-optimized color processing
- Real-time parameter controls
- Perfect for custom color grading tools and artistic effects

## Generated Project Structure

Each generated project includes:
- **README.md** - Comprehensive setup and usage instructions
- **Source code** - Working example implementation
- **Build scripts** - Platform-specific build automation
- **Installation tools** - Helper scripts for deployment
- **.gitignore** - Appropriate ignore patterns
- **LICENSE** - MIT license template
- **Platform notes** - Windows/macOS/Linux specific guidance

## Customizing the Plan

Modify `PLAN.md` to customize the generated projects:
- Add specific requirements for your use case
- Include additional features or constraints
- Specify particular APIs or frameworks to use

## Troubleshooting

### Build Issues
- Ensure you have the required development tools for your platform
- Check that DaVinci Resolve is properly installed
- Verify file paths and permissions

### Installation Issues
- Make sure DaVinci Resolve is closed when installing extensions
- Check that the target directories exist and are writable
- Verify that extensions are being installed to the correct locations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different extension types
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- Check the generated project's README for specific setup instructions
- Review DaVinci Resolve documentation for API details
- Submit issues for bugs or feature requests

## Examples

After generation, each project contains working examples:
- **Scripting**: Add timeline markers, import clips, configure render settings
- **Fusion**: Brightness adjustment effect with parameter controls
- **OpenFX**: Basic color correction plugin with render pipeline
- **DCTL**: Contrast adjustment with real-time parameter control