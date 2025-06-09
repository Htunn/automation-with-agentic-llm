#!/usr/bin/env python3
"""
Simple CLI runner for Ansible TinyLlama integration.
"""
import os
import sys
from rich.console import Console
from rich.panel import Panel
import click

console = Console()

# Import CLI functions from the main CLI module
from src.api.cli import (
    generate_playbook, 
    analyze_playbook, 
    analyze_inventory, 
    setup_examples
)

def show_welcome():
    """Display welcome message and available commands."""
    console.print(Panel.fit("Welcome to Ansible TinyLlama 3 Integration", 
                            title="[bold green]ansible-llm[/bold green]"))
    console.print("Available commands:")
    console.print("  [bold]generate-playbook[/bold] - Generate an Ansible playbook from a description")
    console.print("  [bold]analyze-playbook[/bold] - Analyze an existing Ansible playbook")
    console.print("  [bold]analyze-inventory[/bold] - Analyze an Ansible inventory")
    console.print("  [bold]setup-examples[/bold] - Set up example playbooks and configurations")
    console.print("\nRun [bold]python -m src.main cli COMMAND --help[/bold] for more information on a specific command.")

def run_cli(args=None):
    """
    Run CLI commands based on arguments.
    
    Args:
        args: List of command-line arguments
    """
    # Debug - print out exactly what arguments we received
    console.print(f"[dim]Debug: Received arguments: {args}[/dim]")
    
    if not args or args[0] == '--help':
        show_welcome()
        return
    
    command = args[0]
    cmd_args = args[1:] if len(args) > 1 else []
    
    # Map commands to their functions
    commands = {
        'generate-playbook': handle_generate_playbook,
        'analyze-playbook': handle_analyze_playbook,
        'analyze-inventory': handle_analyze_inventory,
        'setup-examples': handle_setup_examples
    }
    
    if command in commands:
        # Execute the command
        commands[command](cmd_args)
    else:
        console.print(f"[bold red]Unknown command:[/bold red] {command}")
        show_welcome()

def handle_generate_playbook(args):
    """Handle generate-playbook command."""
    if not args or '--help' in args:
        console.print("""
Usage: ansible-llm generate-playbook [OPTIONS] DESCRIPTION

  Generate an Ansible playbook from a natural language description.

Options:
  -o, --output TEXT  Output file for the generated playbook
  --help             Show this message and exit.
""")
        return
    
    # For handling quoted arguments, join everything that's not an option
    description_parts = []
    output = None
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        if arg in ['-o', '--output']:
            if i + 1 < len(args):
                output = args[i + 1]
                skip_next = True
        elif not arg.startswith('-'):
            description_parts.append(arg)
    
    # Join all non-option arguments as the description
    description = ' '.join(description_parts)
    
    # Call the actual function
    generate_playbook(description, output)

def handle_analyze_playbook(args):
    """Handle analyze-playbook command."""
    if not args or '--help' in args:
        console.print("""
Usage: ansible-llm analyze-playbook [OPTIONS] PLAYBOOK_PATH

  Analyze an existing Ansible playbook and suggest improvements.

Options:
  --help  Show this message and exit.
""")
        return
    
    playbook_path = args[0]
    analyze_playbook(playbook_path)

def handle_analyze_inventory(args):
    """Handle analyze-inventory command."""
    if not args or '--help' in args:
        console.print("""
Usage: ansible-llm analyze-inventory [OPTIONS] INVENTORY_PATH

  Analyze an Ansible inventory and provide insights.

Options:
  --help  Show this message and exit.
""")
        return
    
    inventory_path = args[0]
    analyze_inventory(inventory_path)

def handle_setup_examples(args):
    """Handle setup-examples command."""
    if '--help' in args:
        console.print("""
Usage: ansible-llm setup-examples [OPTIONS]

  Set up example playbooks and configurations.

Options:
  --windows  Configure for Windows SSH automation
  --help     Show this message and exit.
""")
        return
    
    windows = '--windows' in args
    setup_examples(windows)
