#!/bin/bash
# Setup SSH for the mock Linux host

# Install OpenSSH Server and other required packages
apt-get update
apt-get install -y openssh-server sudo python3 python3-pip

# Configure SSH
mkdir -p /var/run/sshd
echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config
echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config

# Create ansible user
useradd -m ansible_user
usermod -aG sudo ansible_user
echo "ansible_user:ansible_password" | chpasswd
echo "ansible_user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Setup SSH keys
if [ -f /config/id_rsa.pub ]; then
    mkdir -p /home/ansible_user/.ssh
    cp /config/id_rsa.pub /home/ansible_user/.ssh/authorized_keys
    chmod 700 /home/ansible_user/.ssh
    chmod 600 /home/ansible_user/.ssh/authorized_keys
    chown -R ansible_user:ansible_user /home/ansible_user/.ssh
    echo "SSH key-based authentication configured"
else
    echo "No SSH key found at /config/id_rsa.pub"
fi

# Configure and start SSH properly
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
echo "ListenAddress 0.0.0.0" >> /etc/ssh/sshd_config
echo "LogLevel DEBUG3" >> /etc/ssh/sshd_config

# Make sure we have SSH host keys
ssh-keygen -A

# DO NOT start SSH in background (let the entrypoint handle it)
echo "Checking SSH configuration:"
cat /etc/ssh/sshd_config | grep -E 'PasswordAuthentication|PermitRootLogin|PubkeyAuthentication|ListenAddress'

# Check available network interfaces
echo "Network interfaces:"
ip addr

# Print ports in use
echo "Listening ports:"
netstat -tulpn || ss -tulpn

# Setup test directories and files
mkdir -p /home/ansible_user/test_dir
echo "Test file content" > /home/ansible_user/test_dir/test_file.txt
mkdir -p /home/ansible_user/.ansible/tmp
chmod 700 /home/ansible_user/.ansible/tmp
chown -R ansible_user:ansible_user /home/ansible_user/test_dir
chown -R ansible_user:ansible_user /home/ansible_user/.ansible

# Install Python packages for Ansible testing
pip3 install pytest pytest-ansible

# Generate host keys if not present
ssh-keygen -A

echo "Mock Linux host setup complete"
