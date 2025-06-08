# Windows SSH Automation Quick Start Guide

This guide provides a quick start for using the Ansible TinyLlama Integration specifically for Windows automation via SSH.

## Prerequisites

- Python 3.12+
- Ansible 2.14+
- Windows hosts with OpenSSH Server installed
- SSH access to Windows machines

## Setup Steps

1. **Set up your environment**

   ```bash
   # Clone the repository (if not already done)
   git clone <repository-url>
   cd ansible-llm
   
   # Create and activate virtual environment
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install requirements
   pip install -r requirements.txt
   
   # Run setup with Windows SSH option
   python setup.py --setup-windows-ssh
   ```

2. **Configure Windows hosts for SSH**

   Follow the detailed guide in `examples/windows_ssh/setup_guide.md` to:
   
   - Install OpenSSH Server on Windows
   - Configure SSH for authentication
   - Set appropriate firewall rules
   - Enable key-based authentication (recommended)

3. **Update inventory file**

   Edit the inventory file at `examples/windows_ssh/inventory.ini` with your Windows hosts:
   
   ```ini
   [windows_servers]
   win-server1.example.com
   win-server2.example.com

   [windows_servers:vars]
   ansible_connection=ssh
   ansible_shell_type=cmd
   ansible_user=Administrator
   # Use SSH key authentication or store passwords in a vault
   # ansible_password=your_secure_password
   ansible_port=22
   ```

4. **Run an example playbook**

   ```bash
   ansible-playbook -i examples/windows_ssh/inventory.ini examples/windows_ssh/example_playbook.yml
   ```

5. **Generate Windows-specific playbooks with TinyLlama**

   ```bash
   # Start the CLI
   python -m src.main cli
   
   # Generate a playbook (once model is installed)
   python -m src.main cli generate-playbook "Install and configure IIS on Windows servers"
   ```

## Key Concepts

### Windows SSH vs WinRM

This project uses SSH instead of WinRM for Windows automation because:

- SSH is more consistent across platforms
- SSH has better security with key-based authentication
- SSH doesn't require complex HTTPS/certificate setup
- SSH has better performance for file transfers

### Windows Modules

When automating Windows via SSH, use Windows-specific Ansible modules:

- `win_file` instead of `file`
- `win_copy` instead of `copy`
- `win_shell` instead of `shell`
- `win_command` instead of `command`
- `win_package` for software installation
- `win_service` for Windows services
- `win_feature` for Windows features

### SSH Connection Settings

Always include these connection settings in your playbooks:

```yaml
vars:
  ansible_connection: ssh
  ansible_shell_type: cmd
```

## Troubleshooting

- **Connection Issues**: Verify SSH server is running and port 22 is accessible
- **Authentication Failures**: Check user credentials and SSH key permissions
- **Command Execution Errors**: Make sure `ansible_shell_type` is set to `cmd`
- **Module Failures**: Verify you're using Windows-specific modules (`win_*`)

## Example Workflows

See the `examples/windows_ssh` directory for:

- Basic Windows server management
- OpenSSH Server setup
- Sample inventory configuration

## Get Help

Run the demo script for a guided experience:

```bash
./examples/windows_ssh/demo.sh
```
