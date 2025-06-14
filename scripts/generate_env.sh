#!/bin/bash
# Generate .env file for the Ansible TinyLlama Integration

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env"
SAMPLE_ENV=".env.example"
CONFIG_DIR="config"
CONFIG_FILE="config.toml"
PROD_CONFIG="config.prod.toml"

# Banner
echo -e "${BLUE}"
echo "=========================================================="
echo "        Environment Configuration Generator               "
echo "=========================================================="
echo -e "${NC}"

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Warning: $ENV_FILE already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo "Keeping existing $ENV_FILE file."
        exit 0
    fi
fi

# Check if we have a sample .env file
if [ ! -f "$SAMPLE_ENV" ]; then
    echo -e "${YELLOW}No $SAMPLE_ENV file found. Creating a basic template.${NC}"
    cat > $SAMPLE_ENV << EOL
# Example environment variables for Ansible-TinyLlama Integration
# Copy this file to .env and modify values as needed

# LLM Configuration
MODEL_NAME=TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T
QUANTIZATION=4bit
MODEL_PATH=/app/models

# API Settings
API_HOST=127.0.0.1
API_PORT=8000
API_DEBUG=false
API_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Security Settings (generate these with strong random values in production)
# Generate with: openssl rand -hex 32
SECRET_KEY=replacethiswithastrongrandomkeygeneratedwith_openssl_rand_hex_32
JWT_ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/ansible_llm.log

# Ansible Settings
ANSIBLE_CALLBACK_PLUGINS=/app/src/ansible_plugins/callbacks
ANSIBLE_LIBRARY=/app/src/ansible_plugins/modules
ANSIBLE_FILTER_PLUGINS=/app/src/ansible_plugins/filters

# Monitoring
ENABLE_METRICS=true
EOL
fi

echo "Generating $ENV_FILE file..."

# Check if we're in dev or production
read -p "Is this a production environment? (y/N): " IS_PROD
if [[ "$IS_PROD" =~ ^[Yy]$ ]]; then
    ENVIRONMENT="production"
    if [ -f "$CONFIG_DIR/$PROD_CONFIG" ]; then
        CONFIG_TEMPLATE="$CONFIG_DIR/$PROD_CONFIG"
    else
        CONFIG_TEMPLATE="$CONFIG_DIR/$CONFIG_FILE"
    fi
    
    # Generate strong random key for production
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
    else
        SECRET_KEY="insecure_key_please_generate_with_openssl_rand_hex_32"
        echo -e "${YELLOW}Warning: openssl not available. Using insecure default key.${NC}"
        echo -e "${YELLOW}Please update SECRET_KEY in $ENV_FILE with a secure value!${NC}"
    fi
else
    ENVIRONMENT="development"
    CONFIG_TEMPLATE="$CONFIG_DIR/$CONFIG_FILE"
    SECRET_KEY="dev_secret_key_do_not_use_in_production"
fi

# Copy sample env as a starting point
cp "$SAMPLE_ENV" "$ENV_FILE"

# Update the SECRET_KEY in the .env file
sed -i.bak "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" "$ENV_FILE"
rm -f "${ENV_FILE}.bak"

# Update environment-specific settings
if [[ "$ENVIRONMENT" == "production" ]]; then
    sed -i.bak "s|API_HOST=.*|API_HOST=0.0.0.0|g" "$ENV_FILE"
    sed -i.bak "s|API_DEBUG=.*|API_DEBUG=false|g" "$ENV_FILE"
    sed -i.bak "s|LOG_LEVEL=.*|LOG_LEVEL=INFO|g" "$ENV_FILE"
    rm -f "${ENV_FILE}.bak"
else
    sed -i.bak "s|API_HOST=.*|API_HOST=127.0.0.1|g" "$ENV_FILE"
    sed -i.bak "s|API_DEBUG=.*|API_DEBUG=true|g" "$ENV_FILE"
    sed -i.bak "s|LOG_LEVEL=.*|LOG_LEVEL=DEBUG|g" "$ENV_FILE"
    rm -f "${ENV_FILE}.bak"
fi

echo -e "${GREEN}Successfully created $ENV_FILE for $ENVIRONMENT environment!${NC}"
echo ""
echo "Next steps:"
echo "1. Review and adjust settings in $ENV_FILE"
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "2. Ensure all security settings are properly configured"
    echo "3. Use docker-compose.prod.yml for deployment"
else
    echo "2. Run the application in development mode"
    echo "3. Consider setting up a virtual environment"
fi
echo ""
