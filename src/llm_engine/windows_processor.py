"""
Response processor for Windows-specific tasks.
"""
import logging
import re
from src.llm_engine.response_processor import extract_yaml_from_response, validate_ansible_playbook

logger = logging.getLogger("ansible_llm")

def process_windows_ssh_response(response):
    """
    Process a Windows SSH playbook generation response from the LLM.
    Ensures proper SSH settings are applied for Windows hosts.
    
    Args:
        response: Raw response from the LLM
        
    Returns:
        dict: Processed and validated response with Windows SSH configurations
    """
    # First extract the YAML content
    yaml_content = extract_yaml_from_response(response)
    
    # Validate the playbook
    is_valid, validation_result = validate_ansible_playbook(yaml_content)
    
    if not is_valid:
        return {
            "raw_response": response,
            "yaml_content": yaml_content,
            "is_valid": False,
            "validation_message": validation_result,
            "processed_playbook": None
        }
    
    # Check and fix Windows SSH connection settings
    modified_yaml = ensure_windows_ssh_settings(yaml_content)
    
    return {
        "raw_response": response,
        "yaml_content": yaml_content,
        "modified_yaml": modified_yaml,
        "is_valid": True,
        "validation_message": "Valid Windows SSH Ansible playbook",
        "processed_playbook": validation_result
    }

def ensure_windows_ssh_settings(yaml_content):
    """
    Ensure that the YAML content has proper Windows SSH connection settings.
    
    Args:
        yaml_content: YAML content as a string
        
    Returns:
        str: Modified YAML content with proper Windows SSH settings
    """
    # Define patterns to search for
    hosts_pattern = re.compile(r'hosts:\s*([^\n]+)')
    vars_pattern = re.compile(r'vars:')
    
    # Check if any hosts are defined
    hosts_match = hosts_pattern.search(yaml_content)
    if not hosts_match:
        logger.warning("No hosts defined in Windows playbook")
        return yaml_content
    
    # Check if vars section exists
    vars_match = vars_pattern.search(yaml_content)
    ssh_settings = """
  vars:
    ansible_connection: ssh
    ansible_shell_type: cmd
    # Uncomment and set password if not using key-based authentication
    # ansible_password: "{{ windows_ssh_password }}"
"""
    
    if not vars_match:
        # Add vars section with SSH settings after hosts line
        hosts_line_end = hosts_match.end()
        modified_yaml = (
            yaml_content[:hosts_line_end] + 
            ssh_settings +
            yaml_content[hosts_line_end:]
        )
        logger.info("Added Windows SSH connection settings to playbook")
        return modified_yaml
    else:
        # Check if ssh settings exist in vars section
        if "ansible_connection: ssh" not in yaml_content:
            logger.warning("Windows playbook missing SSH connection settings")
            # Would need more complex modification to add to existing vars
            # For now, we'll just return a warning
            return yaml_content + "\n# WARNING: Consider adding 'ansible_connection: ssh' to vars section"
    
    return yaml_content

def validate_windows_modules(yaml_content):
    """
    Validate that Windows-specific modules are being used.
    
    Args:
        yaml_content: YAML content as a string
        
    Returns:
        tuple: (is_valid, message)
    """
    # List of common Windows modules
    windows_modules = [
        'win_copy', 'win_file', 'win_command', 'win_shell', 
        'win_package', 'win_service', 'win_feature'
    ]
    
    # Regular modules that should be replaced with Windows versions
    module_replacements = {
        'copy': 'win_copy',
        'file': 'win_file',
        'command': 'win_command',
        'shell': 'win_shell',
        'package': 'win_package',
        'service': 'win_service'
    }
    
    # Check if any Windows modules are being used
    has_windows_module = any(module in yaml_content for module in windows_modules)
    
    if not has_windows_module:
        logger.warning("No Windows-specific modules found in playbook")
        
        # Check for regular modules that should be replaced
        replacements_needed = []
        for regular, windows in module_replacements.items():
            if f"  {regular}:" in yaml_content and f"  {windows}:" not in yaml_content:
                replacements_needed.append(f"{regular} -> {windows}")
        
        if replacements_needed:
            message = "Consider replacing these modules with Windows versions: " + ", ".join(replacements_needed)
            return False, message
    
    return True, "Valid Windows modules used"
