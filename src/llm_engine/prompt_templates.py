"""
Prompt templates for TinyLlama 3.
"""

# Template for generating an Ansible playbook from a natural language description
PLAYBOOK_GENERATION_TEMPLATE = """
You are an Ansible automation expert. Create a well-structured Ansible playbook that accomplishes the following task:

{user_task_description}

Target environment: {environment_details}
Available inventory: {inventory_summary}
Company best practices: {best_practices}

Generate a complete, production-ready playbook following Ansible best practices.
"""

# Template for analyzing an existing Ansible playbook
PLAYBOOK_ANALYSIS_TEMPLATE = """
You are an Ansible automation expert. Analyze the following Ansible playbook and provide:
1. A summary of what the playbook does
2. Potential issues or improvements
3. Security considerations
4. Best practices that should be applied

Playbook:
{playbook_content}
"""

# Template for Windows SSH automation
WINDOWS_SSH_TEMPLATE = """
You are an Ansible automation expert specialized in Windows automation using SSH instead of WinRM. 
Create a well-structured Ansible playbook that accomplishes the following task on Windows hosts:

{user_task_description}

Ensure you use the SSH connection method and appropriate modules for Windows hosts.
Include any necessary configuration or setup steps for SSH on Windows.

Generate a complete, production-ready playbook following Ansible best practices.
"""

# Template for generating infrastructure analysis
INFRASTRUCTURE_ANALYSIS_TEMPLATE = """
You are an infrastructure automation expert. Analyze the following Ansible inventory and provide insights:

1. Infrastructure composition and organization
2. Potential optimization opportunities
3. Security considerations
4. Recommendations for better management

Inventory:
{inventory_content}
"""

# Template for dynamic decision making during playbook execution
DECISION_MAKING_TEMPLATE = """
You are an Ansible automation expert. Based on the following playbook execution results,
make a recommendation for the next steps:

Playbook: {playbook_name}
Task that failed: {failed_task}
Error message: {error_message}
Host details: {host_details}
Previous task results: {previous_results}

Provide specific recommendations on how to resolve this issue and continue the automation.
"""
