#!/usr/bin/env python3
"""
Simple CLI implementation that bypasses Click's argument parsing.
"""
import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

def generate_playbook(description, output=None):
    """Generate an Ansible playbook from a natural language description."""
    console.print(Panel.fit(f"Generating playbook from: {description}"))
    console.print("Output file: " + (output or "stdout"))
    # TODO: Implement actual playbook generation
    console.print("Playbook generation not yet implemented")
    
    # Example of what the playbook might look like
    playbook = """---
- name: Install and configure nginx
  hosts: web_servers
  become: true
  tasks:
    - name: Install nginx package
      apt:
        name: nginx
        state: present
        update_cache: yes
      
    - name: Ensure nginx is started and enabled
      service:
        name: nginx
        state: started
        enabled: yes
"""
    
    if output:
        try:
            with open(output, 'w') as f:
                f.write(playbook)
            console.print(f"[green]Playbook written to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Error writing playbook: {str(e)}[/red]")
    else:
        console.print("\n" + playbook)
    
def analyze_playbook(playbook_path):
    """Analyze an existing Ansible playbook and suggest improvements."""
    from src.llm_engine.model_loader import load_model
    from src.llm_engine.response_processor import extract_yaml_from_response, process_analysis_response
    import yaml
    import os.path
    import logging

    logger = logging.getLogger("ansible_llm")
    
    console.print(Panel.fit(f"Analyzing playbook: {playbook_path}"))
    
    # Check if file exists
    if not os.path.exists(playbook_path):
        console.print(f"[red]Error: Playbook file not found: {playbook_path}[/red]")
        return
    
    try:
        with open(playbook_path, 'r') as f:
            playbook_content = f.read()
            
        # Try to parse YAML to validate
        try:
            yaml.safe_load(playbook_content)
        except yaml.YAMLError as e:
            console.print(f"[red]Error: Invalid YAML in playbook: {str(e)}[/red]")
            return
            
        # Initialize LLM
        try:
            # Load model and tokenizer
            # Try to use the chat-specific model which handles analysis tasks better
            try:
                model_name = os.environ.get("MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v0.1")
                console.print(f"[yellow]Using model: {model_name}[/yellow]")
                model, tokenizer = load_model(model_name=model_name)
            except Exception as e:
                logger.error(f"Error loading specified model: {str(e)}")
                console.print(f"[red]Error loading specified model: {str(e)}[/red]")
                console.print("[yellow]Falling back to default model...[/yellow]")
                model, tokenizer = load_model()
            
            # Create prompt for analysis
            prompt = f"""
You are an expert Ansible consultant tasked with analyzing playbooks for best practices, optimizations, and potential issues.
Please analyze the following Ansible playbook and provide:

1. A brief overview of what the playbook does
2. Potential issues or bugs you identify
3. Optimization recommendations
4. Security considerations
5. Best practice improvements

Playbook:
```yaml
{playbook_content}
```

Please provide a comprehensive analysis.
"""
            
            # Call the model
            console.print("[yellow]Analyzing playbook with LLM, please wait...[/yellow]")
            
            # Generate response using tokenizer and model with better error handling
            try:
                # Add temperature parameter to reduce randomness and increase coherence
                inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
                outputs = model.generate(
                    **inputs, 
                    max_new_tokens=1024,
                    temperature=0.5,  # Lower temperature for more focused output
                    repetition_penalty=1.3,  # Penalize repetition more heavily
                    do_sample=True  # Enable sampling to avoid deterministic outputs
                )
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Process the response using the proper function
                llm_response = response[len(prompt):]  # Only use the response part, not the prompt
            except Exception as e:
                logger.error(f"Error during model generation: {str(e)}")
                console.print(f"[red]Error during model generation: {str(e)}[/red]")
                console.print("[yellow]Try using a different model with './dev.sh analyze-playbook your_playbook.yml tiny'[/yellow]")
                return
            
            # Check if the response is empty or just whitespace
            if not llm_response or llm_response.strip() == "":
                console.print("[red]No analysis results generated. The model returned an empty response.[/red]")
                console.print("\n[yellow]This might be due to insufficient model capacity or memory constraints.[/yellow]")
                console.print("[yellow]Try using a smaller playbook or running with the 'tiny' model option:[/yellow]")
                console.print("./dev.sh analyze-playbook your_playbook.yml tiny")
                return
                
            # Check for binary-like patterns directly
            import re
            # Simple binary pattern detection
            has_binary_pattern = False
            # Check for repetitive patterns that indicate output issues
            if re.search(r'((\d+\.){10,})', llm_response):
                has_binary_pattern = True
            # Check repetitive zeros and ones
            if re.search(r'((0+1+){10,})', llm_response):
                has_binary_pattern = True
            # Check for long sequences of special characters
            for char in '.,;:-_=+<>[](){}|':
                if re.search(f'({re.escape(char)}){{{20,}}}', llm_response):
                    has_binary_pattern = True
                    
            if has_binary_pattern:
                console.print("[red]Warning: The model produced binary-like output patterns.[/red]")
                console.print("[yellow]Attempting to fix by switching to fallback analysis mode...[/yellow]")
                # Create a simple analysis result for fallback
                llm_response = f"""
Summary: The playbook appears to be an Ansible playbook but detailed analysis couldn't be performed.

Issues:
- The model encountered difficulties analyzing this particular playbook

Best Practices:
- Consider breaking down complex playbooks into smaller components
- Use standard Ansible modules and avoid custom scripts when possible
- Follow Ansible's YAML formatting guidelines
"""
            
            # Enhanced error handling for response processing
            try:
                processed_response = process_analysis_response(llm_response)
                
                # Display the results
                console.print("\n[bold green]Playbook Analysis Results:[/bold green]\n")
                
                if isinstance(processed_response, dict) and "structured_analysis" in processed_response:
                    # If response was successfully structured, display it nicely
                    analysis = processed_response["structured_analysis"]
                    
                    # Check if any analysis sections have content
                    has_content = False
                    if "summary" in analysis and analysis["summary"].strip():
                        has_content = True
                    if "issues" in analysis and analysis["issues"]:
                        has_content = True
                    if "security" in analysis and analysis["security"]:
                        has_content = True
                    if "best_practices" in analysis and analysis["best_practices"]:
                        has_content = True
                    
                    if not has_content:
                        # If no structured content was extracted, fall back to raw display
                        console.print("[yellow]Couldn't structure the analysis into sections. Showing raw output:[/yellow]\n")
                        console.print(llm_response)
                        return
                    
                    # Display summary
                    if "summary" in analysis and analysis["summary"].strip():
                        console.print("[bold]Summary:[/bold]")
                        console.print(analysis["summary"].strip())
                        console.print("")
                    
                    # Display issues
                    if "issues" in analysis and analysis["issues"]:
                        console.print("[bold]Potential Issues:[/bold]")
                        for issue in analysis["issues"]:
                            console.print(f"• {issue}")
                        console.print("")
                    
                    # Display security concerns
                    if "security" in analysis and analysis["security"]:
                        console.print("[bold]Security Considerations:[/bold]")
                        for concern in analysis["security"]:
                            console.print(f"• {concern}")
                        console.print("")
                    
                    # Display best practices
                    if "best_practices" in analysis and analysis["best_practices"]:
                        console.print("[bold]Best Practice Recommendations:[/bold]")
                        for practice in analysis["best_practices"]:
                            console.print(f"• {practice}")
                else:
                    # If structured analysis failed, display raw response
                    console.print("[yellow]Couldn't parse structured analysis format. Showing raw output:[/yellow]\n")
                    console.print(llm_response)
            except Exception as e:
                # If processing fails, show raw response
                logger.error(f"Error during response processing: {str(e)}")
                console.print("[yellow]Error processing response into structured format. Showing raw output:[/yellow]\n")
                console.print(llm_response)
            
        except Exception as e:
            logger.error(f"Error during playbook analysis: {str(e)}")
            console.print(f"[red]Error during analysis: {str(e)}[/red]")
            console.print("[yellow]Playbook analysis implementation is in progress. The current feature is experimental.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error reading playbook file: {str(e)}[/red]")
    
def analyze_inventory(inventory_path):
    """Analyze an Ansible inventory and provide insights."""
    console.print(Panel.fit(f"Analyzing inventory: {inventory_path}"))
    # TODO: Implement inventory analysis
    console.print("Inventory analysis not yet implemented")
    
def setup_examples(windows=False):
    """Set up example playbooks and configurations."""
    if windows:
        console.print(Panel.fit("Setting up Windows SSH automation examples"))
        # TODO: Implement Windows SSH example setup
        console.print("Windows SSH example setup not yet implemented")
    else:
        console.print(Panel.fit("Setting up general automation examples"))
        # TODO: Implement general example setup
        console.print("General example setup not yet implemented")

def run_cli(args):
    """Run CLI commands based on command-line arguments."""
    if not args:
        show_help()
        return
        
    command = args[0]
    
    if command == "--help" or command == "help":
        show_help()
        return
        
    if command == "generate-playbook":
        handle_generate_playbook(args[1:])
    elif command == "analyze-playbook":
        handle_analyze_playbook(args[1:])
    elif command == "analyze-inventory":
        handle_analyze_inventory(args[1:])
    elif command == "setup-examples":
        handle_setup_examples(args[1:])
    else:
        console.print(f"[bold red]Unknown command:[/bold red] {command}")
        show_help()
        
def show_help():
    """Show help message."""
    console.print(Panel.fit("Welcome to Ansible TinyLlama 3 Integration", 
                           title="[bold green]ansible-llm[/bold green]"))
    console.print("Available commands:")
    console.print("  [bold]generate-playbook[/bold] - Generate an Ansible playbook from a description")
    console.print("  [bold]analyze-playbook[/bold] - Analyze an existing Ansible playbook")
    console.print("  [bold]analyze-inventory[/bold] - Analyze an Ansible inventory")
    console.print("  [bold]setup-examples[/bold] - Set up example playbooks and configurations")
    console.print("\nRun [bold]python -m src.main cli COMMAND --help[/bold] for more information on a specific command.")
    
def handle_generate_playbook(args):
    """Handle generate-playbook command."""
    if not args or "--help" in args:
        console.print("""
Usage: ansible-llm generate-playbook [OPTIONS] DESCRIPTION

  Generate an Ansible playbook from a natural language description.

Options:
  -o, --output TEXT  Output file for the generated playbook
  --help             Show this message and exit.
""")
        return
        
    # Parse arguments
    output = None
    description_parts = []
    skip_next = False
    
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
            
        if arg in ["-o", "--output"]:
            if i + 1 < len(args):
                output = args[i + 1]
                skip_next = True
        elif not arg.startswith("-"):
            description_parts.append(arg)
    
    if not description_parts:
        console.print("[bold red]Error:[/bold red] Description is required")
        return
        
    description = " ".join(description_parts)
    generate_playbook(description, output)
    
def handle_analyze_playbook(args):
    """Handle analyze-playbook command."""
    if not args or "--help" in args:
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
    if not args or "--help" in args:
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
    if "--help" in args:
        console.print("""
Usage: ansible-llm setup-examples [OPTIONS]

  Set up example playbooks and configurations.

Options:
  --windows  Configure for Windows SSH automation
  --help     Show this message and exit.
""")
        return
        
    windows = "--windows" in args
    setup_examples(windows)
