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

from src.api.cli import main as cli_main
from src.llm_engine.model_loader import load_model
from src.utils.logger import setup_logger

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ansible TinyLlama 3 Integration")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", type=str, default=None, help="Path to configuration file")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run CLI interface")
    
    # API command
    api_parser = subparsers.add_parser("api", help="Run API server")
    api_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    
    # Model commands
    model_parser = subparsers.add_parser("model", help="Model management")
    model_parser.add_argument("--download", action="store_true", help="Download the model")
    model_parser.add_argument("--quantize", choices=["4bit", "8bit"], help="Quantize the model")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(level=log_level)
    
    logger.info("Starting Ansible TinyLlama 3 Integration")
    
    if args.command == "cli":
        cli_main()
    elif args.command == "api":
        from src.api.rest_api import start_api_server
        start_api_server(host=args.host, port=args.port)
    elif args.command == "model":
        if args.download:
            logger.info("Downloading model...")
            # Implement model downloading
        if args.quantize:
            logger.info(f"Quantizing model to {args.quantize}...")
            # Implement model quantization
    else:
        # Default to CLI
        cli_main()

if __name__ == "__main__":
    main()
