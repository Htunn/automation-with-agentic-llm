"""Integration tests for Linux SSH functionality."""

import pytest
import subprocess
import os

def test_linux_ssh_connectivity():
    """Test the SSH connectivity to the mock Linux host."""
    result = subprocess.run(
        ["sshpass", "-p", "ansible_password", 
         "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", 
         "ansible_user@mock_linux_host", "echo 'SSH Connection Test'"],
        capture_output=True,
        text=True,
        check=False
    )
    
    assert result.returncode == 0, f"SSH connection failed with: {result.stderr}"
    assert "SSH Connection Test" in result.stdout, "Expected test string not found in output"

def test_linux_ansible_ping():
    """Test the Ansible ping module against mock Linux host."""
    result = subprocess.run(
        ["ansible", "-i", "/app/tests/mock_linux_host/inventory.ini", "linux", "-m", "ping"],
        capture_output=True,
        text=True,
        env={**os.environ, "ANSIBLE_HOST_KEY_CHECKING": "False"},
        check=False
    )
    
    assert result.returncode == 0, f"Ansible ping failed with: {result.stderr}"
    assert "SUCCESS" in result.stdout, "Expected 'SUCCESS' not found in ping output"

def test_linux_command_module():
    """Test the Ansible command module against mock Linux host."""
    result = subprocess.run(
        ["ansible", "-i", "/app/tests/mock_linux_host/inventory.ini", "linux", 
         "-m", "command", "-a", "uname -a"],
        capture_output=True,
        text=True,
        env={**os.environ, "ANSIBLE_HOST_KEY_CHECKING": "False"},
        check=False
    )
    
    assert result.returncode == 0, f"Ansible command failed with: {result.stderr}"
    assert "Linux" in result.stdout, "Expected 'Linux' not found in command output"
