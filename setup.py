#!/usr/bin/env python3
"""
Setup script for the Ansible TinyLlama 3 Integration.
"""
import os
import sys
import argparse
from pathlib import Path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Set up the Ansible TinyLlama Integration")
    parser.add_argument("--download-model", action="store_true", help="Download the TinyLlama model")
    parser.add_argument("--quantize", choices=["4bit", "8bit"], help="Quantize the model")
    parser.add_argument("--setup-windows-ssh", action="store_true", help="Set up Windows SSH examples")
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Add the project root directory to the Python path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Create necessary directories
    dirs_to_create = [
        project_root / "models",
        project_root / "logs",
        project_root / "configs",
    ]
    
    for directory in dirs_to_create:
        directory.mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Set up virtual environment if not already active
    if not os.environ.get("VIRTUAL_ENV"):
        print("No active virtual environment detected.")
        print("Please create and activate a virtual environment before running this script:")
        print("python3.12 -m venv venv")
        print("source venv/bin/activate")
        return
    
    # Install requirements
    print("Installing requirements...")
    os.system(f"{sys.executable} -m pip install -r {project_root / 'requirements.txt'}")
    
    # Download model if requested
    if args.download_model:
        from src.llm_engine.model_loader import download_model
        download_model()
    
    # Set up Windows SSH examples if requested
    if args.setup_windows_ssh:
        print("Setting up Windows SSH examples...")
        # Copy example files to a user-accessible location
        examples_dir = project_root / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        windows_ssh_dir = examples_dir / "windows_ssh"
        windows_ssh_dir.mkdir(exist_ok=True)
        
        # Copy example files
        import shutil
        src_examples = project_root / "src" / "examples" / "windows_ssh"
        for file in src_examples.glob("*"):
            shutil.copy(file, windows_ssh_dir / file.name)
        
        print(f"Windows SSH examples have been set up in {windows_ssh_dir}")
    
    print("Setup complete!")

if __name__ == "__main__":
    main()
