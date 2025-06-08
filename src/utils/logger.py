"""
Logger setup for the application.
"""
import logging
import os
from pathlib import Path

def setup_logger(name="ansible_llm", level=logging.INFO):
    """Set up and configure a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create logs directory if it doesn't exist
    log_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "ansible_llm.log")
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
