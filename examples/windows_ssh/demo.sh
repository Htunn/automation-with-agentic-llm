#!/bin/bash
# This script demonstrates the complete workflow for Windows SSH automation

# Set up environment
echo "Setting up environment..."
cd "$(dirname "$0")/.."
source venv/bin/activate

# Step 1: Display help
echo "============================================"
echo "Step 1: Showing available commands"
echo "============================================"
python -m src.main --help

# Step 2: Generate a Windows SSH playbook
echo "============================================"
echo "Step 2: Generate a Windows SSH playbook"
echo "============================================"
# Note: In a real setup, this would use the LLM to generate
# For demo purposes, we'll copy an example instead
cp src/examples/windows_ssh/example_playbook.yml examples/windows_ssh/generated_playbook.yml
echo "Example playbook copied to examples/windows_ssh/generated_playbook.yml"

# Step 3: Show the setup guide
echo "============================================"
echo "Step 3: Display Windows SSH setup guide"
echo "============================================"
echo "Opening setup guide..."
cat src/examples/windows_ssh/setup_guide.md | head -20

# Step 4: Run the CLI setup examples command
echo "============================================"
echo "Step 4: Running CLI setup examples command"
echo "============================================"
python -m src.main cli setup-examples --windows

echo "============================================"
echo "Demo complete! Windows SSH automation is ready."
echo "============================================"
