"""
Unit tests for the model_download module.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.llm_engine.model_download import (
    get_model_path,
    list_available_models,
    download_model,
    AVAILABLE_MODELS
)


class TestModelDownload(unittest.TestCase):
    """Tests for the model_download module."""

    def setUp(self):
        """Set up test environment."""
        # Save any existing environment variable
        self.original_model_path = os.environ.get("ANSIBLE_LLM_MODEL_PATH")

    def tearDown(self):
        """Clean up test environment."""
        # Restore environment variable
        if self.original_model_path:
            os.environ["ANSIBLE_LLM_MODEL_PATH"] = self.original_model_path
        elif "ANSIBLE_LLM_MODEL_PATH" in os.environ:
            del os.environ["ANSIBLE_LLM_MODEL_PATH"]

    def test_get_model_path_from_env(self):
        """Test getting model path from environment variable."""
        test_path = "/test/model/path"
        os.environ["ANSIBLE_LLM_MODEL_PATH"] = test_path
        path = get_model_path()
        self.assertEqual(str(path), test_path)

    def test_get_model_path_default(self):
        """Test getting default model path."""
        if "ANSIBLE_LLM_MODEL_PATH" in os.environ:
            del os.environ["ANSIBLE_LLM_MODEL_PATH"]
        path = get_model_path()
        # Expected to be project_root/models
        expected = project_root / "models"
        self.assertEqual(path, expected)

    def test_available_models(self):
        """Test that available models dictionary is not empty."""
        self.assertTrue(len(AVAILABLE_MODELS) > 0)
        # Check structure (key -> repo_id)
        for model_id, repo_id in AVAILABLE_MODELS.items():
            self.assertIsInstance(model_id, str)
            self.assertIsInstance(repo_id, str)
            # Repository IDs typically have a / in them (organization/model)
            self.assertIn("/", repo_id)

    @patch("src.llm_engine.model_download.logger")
    def test_list_available_models(self, mock_logger):
        """Test listing available models."""
        list_available_models()
        # Verify logger was called
        self.assertTrue(mock_logger.info.called)
        # First call should be about available models
        self.assertIn("Available", mock_logger.info.call_args_list[0][0][0])

    @patch("src.llm_engine.model_download.snapshot_download")
    @patch("src.llm_engine.model_download.AutoTokenizer")
    @patch("src.llm_engine.model_download.AutoModelForCausalLM")
    @patch("src.llm_engine.model_download.logger")
    @patch("src.llm_engine.model_download.Path.exists")
    @patch("src.llm_engine.model_download.Path.mkdir")
    def test_download_model_already_exists(self, mock_mkdir, mock_exists, 
                                          mock_logger, mock_model, mock_tokenizer, 
                                          mock_snapshot):
        """Test downloading a model that already exists."""
        # Mock that the model already exists
        mock_exists.return_value = True
        
        # Call with force=False (default)
        result = download_model("tinyllama-1.1b")
        
        # Verify logger was called with "already exists" message
        mock_exists.assert_called_once()
        self.assertTrue(any("already exists" in str(args) 
                          for args in mock_logger.info.call_args_list))
        
        # Verify no download attempt was made
        mock_snapshot.assert_not_called()
        mock_tokenizer.from_pretrained.assert_not_called()
        mock_model.from_pretrained.assert_not_called()

    @patch("src.llm_engine.model_download.snapshot_download")
    @patch("src.llm_engine.model_download.AutoTokenizer")
    @patch("src.llm_engine.model_download.AutoModelForCausalLM")
    @patch("src.llm_engine.model_download.logger")
    @patch("src.llm_engine.model_download.Path.exists")
    @patch("src.llm_engine.model_download.Path.mkdir")
    def test_download_model_force(self, mock_mkdir, mock_exists, 
                                mock_logger, mock_model, mock_tokenizer, 
                                mock_snapshot):
        """Test force downloading a model that already exists."""
        # Mock that the model already exists
        mock_exists.return_value = True
        
        # Setup mock tokenizer and model
        mock_tokenizer.from_pretrained.return_value = MagicMock()
        mock_model.from_pretrained.return_value = MagicMock()
        
        # Call with force=True
        result = download_model("tinyllama-1.1b", force=True)
        
        # Verify download attempt was made despite model existing
        mock_snapshot.assert_called_once()
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()


if __name__ == "__main__":
    unittest.main()
