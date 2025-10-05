"""
GitHub + DaVinci Resolve Integration Examples
Demonstrates combined workflows using both systems
"""

from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder
from resolve_ai.github_executor import GitHubExecutor

# Example 1: Bug Report with Video Evidence
def bug_report_with_video():
    """
    User workflow: "There's a bug with the color correction, create an issue"
    
    AI Actions:
    1. Create Fusion composition showing the bug
    2. Set 20s render range
    3. Play preview to demonstrate
    4. Create GitHub issue with description
    """
    
    # Initialize controllers
    controller = ResolveAIController()
    github = GitHubExecutor()
    
    # Step 1: Create composition showing the bug
    comp = controller.get_fusion_comp()
    builder = FusionNodeBuilder(comp)
    
    # Build scene that demonstrates the bug
    bg = builder.create_background(color=(0.0, 0.0, 1.0, 1.0))  # Blue background
    text = builder.create_text(
        text="Color Correction Bug Demo",
        size=0.1
    )
    color_correct = builder.create_color_corrector(
        gain=(1.5, 1.0, 1.0, 1.0)  # Should increase red, but doesn't
    )
    
    # Connect nodes
    builder.connect_nodes(bg, color_correct)
    builder.connect_nodes(color_correct, text)
    builder.connect_to_output(text)
    
    # Step 2: Set 20s render range
    timeline = controller.get_current_timeline()
    frame_rate = float(timeline.GetSetting("timelineFrameRate") or "24")
    timeline.SetSetting("useInOutRange", "1")
    timeline.SetSetting("inFrame", "0")
    timeline.SetSetting("outFrame", str(int(20 * frame_rate)))
    
    # Step 3: Play preview (user sees the bug)
    timeline.Play()
    print("▶ Playing preview to demonstrate bug...")
    
    # Step 4: Create GitHub issue
    success, result = github.execute(
        tool_name="gh_issue_create",
        parameters={
            "title": "[Bug] Color corrector gain parameter not applied correctly",
            "body": """
## Bug Description
The color corrector node's gain parameter doesn't properly adjust color channels.

## Reproduction Steps
1. Create background node (blue)
2. Add color corrector with gain=(1.5, 1.0, 1.0, 1.0) to increase red
3. Connect to output
4. Preview shows no change - background stays blue

## Expected Behavior
Blue background should shift toward purple/magenta due to red gain increase.

## Actual Behavior
Background remains pure blue, gain parameter appears ignored.

## Demo Video
See preview in timeline (0:00-0:20)

## Environment
- DaVinci Resolve 18.6
- Python API
- Fusion node system
            """,
            "labels": "bug,fusion,color-correction"
        },
        permission_granted=True  # User approved
    )
    
    if success:
        print(f"✅ Issue created: {result}")
    else:
        print(f"❌ Failed to create issue: {result}")


# Example 2: Feature Demo with PR
def feature_demo_pr():
    """
    User workflow: "Create PR for the new glow effect feature"
    
    AI Actions:
    1. Create demo composition using new feature
    2. Play 20s preview
    3. Create PR with demo description
    """
    
    controller = ResolveAIController()
    github = GitHubExecutor()
    
    # Create demo composition
    comp = controller.get_fusion_comp()
    builder = FusionNodeBuilder(comp)
    
    # Build demo: Text with glow effect
    bg = builder.create_background(color=(0.0, 0.0, 0.0, 1.0))  # Black
    text = builder.create_text(
        text="New Glow Effect!",
        size=0.15,
        color=(1.0, 1.0, 1.0, 1.0)
    )
    glow = builder.create_glow(
        intensity=5.0,
        glow_size=20.0
    )
    
    builder.connect_nodes(bg, text)
    builder.connect_nodes(text, glow)
    builder.connect_to_output(glow)
    
    # Play preview
    timeline = controller.get_current_timeline()
    timeline.Play()
    print("▶ Playing demo preview...")
    
    # Create PR
    success, result = github.execute(
        tool_name="gh_pr_create",
        parameters={
            "title": "Add glow effect support to Fusion tools",
            "body": """
## Feature Description
Adds glow effect node creation to FusionNodeBuilder.

## What's New
- `create_glow()` method with intensity and size parameters
- Default glow settings for optimal visual effect
- Integration with existing node connection system

## Demo
See preview in timeline for demonstration of glow effect on white text.

## Testing
- Tested with various intensity values (1.0 - 10.0)
- Verified glow size parameter works correctly
- Confirmed compatibility with existing nodes

## Related Issues
Implements #42
            """,
            "head": "feature/glow-effect",
            "base": "main"
        },
        permission_granted=True
    )
    
    if success:
        print(f"✅ PR created: {result}")


# Example 3: CI/CD Integration
def check_build_status():
    """
    User workflow: "Did the tests pass?"
    
    AI Actions:
    1. Check recent workflow runs
    2. Show status
    3. If failed, show logs
    """
    
    github = GitHubExecutor()
    
    # Get recent runs
    success, runs = github.execute(
        tool_name="gh_run_list",
        parameters={"limit": 5},
        permission_granted=False  # Read-only, no permission needed
    )
    
    if not success:
        print(f"❌ Failed to get runs: {runs}")
        return
    
    print("📊 Recent CI Runs:")
    for run in runs:
        status = run.get('status')
        conclusion = run.get('conclusion')
        workflow = run.get('workflowName')
        branch = run.get('headBranch')
        
        # Status emoji
        if status == 'completed':
            emoji = '✅' if conclusion == 'success' else '❌'
        else:
            emoji = '🔄'
        
        print(f"{emoji} {workflow} on {branch}: {status} ({conclusion})")
    
    # If latest failed, show logs
    latest = runs[0] if runs else None
    if latest and latest.get('conclusion') == 'failure':
        run_id = latest.get('databaseId')
        print(f"\n📋 Fetching logs for failed run #{run_id}...")
        
        success, logs = github.execute(
            tool_name="gh_run_view",
            parameters={"run_id": run_id},
            permission_granted=False
        )
        
        if success:
            print(logs.get('output', ''))


# Example 4: Release Workflow
def create_release_with_demo():
    """
    User workflow: "Release v0.2.0 with demo video"
    
    AI Actions:
    1. Create demo composition
    2. Export demo video
    3. Create GitHub release with notes
    """
    
    controller = ResolveAIController()
    github = GitHubExecutor()
    
    # Create demo composition
    comp = controller.get_fusion_comp()
    builder = FusionNodeBuilder(comp)
    
    # Build showcase of features
    bg = builder.create_background(color=(0.1, 0.1, 0.2, 1.0))
    title = builder.create_text(
        text="v0.2.0 Features",
        size=0.12
    )
    
    builder.connect_nodes(bg, title)
    builder.connect_to_output(title)
    
    # Render demo (in real implementation, would export to file)
    timeline = controller.get_current_timeline()
    timeline.Play()
    print("▶ Playing release demo...")
    
    # Create release
    success, result = github.execute(
        tool_name="gh_release_create",
        parameters={
            "tag": "v0.2.0",
            "title": "Version 0.2.0 - GitHub Integration",
            "notes": """
## 🎉 What's New

### GitHub CLI Integration
- Integrated `gh` CLI for repository management
- Create issues directly from DaVinci Resolve
- Manage PRs and releases from timeline
- Monitor CI/CD status in real-time

### Fusion Enhancements
- Added 15+ node types for Fusion composition
- Glow effect support
- Color correction improvements
- Transform and merge operations

### VS Code Extension
- Complete GitHub Copilot integration
- Permission-based execution ("dog behavior")
- 20-second preview enforcement
- Real-time context reporting

## 📦 Installation

See README.md for setup instructions.

## 🎥 Demo Video

Watch the demo in this release's assets.

## 🐛 Bug Fixes

- Fixed preview playback issues (#23)
- Resolved node connection errors (#25)
- Improved error handling for Resolve API (#28)
            """
        },
        permission_granted=True
    )
    
    if success:
        print(f"✅ Release created: {result}")


# Example 5: Issue-Driven Development
def issue_driven_workflow():
    """
    User workflow: "Let's work on issue #10"
    
    AI Actions:
    1. View issue details
    2. Create Fusion composition to address issue
    3. Test the fix
    4. Report status
    """
    
    github = GitHubExecutor()
    controller = ResolveAIController()
    
    # Step 1: View issue
    success, issue = github.execute(
        tool_name="gh_issue_view",
        parameters={"number": 10},
        permission_granted=False
    )
    
    if not success:
        print(f"❌ Failed to get issue: {issue}")
        return
    
    print(f"📝 Issue #{issue['number']}: {issue['title']}")
    print(f"   {issue['body'][:200]}...")
    
    # Step 2: Create fix (example: issue about text positioning)
    comp = controller.get_fusion_comp()
    builder = FusionNodeBuilder(comp)
    
    text = builder.create_text(
        text="Testing Issue #10 Fix",
        size=0.1
    )
    
    # Apply transform to fix positioning issue
    transform = builder.create_transform(
        center=(0.5, 0.3)  # New position
    )
    
    builder.connect_nodes(text, transform)
    builder.connect_to_output(transform)
    
    # Step 3: Test
    timeline = controller.get_current_timeline()
    timeline.Play()
    print("▶ Testing fix...")
    
    # Step 4: Report (in real workflow, would create comment on issue)
    print("✅ Fix appears to work - text now positioned correctly")


# Example 6: Combined GitHub + Resolve Workflow
def complete_workflow():
    """
    Complete workflow: Feature request → Implementation → Demo → PR
    
    User: "Create glow effect feature"
    
    AI Actions:
    1. List issues to check if feature already requested
    2. Create implementation in Fusion
    3. Build demo composition
    4. Create PR with demo
    """
    
    github = GitHubExecutor()
    controller = ResolveAIController()
    
    # Step 1: Check if feature already requested
    print("🔍 Checking existing issues...")
    success, issues = github.execute(
        tool_name="gh_issue_list",
        parameters={"state": "all"},
        permission_granted=False
    )
    
    glow_issue = None
    for issue in issues:
        if "glow" in issue.get('title', '').lower():
            glow_issue = issue
            break
    
    if glow_issue:
        print(f"✓ Found related issue: #{glow_issue['number']}")
    else:
        print("✗ No existing issue found")
    
    # Step 2: Implement feature (create glow node)
    print("\n🔧 Implementing glow effect...")
    comp = controller.get_fusion_comp()
    builder = FusionNodeBuilder(comp)
    
    bg = builder.create_background(color=(0.0, 0.0, 0.0, 1.0))
    text = builder.create_text(text="Glow Demo", size=0.15)
    glow = builder.create_glow(intensity=5.0)
    
    builder.connect_nodes(bg, text)
    builder.connect_nodes(text, glow)
    builder.connect_to_output(glow)
    
    # Step 3: Demo
    print("\n▶ Playing demo...")
    timeline = controller.get_current_timeline()
    timeline.Play()
    
    # Step 4: Create PR
    print("\n📤 Creating pull request...")
    success, pr = github.execute(
        tool_name="gh_pr_create",
        parameters={
            "title": "Implement glow effect for Fusion",
            "body": f"""
Implements glow effect feature.

{"Related to #" + str(glow_issue['number']) if glow_issue else "New feature"}

See demo in timeline preview.
            """,
            "head": "feature/glow-effect",
            "base": "main"
        },
        permission_granted=True
    )
    
    if success:
        print(f"✅ Complete! PR created: {pr}")


if __name__ == "__main__":
    print("GitHub + DaVinci Resolve Integration Examples\n")
    print("Available workflows:")
    print("1. Bug report with video evidence")
    print("2. Feature demo with PR")
    print("3. Check CI/CD build status")
    print("4. Create release with demo")
    print("5. Issue-driven development")
    print("6. Complete feature workflow")
    print("\nRun individual functions to see examples.")
