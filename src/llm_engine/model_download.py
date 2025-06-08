#!/usr/bin/env python3
"""
Script to download TinyLlama models for the Ansible-TinyLlama Integration.
This script can be run directly or imported as a module.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from tqdm import tqdm

# Add project root to path to allow importing project modules
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from huggingface_hub import snapshot_download
    DEPS_AVAILABLE = True
except ImportError as e:
    DEPS_AVAILABLE = False
    DEPS_ERROR = str(e)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("model_download")

# Available TinyLlama models
AVAILABLE_MODELS = {
    "tinyllama-1.1b": "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
    "tinyllama-1.1b-chat": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "tinyllama-1.1b-python": "TinyLlama/TinyLlama-1.1B-Python-v0.1"
}

def get_model_path():
    """Get the path to the model directory."""
    # Check if the environment variable is set
    model_path = os.environ.get("ANSIBLE_LLM_MODEL_PATH")
    if model_path:
        return Path(model_path)
    
    # Default to models directory in project root
    return project_root / "models"

def list_available_models():
    """List all available models."""
    logger.info("Available TinyLlama models:")
    for key, value in AVAILABLE_MODELS.items():
        logger.info(f"  - {key}: {value}")
    
    # Check which models are already downloaded
    model_dir = get_model_path()
    if model_dir.exists():
        downloaded = [d.name for d in model_dir.iterdir() if d.is_dir()]
        if downloaded:
            logger.info("\nDownloaded models:")
            for model in downloaded:
                logger.info(f"  - {model}")
        else:
            logger.info("\nNo models downloaded yet.")

def download_model(model_id, use_auth_token=None, quantize=None, local_dir=None, force=False):
    """
    Download a TinyLlama model.
    
    Args:
        model_id: The model ID (key from AVAILABLE_MODELS) or full Hugging Face model name
        use_auth_token: Optional Hugging Face token for private models
        quantize: Whether to quantize the model ('4bit', '8bit', or None)
        local_dir: Optional custom directory to save the model
        force: Whether to force download even if the model exists
        
    Returns:
        Path: The path to the downloaded model
    """
    if not DEPS_AVAILABLE:
        logger.error(f"Required dependencies not available: {DEPS_ERROR}")
        logger.error("Please install the required dependencies: pip install torch transformers huggingface_hub")
        return None
    
    # Get the model name from our dictionary or use directly if provided
    model_name = AVAILABLE_MODELS.get(model_id, model_id)
    
    # Get model directory
    if local_dir:
        model_dir = Path(local_dir)
    else:
        model_dir = get_model_path()
    
    # Create model directory if it doesn't exist
    model_dir.mkdir(exist_ok=True, parents=True)
    
    # Get model-specific directory name
    model_specific_name = model_name.split("/")[-1]
    model_path = model_dir / model_specific_name
    
    # Check if model already exists
    if model_path.exists() and not force:
        logger.info(f"Model already exists at {model_path}")
        logger.info("Use --force to redownload.")
        return model_path
    
    logger.info(f"Downloading model {model_name}")
    
    try:
        # Method 1: Use snapshot_download for more control
        logger.info("Downloading model files...")
        snapshot_download(
            repo_id=model_name,
            local_dir=str(model_path),
            local_dir_use_symlinks=False,
            token=use_auth_token,
            revision="main"
        )
        
        # Method 2: Alternative approach using AutoTokenizer and AutoModelForCausalLM
        # This will also download the model if needed
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, token=use_auth_token)
        
        logger.info("Loading model...")
        if quantize == '4bit':
            try:
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(load_in_4bit=True)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    quantization_config=quantization_config,
                    token=use_auth_token
                )
            except ImportError:
                logger.warning("4-bit quantization requires additional dependencies. Falling back to regular model.")
                model = AutoModelForCausalLM.from_pretrained(model_name, token=use_auth_token)
        elif quantize == '8bit':
            try:
                model = AutoModelForCausalLM.from_pretrained(model_name, load_in_8bit=True, token=use_auth_token)
            except ImportError:
                logger.warning("8-bit quantization requires additional dependencies. Falling back to regular model.")
                model = AutoModelForCausalLM.from_pretrained(model_name, token=use_auth_token)
        else:
            model = AutoModelForCausalLM.from_pretrained(model_name, token=use_auth_token)
        
        # Save model and tokenizer locally
        logger.info(f"Saving model to {model_path}")
        model.save_pretrained(model_path)
        tokenizer.save_pretrained(model_path)
        
        logger.info(f"Model successfully downloaded and saved to {model_path}")
        return model_path
    
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return None

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="Download TinyLlama models for Ansible-TinyLlama Integration")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available models")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a model")
    download_parser.add_argument("model_id", help="Model ID or name to download")
    download_parser.add_argument("--token", help="HuggingFace authentication token for private models")
    download_parser.add_argument("--output", "-o", help="Custom directory to save the model")
    download_parser.add_argument("--quantize", choices=["4bit", "8bit"], help="Quantize the model")
    download_parser.add_argument("--force", "-f", action="store_true", help="Force download even if model exists")
    
    args = parser.parse_args()
    
    if not args.command or args.command == "list":
        list_available_models()
    elif args.command == "download":
        download_model(
            model_id=args.model_id, 
            use_auth_token=args.token, 
            quantize=args.quantize,
            local_dir=args.output,
            force=args.force
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
