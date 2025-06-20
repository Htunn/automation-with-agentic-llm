#!/bin/bash
# This script sets up the mock hosts containers for testing

# Create directories for mock hosts if they don't exist
mkdir -p tests/mock_windows_host
mkdir -p tests/mock_linux_host

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

# Generate a test SSH key for mock Linux host if it doesn't exist
if [ ! -f tests/mock_linux_host/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f tests/mock_linux_host/id_rsa -N ""
    chmod 600 tests/mock_linux_host/id_rsa
    chmod 644 tests/mock_linux_host/id_rsa.pub
    echo "Generated SSH keys for mock Linux host"
fi

# Create a test inventory file for the mock Linux host
cat > tests/mock_linux_host/inventory.ini << EOF
[linux]
mock_linux ansible_host=mock_linux_host ansible_port=22 ansible_user=ansible_user ansible_password=ansible_password ansible_ssh_private_key_file=/app/tests/mock_linux_host/id_rsa

[linux:vars]
ansible_connection=ssh
ansible_python_interpreter=/usr/bin/python3
ansible_become=true
ansible_become_method=sudo
ansible_become_user=root
EOF

echo "Created test inventory for mock Linux host"

# Create SSH config directory in your user's home directory if it doesn't exist
mkdir -p ~/.ssh
# Add entries to SSH config to disable host key checking for test hosts
cat > ~/.ssh/config << EOF
Host mock_linux_host
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null

Host mock_windows_host
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
EOF

chmod 600 ~/.ssh/config
echo "Updated SSH config for host key checking"
echo "Setup complete!"
