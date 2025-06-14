"""
Advanced integration tests for Linux automation features.
Tests the execution of Linux-specific playbooks against the mock Linux host.
"""

import os
import sys
import pytest
import subprocess
import time

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_linux_system_management_playbook():
    """Test running the Linux system management playbook."""
    result = subprocess.run(
        ["ansible-playbook", "-i", "tests/mock_linux_host/inventory.ini", 
         "src/examples/linux_automation/linux_system_management.yml",
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Playbook stdout: {result.stdout}")
    print(f"Playbook stderr: {result.stderr}")
    
    assert result.returncode == 0, f"Linux system management playbook failed: {result.stderr}"
    assert "failed=0" in result.stdout, "Playbook reported failures"
    
    # Check for expected output from the playbook
    assert "System Report" in result.stdout or "system_report" in result.stdout
    assert "PLAY RECAP" in result.stdout

def test_linux_security_hardening_playbook():
    """Test running the Linux security hardening playbook."""
    result = subprocess.run(
        ["ansible-playbook", "-i", "tests/mock_linux_host/inventory.ini", 
         "src/examples/linux_automation/linux_security_hardening.yml",
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Playbook stdout: {result.stdout}")
    print(f"Playbook stderr: {result.stderr}")
    
    assert result.returncode == 0, f"Linux security hardening playbook failed: {result.stderr}"
    assert "failed=0" in result.stdout, "Playbook reported failures"
    
    # Check for expected security features
    assert "SSH" in result.stdout and "hardening" in result.stdout
    assert "ufw" in result.stdout.lower() or "firewall" in result.stdout.lower()

def test_linux_common_role():
    """Test the linux_common role using a simple test playbook."""
    # Create a temporary test playbook
    test_playbook = """---
- name: Test linux_common role
  hosts: linux
  gather_facts: true
  
  roles:
    - linux_common
"""
    
    # Write test playbook to a temporary file
    with open("/tmp/test_linux_common_role.yml", "w") as f:
        f.write(test_playbook)
    
    # Run the test playbook
    result = subprocess.run(
        ["ansible-playbook", "-i", "tests/mock_linux_host/inventory.ini", 
         "/tmp/test_linux_common_role.yml",
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Role test stdout: {result.stdout}")
    print(f"Role test stderr: {result.stderr}")
    
    assert result.returncode == 0, f"Linux common role test failed: {result.stderr}"
    assert "failed=0" in result.stdout, "Role reported failures"

def test_linux_package_installation():
    """Test installing a package on the Linux host."""
    # Define a simple playbook to install a package
    test_playbook = """---
- name: Test package installation
  hosts: linux
  become: true
  
  tasks:
    - name: Update cache
      apt:
        update_cache: yes
      
    - name: Install a specific package
      apt:
        name: tree
        state: present
        
    - name: Verify package installation
      command: which tree
      register: cmd_result
      changed_when: false
      failed_when: cmd_result.rc != 0
"""
    
    # Write test playbook to a temporary file
    with open("/tmp/test_linux_package.yml", "w") as f:
        f.write(test_playbook)
    
    # Run the test playbook
    result = subprocess.run(
        ["ansible-playbook", "-i", "tests/mock_linux_host/inventory.ini", 
         "/tmp/test_linux_package.yml",
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"Package test stdout: {result.stdout}")
    print(f"Package test stderr: {result.stderr}")
    
    assert result.returncode == 0, f"Package installation test failed: {result.stderr}"
    assert "failed=0" in result.stdout, "Package installation reported failures"

def test_linux_file_operations():
    """Test file operations on the Linux host."""
    # Define a simple playbook to perform file operations
    test_playbook = """---
- name: Test file operations
  hosts: linux
  
  tasks:
    - name: Create a directory
      file:
        path: /home/ansible_user/test_directory
        state: directory
        mode: '0755'
      
    - name: Create a file with content
      copy:
        content: |
          This is a test file
          Created by Ansible automation tests
          Testing Linux file operations
        dest: /home/ansible_user/test_directory/test_file.txt
        mode: '0644'
        
    - name: Read the file content
      command: cat /home/ansible_user/test_directory/test_file.txt
      register: file_content
      changed_when: false
      
    - name: Verify file content
      assert:
        that: "'Created by Ansible automation tests' in file_content.stdout"
        fail_msg: "File content verification failed"
"""
    
    # Write test playbook to a temporary file
    with open("/tmp/test_linux_file_ops.yml", "w") as f:
        f.write(test_playbook)
    
    # Run the test playbook
    result = subprocess.run(
        ["ansible-playbook", "-i", "tests/mock_linux_host/inventory.ini", 
         "/tmp/test_linux_file_ops.yml",
         "-e", "ansible_host_key_checking=false"],
        capture_output=True,
        text=True
    )
    
    print(f"File operations test stdout: {result.stdout}")
    print(f"File operations test stderr: {result.stderr}")
    
    assert result.returncode == 0, f"File operations test failed: {result.stderr}"
    assert "failed=0" in result.stdout, "File operations reported failures"
