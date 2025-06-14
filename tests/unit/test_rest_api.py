#!/usr/bin/env python3
"""
Unit tests for the REST API.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path
import json
from fastapi.testclient import TestClient
from fastapi import status

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the app after adjusting the Python path
from src.api.rest_api import app, API_VERSION

class TestRestAPI(unittest.TestCase):
    """Tests for the REST API."""
    
    def setUp(self):
        """Set up the test client."""
        self.client = TestClient(app)
        # Mock environment variables
        os.environ["SECRET_KEY"] = "testsecretkey"
    
    def tearDown(self):
        """Clean up after tests."""
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]
    
    @patch('src.api.rest_api.model', MagicMock())
    @patch('src.api.rest_api.tokenizer', MagicMock())
    def test_health_check(self):
        """Test the health check endpoint with the model loaded."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], API_VERSION)
        self.assertTrue(data["model_loaded"])
        self.assertIn("timestamp", data)
        
        # Check header
        self.assertEqual(response.headers["X-API-Version"], API_VERSION)
    
    @patch('src.api.rest_api.model', None)
    @patch('src.api.rest_api.tokenizer', None)
    def test_health_check_no_model(self):
        """Test the health check endpoint when the model is not loaded."""
        response = self.client.get("/health")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["version"], API_VERSION)
        self.assertFalse(data["model_loaded"])
    
    @patch('src.api.rest_api.model')
    @patch('src.api.rest_api.tokenizer')
    def test_generate_playbook(self, mock_tokenizer, mock_model):
        """Test the generate playbook endpoint."""
        # Mock model generation
        mock_model.generate.return_value = MagicMock()
        mock_tokenizer.decode.return_value = "---\n- name: Generated playbook\n  hosts: all\n  tasks:\n    - name: Test task\n      debug:\n        msg: Hello world"
        
        payload = {
            "description": "Configure a web server",
            "target_os": "Linux",
            "additional_context": "Use nginx"
        }
        
        response = self.client.post(
            "/generate_playbook",
            json=payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("playbook", data)
        self.assertIn("- name: Generated playbook", data["playbook"])
    
    @patch('src.api.rest_api.model', None)
    def test_generate_playbook_no_model(self):
        """Test the generate playbook endpoint when model is not loaded."""
        payload = {
            "description": "Configure a web server",
            "target_os": "Linux"
        }
        
        response = self.client.post(
            "/generate_playbook",
            json=payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
    
    @patch('src.api.rest_api.model')
    def test_analyze_playbook(self, mock_model):
        """Test the analyze playbook endpoint."""
        # Mock model
        mock_model.return_value = MagicMock()
        
        payload = {
            "playbook": "---\n- name: Test playbook\n  hosts: all\n  tasks:\n    - debug:\n        msg: Hello"
        }
        
        response = self.client.post(
            "/analyze_playbook",
            json=payload
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("analysis", data)
        self.assertIn("suggestions", data)
        self.assertIn("security_issues", data)
    
    @patch('src.api.rest_api.load_model')
    def test_startup_event(self, mock_load_model):
        """Test the startup event handler."""
        # Mock model loader
        mock_model = MagicMock()
        mock_tokenizer = MagicMock()
        mock_load_model.return_value = (mock_model, mock_tokenizer)
        
        # Import inside test to ensure mocks are applied
        from src.api.rest_api import startup_event
        
        # Run the event handler
        import asyncio
        asyncio.run(startup_event())
        
        # Check that model was loaded
        mock_load_model.assert_called_once()
    
    @patch('src.api.rest_api.load_model')
    def test_startup_event_error(self, mock_load_model):
        """Test the startup event handler when model loading fails."""
        # Mock model loader
        mock_load_model.side_effect = Exception("Model loading failed")
        
        # Import inside test to ensure mocks are applied
        from src.api.rest_api import startup_event
        
        # Run the event handler
        import asyncio
        asyncio.run(startup_event())
        
        # Check that model was attempted to be loaded
        mock_load_model.assert_called_once()

if __name__ == '__main__':
    unittest.main()
