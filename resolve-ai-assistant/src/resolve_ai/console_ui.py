"""
DaVinci Resolve AI Assistant - Console UI

Rich-formatted console interface for interacting with the AI assistant.
Displays Copilot analysis, task routing, execution progress, and results.
"""

import sys
from typing import Optional, List
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box

from .assistant import ResolveAssistant, AssistantState, IterationResult


class ConsoleUI:
    """
    Rich console interface for DaVinci Resolve AI Assistant
    
    Features:
    - Natural language input prompt
    - Real-time status display
    - Task routing visualization
    - Execution progress tracking
    - Result summaries with timing
    """
    
    def __init__(self, assistant: ResolveAssistant):
        """
        Initialize console UI
        
        Args:
            assistant: ResolveAssistant instance
        """
        self.assistant = assistant
        self.console = Console()
        self.history: List[IterationResult] = []
    
    def display_welcome(self):
        """Display welcome banner and system status"""
        welcome_text = """
# 🎬 DaVinci Resolve AI Assistant

**Natural Language Control** • **Fusion Automation** • **AI Generation**

Powered by:
- GitHub Copilot CLI for AI assistance
- DaVinci Resolve Python API for Fusion control
- ComfyUI + Wan 2.2 for AI-generated graphics
        """
        
        self.console.print(Panel(
            Markdown(welcome_text),
            border_style="cyan",
            box=box.DOUBLE
        ))
        
        # Display system status
        self.display_status()
    
    def display_status(self):
        """Display current system status"""
        status = self.assistant.get_status()
        
        table = Table(title="System Status", box=box.ROUNDED, show_header=False)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        
        # DaVinci Resolve connection
        resolve_status = "✓ Connected" if status['resolve_connected'] else "✗ Disconnected"
        resolve_color = "green" if status['resolve_connected'] else "red"
        table.add_row("DaVinci Resolve", f"[{resolve_color}]{resolve_status}[/]")
        
        # Fusion composition
        fusion_status = "✓ Available" if status['fusion_available'] else "✗ Not Available"
        fusion_color = "green" if status['fusion_available'] else "yellow"
        table.add_row("Fusion Composition", f"[{fusion_color}]{fusion_status}[/]")
        
        # ComfyUI connection
        comfyui_status = "✓ Connected" if status['comfyui_available'] else "✗ Disconnected"
        comfyui_color = "green" if status['comfyui_available'] else "red"
        table.add_row("ComfyUI Server", f"[{comfyui_color}]{comfyui_status}[/]")
        
        # Copilot CLI
        copilot_status = "✓ Available" if status['copilot_available'] else "✗ Not Available"
        copilot_color = "green" if status['copilot_available'] else "red"
        table.add_row("GitHub Copilot CLI", f"[{copilot_color}]{copilot_status}[/]")
        
        # Iteration limit
        table.add_row("Iteration Limit", f"[blue]{status['iteration_limit']}s[/]")
        
        self.console.print(table)
        self.console.print()
    
    def get_user_input(self) -> Optional[str]:
        """
        Get natural language input from user
        
        Returns:
            User input string or None if exit command
        """
        try:
            user_input = Prompt.ask(
                "\n[bold cyan]What would you like to create?[/]",
                default=""
            ).strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q', 'bye']:
                return None
            
            # Check for special commands
            if user_input.lower() == 'status':
                self.display_status()
                return ""
            
            if user_input.lower() == 'clear':
                self.console.clear()
                self.display_welcome()
                return ""
            
            if user_input.lower() == 'history':
                self.display_history()
                return ""
            
            if user_input.lower() == 'help':
                self.display_help()
                return ""
            
            return user_input if user_input else ""
            
        except (KeyboardInterrupt, EOFError):
            return None
    
    def process_with_progress(self, user_input: str) -> IterationResult:
        """
        Process user input with progress display
        
        Args:
            user_input: Natural language command
            
        Returns:
            IterationResult
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            # Create progress tasks
            task = progress.add_task("[cyan]Processing request...", total=4)
            
            # Analyzing
            progress.update(task, description="[cyan]Analyzing with Copilot CLI...")
            progress.advance(task)
            
            # Routing
            progress.update(task, description="[yellow]Routing task...")
            progress.advance(task)
            
            # Executing
            progress.update(task, description="[green]Executing...")
            progress.advance(task)
            
            # Actually process the request
            result = self.assistant.process_request(user_input)
            
            # Complete
            progress.update(task, description="[bold green]Complete!")
            progress.advance(task)
        
        return result
    
    def display_result(self, result: IterationResult):
        """
        Display execution result
        
        Args:
            result: IterationResult to display
        """
        # Determine panel style based on success
        if result.success:
            border_style = "green"
            title = "✓ Success"
        else:
            border_style = "red"
            title = "✗ Error"
        
        # Build result content
        content = Text()
        content.append(f"{result.message}\n\n", style="bold")
        content.append(f"Duration: {result.duration:.2f}s", style="cyan")
        
        # Add timing warning if over limit
        if result.duration > self.assistant.iteration_limit:
            content.append(f" ⚠️ Over {self.assistant.iteration_limit}s limit!", style="yellow bold")
        
        content.append("\n")
        
        # Show created nodes
        if result.nodes_created:
            content.append(f"\nFusion Nodes Created: {len(result.nodes_created)}\n", style="blue bold")
            for node in result.nodes_created:
                content.append(f"  • {node}\n", style="blue")
        
        # Show generated images
        if result.images_generated:
            content.append(f"\nAI Images Generated: {len(result.images_generated)}\n", style="magenta bold")
            for img in result.images_generated:
                content.append(f"  • {img}\n", style="magenta")
        
        # Show error if any
        if result.error:
            content.append(f"\nError Details:\n", style="red bold")
            content.append(f"{result.error}\n", style="red")
        
        self.console.print(Panel(
            content,
            title=title,
            border_style=border_style,
            box=box.ROUNDED
        ))
    
    def display_history(self):
        """Display execution history"""
        if not self.history:
            self.console.print("[yellow]No history yet[/]")
            return
        
        table = Table(title="Execution History", box=box.ROUNDED)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Status", style="bold", width=8)
        table.add_column("Duration", style="blue", width=10)
        table.add_column("Message", style="white")
        
        for i, result in enumerate(self.history[-10:], 1):  # Last 10 results
            status = "✓" if result.success else "✗"
            status_color = "green" if result.success else "red"
            duration = f"{result.duration:.2f}s"
            
            table.add_row(
                str(i),
                f"[{status_color}]{status}[/]",
                duration,
                result.message[:50] + "..." if len(result.message) > 50 else result.message
            )
        
        self.console.print(table)
    
    def display_help(self):
        """Display help information"""
        help_text = """
# Commands

**Natural Language**: Type what you want to create
- "Create a red background with white text"
- "Generate a fantasy dragon scene"
- "Add a blue glow to the text"

**Special Commands**:
- `status` - Show system status
- `clear` - Clear console
- `history` - Show execution history
- `help` - Show this help
- `exit` or `quit` - Exit assistant

# Examples

**Fusion Tasks** (instant execution):
- "Create a blue background"
- "Add text that says Welcome in red"
- "Add a glow effect to the last node"

**ComfyUI Tasks** (AI generation ~10-15s):
- "Generate a cyberpunk cityscape"
- "Create a fantasy character portrait"
- "Generate a nebula background"

**Hybrid Tasks** (combination):
- "Create a title card with AI-generated space background"
- "Generate dragon and composite with text overlay"
        """
        
        self.console.print(Panel(
            Markdown(help_text),
            title="Help",
            border_style="blue",
            box=box.ROUNDED
        ))
    
    def run(self):
        """
        Main UI loop
        
        Continuously prompts for input and processes requests until exit
        """
        self.console.clear()
        self.display_welcome()
        
        self.console.print("\n[dim]Type 'help' for commands, 'exit' to quit[/]\n")
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                # Check for exit
                if user_input is None:
                    self.console.print("\n[cyan]Goodbye! 👋[/]\n")
                    break
                
                # Skip empty input or special commands already handled
                if not user_input:
                    continue
                
                # Process request with progress display
                result = self.process_with_progress(user_input)
                
                # Store in history
                self.history.append(result)
                
                # Display result
                self.display_result(result)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/]")
                continue
            
            except Exception as e:
                self.console.print(f"\n[red]Unexpected error: {e}[/]")
                continue


def launch_console_ui(comfyui_url: str = "http://localhost:8188"):
    """
    Launch the console UI
    
    Args:
        comfyui_url: URL of ComfyUI server
    """
    try:
        # Create assistant
        assistant = ResolveAssistant(comfyui_url=comfyui_url)
        
        # Create and run UI
        ui = ConsoleUI(assistant)
        ui.run()
        
    except Exception as e:
        console = Console()
        console.print(f"\n[red]Failed to start assistant: {e}[/]")
        console.print("\n[yellow]Please ensure:[/]")
        console.print("  • DaVinci Resolve is running")
        console.print("  • ComfyUI server is running (http://localhost:8188)")
        console.print("  • GitHub Copilot CLI is installed (gh copilot)")
        sys.exit(1)


if __name__ == "__main__":
    launch_console_ui()
