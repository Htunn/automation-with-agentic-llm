#!/bin/bash
# This script sets up the mock Windows host container for testing

# Create directory for mock Windows host if it doesn't exist
mkdir -p tests/mock_windows_host

# Generate a test SSH key if it doesn't exist
if [ ! -f tests/mock_windows_host/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f tests/mock_windows_host/id_rsa -N ""
    cat tests/mock_windows_host/id_rsa.pub > tests/mock_windows_host/authorized_keys
    chmod 600 tests/mock_windows_host/id_rsa
    chmod 644 tests/mock_windows_host/authorized_keys
    echo "Generated SSH keys for mock Windows host"
fi

# Create a test inventory file for the mock Windows host
cat > tests/mock_windows_host/inventory.ini << EOF
[windows]
mock_windows ansible_host=mock_windows_host ansible_port=22 ansible_user=ansible_user ansible_password=ansible_password ansible_ssh_private_key_file=/app/tests/mock_windows_host/id_rsa

[windows:vars]
ansible_connection=ssh
ansible_shell_type=powershell
ansible_shell_executable=powershell
ansible_become=false
EOF

echo "Created test inventory for mock Windows host"
echo "Setup complete!"
