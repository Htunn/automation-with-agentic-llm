#!/bin/bash
# Setup script for development environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "==========================================================="
echo "          Ansible TinyLlama Development Setup              "
echo "==========================================================="
echo -e "${NC}"

# Check Python version
REQUIRED_PY_VERSION="3.12"
PY_CMD=""

echo "Checking Python version..."
if command -v python3.12 &> /dev/null; then
    PY_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ "$PY_VERSION" == "$REQUIRED_PY_VERSION"* ]]; then
        PY_CMD="python3"
    else
        echo -e "${YELLOW}Warning: Python $PY_VERSION found, but Python $REQUIRED_PY_VERSION is recommended.${NC}"
        read -p "Continue with Python $PY_VERSION? (y/N): " CONTINUE
        if [[ "$CONTINUE" =~ ^[Yy]$ ]]; then
            PY_CMD="python3"
        else
            echo -e "${RED}Please install Python $REQUIRED_PY_VERSION and try again.${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}Error: Python 3 not found. Please install Python $REQUIRED_PY_VERSION and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}Using $PY_CMD version $($PY_CMD --version 2>&1)${NC}"

# Create and activate virtual environment
echo "Setting up virtual environment..."

if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment 'venv' already exists.${NC}"
    read -p "Recreate virtual environment? (y/N): " RECREATE_VENV
    if [[ "$RECREATE_VENV" =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf venv
        $PY_CMD -m venv venv
    fi
else
    $PY_CMD -m venv venv
fi

# Source the virtual environment
if [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win"* ]]; then
    # Windows using Git Bash or similar
    source venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source venv/bin/activate
fi

# Install development dependencies
echo "Installing development dependencies..."
pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs models

# Check if model exists and offer to download
if [ ! "$(ls -A models 2>/dev/null)" ]; then
    echo -e "${YELLOW}No models found in models directory.${NC}"
    read -p "Download TinyLlama model? (Y/n): " DOWNLOAD_MODEL
    if [[ ! "$DOWNLOAD_MODEL" =~ ^[Nn]$ ]]; then
        echo "Downloading TinyLlama model..."
        if [ -f "models/download_models.sh" ]; then
            bash models/download_models.sh download tinyllama-1.1b-chat
        else
            echo -e "${RED}Error: models/download_models.sh not found.${NC}"
            echo "Please download the model manually."
        fi
    fi
fi

# Generate environment configuration
if [ ! -f ".env" ]; then
    echo "Generating environment configuration..."
    if [ -f "scripts/generate_env.sh" ]; then
        bash scripts/generate_env.sh
    else
        echo -e "${YELLOW}Warning: scripts/generate_env.sh not found. Skipping .env generation.${NC}"
    fi
fi

# Run system check
echo "Running system check..."
python -m src.utils.system_check

echo -e "${GREEN}"
echo "==========================================================="
echo "Development environment setup complete!"
echo "==========================================================="
echo -e "${NC}"

echo "Next steps:"
echo "1. Review and adjust .env file if needed"
echo "2. Start the development server: python -m src.main api"
echo "3. Or use the CLI: python -m src.main cli"
echo ""
echo "Happy coding!"
