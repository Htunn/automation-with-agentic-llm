"""
Configuration loading and management for the Ansible TinyLlama integration.
"""
import os
import sys
import tomli
import logging
from pathlib import Path

logger = logging.getLogger("ansible_llm")

def get_config_path():
    """Get the path to the configuration file."""
    # Check environment variable
    if "ANSIBLE_LLM_CONFIG" in os.environ:
        return os.environ["ANSIBLE_LLM_CONFIG"]
    
    # Default locations
    config_locations = [
        Path(os.getcwd()) / "config" / "config.toml",
        Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "config" / "config.toml",
        Path(os.path.expanduser("~")) / ".ansible_llm" / "config.toml",
        Path("/etc/ansible_llm/config.toml")
    ]
    
    for path in config_locations:
        if path.exists():
            return str(path)
    
    # If no config file found, use default
    default_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "config" / "config.toml"
    logger.warning(f"No config file found, using default location: {default_path}")
    return str(default_path)

def load_config(config_path=None):
    """
    Load the configuration from a TOML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: The configuration
    """
    if not config_path:
        config_path = get_config_path()
    
    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        # Return default configuration
        return {
            "llm": {
                "model_name": "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T",
                "quantization": "4bit",
                "max_tokens": 1024,
                "temperature": 0.7
            },
            "api": {
                "host": "127.0.0.1",
                "port": 8000,
                "debug": False
            },
            "ansible": {
                "callback_plugins_path": "./src/ansible_plugins/callbacks",
                "library_path": "./src/ansible_plugins/modules",
                "filter_plugins_path": "./src/ansible_plugins/filters"
            },
            "windows_ssh": {
                "default_user": "Administrator",
                "default_port": 22,
                "enable_key_auth": True
            },
            "logging": {
                "level": "INFO",
                "file": "./logs/ansible_llm.log",
                "max_file_size_mb": 10,
                "backup_count": 5
            }
        }
