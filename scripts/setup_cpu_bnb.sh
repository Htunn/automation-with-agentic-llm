#!/bin/bash
# Setup bitsandbytes for CPU compatibility

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up bitsandbytes for CPU compatibility${NC}"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}No virtual environment detected. Activating project venv...${NC}"
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}No virtual environment found. Please run install.sh first or activate your venv.${NC}"
        exit 1
    fi
fi

# Uninstall existing bitsandbytes
echo -e "${BLUE}Removing existing bitsandbytes installation...${NC}"
pip uninstall -y bitsandbytes

# Install CPU-compatible version using alternative index
echo -e "${BLUE}Installing CPU-compatible bitsandbytes...${NC}"
pip install -U bitsandbytes --prefer-binary --extra-index-url=https://jllllll.github.io/bitsandbytes-windows-webui

# Setup the CPU config
echo -e "${BLUE}Setting up environment for CPU usage...${NC}"
export BNB_FORCE_CPU=1

# Creating a helper script to set the environment variable
echo -e "#!/bin/bash\nexport BNB_FORCE_CPU=1\nexport QUANTIZATION=\"none\"\n\necho \"CPU env variables for bitsandbytes have been set.\"" > scripts/set_cpu_env.sh
chmod +x scripts/set_cpu_env.sh

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}For future model runs, you can use:${NC}"
echo -e "  source scripts/set_cpu_env.sh"
echo -e "${YELLOW}Or set these environment variables:${NC}"
echo -e "  export BNB_FORCE_CPU=1"
echo -e "  export QUANTIZATION=\"none\""
echo ""
echo -e "${BLUE}To run the API without quantization:${NC}"
echo -e "  QUANTIZATION=none python -m src.main api"
