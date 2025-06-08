"""
Integration tests for the CLI functionality.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_cli_help():
    """Test that the CLI help command works."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Run the CLI with the help flag
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "--help"],
        cwd=str(project_root),
        capture_output=True,
        text=True
    )
    
    # Check that the command succeeded
    assert result.returncode == 0
    
    # Check that the output contains expected help text
    assert "Ansible TinyLlama 3 Integration" in result.stdout
    assert "cli" in result.stdout
    assert "api" in result.stdout
    assert "model" in result.stdout
