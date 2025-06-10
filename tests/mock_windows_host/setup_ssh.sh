#!/bin/bash
# Setup SSH keys for the mock Windows host

# If there's an authorized_keys file mounted
if [ -f /config/authorized_keys ]; then
    mkdir -p /home/ansible_user/.ssh
    cp /config/authorized_keys /home/ansible_user/.ssh/authorized_keys
    chmod 700 /home/ansible_user/.ssh
    chmod 600 /home/ansible_user/.ssh/authorized_keys
    chown -R ansible_user:ansible_user /home/ansible_user/.ssh
    echo "Configured SSH authorized keys"
else
    echo "No authorized_keys file found in /config"
fi

# Create Windows-like PowerShell profile
mkdir -p /home/ansible_user/Documents/WindowsPowerShell
cat > /home/ansible_user/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1 << 'EOF'
# Mock Windows PowerShell Profile
function prompt {
    Write-Host "PS C:\>" -NoNewLine -ForegroundColor Green
    return " "
}

# Set aliases to make it more Windows-like
Set-Alias -Name dir -Value Get-ChildItem
Set-Alias -Name cls -Value Clear-Host

# Pretend we're on Windows
$env:OS = "Windows_NT"
$env:COMPUTERNAME = "MOCK-WINDOWS"
$env:USERDOMAIN = "MOCKDOMAIN"
$env:USERNAME = "ansible_user"
$env:PROCESSOR_ARCHITECTURE = "AMD64"
$env:SystemRoot = "C:\Windows"

# Display welcome message
Write-Host "Mock Windows PowerShell Environment" -ForegroundColor Blue
Write-Host "Running on PowerShell Core in Linux container" -ForegroundColor Gray
Write-Host "Ready for Ansible SSH testing" -ForegroundColor Green
EOF

# Make sure PowerShell profile is owned by the user
chown -R ansible_user:ansible_user /home/ansible_user/Documents

echo "PowerShell profile configured"
