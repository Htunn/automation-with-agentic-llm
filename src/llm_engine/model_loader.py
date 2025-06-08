"""
Model loader for TinyLlama 3.
"""
import os
import logging
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.llm_engine.model_download import get_model_path, download_model as download_model_func

logger = logging.getLogger("ansible_llm")

def load_model(model_name="TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T", 
               quantization=None,
               device=None):
    """
    Load the TinyLlama model.
    
    Args:
        model_name: The name or path of the model to load.
        quantization: The quantization level (None, "4bit", or "8bit").
        device: The device to load the model on. If None, will try to use CUDA if available.
        
    Returns:
        tuple: The loaded model and tokenizer.
    """
    logger.info(f"Loading model {model_name}")
    
    # Set device
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    model_path = get_model_path() / model_name.split("/")[-1]
    
    # Check if model is downloaded
    if model_path.exists():
        logger.info(f"Loading model from {model_path}")
        model_name_or_path = str(model_path)
    else:
        logger.info(f"Model not found locally, loading from Hugging Face Hub: {model_name}")
        model_name_or_path = model_name
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    
    # Load model with quantization if specified
    if quantization == "4bit":
        try:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(load_in_4bit=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_name_or_path,
                quantization_config=quantization_config,
                device_map=device
            )
        except ImportError:
            logger.warning("4-bit quantization requires additional dependencies. Falling back to 8-bit.")
            quantization = "8bit"
    
    if quantization == "8bit":
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name_or_path, load_in_8bit=True, device_map=device)
        except ImportError:
            logger.warning("8-bit quantization requires additional dependencies. Loading full model.")
            model = AutoModelForCausalLM.from_pretrained(model_name_or_path).to(device)
    else:
        # Load normal model
        model = AutoModelForCausalLM.from_pretrained(model_name_or_path).to(device)
    
    logger.info("Model loaded successfully")
    return model, tokenizer

def download_model(model_name="TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T", quantization=None):
    """
    Download the model files.
    
    Args:
        model_name: The name of the model to download.
        quantization: Optional quantization level ("4bit" or "8bit").
    
    Returns:
        Path to the downloaded model or None if download failed.
    """
    return download_model_func(model_id=model_name, quantize=quantization)
