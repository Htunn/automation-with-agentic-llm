"""
Integration tests for the Linux processor module.
Tests the Linux processor's ability to generate and execute Linux automation.
"""

import os
import sys
import pytest
import subprocess
from unittest.mock import MagicMock

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.llm_engine.linux_processor import LinuxProcessor

class TestLinuxProcessor:
    """Test cases for the Linux processor."""
    
    def test_linux_processor_initialization(self):
        """Test creating a LinuxProcessor instance."""
        processor = LinuxProcessor()
        assert processor is not None
        
    def test_detect_linux_distribution(self):
        """Test the distribution detection function."""
        processor = LinuxProcessor()
        
        # Test Ubuntu detection
        facts = {"ansible_distribution": "Ubuntu", "ansible_distribution_version": "22.04"}
        distro, pkg_mgr = processor.detect_linux_distribution(facts)
        assert distro == "ubuntu"
        assert pkg_mgr == "apt"
        
        # Test CentOS detection
        facts = {"ansible_distribution": "CentOS", "ansible_distribution_version": "8"}
        distro, pkg_mgr = processor.detect_linux_distribution(facts)
        assert distro == "centos"
        assert pkg_mgr == "yum"
        
    def test_generate_package_tasks(self):
        """Test generating package installation tasks."""
        processor = LinuxProcessor()
        packages = ["nginx", "htop", "vim"]
        
        # Test apt tasks
        apt_tasks = processor.generate_package_tasks(packages, package_manager="apt")
        assert len(apt_tasks) >= 2  # Should have at least update cache and install tasks
        assert "apt" in str(apt_tasks)
        
        # Test with generic package manager
        generic_tasks = processor.generate_package_tasks(packages)
        assert len(generic_tasks) > 0
        
    def test_generate_service_tasks(self):
        """Test generating service management tasks."""
        processor = LinuxProcessor()
        service_tasks = processor.generate_service_tasks("nginx", "started", True)
        
        assert len(service_tasks) == 1
        assert service_tasks[0]["name"] == "Manage service nginx"
        assert service_tasks[0]["ansible.builtin.service"]["name"] == "nginx"
        assert service_tasks[0]["ansible.builtin.service"]["state"] == "started"
        assert service_tasks[0]["ansible.builtin.service"]["enabled"] is True
        
    def test_generate_user_tasks(self):
        """Test generating user management tasks."""
        processor = LinuxProcessor()
        user_tasks = processor.generate_user_tasks("testuser", groups=["sudo", "docker"])
        
        assert len(user_tasks) == 1
        assert user_tasks[0]["name"] == "Manage user testuser"
        assert user_tasks[0]["ansible.builtin.user"]["name"] == "testuser"
        assert "sudo" in user_tasks[0]["ansible.builtin.user"]["groups"]
        
    def test_generate_firewall_tasks(self):
        """Test generating firewall tasks."""
        processor = LinuxProcessor()
        fw_tasks = processor.generate_firewall_tasks(service_name="ssh")
        
        assert len(fw_tasks) > 0
        assert any("ssh" in str(task) for task in fw_tasks)
        
    @pytest.mark.skipif(not os.path.exists("/app/tests/mock_linux_host"), 
                       reason="Linux mock host environment not available")
    def test_process_linux_request_with_mock_llm(self):
        """Test processing a Linux request with a mock LLM."""
        # Create a mock model interface
        mock_model = MagicMock()
        mock_model.generate.return_value = """
        This playbook updates the system and installs Nginx.
        
        ```yaml
        ---
        - name: Install and configure Nginx
          hosts: linux
          become: true
          
          tasks:
            - name: Update apt cache
              apt:
                update_cache: yes
                
            - name: Install Nginx
              apt:
                name: nginx
                state: present
                
            - name: Start Nginx service
              service:
                name: nginx
                state: started
                enabled: yes
        ```
        """
        
        processor = LinuxProcessor(model_interface=mock_model)
        result = processor.process_linux_request("Install and configure Nginx")
        
        assert result["success"] is True
        assert "playbook" in result
        assert "explanation" in result
        assert "Install Nginx" in result["playbook_yaml"]
        
    def test_get_linux_facts_prompt(self):
        """Test getting the Linux facts prompt."""
        processor = LinuxProcessor()
        prompt = processor.get_linux_facts_prompt()
        
        assert prompt is not None
        assert "Gather Linux system facts" in prompt
        assert "ansible_distribution" in prompt
