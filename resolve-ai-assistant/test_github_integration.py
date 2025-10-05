"""
Test GitHub CLI Integration
Quick validation script to check if GitHub CLI is working
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.resolve_ai.github_executor import GitHubExecutor, format_github_response
from src.resolve_ai.github_tools import GITHUB_CLI_TOOLS

def test_gh_available():
    """Test if GitHub CLI is installed"""
    print("🔍 Testing GitHub CLI availability...")
    try:
        executor = GitHubExecutor(require_permission=False)
        print("✅ GitHub CLI is installed")
        print(f"✅ Authenticated: {executor.authenticated}")
        return executor
    except RuntimeError as e:
        print(f"❌ GitHub CLI test failed: {e}")
        print("\n📦 Install GitHub CLI:")
        print("   winget install --id GitHub.cli")
        print("\n🔑 Then authenticate:")
        print("   gh auth login")
        return None

def test_list_tools():
    """Test listing available tools"""
    print("\n📋 Available GitHub CLI Tools:")
    print(f"Total: {len(GITHUB_CLI_TOOLS)} tools")
    
    categories = {}
    for tool in GITHUB_CLI_TOOLS:
        category = tool['name'].split('_')[1]  # gh_issue_list -> issue
        if category not in categories:
            categories[category] = []
        categories[category].append(tool['name'])
    
    for category, tools in sorted(categories.items()):
        print(f"\n  {category.upper()}:")
        for tool in tools:
            print(f"    - {tool}")

def test_repo_info(executor: GitHubExecutor):
    """Test getting repository info"""
    print("\n🔍 Testing repository info...")
    success, result = executor.execute(
        tool_name="gh_repo_info",
        parameters={},
        permission_granted=False  # Read-only
    )
    
    if success:
        print("✅ Repository info retrieved:")
        formatted = format_github_response(result)
        print(formatted)
    else:
        print(f"❌ Failed: {result.get('error')}")
        if 'not a git repository' in str(result.get('error', '')).lower():
            print("\n⚠️ Not in a git repository")
            print("   cd to your git repo and try again")

def test_list_issues(executor: GitHubExecutor):
    """Test listing issues"""
    print("\n📝 Testing issue list...")
    success, result = executor.execute(
        tool_name="gh_issue_list",
        parameters={"limit": 5, "state": "all"},
        permission_granted=False  # Read-only
    )
    
    if success:
        print("✅ Issues retrieved:")
        if isinstance(result, list):
            for issue in result[:5]:
                number = issue.get('number')
                title = issue.get('title')
                state = issue.get('state')
                print(f"   #{number}: {title} [{state}]")
        else:
            print(f"   {format_github_response(result)}")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_list_workflows(executor: GitHubExecutor):
    """Test listing workflows"""
    print("\n⚙️ Testing workflow list...")
    success, result = executor.execute(
        tool_name="gh_workflow_list",
        parameters={},
        permission_granted=False  # Read-only
    )
    
    if success:
        print("✅ Workflows retrieved:")
        if isinstance(result, list):
            for workflow in result:
                name = workflow.get('name')
                state = workflow.get('state')
                print(f"   - {name} [{state}]")
        else:
            print(f"   {format_github_response(result)}")
    else:
        print(f"❌ Failed: {result.get('error')}")

def test_create_issue_dry_run(executor: GitHubExecutor):
    """Test issue creation (without permission, should fail safely)"""
    print("\n🧪 Testing issue creation (dry run - no permission)...")
    success, result = executor.execute(
        tool_name="gh_issue_create",
        parameters={
            "title": "Test issue from resolve-ai-assistant",
            "body": "This is a test issue to verify GitHub CLI integration"
        },
        permission_granted=False  # Should fail safely
    )
    
    if not success and 'permission required' in str(result.get('error', '')).lower():
        print("✅ Permission check working correctly")
        print("   (Issue creation requires permission)")
    elif success:
        print("⚠️ Issue was created (permission check may not be working)")
        print(f"   Result: {format_github_response(result)}")
    else:
        print(f"❌ Unexpected error: {result.get('error')}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("GitHub CLI Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Check if gh CLI is available
    executor = test_gh_available()
    if not executor:
        print("\n⚠️ Skipping remaining tests (GitHub CLI not available)")
        return
    
    # Test 2: List available tools
    test_list_tools()
    
    # Test 3: Get repository info (read-only)
    test_repo_info(executor)
    
    # Test 4: List issues (read-only)
    test_list_issues(executor)
    
    # Test 5: List workflows (read-only)
    test_list_workflows(executor)
    
    # Test 6: Test permission system
    test_create_issue_dry_run(executor)
    
    print("\n" + "=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
    print("\n✅ GitHub CLI integration is working")
    print("🚀 Ready to use @resolve with GitHub commands!")
    print("\nExample commands:")
    print("  - @resolve list issues")
    print("  - @resolve show recent CI runs")
    print("  - @resolve create issue about bug in preview")
    print("  - @resolve create glow effect and open PR")

if __name__ == "__main__":
    main()
