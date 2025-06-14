#!/usr/bin/env python3
"""
Main entry point for the Ansible TinyLlama 3 integration.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.api.direct_cli import run_cli
from src.llm_engine.model_loader import load_model
from src.llm_engine.model_download import list_available_models, download_model
from src.utils.logger import setup_logger

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ansible TinyLlama 3 Integration")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", type=str, default=None, help="Path to configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # CLI command - allow it to accept any arguments after 'cli'
    cli_parser = subparsers.add_parser("cli", help="Run CLI interface")
    cli_parser.add_argument('cli_args', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    
    # API command
    api_parser = subparsers.add_parser("api", help="Run API server")
    api_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    # Model commands
    model_parser = subparsers.add_parser("model", help="Model management")
    model_subparsers = model_parser.add_subparsers(dest="model_command", help="Model command to run")
    
    # Model list command
    list_parser = model_subparsers.add_parser("list", help="List available models")
    
    # Model download command
    download_parser = model_subparsers.add_parser("download", help="Download a model")
    download_parser.add_argument("model_id", help="Model ID or name to download")
    download_parser.add_argument("--token", help="HuggingFace authentication token for private models")
    download_parser.add_argument("--output", "-o", help="Custom directory to save the model")
    download_parser.add_argument("--quantize", choices=["4bit", "8bit"], help="Quantize the model")
    download_parser.add_argument("--force", "-f", action="store_true", help="Force download even if model exists")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    # Special case for 'cli' command - we need to handle this before argparse
    # to preserve quoted arguments and pass them correctly to Click
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Setup logging first
        debug_mode = "--debug" in sys.argv
        log_level = logging.DEBUG if debug_mode else logging.INFO
        logger = setup_logger(level=log_level)
        
        logger.info("Starting Ansible TinyLlama 3 Integration")
        
        # Extract all arguments after "cli"
        cli_args = sys.argv[2:]
        # Run the CLI module with these arguments
        run_cli(cli_args)
        return
    
    # For all other commands (model, api, etc.), use argparse as usual
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(level=log_level)
    
    logger.info("Starting Ansible TinyLlama 3 Integration")
    
    if args.command == "api":
        from src.api.rest_api import start_api_server
        start_api_server(host=args.host, port=args.port)
    elif args.command == "model":
        if not args.model_command or args.model_command == "list":
            list_available_models()
        elif args.model_command == "download":
            download_model(
                model_id=args.model_id,
                use_auth_token=args.token,
                quantize=args.quantize,
                local_dir=args.output,
                force=args.force
            )
        else:
            logger.error("Invalid model command. Use 'list' or 'download'.")
    elif not args.command:
        # Default to showing help
        logger.info("No command specified. Use --help to see available commands.")
        parser = argparse.ArgumentParser(description="Ansible TinyLlama 3 Integration")
        parser.print_help()
    else:
        logger.error(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
