"""
Linux Processor for handling Linux-specific automation tasks with LLM guidance.
This module integrates with the LLM engine to process Linux-specific requests
and generate relevant Ansible automation code.
"""

import os
import re
import yaml
import logging
from typing import Dict, List, Optional, Tuple, Union, Any

# Get the logger
logger = logging.getLogger(__name__)

class LinuxProcessor:
    """
    Processes Linux-specific requests and generates appropriate Ansible automation.
    Designed to integrate with the LLM engine.
    """
    
    def __init__(self, model_interface=None):
        """
        Initialize the Linux Processor.
        
        Args:
            model_interface: The LLM model interface to use for generating responses
        """
        self.model_interface = model_interface
        self.distro_package_managers = {
            'ubuntu': 'apt',
            'debian': 'apt',
            'centos': 'yum',
            'redhat': 'yum',
            'fedora': 'dnf',
            'suse': 'zypper',
            'arch': 'pacman',
            'alpine': 'apk'
        }
    
    def detect_linux_distribution(self, facts: Dict) -> Tuple[str, str]:
        """
        Detect Linux distribution based on Ansible facts.
        
        Args:
            facts: Ansible gathered facts dictionary
            
        Returns:
            Tuple of (distribution_name, package_manager)
        """
        if not facts or 'ansible_distribution' not in facts:
            return 'unknown', 'unknown'
            
        distro = facts['ansible_distribution'].lower()
        
        # Find matching package manager
        for key, manager in self.distro_package_managers.items():
            if key in distro:
                return distro, manager
                
        return distro, 'unknown'
    
    def generate_package_tasks(self, 
                              packages: List[str], 
                              state: str = 'present',
                              package_manager: str = None) -> List[Dict]:
        """
        Generate package installation tasks based on the package manager.
        
        Args:
            packages: List of packages to install
            state: State of packages (present, absent, latest)
            package_manager: Package manager to use, or None for automatic
            
        Returns:
            List of Ansible tasks
        """
        tasks = []
        
        if not package_manager or package_manager == 'apt':
            # For Debian/Ubuntu systems
            tasks.append({
                'name': f'Update package cache',
                'ansible.builtin.apt': {
                    'update_cache': True,
                    'cache_valid_time': 3600
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "Debian"'
            })
            
            tasks.append({
                'name': f'Install packages with apt',
                'ansible.builtin.apt': {
                    'name': packages,
                    'state': state
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "Debian"'
            })
            
        if not package_manager or package_manager in ['yum', 'dnf']:
            # For RedHat/CentOS/Fedora systems
            tasks.append({
                'name': f'Install packages with yum/dnf',
                'ansible.builtin.package': {
                    'name': packages,
                    'state': state
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "RedHat"'
            })
            
        if not package_manager or package_manager == 'zypper':
            # For SUSE systems
            tasks.append({
                'name': f'Install packages with zypper',
                'ansible.builtin.zypper': {
                    'name': packages,
                    'state': state
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "Suse"'
            })
            
        if not package_manager or package_manager == 'pacman':
            # For Arch Linux systems
            tasks.append({
                'name': f'Install packages with pacman',
                'ansible.builtin.pacman': {
                    'name': packages,
                    'state': state,
                    'update_cache': True
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "Archlinux"'
            })
            
        # Add a generic fallback if no specific package manager is matched
        if not tasks:
            tasks.append({
                'name': f'Install packages using generic package module',
                'ansible.builtin.package': {
                    'name': packages,
                    'state': state
                },
                'become': True
            })
            
        return tasks
    
    def generate_service_tasks(self, 
                              service_name: str, 
                              state: str = 'started', 
                              enabled: bool = True) -> List[Dict]:
        """
        Generate service management tasks.
        
        Args:
            service_name: Name of the service
            state: State of the service (started, stopped, restarted)
            enabled: Whether to enable the service on boot
            
        Returns:
            List of Ansible tasks
        """
        return [{
            'name': f'Manage service {service_name}',
            'ansible.builtin.service': {
                'name': service_name,
                'state': state,
                'enabled': enabled
            },
            'become': True
        }]
    
    def generate_user_tasks(self, 
                           username: str, 
                           state: str = 'present',
                           groups: List[str] = None,
                           shell: str = '/bin/bash',
                           create_home: bool = True) -> List[Dict]:
        """
        Generate user management tasks.
        
        Args:
            username: Username to create/modify
            state: present or absent
            groups: List of groups to add the user to
            shell: Default shell
            create_home: Whether to create home directory
            
        Returns:
            List of Ansible tasks
        """
        user_task = {
            'name': f'Manage user {username}',
            'ansible.builtin.user': {
                'name': username,
                'state': state,
                'shell': shell,
                'create_home': create_home
            },
            'become': True
        }
        
        if groups:
            user_task['ansible.builtin.user']['groups'] = groups
            
        return [user_task]
    
    def generate_firewall_tasks(self, 
                               service_name: str = None,
                               port: Union[int, str] = None,
                               protocol: str = 'tcp',
                               state: str = 'enabled') -> List[Dict]:
        """
        Generate firewall management tasks (using ufw for Ubuntu/Debian)
        
        Args:
            service_name: Name of the service to allow
            port: Port number to allow
            protocol: Protocol (tcp, udp)
            state: enabled or disabled
            
        Returns:
            List of Ansible tasks
        """
        tasks = []
        
        # Install ufw if needed (Debian/Ubuntu)
        tasks.append({
            'name': 'Install ufw (Uncomplicated Firewall)',
            'ansible.builtin.apt': {
                'name': 'ufw',
                'state': 'present'
            },
            'become': True,
            'when': 'ansible_facts["os_family"] == "Debian"'
        })
        
        # For RHEL systems, use firewalld
        tasks.append({
            'name': 'Install firewalld',
            'ansible.builtin.package': {
                'name': 'firewalld',
                'state': 'present'
            },
            'become': True,
            'when': 'ansible_facts["os_family"] == "RedHat"'
        })
        
        # Configure firewall rules
        if service_name:
            tasks.append({
                'name': f'Allow {service_name} in ufw',
                'ansible.builtin.ufw': {
                    'rule': 'allow',
                    'name': service_name
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "Debian"'
            })
            
            tasks.append({
                'name': f'Allow {service_name} in firewalld',
                'ansible.posix.firewalld': {
                    'service': service_name,
                    'permanent': True,
                    'state': 'enabled'
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "RedHat"'
            })
        
        if port:
            tasks.append({
                'name': f'Allow port {port}/{protocol} in ufw',
                'ansible.builtin.ufw': {
                    'rule': 'allow',
                    'port': str(port),
                    'proto': protocol
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "Debian"'
            })
            
            tasks.append({
                'name': f'Allow port {port}/{protocol} in firewalld',
                'ansible.posix.firewalld': {
                    'port': f'{port}/{protocol}',
                    'permanent': True,
                    'state': 'enabled'
                },
                'become': True,
                'when': 'ansible_facts["os_family"] == "RedHat"'
            })
        
        # Ensure firewall is enabled
        tasks.append({
            'name': 'Enable ufw',
            'ansible.builtin.ufw': {
                'state': state
            },
            'become': True,
            'when': 'ansible_facts["os_family"] == "Debian"'
        })
        
        tasks.append({
            'name': 'Enable firewalld',
            'ansible.builtin.service': {
                'name': 'firewalld',
                'state': 'started',
                'enabled': True
            },
            'become': True,
            'when': 'ansible_facts["os_family"] == "RedHat"'
        })
        
        return tasks
    
    def process_linux_request(self, user_request: str) -> Dict:
        """
        Process a Linux-specific request using LLM and generate Ansible code.
        
        Args:
            user_request: User's request for Linux automation
            
        Returns:
            Dictionary with the generated automation code and explanation
        """
        if not self.model_interface:
            logger.warning("No model interface provided. Cannot process request.")
            return {
                "success": False,
                "error": "Model interface not available for Linux processing"
            }
        
        # Generate prompt for the LLM
        prompt = f"""
        You are an expert in Linux system administration and Ansible automation.
        Please generate Ansible code for the following Linux automation request:
        
        REQUEST: {user_request}
        
        Provide your response in the following format:
        1. A brief explanation of the task
        2. A complete Ansible playbook in YAML format
        """
        
        # Get response from LLM
        try:
            response = self.model_interface.generate(prompt)
            
            # Extract the playbook from the response
            playbook_match = re.search(r"```(?:yaml|ansible)?\s*(---[\s\S]*?)```", response)
            
            if not playbook_match:
                logger.warning("Could not extract valid Ansible playbook from LLM response.")
                return {
                    "success": False,
                    "error": "Failed to generate valid Ansible playbook",
                    "raw_response": response
                }
            
            playbook_yaml = playbook_match.group(1).strip()
            
            # Validate the YAML
            try:
                playbook = yaml.safe_load(playbook_yaml)
            except Exception as e:
                logger.warning(f"Generated YAML is invalid: {e}")
                return {
                    "success": False,
                    "error": f"Generated YAML is invalid: {e}",
                    "raw_response": response
                }
            
            # Extract explanation (everything before the first code block)
            explanation = response.split("```")[0].strip()
            
            return {
                "success": True,
                "explanation": explanation,
                "playbook": playbook,
                "playbook_yaml": playbook_yaml
            }
            
        except Exception as e:
            logger.error(f"Error processing Linux request: {e}")
            return {
                "success": False,
                "error": f"Error processing request: {e}"
            }
    
    def get_linux_facts_prompt(self) -> str:
        """
        Generate a prompt for collecting Linux system facts.
        
        Returns:
            Ansible playbook as string for fact gathering
        """
        return """---
- name: Gather Linux system facts
  hosts: linux
  gather_facts: true
  
  tasks:
    - name: Display Linux distribution information
      ansible.builtin.debug:
        var: ansible_distribution
        
    - name: Display Linux version
      ansible.builtin.debug:
        var: ansible_distribution_version
        
    - name: Display kernel information
      ansible.builtin.debug:
        var: ansible_kernel
        
    - name: Display system architecture
      ansible.builtin.debug:
        var: ansible_architecture
        
    - name: Display memory information
      ansible.builtin.debug:
        msg: "{{ ansible_memtotal_mb }} MB total memory"
        
    - name: Display processor information
      ansible.builtin.debug:
        var: ansible_processor
"""
