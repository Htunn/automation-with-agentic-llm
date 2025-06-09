"""
CLI wrapper for Ansible TinyLlama 3 Integration.
This module provides a simple wrapper to run the Click-based CLI.
"""
import os
import sys
import click
from .cli import cli

def run_cli(args=None):
    """
    Run the Click-based CLI with the given arguments.
    
    Args:
        args: List of command-line arguments (optional, defaults to sys.argv[1:])
    """
    try:
        # Store original sys.argv
        original_argv = sys.argv.copy()
        
        # Replace sys.argv with 'ansible-llm' as the program name (which Click uses)
        # and the provided arguments
        sys.argv = ['ansible-llm'] + (args or [])
        
        # Run the CLI directly using the modified sys.argv
        from .cli import main as cli_main
        cli_main()
        
    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[bold red]Error running CLI:[/bold red] {str(e)}")
        # Only show traceback in debug mode to keep the UI clean
        if "--debug" in original_argv:
            import traceback
            console.print(traceback.format_exc())
    finally:
        # Restore original sys.argv
        sys.argv = original_argv
