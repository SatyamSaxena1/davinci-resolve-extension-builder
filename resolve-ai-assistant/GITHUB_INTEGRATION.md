# GitHub CLI Integration Guide

## Overview

The Resolve AI Assistant now integrates with GitHub CLI (`gh`) to provide seamless repository management alongside DaVinci Resolve automation. This allows you to create issues, manage pull requests, monitor CI/CD, and handle releases - all from within your video editing workflow.

## Prerequisites

1. **Install GitHub CLI**:
   - Windows: `winget install --id GitHub.cli`
   - Or download from: https://cli.github.com/

2. **Authenticate**:
   ```bash
   gh auth login
   ```
   Follow the prompts to authenticate with your GitHub account.

3. **Verify Installation**:
   ```bash
   gh auth status
   ```
   Should show: "✓ Logged in to github.com as [your-username]"

## Available GitHub Commands

### Repository Information
- `gh_repo_info` - Get current repository details
- `gh_branch_list` - List all branches
- `gh_commit_list` - Show recent commits

### Issue Management
- `gh_issue_list` - List issues (open/closed/all)
- `gh_issue_create` - Create new issue
- `gh_issue_view` - View issue details

### Pull Requests
- `gh_pr_list` - List pull requests
- `gh_pr_create` - Create new pull request
- `gh_pr_view` - View PR details
- `gh_pr_checkout` - Checkout PR locally

### Workflows & CI/CD
- `gh_workflow_list` - List GitHub Actions workflows
- `gh_workflow_run` - Trigger workflow run
- `gh_run_list` - List recent workflow runs
- `gh_run_view` - View run logs

### Releases
- `gh_release_list` - List releases
- `gh_release_create` - Create new release

## Usage Examples

### Example 1: Bug Report with Video

**User**: "There's a bug where the preview doesn't play. Create an issue."

**AI Response**:
```
I'll create an issue for this bug.

Title: [Bug] Preview playback not working
Body: Preview doesn't play after creating Fusion nodes.

Steps to reproduce:
1. Create background node
2. Add text node
3. Run preview
4. Nothing happens

❓ Shall I create this issue?
```

**User**: "Yes"

**Result**:
```
✅ Issue #42 created successfully
URL: https://github.com/user/repo/issues/42
```

### Example 2: Feature Demo PR

**User**: "Create a PR for the glow effect feature"

**AI Response**:
```
I'll create a demo composition and open a PR.

Steps:
1. Create demo composition with glow effect
2. Play 20s preview
3. Create PR with demo description

❓ Proceed?
```

**User**: "Yes"

**Result**:
```
✓ Created demo composition
✓ Playing preview...
✓ Creating PR...

✅ PR #15 created successfully
Title: Add glow effect support
URL: https://github.com/user/repo/pull/15
```

### Example 3: CI/CD Status Check

**User**: "Did the tests pass?"

**AI Response**:
```
📊 Recent CI Runs:

✅ test-extension on main: completed (success)
✅ build on main: completed (success)
❌ test-python on feature/new-nodes: completed (failure)
🔄 deploy on main: in_progress

The latest run on your branch failed. Checking logs...

Error: fusion_tools.py:145 - TypeError: expected float, got str

Would you like me to fix this issue?
```

### Example 4: Combined Workflow

**User**: "Create lower-third with red text, then open a PR"

**AI Response**:
```
## 📋 Plan

→ **Step 1**: Create lower-third composition (red text)
□ **Step 2**: Preview composition (20s)
□ **Step 3**: Create PR with demo

❓ Shall I proceed with Step 1?
```

**User**: "Yes"

**Execution**:
```
✓ Create lower-third composition (red text)
✓ Preview composition (20s)
▶ Playing preview...

─────────────────────────────

❓ Continue with Step 3: Create PR with demo?
```

**User**: "Yes"

**Result**:
```
✓ Create PR with demo

PR Created:
Title: Add lower-third template with customizable colors
Body: Includes demo composition showing red text lower-third.

✅ All steps complete! 🎉
```

## Workflow Patterns

### Pattern 1: Issue-Driven Development

```
User: "Let's work on issue #10"
AI: [Views issue details]
AI: [Creates Fusion composition to fix issue]
AI: [Tests the fix with preview]
AI: [Reports status]
```

### Pattern 2: Feature with Demo

```
User: "Add glow effect and demo it"
AI: [Implements glow node creation]
AI: [Creates demo composition]
AI: [Plays 20s preview]
AI: [Opens PR with demo link]
```

### Pattern 3: Bug Report

```
User: "The text color is wrong, report it"
AI: [Shows current behavior in composition]
AI: [Captures screenshot/video]
AI: [Creates issue with reproduction steps]
```

### Pattern 4: Release Management

```
User: "Release v0.3.0"
AI: [Lists changes since last release]
AI: [Creates demo showcasing new features]
AI: [Generates release notes]
AI: [Creates GitHub release]
```

## GitHub + Resolve Integration

The power comes from combining both systems:

### Scenario 1: Visual Bug Reports
1. Create composition demonstrating bug
2. Set 20s render range
3. Play preview (user sees the issue)
4. Create GitHub issue with video evidence

### Scenario 2: Feature Demo PRs
1. Implement feature in Fusion
2. Build demo composition
3. Export demo video
4. Create PR with demo attached
5. Link related issues

### Scenario 3: CI/CD Integration
1. Make changes in Resolve automation
2. Run local tests (preview)
3. Commit changes
4. Trigger CI workflow
5. Monitor build status
6. Create release when tests pass

## Permission Model

GitHub commands follow the same "dog behavior" pattern:

- **Read-only commands** (list, view): No permission needed
- **Write commands** (create issue/PR): Requires approval
- **Destructive commands** (close, merge, delete): Explicit confirmation

Example:
```
AI: "I'll create an issue for this bug. Shall I proceed?"
User: "Yes"
AI: ✅ [Creates issue]

AI: "I'll merge this PR. This is permanent. Confirm?"
User: "Merge it"
AI: ✅ [Merges PR]
```

## Configuration

Add to `.vscode/settings.json`:

```json
{
  "resolve.github.enabled": true,
  "resolve.github.requirePermission": true,
  "resolve.github.autoLinkIssues": true
}
```

## Safety Features

1. **Authentication Check**: Verifies `gh auth status` before execution
2. **Permission Guards**: Asks before modifying data
3. **Read-only by Default**: Most commands are safe queries
4. **Explicit Confirmation**: Destructive operations require clear approval
5. **Error Handling**: Graceful failure with helpful messages

## Troubleshooting

### "GitHub CLI not found"
**Solution**: Install from https://cli.github.com/ and restart VS Code

### "Not authenticated"
**Solution**: Run `gh auth login` in terminal

### "Permission denied"
**Solution**: Check repository access rights on GitHub

### "Command timeout"
**Solution**: Check network connection and GitHub status

## Advanced Usage

### Custom Workflows

You can chain operations:

```
User: "Create glow effect, test it, open issue if broken, or PR if working"

AI: [Creates glow implementation]
AI: [Tests with preview]
AI: [Evaluates results]
AI: [Opens PR] ✅ (if working)
OR
AI: [Opens issue] ❌ (if broken)
```

### Integration with Existing Tools

Works alongside VS Code's GitHub integration:
- Use `@resolve` for automated workflows
- Use GitHub web UI for manual review
- Use GitHub CLI directly when needed
- All tools see the same data

## Best Practices

1. **Always preview before creating PR** - Shows working feature
2. **Link issues in PR descriptions** - Use "Implements #42" syntax
3. **Use descriptive titles** - Makes issues/PRs searchable
4. **Tag appropriately** - Add labels for bug, enhancement, etc.
5. **Include reproduction steps** - Especially for bugs
6. **Demo with video** - 20s preview is perfect for showcasing

## Examples in Code

See `examples/github_resolve_workflows.py` for complete Python examples:
- Bug report with video evidence
- Feature demo with PR
- CI/CD status checking
- Release workflow
- Issue-driven development
- Complete integrated workflows

## Integration Architecture

```
User Query (@resolve chat)
        ↓
Chat Participant (TypeScript)
        ↓
    [Detects GitHub keywords]
        ↓
Python Bridge (child_process)
        ↓
vscode_bridge.py (command router)
        ↓
github_executor.py (safety checks)
        ↓
GitHub CLI (gh command)
        ↓
GitHub API
```

Parallel to:

```
User Query (@resolve chat)
        ↓
Chat Participant (TypeScript)
        ↓
    [Detects Resolve keywords]
        ↓
Python Bridge (child_process)
        ↓
vscode_bridge.py (command router)
        ↓
controller.py / fusion_tools.py
        ↓
DaVinci Resolve API
```

Both systems available in same conversation!

## Next Steps

1. **Install GitHub CLI**: `winget install --id GitHub.cli`
2. **Authenticate**: `gh auth login`
3. **Try simple command**: "@resolve list issues"
4. **Create workflow**: "@resolve create glow effect and open PR"
5. **Explore patterns**: See `examples/github_resolve_workflows.py`

## Resources

- GitHub CLI Docs: https://cli.github.com/manual/
- GitHub API: https://docs.github.com/rest
- Project README: `README.md`
- Python Examples: `examples/github_resolve_workflows.py`
- Tool Definitions: `src/resolve_ai/github_tools.py`

---

**Remember**: GitHub CLI integration gives your AI assistant "practical intelligence" about your development workflow, making it a true end-to-end automation companion!
