"""Integration tests for Linux host functionality."""

import pytest
import subprocess
import os
import sys
import time

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_linux_ssh_connectivity():
    """Test SSH connectivity to the mock Linux host."""
    result = subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", 
         "-p", "2223", "ansible_user@localhost", "echo", "SSH Connection Test"],
        capture_output=True,
        text=True
    )
    
    print(f"SSH connection test stdout: {result.stdout}")
    print(f"SSH connection test stderr: {result.stderr}")
    assert result.returncode == 0, f"SSH connection failed with: {result.stderr}"
    assert "SSH Connection Test" in result.stdout, "Expected test string not found in output"

def test_linux_ansible_ping():
    """Test Ansible ping module against the Linux host."""
    result = subprocess.run(
        ["ansible", "-i", "tests/mock_linux_host/inventory.ini", "linux", 
         "-m", "ping", "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Ansible ping test stdout: {result.stdout}")
    print(f"Ansible ping test stderr: {result.stderr}")
    assert result.returncode == 0, f"Ansible ping failed with: {result.stderr}"
    assert "SUCCESS" in result.stdout, "Expected 'SUCCESS' not found in ping output"

def test_linux_ansible_gather_facts():
    """Test gathering facts from the Linux host."""
    result = subprocess.run(
        ["ansible", "-i", "tests/mock_linux_host/inventory.ini", "linux", 
         "-m", "setup", "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Ansible setup test stdout: {result.stdout}")
    print(f"Ansible setup test stderr: {result.stderr}")
    assert result.returncode == 0, f"Ansible setup failed with: {result.stderr}"
    assert "ansible_distribution" in result.stdout, "Expected fact 'ansible_distribution' not found in output"
    assert "Ubuntu" in result.stdout, "Expected Ubuntu distribution not found in output"

def test_linux_ansible_command():
    """Test running a command on the Linux host via Ansible."""
    result = subprocess.run(
        ["ansible", "-i", "tests/mock_linux_host/inventory.ini", "linux", 
         "-m", "command", "-a", "python3 --version", 
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Ansible command test stdout: {result.stdout}")
    print(f"Ansible command test stderr: {result.stderr}")
    assert result.returncode == 0, f"Ansible command failed with: {result.stderr}"
    assert "Python 3" in result.stdout, "Expected 'Python 3' not found in command output"

def test_linux_ansible_playbook():
    """Test running the test playbook on the Linux host."""
    result = subprocess.run(
        ["ansible-playbook", "-i", "tests/mock_linux_host/inventory.ini", 
         "tests/mock_linux_host/test_playbook.yml", 
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Ansible playbook test stdout: {result.stdout}")
    print(f"Ansible playbook test stderr: {result.stderr}")
    assert result.returncode == 0, f"Ansible playbook failed with: {result.stderr}"
    assert "changed=" in result.stdout, "Expected 'changed=' not found in playbook output"
