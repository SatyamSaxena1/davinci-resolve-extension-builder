"""
Command Line Interface for Resolve AI Assistant
Conversational AI interface with OpenAI function calling
"""

import os
import sys
import json
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from resolve_ai.controller import ResolveAIController
from resolve_ai.fusion_tools import FusionNodeBuilder
from resolve_ai.ai_tools import RESOLVE_TOOLS, FunctionExecutor


# Load environment variables
load_dotenv()

# Initialize Rich console for beautiful output
console = Console()


class ResolveAIAssistant:
    """Conversational AI assistant for DaVinci Resolve"""
    
    def __init__(self):
        """Initialize the AI assistant"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        
        if not self.api_key:
            console.print("[red]Error: OPENAI_API_KEY not found in environment variables[/red]")
            console.print("Please create a .env file with your OpenAI API key")
            sys.exit(1)
        
        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Initialize Resolve controller
        try:
            console.print("[yellow]Connecting to DaVinci Resolve...[/yellow]")
            self.controller = ResolveAIController()
            
            # Try to get Fusion composition
            fusion_comp = self.controller.get_fusion_comp()
            if fusion_comp:
                self.fusion_builder = FusionNodeBuilder(fusion_comp)
                console.print("[green]✓ Connected to Resolve with Fusion composition[/green]")
            else:
                self.fusion_builder = None
                console.print("[yellow]⚠ Connected to Resolve (no Fusion composition available)[/yellow]")
                console.print("[dim]To use Fusion tools, select a clip on the timeline first[/dim]")
            
            self.function_executor = FunctionExecutor(self.controller, self.fusion_builder)
            
        except Exception as e:
            console.print(f"[red]Error connecting to DaVinci Resolve: {e}[/red]")
            console.print("\n[yellow]Make sure:[/yellow]")
            console.print("1. DaVinci Resolve is running")
            console.print("2. A project is open")
            console.print("3. Script API is properly configured")
            sys.exit(1)
        
        # System prompt
        self.system_prompt = """You are an expert AI assistant for DaVinci Resolve video editing software.
You help users automate their editing workflow, create Fusion compositions, manage timelines, and control the editing process.

You have access to tools for:
- Creating and manipulating Fusion nodes (Background, Transform, Text, Merge, ColorCorrector, Blur, Glow, etc.)
- Connecting nodes to build complex compositions
- Managing timelines and markers
- Importing media and managing the media pool
- Creating templates like lower-thirds

When users ask you to create visual effects or compositions, use the Fusion node tools to build them step by step.
Always explain what you're doing in a friendly, clear way.

For Fusion compositions:
- Position nodes intelligently (use x_pos, y_pos to arrange them left-to-right)
- Remember to connect nodes properly (Background, Transform, Merge patterns)
- Use descriptive names for nodes
- For Merge nodes: use "Background" and "Foreground" as input names

Be creative and helpful! If a user asks for something complex, break it down into steps and execute them."""

        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    def chat(self, user_message: str) -> str:
        """
        Send a message and get AI response with function calling
        
        Args:
            user_message: User's message
        
        Returns:
            AI's text response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response from OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            tools=RESOLVE_TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If AI wants to call functions
        if tool_calls:
            # Add AI's response to history
            self.conversation_history.append(response_message)
            
            # Execute each function call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                console.print(f"[cyan]→ Executing: {function_name}[/cyan]")
                
                # Execute the function
                result = self.function_executor.execute(function_name, function_args)
                
                # Add function result to history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(result)
                })
            
            # Get final response after function execution
            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history
            )
            
            final_message = second_response.choices[0].message
            self.conversation_history.append(final_message)
            
            return final_message.content
        
        else:
            # No function calls, just return the message
            self.conversation_history.append(response_message)
            return response_message.content
    
    def run(self):
        """Run the interactive CLI"""
        console.print(Panel.fit(
            "[bold cyan]DaVinci Resolve AI Assistant[/bold cyan]\n"
            "Control Resolve with natural language commands\n"
            "[dim]Type 'exit' or 'quit' to exit[/dim]",
            border_style="cyan"
        ))
        
        # Show initial status
        status = self.controller.get_status()
        if status["project_open"]:
            project_info = status["project_info"]
            console.print(f"\n[green]Connected to project: {project_info['project_name']}[/green]")
            if project_info["current_timeline"]:
                console.print(f"[green]Current timeline: {project_info['current_timeline']}[/green]")
        
        console.print("\n[yellow]Example commands:[/yellow]")
        console.print("• Create a lower-third with title 'John Doe' and subtitle 'CEO'")
        console.print("• Add a blue marker at frame 100 with note 'Start of scene'")
        console.print("• Create a text node that says 'Hello World' in red")
        console.print("• Show me what nodes are in the Fusion composition")
        console.print()
        
        # Main conversation loop
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if not user_input.strip():
                    continue
                
                # Get AI response
                console.print("\n[bold cyan]AI Assistant[/bold cyan]")
                
                with console.status("[cyan]Thinking...[/cyan]"):
                    response = self.chat(user_input)
                
                # Display response
                if response:
                    console.print(Markdown(response))
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                console.print("[dim]Try rephrasing your request or check if Resolve is still running[/dim]")


def main():
    """Main entry point"""
    assistant = ResolveAIAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
