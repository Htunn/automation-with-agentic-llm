"""
Unit tests for the TinyLlama Model Loader.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.llm_engine.model_loader import get_model_path, load_model

class TestModelLoader:
    """Tests for the model_loader module."""
    
    def test_get_model_path_env_var(self):
        """Test that get_model_path uses the environment variable if set."""
        with patch.dict(os.environ, {"ANSIBLE_LLM_MODEL_PATH": "/test/path"}):
            path = get_model_path()
            assert str(path) == "/test/path"
    
    def test_get_model_path_default(self):
        """Test that get_model_path returns the default path if no env var is set."""
        with patch.dict(os.environ, clear=True):
            path = get_model_path()
            assert "models" in str(path)
    
    @patch("src.llm_engine.model_loader.AutoModelForCausalLM")
    @patch("src.llm_engine.model_loader.AutoTokenizer")
    @patch("src.llm_engine.model_loader.torch")
    def test_load_model_basic(self, mock_torch, mock_tokenizer, mock_model):
        """Test that load_model loads the model and tokenizer."""
        # Setup mocks
        mock_torch.cuda.is_available.return_value = False
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        
        # Call function
        model, tokenizer = load_model(model_name="test-model")
        
        # Assert
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()
        assert model is not None
        assert tokenizer is not None
