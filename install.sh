#!/bin/bash
# Installation script for Ansible TinyLlama Integration

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
echo "          Ansible TinyLlama Integration Installer          "
echo "==========================================================="
echo -e "${NC}"

# Check if script is run with root/sudo
if [[ $EUID -eq 0 ]]; then
    echo -e "${YELLOW}WARNING: Running as root. It's recommended to run as a regular user.${NC}"
    read -p "Continue as root? (y/N): " ROOT_CONFIRM
    if [[ ! "$ROOT_CONFIRM" =~ ^[Yy]$ ]]; then
        echo "Exiting."
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Python 3.12+
echo -e "\n${BLUE}Checking Python version...${NC}"
if command -v python3 >/dev/null 2>&1; then
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ $(echo "$PY_VERSION >= 3.12" | bc -l) -eq 1 ]]; then
        echo -e "${GREEN}Found Python $PY_VERSION. This version is compatible.${NC}"
        PYTHON_CMD=python3
    else
        echo -e "${RED}Python version $PY_VERSION detected. Version 3.12 or higher is required.${NC}"
        exit 1
    fi
else
    echo -e "${RED}Python 3 not found. Please install Python 3.12 or higher.${NC}"
    exit 1
fi

# Check for pip
echo -e "\n${BLUE}Checking pip installation...${NC}"
if ! command -v pip3 >/dev/null 2>&1; then
    echo -e "${RED}pip3 not found. Installing pip...${NC}"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $PYTHON_CMD get-pip.py
    rm get-pip.py
else
    echo -e "${GREEN}pip3 is installed.${NC}"
fi

# Check for virtual environment
echo -e "\n${BLUE}Setting up virtual environment...${NC}"
if ! command -v virtualenv >/dev/null 2>&1; then
    echo -e "${YELLOW}virtualenv not found. Installing...${NC}"
    pip3 install virtualenv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    virtualenv -p $PYTHON_CMD venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo -e "\n${BLUE}Installing dependencies...${NC}"
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies if requested
read -p "Install development dependencies? (y/N): " DEV_DEPS
if [[ "$DEV_DEPS" =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Create necessary directories
echo -e "\n${BLUE}Setting up project directories...${NC}"
mkdir -p models logs config

# Install Git hooks
echo -e "\n${BLUE}Setting up Git hooks...${NC}"
if [ -d ".git" ]; then
    if [ -d ".github/hooks" ]; then
        echo "Installing pre-commit hook..."
        mkdir -p .git/hooks
        cp .github/hooks/pre-commit .git/hooks/
        chmod +x .git/hooks/pre-commit
        echo -e "${GREEN}Git hooks installed.${NC}"
    else
        echo -e "${YELLOW}No hooks found in .github/hooks directory.${NC}"
    fi
else
    echo -e "${YELLOW}Not a git repository, skipping Git hooks installation.${NC}"
fi

# Download model (optional)
echo -e "\n${BLUE}Model setup...${NC}"
read -p "Download the default TinyLlama model now? This may take some time. (y/N): " DOWNLOAD_MODEL
if [[ "$DOWNLOAD_MODEL" =~ ^[Yy]$ ]]; then
    echo "Downloading TinyLlama model..."
    cd models
    if [ -f "download_models.sh" ]; then
        bash download_models.sh download TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T
    else
        $PYTHON_CMD -m src.llm_engine.model_download download TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T
    fi
    cd ..
    echo -e "${GREEN}Model downloaded successfully.${NC}"
else
    echo "Skipping model download. You can download it later with: ./models/download_models.sh"
fi

# Run system checks
echo -e "\n${BLUE}Running system checks...${NC}"
$PYTHON_CMD -m src.utils.system_check

# Success message
echo -e "\n${GREEN}Installation complete!${NC}"
echo -e "${BLUE}To activate the environment, run: source venv/bin/activate${NC}"
echo -e "${BLUE}To start the API server: python -m src.main api${NC}"
echo -e "${BLUE}To use the CLI interface: python -m src.main cli${NC}"

# Docker instructions
echo -e "\n${YELLOW}Docker Instructions:${NC}"
echo "To build and run with Docker:"
echo "  docker-compose build"
echo "  docker-compose up -d"
echo "For production deployment:"
echo "  docker-compose -f docker-compose.prod.yml build"
echo "  docker-compose -f docker-compose.prod.yml up -d"

echo -e "\n${BLUE}Thank you for installing Ansible TinyLlama Integration!${NC}"
