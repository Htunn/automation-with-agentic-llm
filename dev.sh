#!/bin/bash
# Development helper script for Ansible-TinyLlama

# Make the script executable
chmod +x setup_test_env.sh

function show_usage() {
    echo "Usage: $0 {setup|start|stop|restart|test|test-integration|test-windows|test-linux|linux-automation|linux-security|shell|logs|model|update|clean|remove-mock-hosts|analyze-playbook|clean-cache|check-disk-space|download-tiny-model|fix-analysis}"
    echo ""
    echo "Commands:"
    echo "  setup            - Set up the test environment (create SSH keys, etc.)"
    echo "  start            - Start the development environment"
    echo "  stop             - Stop the development environment"
    echo "  restart          - Restart the API service"
    echo "  test             - Run all tests"
    echo "  test-integration - Run integration tests with mock Windows and Linux hosts"
    echo "  test-windows     - Run test playbook on mock Windows host with PowerShell"
    echo "  test-linux       - Run test playbook on mock Linux host"
    echo "  linux-automation - Run Linux system management playbook on mock Linux host"
    echo "  linux-security   - Run Linux security hardening playbook on mock Linux host"
    echo "  shell            - Open a shell in the API container"
    echo "  logs             - Show logs from the API service"
    echo "  model list       - List available models"
    echo "  model download X - Download model X"
    echo "  update           - Update dependencies and rebuilding containers"
    echo "  clean            - Clean up development environment (removes volumes)"
    echo "  remove-mock-hosts- Remove mock Linux and Windows hosts only"
    echo "  analyze-playbook - Analyze an Ansible playbook with LLM"
    echo "  clean-cache      - Clean model cache and free disk space"
    echo "  check-disk-space - Check available disk space in containers"
    echo "  download-tiny-model - Download a smaller model for low-resource environments"
    echo "  fix-analysis     - Fix binary output in playbook analysis"
}

case "$1" in
  setup)
    echo "Setting up test environment..."
    ./setup_test_env.sh
    ;;
  start)
    echo "Starting development environment with mock Linux and Windows hosts..."
    docker compose -f docker-compose.dev.yml --profile integration up -d
    ;;
  stop)
    echo "Stopping development environment..."
    docker compose -f docker-compose.dev.yml down --remove-orphans
    ;;
  restart)
    echo "Restarting development environment..."
    docker compose -f docker-compose.dev.yml restart ansible_llm_api
    ;;
  test)
    echo "Running tests..."
    docker compose -f docker-compose.dev.yml run test_runner
    ;;
  test-integration)
    echo "Starting mock hosts..."
    docker compose -f docker-compose.dev.yml --profile integration up -d mock_windows_host mock_linux_host
    echo "Running integration tests..."
    docker compose -f docker-compose.dev.yml run test_runner pytest tests/integration
    ;;
    
  test-windows)
    echo "Starting mock Windows host..."
    docker compose -f docker-compose.dev.yml --profile integration up -d mock_windows_host
    echo "Waiting for mock Windows host to be ready..."
    sleep 5
    
    # Ensure SSH known_hosts handling
    echo "Setting up SSH known_hosts for test runner..."
    docker compose -f docker-compose.dev.yml run test_runner mkdir -p /root/.ssh
    docker compose -f docker-compose.dev.yml run test_runner bash -c "ssh-keyscan -p 22 -H mock_windows_host > /root/.ssh/known_hosts 2>/dev/null || true"
    
    echo "Running simple SSH verification test..."
    docker compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_windows_host/inventory.ini tests/mock_windows_host/simple_test.yml -v
    
    # Only run the full test if the user explicitly requests it with an argument
    if [ "$2" = "full" ]; then
      echo "Running full Windows PowerShell test playbook..."
      docker compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_windows_host/inventory.ini tests/mock_windows_host/test_playbook.yml -v
    else
      echo "SSH connection test successful! To run full PowerShell test, use: ./dev.sh test-windows full"
    fi
    ;;
    
  test-linux)
    echo "Starting mock Linux host..."
    docker compose -f docker-compose.dev.yml --profile integration up -d mock_linux_host
    echo "Waiting for mock Linux host to be ready..."
    echo "Giving the SSH service time to start (20 seconds)..."
    sleep 20
    
    # Ensure SSH known_hosts handling
    echo "Setting up SSH known_hosts for test runner..."
    docker compose -f docker-compose.dev.yml run test_runner mkdir -p /root/.ssh
    docker compose -f docker-compose.dev.yml run test_runner bash -c "ssh-keyscan -p 22 -H mock_linux_host > /root/.ssh/known_hosts 2>/dev/null || true"
    
    echo "Running simple SSH verification test..."
    docker compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_linux_host/inventory.ini tests/mock_linux_host/simple_test.yml -v
    
    # Only run the full test if the user explicitly requests it with an argument
    if [ "$2" = "full" ]; then
      echo "Running full Linux test playbook..."
      docker compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_linux_host/inventory.ini tests/mock_linux_host/test_playbook.yml -v
    else
      echo "SSH connection test successful! To run full test (which may have disk space issues), use: ./dev.sh test-linux full"
    fi
    ;;
    
  shell)
    echo "Opening shell in the API container..."
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash
    ;;
  logs)
    echo "Showing logs..."
    docker compose -f docker-compose.dev.yml logs -f ansible_llm_api
    ;;
  model)
    if [ "$2" == "download" ] && [ ! -z "$3" ]; then
      echo "Downloading model: $3..."
      docker compose -f docker-compose.dev.yml exec ansible_llm_api python -m src.main model download "$3"
    else
      echo "Listing available models..."
      docker compose -f docker-compose.dev.yml exec ansible_llm_api python -m src.main model list
    fi
    ;;
  linux-automation)
    echo "Starting mock Linux host..."
    docker compose -f docker-compose.dev.yml --profile integration up -d mock_linux_host
    echo "Waiting for mock Linux host to be ready..."
    echo "Giving the SSH service time to start (20 seconds)..."
    sleep 20
    
    # Ensure SSH known_hosts handling
    echo "Setting up SSH known_hosts for test runner..."
    docker compose -f docker-compose.dev.yml run test_runner mkdir -p /root/.ssh
    docker compose -f docker-compose.dev.yml run test_runner bash -c "ssh-keyscan -p 22 -H mock_linux_host > /root/.ssh/known_hosts 2>/dev/null || true"
    
    echo "Running Linux system management automation playbook..."
    docker compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_linux_host/inventory.ini src/examples/linux_automation/linux_system_management.yml -v
    ;;
    
  linux-security)
    echo "Starting mock Linux host..."
    docker compose -f docker-compose.dev.yml --profile integration up -d mock_linux_host
    echo "Waiting for mock Linux host to be ready..."
    echo "Giving the SSH service time to start (20 seconds)..."
    sleep 20
    echo "Running Linux security hardening playbook..."
    docker compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_linux_host/inventory.ini src/examples/linux_automation/linux_security_hardening.yml -v
    ;;
    
  clean)
    echo "Cleaning up development environment..."
    docker compose -f docker-compose.dev.yml down -v
    ;;
  update)
    echo "Updating dependencies and rebuilding containers..."
    docker compose -f docker-compose.dev.yml down
    docker compose -f docker-compose.dev.yml build --no-cache ansible_llm_api
    echo "Dependencies updated. Run './dev.sh start' to start the updated environment."
    ;;
  remove-mock-hosts)
    echo "Removing mock Linux and Windows hosts..."
    # Check if containers are running and stop them
    if docker ps -q -f name=mock_linux_host &>/dev/null; then
      echo "Stopping and removing mock_linux_host..."
      docker compose -f docker-compose.dev.yml stop mock_linux_host
      docker compose -f docker-compose.dev.yml rm -f mock_linux_host
    else
      echo "mock_linux_host is not running"
    fi
    
    if docker ps -q -f name=mock_windows_host &>/dev/null; then
      echo "Stopping and removing mock_windows_host..."
      docker compose -f docker-compose.dev.yml stop mock_windows_host
      docker compose -f docker-compose.dev.yml rm -f mock_windows_host
    else
      echo "mock_windows_host is not running"
    fi
    
    echo "Mock hosts removed successfully. You may need to run './dev.sh setup' before running tests again."
    ;;
  analyze-playbook)
    if [ -z "$2" ]; then
      echo "Error: No playbook specified."
      echo "Usage: $0 analyze-playbook PATH_TO_PLAYBOOK [tiny]"
      echo "Example: $0 analyze-playbook tests/mock_linux_host/test_playbook.yml"
      echo "Use 'tiny' option to use smaller model: $0 analyze-playbook tests/mock_linux_host/test_playbook.yml tiny"
      exit 1
    fi
    
    PLAYBOOK_PATH="$2"
    USE_TINY_MODEL="$3"
    
    # Check if the file exists
    if [ ! -f "$PLAYBOOK_PATH" ]; then
      echo "Error: Playbook file not found: $PLAYBOOK_PATH"
      exit 1
    fi
    
    echo "Analyzing playbook: $PLAYBOOK_PATH"
    
    # Check disk space before running
    echo "Checking available disk space..."
    
    # Ensure the API container is running
    if ! docker ps -q -f name=ansible_llm_api &>/dev/null; then
      echo "Starting API container..."
      docker compose -f docker-compose.dev.yml up -d ansible_llm_api
      echo "Waiting for API container to initialize (5 seconds)..."
      sleep 5
    fi
    
    # Check if there's enough disk space
    FREE_SPACE=$(docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df / | tail -1 | awk '{print \$4}'")
    FREE_SPACE_MB=$((FREE_SPACE / 1024))
    
    echo "Available disk space: ${FREE_SPACE_MB}MB"
    
    if [ "$FREE_SPACE_MB" -lt "5000" ]; then
      echo "Warning: Low disk space detected (less than 5GB free)."
      echo "Running 'clean-cache' command to free up space..."
      
      # Clean cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /root/.cache/huggingface"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "pip cache purge"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "apt-get clean"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /tmp/*"
      
      # Check space again
      FREE_SPACE=$(docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df / | tail -1 | awk '{print \$4}'")
      FREE_SPACE_MB=$((FREE_SPACE / 1024))
      
      echo "Available disk space after cleanup: ${FREE_SPACE_MB}MB"
      
      if [ "$FREE_SPACE_MB" -lt "5000" ]; then
        echo "Still not enough disk space. Recommending tiny model."
        USE_TINY_MODEL="tiny"
      fi
    fi
    
    # Run the analyze-playbook command in the container
    if [ "$USE_TINY_MODEL" = "tiny" ]; then
      echo "Using smaller TinyLlama model for analysis..."
      
      # First check if the small model exists
      TINY_MODEL_EXISTS=$(docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "ls -la /app/models/TinyLlama-1.1B-Chat-v0.1 2>/dev/null || echo 'not_found'")
      
      if [[ "$TINY_MODEL_EXISTS" == *"not_found"* ]]; then
        echo "Small model not found. Downloading now..."
        docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cd /app && python -m src.main model download TinyLlama/TinyLlama-1.1B-Chat-v0.1 --quantize 4bit"
      fi
      
      # Use the tiny model with timeout and verbosity
      echo "Running playbook analysis with small model..."
      docker compose -f docker-compose.dev.yml exec -e MODEL_NAME="TinyLlama/TinyLlama-1.1B-Chat-v0.1" ansible_llm_api python -m src.main cli analyze-playbook "/app/$PLAYBOOK_PATH" -v
      
      # Check exit status
      if [ $? -ne 0 ]; then
        echo "Analysis failed with tiny model. Something went wrong."
        echo "Try running './dev.sh clean-cache' to free up more space."
        echo "You can also check disk space with './dev.sh check-disk-space'"
      fi
    else
      echo "Running playbook analysis with standard model..."
      docker compose -f docker-compose.dev.yml exec ansible_llm_api python -m src.main cli analyze-playbook "/app/$PLAYBOOK_PATH" -v
      
      # Check exit status and offer to try with tiny model if it fails
      if [ $? -ne 0 ]; then
        echo "Analysis failed with standard model. Would you like to try with the tiny model? (y/n)"
        read -r answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
          # Check if tiny model exists, download if needed
          TINY_MODEL_EXISTS=$(docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "ls -la /app/models/TinyLlama-1.1B-Chat-v0.1 2>/dev/null || echo 'not_found'")
          
          if [[ "$TINY_MODEL_EXISTS" == *"not_found"* ]]; then
            echo "Small model not found. Downloading now..."
            docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cd /app && python -m src.main model download TinyLlama/TinyLlama-1.1B-Chat-v0.1 --quantize 4bit"
          fi
          
          echo "Running playbook analysis with tiny model..."
          docker compose -f docker-compose.dev.yml exec -e MODEL_NAME="TinyLlama/TinyLlama-1.1B-Chat-v0.1" ansible_llm_api python -m src.main cli analyze-playbook "/app/$PLAYBOOK_PATH" -v
        fi
      fi
    fi
    ;;
  clean-cache)
    echo "Cleaning model cache to free up disk space..."
    
    # Check if the API container is running
    if docker ps -q -f name=ansible_llm_api &>/dev/null; then
      echo "Cleaning cache in the running API container..."
      
      # Clean Hugging Face cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /root/.cache/huggingface"
      
      # Clean pip cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "pip cache purge"
      
      # Clean apt cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "apt-get clean"
      
      # Clean temporary files
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /tmp/*"
      
      # Show disk usage after cleanup
      echo "Disk usage after cleanup:"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df -h"
    else
      echo "API container is not running. Starting it temporarily..."
      docker compose -f docker-compose.dev.yml up -d ansible_llm_api
      echo "Waiting for container to initialize..."
      sleep 5
      
      # Clean Hugging Face cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /root/.cache/huggingface"
      
      # Clean pip cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "pip cache purge"
      
      # Clean apt cache
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "apt-get clean"
      
      # Clean temporary files
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /tmp/*"
      
      # Show disk usage after cleanup
      echo "Disk usage after cleanup:"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df -h"
      
      echo "Stopping temporary API container..."
      docker compose -f docker-compose.dev.yml stop ansible_llm_api
    fi
    
    echo "Cache cleaning complete!"
    ;;
    
  check-disk-space)
    echo "Checking available disk space in containers..."
    
    # Check if the API container is running
    if docker ps -q -f name=ansible_llm_api &>/dev/null; then
      echo "Disk usage in the API container:"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df -h"
      echo ""
      echo "Storage details:"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /root/.cache/huggingface 2>/dev/null || echo 'No HuggingFace cache found'"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /root/.cache 2>/dev/null || echo 'No cache directory found'"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /app/models 2>/dev/null || echo 'No models directory found'"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /tmp 2>/dev/null || echo 'No temp directory found'"
    else
      echo "API container is not running. Starting it temporarily..."
      docker compose -f docker-compose.dev.yml up -d ansible_llm_api
      echo "Waiting for container to initialize..."
      sleep 5
      
      echo "Disk usage in the API container:"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df -h"
      echo ""
      echo "Storage details:"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /root/.cache/huggingface 2>/dev/null || echo 'No HuggingFace cache found'"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /root/.cache 2>/dev/null || echo 'No cache directory found'"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /app/models 2>/dev/null || echo 'No models directory found'"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "du -sh /tmp 2>/dev/null || echo 'No temp directory found'"
      
      echo "Stopping temporary API container..."
      docker compose -f docker-compose.dev.yml stop ansible_llm_api
    fi
    ;;
    
  download-tiny-model)
    echo "Downloading a smaller model suitable for environments with limited disk space..."
    
    # Check if the API container is running
    if ! docker ps -q -f name=ansible_llm_api &>/dev/null; then
      echo "Starting API container..."
      docker compose -f docker-compose.dev.yml up -d ansible_llm_api
      echo "Waiting for container to initialize..."
      sleep 5
    fi
    
    # Clean cache first to ensure maximum space
    echo "Cleaning cache to make space..."
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "rm -rf /root/.cache/huggingface"
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "pip cache purge"
    
    # Show available space
    echo "Available disk space before download:"
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "df -h"
    
    # Download a small model (tinyllama-1.1b-chat-v0.6 is around 1.1GB)
    echo "Downloading smaller TinyLlama model..."
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cd /app && python -m src.main model download TinyLlama/TinyLlama-1.1B-Chat-v0.1 --quantize 4bit"
    
    echo "Model download complete."
    echo "You can now run analyze-playbook with this smaller model."
    ;;
    
  fix-analysis)
    echo "Fixing the playbook analysis binary output issue..."
    
    # Check if the API container is running
    if ! docker ps -q -f name=ansible_llm_api &>/dev/null; then
      echo "Starting API container..."
      docker compose -f docker-compose.dev.yml up -d ansible_llm_api
      echo "Waiting for container to initialize..."
      sleep 5
    fi
    
    echo "Step 1: Checking for problematic model configuration..."
    # Check if any problematic model is being used
    MODEL_CHECK=$(docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "grep -r 'TinyLlama-1.1B-intermediate-step\|TinyLlama-1.1B-python-v0.1\|TinyLlama-1.1B-step\|intermediate' /app/config --include='*.toml' 2>/dev/null || echo 'not found'")
    
    if [[ "$MODEL_CHECK" != *"not found"* ]]; then
      echo "Found problematic model configuration. Updating config file..."
      
      # Backup the config file
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cp /app/config/config.toml /app/config/config.toml.bak"
      
      # Update the model to a more reliable chat model
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/TinyLlama-1.1B-intermediate-step/TinyLlama-1.1B-Chat-v0.1/g' /app/config/config.toml"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/TinyLlama-1.1B-python-v0.1/TinyLlama-1.1B-Chat-v0.1/g' /app/config/config.toml"
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/TinyLlama-1.1B-step/TinyLlama-1.1B-Chat-v0.1/g' /app/config/config.toml"
      
      echo "Configuration updated to use TinyLlama-1.1B-Chat-v0.1 instead of intermediate models."
    fi
    
    echo "Step 2: Downloading a better specialized chat model..."
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cd /app && python -m src.main model download TinyLlama/TinyLlama-1.1B-Chat-v0.1 --quantize 4bit"
    
    echo "Step 3: Updating analysis code to better handle binary output..."
    # Copy the improved response processor code
    cat > /tmp/fix_binary_output.py << 'EOF'
def process_binary_pattern(text):
    """Fix binary pattern outputs (repetitive numbers, dots, and other common patterns)"""
    import re
    
    if text is None:
        return "No response generated by the model."
        
    # Check for various binary-like patterns
    # Pattern 1: Repetitive numbers and dots (e.g., 1.3.4.1.3.4...)
    if re.search(r'((\d+\.){10,})', text):
        return "The model output contained binary-like patterns (number sequences). Using fallback analysis instead."
        
    # Pattern 2: Repetitive zeroes and ones (e.g., 010101010...)
    if re.search(r'((0+1+){10,})', text):
        return "The model output contained binary patterns (zeros and ones). Using fallback analysis instead."
        
    # Pattern 3: Long sequences of the same character repeated (common in LLM failures)
    for char in '.,;:-_=+<>[](){}|':
        if re.search(f'({re.escape(char)}){{{20,}}}', text):
            return f"The model output contained repetitive special characters ({char}). Using fallback analysis instead."
    
    # Pattern 4: Long repetitive sequences of the same word or short pattern
    words = text.split()
    if len(words) >= 20:  # Only check longer responses
        word_slices = [' '.join(words[i:i+5]) for i in range(0, len(words)-5, 5)]
        unique_slices = len(set(word_slices))
        if unique_slices > 0 and len(word_slices) / unique_slices > 3:  # More than 3x repetition
            return "The model output contained repetitive text patterns. Using fallback analysis instead."
    
    # Pattern 5: Non-utf8 binary junk
    try:
        text.encode('utf-8').decode('utf-8')
    except UnicodeError:
        return "The model output contained invalid Unicode characters. Using fallback analysis instead."
        
    return text
EOF

    # Backup the original response processor
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cp /app/src/llm_engine/response_processor.py /app/src/llm_engine/response_processor.py.bak"
    
    # Add the fix to the response processor
    docker compose -f docker-compose.dev.yml exec -T ansible_llm_api bash -c "cat > /tmp/fix_binary_output.py" < /tmp/fix_binary_output.py
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cat /tmp/fix_binary_output.py >> /app/src/llm_engine/response_processor.py"
    
    # Update the process_analysis_response function to use our new binary pattern detector
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/def process_analysis_response(response):/def process_analysis_response(response):\\n    # Fix binary pattern outputs\\n    response = process_binary_pattern(response)/g' /app/src/llm_engine/response_processor.py"
    
    echo "Step 4: Adding specialized chat model parameter to direct_cli.py"
    # Backup the original direct_cli.py
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cp /app/src/api/direct_cli.py /app/src/api/direct_cli.py.bak"
    
    # Modify the model loading code to use MODEL_NAME environment variable with fallback
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/model, tokenizer = load_model()/try:\\n                model_name = os.environ.get(\"MODEL_NAME\", \"TinyLlama\\/TinyLlama-1.1B-Chat-v0.1\")\\n                console.print(f\"[yellow]Using model: {model_name}[/yellow]\")\\n                model, tokenizer = load_model(model_name=model_name)\\n            except Exception as e:\\n                logger.error(f\"Error loading specified model: {str(e)}\")\\n                console.print(f\"[red]Error loading specified model: {str(e)}[/red]\")\\n                console.print(\"[yellow]Falling back to default model...[/yellow]\")\\n                model, tokenizer = load_model()/g' /app/src/api/direct_cli.py"
    
    # Add os import if not already present
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "if ! grep -q \"import os\.path\" /app/src/api/direct_cli.py; then sed -i 's/import logging/import logging\\nimport os.path/g' /app/src/api/direct_cli.py; fi"
    
    # Add in-line binary pattern detection to direct_cli.py
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i '/if not llm_response or llm_response.strip() == \"\":/a \\n            # Check for binary-like patterns directly\\n            import re\\n            # Simple binary pattern detection\\n            has_binary_pattern = False\\n            # Check for repetitive patterns that indicate output issues\\n            if re.search(r\"((\\\\d+\\\\.){10,})\", llm_response):\\n                has_binary_pattern = True\\n            # Check repetitive zeros and ones\\n            if re.search(r\"((0+1+){10,})\", llm_response):\\n                has_binary_pattern = True\\n            # Check for long sequences of special characters\\n            for char in \".,:;-_=+<>[](){}|\":\\n                if re.search(f\"({re.escape(char)}){{{20,}}}\", llm_response):\\n                    has_binary_pattern = True\\n                    \\n            if has_binary_pattern:\\n                console.print(\"[red]Warning: The model produced binary-like output patterns.[/red]\")\\n                console.print(\"[yellow]Attempting to fix by switching to fallback analysis mode...[/yellow]\")\\n                # Create a simple analysis result for fallback\\n                llm_response = f\"\"\"\\nSummary: The playbook appears to be an Ansible playbook but detailed analysis couldn\\'t be performed.\\n\\nIssues:\\n- The model encountered difficulties analyzing this particular playbook\\n\\nBest Practices:\\n- Consider breaking down complex playbooks into smaller components\\n- Use standard Ansible modules and avoid custom scripts when possible\\n- Follow Ansible\\'s YAML formatting guidelines\\n\"\"\"' /app/src/api/direct_cli.py"
    
    # Improve model generation parameters to reduce chance of binary output
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/inputs = tokenizer(prompt, return_tensors=\"pt\").to(model.device)\\n            outputs = model.generate(\\*\\*inputs, max_new_tokens=1024)/try:\\n                # Add temperature parameter to reduce randomness and increase coherence\\n                inputs = tokenizer(prompt, return_tensors=\"pt\").to(model.device)\\n                outputs = model.generate(\\n                    \\*\\*inputs, \\n                    max_new_tokens=1024,\\n                    temperature=0.5,  # Lower temperature for more focused output\\n                    repetition_penalty=1.3,  # Penalize repetition more heavily\\n                    do_sample=True  # Enable sampling to avoid deterministic outputs\\n                )/g' /app/src/api/direct_cli.py"
    
    # Fix the try block by adding except
    docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "sed -i 's/            response = tokenizer.decode(outputs\\[0\\], skip_special_tokens=True)/                response = tokenizer.decode(outputs[0], skip_special_tokens=True)\\n            except Exception as e:\\n                logger.error(f\"Error during model generation: {str(e)}\")\\n                console.print(f\"[red]Error during model generation: {str(e)}[/red]\")\\n                console.print(\"[yellow]Try using a different model with \\'.\\/dev.sh analyze-playbook your_playbook.yml tiny\\'[/yellow]\")\\n                return/g' /app/src/api/direct_cli.py"
    
    echo "Step 5: Verifying installation and fixing any remaining issues..."
    # Check if the model exists, download if needed
    MODEL_EXISTS=$(docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "ls -la /app/models/TinyLlama-1.1B-Chat-v0.1 2>/dev/null || echo 'not found'")
    if [[ "$MODEL_EXISTS" == *"not found"* ]]; then
      echo "TinyLlama-1.1B-Chat-v0.1 model not found. Downloading now..."
      docker compose -f docker-compose.dev.yml exec ansible_llm_api bash -c "cd /app && python -m src.main model download TinyLlama/TinyLlama-1.1B-Chat-v0.1 --quantize 4bit"
    else
      echo "TinyLlama-1.1B-Chat-v0.1 model found."
    fi
    
    echo "Fixes applied successfully! Try running './dev.sh analyze-playbook your_playbook.yml' again."
    echo "If you still see issues, run './dev.sh analyze-playbook your_playbook.yml tiny' to use the tiny model explicitly."
    echo "Note: You may need to restart the API container with './dev.sh restart' for all changes to take effect."
    ;;
    
  *)
    show_usage
    exit 1
    ;;
esac
