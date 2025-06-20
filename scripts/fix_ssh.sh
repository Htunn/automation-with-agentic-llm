#!/bin/bash
# Script to fix SSH connection issues with test hosts

echo "Fixing SSH connection issues for mock hosts..."

# Create directory structure
mkdir -p tests/mock_linux_host
mkdir -p tests/mock_windows_host

# Generate fresh SSH keys for both hosts
echo "Generating new SSH keys for both hosts..."
ssh-keygen -t rsa -b 4096 -f tests/mock_linux_host/id_rsa -N "" -q
ssh-keygen -t rsa -b 4096 -f tests/mock_windows_host/id_rsa -N "" -q

# Set proper permissions
chmod 600 tests/mock_linux_host/id_rsa tests/mock_windows_host/id_rsa
chmod 644 tests/mock_linux_host/id_rsa.pub tests/mock_windows_host/id_rsa.pub

# Create authorized_keys file for Windows host
cat tests/mock_windows_host/id_rsa.pub > tests/mock_windows_host/authorized_keys
chmod 644 tests/mock_windows_host/authorized_keys

# Make sure the setup scripts are executable
chmod +x tests/mock_linux_host/setup_ssh.sh

# Update the local SSH configuration to trust the mock hosts
mkdir -p ~/.ssh
cat > ~/.ssh/config << EOF
Host mock_linux_host
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null

Host mock_windows_host
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null

# For Docker container hostnames
Host mock_linux
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null

Host mock_windows
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
EOF

chmod 600 ~/.ssh/config

echo "Resetting Docker environment..."
docker compose -f docker-compose.dev.yml down --remove-orphans

echo "Starting mock hosts for verification..."
docker compose -f docker-compose.dev.yml --profile integration up -d mock_linux_host mock_windows_host

echo "Waiting for services to start (30 seconds)..."
sleep 30

echo "Testing SSH to mock_linux_host..."
docker compose -f docker-compose.dev.yml run --rm test_runner bash -c "ssh-keyscan -H mock_linux_host > /root/.ssh/known_hosts 2>/dev/null || true"
docker compose -f docker-compose.dev.yml run --rm test_runner ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i /app/tests/mock_linux_host/id_rsa ansible_user@mock_linux_host "echo 'SSH connection successful'"

echo "SSH setup and verification complete"
echo "You can now run: ./dev.sh test-linux or ./dev.sh test-windows"
