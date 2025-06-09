"""
CLI interface for the Ansible TinyLlama 3 integration.
"""
import click
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Ansible TinyLlama 3 Integration CLI."""
    if ctx.invoked_subcommand is None:
        # Show welcome message and basic help when no subcommand is provided
        console.print(Panel.fit("Welcome to Ansible TinyLlama 3 Integration", 
                               title="[bold green]ansible-llm[/bold green]"))
        console.print("Available commands:")
        console.print("  [bold]generate-playbook[/bold] - Generate an Ansible playbook from a description")
        console.print("  [bold]analyze-playbook[/bold] - Analyze an existing Ansible playbook")
        console.print("  [bold]analyze-inventory[/bold] - Analyze an Ansible inventory")
        console.print("  [bold]setup-examples[/bold] - Set up example playbooks and configurations")
        console.print("\nRun [bold]python -m src.main cli COMMAND --help[/bold] for more information on a specific command.")
    pass

@cli.command()
@click.argument("description")
@click.option("--output", "-o", type=str, help="Output file for the generated playbook")
def generate_playbook(description, output):
    """Generate an Ansible playbook from a natural language description."""
    console.print(Panel.fit(f"Generating playbook from: {description}"))
    # TODO: Implement playbook generation
    console.print("Playbook generation not yet implemented")

@cli.command()
@click.argument("playbook_path", type=click.Path(exists=True))
def analyze_playbook(playbook_path):
    """Analyze an existing Ansible playbook and suggest improvements."""
    console.print(Panel.fit(f"Analyzing playbook: {playbook_path}"))
    # TODO: Implement playbook analysis
    console.print("Playbook analysis not yet implemented")

@cli.command()
@click.argument("inventory_path", type=click.Path(exists=True))
def analyze_inventory(inventory_path):
    """Analyze an Ansible inventory and provide insights."""
    console.print(Panel.fit(f"Analyzing inventory: {inventory_path}"))
    # TODO: Implement inventory analysis
    console.print("Inventory analysis not yet implemented")

@cli.command()
@click.option("--windows", is_flag=True, help="Configure for Windows SSH automation")
def setup_examples(windows):
    """Set up example playbooks and configurations."""
    if windows:
        console.print(Panel.fit("Setting up Windows SSH automation examples"))
        # TODO: Implement Windows SSH example setup
        console.print("Windows SSH example setup not yet implemented")
    else:
        console.print(Panel.fit("Setting up general automation examples"))
        # TODO: Implement general example setup
        console.print("General example setup not yet implemented")

def main():
    """Run the CLI."""
    # Use Click's standard pattern for running commands
    # This will read arguments from sys.argv automatically
    try:
        cli(prog_name="ansible-llm")
    except Exception as e:
        # Provide better error handling for debugging
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
