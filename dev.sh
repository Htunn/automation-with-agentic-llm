#!/bin/bash
# Development helper script for Ansible-TinyLlama

# Make the script executable
chmod +x setup_test_env.sh

function show_usage() {
    echo "Usage: $0 {setup|start|stop|restart|test|test-integration|test-windows|test-linux|linux-automation|linux-security|shell|logs|model|update|clean|remove-mock-hosts}"
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
    echo "  update           - Update dependencies and rebuild containers"
    echo "  clean            - Clean up development environment (removes volumes)"
    echo "  remove-mock-hosts- Remove mock Linux and Windows hosts only"
}

case "$1" in
  setup)
    echo "Setting up test environment..."
    ./setup_test_env.sh
    ;;
  start)
    echo "Starting development environment..."
    docker compose -f docker-compose.dev.yml up -d ansible_llm_api
    ;;
  stop)
    echo "Stopping development environment..."
    docker compose -f docker-compose.dev.yml down
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
  *)
    show_usage
    exit 1
    ;;
esac
