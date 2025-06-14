#!/usr/bin/env python3
"""
Integration tests for the Ansible-TinyLlama integration.
These tests check the interaction between components and real functionality.
"""
import unittest
import os
import sys
import tempfile
import json
from pathlib import Path
import shutil
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestIntegration(unittest.TestCase):
    """Integration tests for Ansible-TinyLlama integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.models_dir = Path(self.test_dir) / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Set environment variables
        os.environ["ANSIBLE_LLM_MODEL_PATH"] = str(self.models_dir)
        
        # Backup the real imports
        self.orig_import = __import__
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
        
        # Clean up environment variables
        if "ANSIBLE_LLM_MODEL_PATH" in os.environ:
            del os.environ["ANSIBLE_LLM_MODEL_PATH"]
    
    @patch('src.llm_engine.model_loader.AutoModelForCausalLM')
    @patch('src.llm_engine.model_loader.AutoTokenizer')
    def test_model_loading_and_inference(self, mock_tokenizer, mock_model):
        """Test the full model loading and inference pipeline."""
        # Set up mocks
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        mock_model.from_pretrained.return_value = mock_model_instance
        
        # Mock the generate method
        mock_model_instance.generate.return_value = MagicMock()
        mock_tokenizer_instance.decode.return_value = "---\n- name: Test playbook"
        
        # Import the real model loader
        from src.llm_engine.model_loader import load_model
        
        # Load the model
        model, tokenizer = load_model(model_name="test-model")
        
        # Now test inference
        from src.llm_engine.response_processor import generate_playbook_text
        
        result = generate_playbook_text(
            prompt="Create a playbook to install nginx",
            model=model,
            tokenizer=tokenizer,
            max_length=100
        )
        
        # Check that we got a valid result
        self.assertIn("- name: Test playbook", result)
    
    @patch('src.api.rest_api.model')
    @patch('src.api.rest_api.tokenizer')
    def test_api_end_to_end(self, mock_tokenizer, mock_model):
        """Test the REST API from request to response."""
        # Import TestClient here to avoid affecting other tests
        from fastapi.testclient import TestClient
        from src.api.rest_api import app
        
        # Set up mocks
        mock_model.generate.return_value = MagicMock()
        mock_tokenizer.decode.return_value = (
            "---\n"
            "- name: Install and configure nginx\n"
            "  hosts: web_servers\n"
            "  become: yes\n"
            "  tasks:\n"
            "    - name: Install nginx\n"
            "      apt:\n"
            "        name: nginx\n"
            "        state: present\n"
        )
        
        # Create a test client
        client = TestClient(app)
        
        # Make a request
        payload = {
            "description": "Install and configure nginx",
            "target_os": "Ubuntu"
        }
        
        response = client.post("/generate_playbook", json=payload)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("playbook", data)
        self.assertIn("- name: Install and configure nginx", data["playbook"])
    
    def test_config_loading(self):
        """Test configuration loading from various sources."""
        # Create a test config file
        config_dir = Path(self.test_dir) / "config"
        config_dir.mkdir(exist_ok=True)
        
        config_path = config_dir / "config.toml"
        with open(config_path, "w") as f:
            f.write("""
            [api]
            host = "127.0.0.1"
            port = 8080
            require_auth = true
            
            [model]
            name = "test-model"
            quantization = "4bit"
            
            [logging]
            level = "INFO"
            file = "./logs/app.log"
            """)
        
        # Import config loader
        from src.config import load_config
        
        # Load the config
        config = load_config(config_path=str(config_path))
        
        # Check values
        self.assertEqual(config["api"]["host"], "127.0.0.1")
        self.assertEqual(config["api"]["port"], 8080)
        self.assertEqual(config["model"]["name"], "test-model")
        self.assertEqual(config["logging"]["level"], "INFO")

if __name__ == "__main__":
    unittest.main()
