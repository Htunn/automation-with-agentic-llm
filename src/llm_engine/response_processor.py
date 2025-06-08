"""
Process and validate LLM responses.
"""
import yaml
import json
import logging

logger = logging.getLogger("ansible_llm")

def extract_yaml_from_response(response):
    """
    Extract YAML content from the LLM response.
    
    Args:
        response: The raw response from the LLM
        
    Returns:
        str: Extracted YAML content
    """
    # Look for YAML code block markers
    yaml_markers = ["```yaml", "```yml"]
    end_marker = "```"
    
    for marker in yaml_markers:
        if marker in response:
            start_idx = response.find(marker) + len(marker)
            end_idx = response.find(end_marker, start_idx)
            
            if end_idx > start_idx:
                return response[start_idx:end_idx].strip()
    
    # If no markers found, try to extract based on content
    if "---" in response:
        # This might be a YAML document without code block markers
        lines = response.split("\n")
        yaml_lines = []
        in_yaml = False
        
        for line in lines:
            if line.strip() == "---":
                in_yaml = True
                yaml_lines.append(line)
            elif in_yaml:
                yaml_lines.append(line)
        
        if yaml_lines:
            return "\n".join(yaml_lines)
    
    # If no YAML markers found, return the original response
    logger.warning("No YAML markers found in response")
    return response

def validate_yaml(yaml_content):
    """
    Validate that the string is valid YAML.
    
    Args:
        yaml_content: The YAML string to validate
        
    Returns:
        tuple: (is_valid, parsed_yaml or error_message)
    """
    try:
        parsed_yaml = yaml.safe_load(yaml_content)
        return True, parsed_yaml
    except yaml.YAMLError as e:
        logger.error(f"YAML validation error: {e}")
        return False, str(e)

def validate_ansible_playbook(playbook_content):
    """
    Validate that the YAML content is a valid Ansible playbook.
    
    Args:
        playbook_content: The playbook YAML
        
    Returns:
        tuple: (is_valid, error_message or None)
    """
    # First validate as YAML
    is_valid, parsed_yaml = validate_yaml(playbook_content)
    if not is_valid:
        return False, f"Invalid YAML: {parsed_yaml}"
    
    # Check if it's a list (Ansible playbooks should be a list of plays)
    if not isinstance(parsed_yaml, list):
        return False, "Playbook should be a list of plays"
    
    # Check if it has at least one play
    if len(parsed_yaml) == 0:
        return False, "Playbook should have at least one play"
    
    # Check if each play has required fields
    for i, play in enumerate(parsed_yaml):
        if not isinstance(play, dict):
            return False, f"Play #{i+1} should be a dictionary"
        
        if "hosts" not in play:
            return False, f"Play #{i+1} is missing 'hosts' field"
        
        if "tasks" not in play and "roles" not in play:
            return False, f"Play #{i+1} should have either 'tasks' or 'roles'"
    
    return True, None

def process_playbook_response(response):
    """
    Process a playbook generation response from the LLM.
    
    Args:
        response: The raw response from the LLM
        
    Returns:
        dict: Processed response with validation information
    """
    yaml_content = extract_yaml_from_response(response)
    is_valid, validation_result = validate_ansible_playbook(yaml_content)
    
    return {
        "raw_response": response,
        "yaml_content": yaml_content,
        "is_valid": is_valid,
        "validation_message": validation_result if not is_valid else "Valid Ansible playbook",
        "processed_playbook": validation_result if is_valid else None
    }

def process_analysis_response(response):
    """
    Process an analysis response from the LLM.
    
    Args:
        response: The raw response from the LLM
        
    Returns:
        dict: Structured analysis
    """
    # Try to identify and extract structured information
    analysis = {
        "summary": "",
        "issues": [],
        "security": [],
        "best_practices": []
    }
    
    # Extract sections
    lines = response.split("\n")
    current_section = None
    
    for line in lines:
        if "summary" in line.lower() and ":" in line:
            current_section = "summary"
            continue
        elif "issue" in line.lower() and ":" in line:
            current_section = "issues"
            continue
        elif "security" in line.lower() and ":" in line:
            current_section = "security"
            continue
        elif "best practice" in line.lower() and ":" in line:
            current_section = "best_practices"
            continue
        
        if current_section == "summary":
            analysis["summary"] += line + "\n"
        elif current_section in ["issues", "security", "best_practices"]:
            if line.strip().startswith("- "):
                analysis[current_section].append(line.strip()[2:])
    
    return {
        "raw_response": response,
        "structured_analysis": analysis
    }
