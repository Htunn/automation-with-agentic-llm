# Linux Automation Examples

This directory contains examples of Linux automation with Ansible and the LLM-driven automation framework. These examples showcase how to perform common system administration tasks on Linux systems.

## Available Resources

### Roles

- **linux_common**: A reusable role that provides common Linux system management tasks:
  - System information gathering
  - Package management
  - Security configuration
  - User management

### Playbooks

- **linux_system_management.yml**: A comprehensive playbook for managing Linux systems
  - Uses the linux_common role 
  - Creates system reports
  - Checks services
  
- **linux_security_hardening.yml**: A specialized playbook for hardening Linux security
  - SSH hardening
  - Firewall configuration
  - Fail2ban setup
  - Automatic security updates
  - File permissions

## Usage

### Running playbooks with the mock Linux host

Use the dev.sh script to run playbooks against the mock Linux host:

```
./dev.sh test-linux
```

### Using a specific playbook

```
# Start the mock Linux host
docker-compose -f docker-compose.dev.yml --profile integration up -d mock_linux_host

# Run the system management playbook
docker-compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_linux_host/inventory.ini src/examples/linux_automation/linux_system_management.yml -v

# Run the security hardening playbook
docker-compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_linux_host/inventory.ini src/examples/linux_automation/linux_security_hardening.yml -v
```

## Integration with LLM

These playbooks and roles can be used as a foundation for the LLM-driven automation. The LLM can:

1. Generate new tasks based on these examples
2. Customize playbooks for specific Linux distributions
3. Provide recommendations for optimizing systems
4. Answer questions about Linux system administration
5. Generate documentation for Linux automation tasks

## Extending the Examples

To extend these examples:

1. Add new tasks to the existing roles
2. Create new specialized roles for specific services (e.g., web servers, databases)
3. Develop new playbooks for specific use cases
4. Add support for additional Linux distributions
