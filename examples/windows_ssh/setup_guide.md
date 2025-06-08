# Setting Up Windows for SSH with Ansible

This guide explains how to set up Windows hosts for management via SSH with Ansible, instead of using the traditional WinRM approach.

## Prerequisites

- Windows Server 2019 or Windows 10 (1809+) with OpenSSH Server support
- Ansible 2.10+ on the control node
- Python 3.8+ on the control node

## Steps on Windows Hosts

1. **Install OpenSSH Server on Windows**

   Open PowerShell as Administrator and run:

   ```powershell
   # Check if OpenSSH is available
   Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
   
   # Install the OpenSSH Server
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   
   # Start the service
   Start-Service sshd
   
   # Make the service start automatically
   Set-Service -Name sshd -StartupType 'Automatic'
   
   # Confirm the Firewall rule is configured
   Get-NetFirewallRule -Name *ssh*
   ```

2. **Configure OpenSSH Server**

   Edit the `C:\ProgramData\ssh\sshd_config` file to allow public key authentication:

   ```
   PubkeyAuthentication yes
   PasswordAuthentication yes  # Set to no after setting up key auth
   ```

3. **Set up SSH Key Authentication (Optional but Recommended)**

   On your Ansible control node:

   ```bash
   # Generate a key if you don't already have one
   ssh-keygen -t rsa -b 4096
   
   # Copy the key to the Windows host
   ssh-copy-id Administrator@windows-host
   ```

   Alternatively, manually copy your public key to `C:\ProgramData\ssh\administrators_authorized_keys` on the Windows host.

   Ensure permissions are set correctly:

   ```powershell
   icacls.exe "C:\ProgramData\ssh\administrators_authorized_keys" /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"
   ```

4. **Restart the SSH Server**

   ```powershell
   Restart-Service sshd
   ```

## Ansible Configuration

1. **Configure Inventory**

   Create or modify your inventory file to use SSH for Windows hosts:

   ```ini
   [windows]
   win-server.example.com
   
   [windows:vars]
   ansible_connection=ssh
   ansible_shell_type=cmd
   ansible_user=Administrator
   # ansible_password=your_secure_password  # Use vault for passwords
   ansible_port=22
   ```

2. **Test the Connection**

   ```bash
   ansible windows -m win_ping
   ```

## Troubleshooting

- **Authentication Issues**: Check the SSH server logs at `C:\ProgramData\ssh\logs\sshd.log`
- **Connection Refused**: Ensure the SSH service is running and the firewall allows inbound connections on port 22
- **Command Execution Issues**: Use `ansible_shell_type=cmd` for Windows Command Prompt or `ansible_shell_type=powershell` for PowerShell

## Advantages of SSH over WinRM

- Consistent connection type across Linux and Windows hosts
- Better security with key-based authentication
- No need to configure WinRM with HTTPS and certificates
- Better performance for file transfers

## Additional Resources

- [OpenSSH for Windows Documentation](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)
- [Ansible Windows SSH Guide](https://docs.ansible.com/ansible/latest/os_guide/windows_setup.html#windows-ssh-setup)
