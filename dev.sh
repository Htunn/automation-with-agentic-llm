#!/bin/bash
# Development helper script for Ansible-TinyLlama

# Make the script executable
chmod +x setup_test_env.sh

case "$1" in
  setup)
    echo "Setting up test environment..."
    ./setup_test_env.sh
    ;;
  start)
    echo "Starting development environment..."
    docker-compose -f docker-compose.dev.yml up -d ansible_llm_api
    ;;
  stop)
    echo "Stopping development environment..."
    docker-compose -f docker-compose.dev.yml down
    ;;
  restart)
    echo "Restarting development environment..."
    docker-compose -f docker-compose.dev.yml restart ansible_llm_api
    ;;
  test)
    echo "Running tests..."
    docker-compose -f docker-compose.dev.yml run test_runner
    ;;
  test-integration)
    echo "Starting mock Windows host..."
    docker-compose -f docker-compose.dev.yml --profile integration up -d mock_windows_host
    echo "Running integration tests..."
    docker-compose -f docker-compose.dev.yml run test_runner pytest tests/integration
    ;;
    
  test-windows)
    echo "Starting mock Windows host..."
    docker-compose -f docker-compose.dev.yml --profile integration up -d mock_windows_host
    echo "Waiting for mock Windows host to be ready..."
    sleep 5
    echo "Running Windows PowerShell test playbook..."
    docker-compose -f docker-compose.dev.yml run test_runner ansible-playbook -i tests/mock_windows_host/inventory.ini tests/mock_windows_host/test_playbook.yml -v
    ;;
  shell)
    echo "Opening shell in the API container..."
    docker-compose -f docker-compose.dev.yml exec ansible_llm_api bash
    ;;
  logs)
    echo "Showing logs..."
    docker-compose -f docker-compose.dev.yml logs -f ansible_llm_api
    ;;
  model)
    if [ "$2" == "download" ] && [ ! -z "$3" ]; then
      echo "Downloading model: $3..."
      docker-compose -f docker-compose.dev.yml exec ansible_llm_api python -m src.main model download "$3"
    else
      echo "Listing available models..."
      docker-compose -f docker-compose.dev.yml exec ansible_llm_api python -m src.main model list
    fi
    ;;
  clean)
    echo "Cleaning up development environment..."
    docker-compose -f docker-compose.dev.yml down -v
    ;;
  *)
    echo "Usage: $0 {setup|start|stop|restart|test|test-integration|test-windows|shell|logs|model|clean}"
    echo ""
    echo "Commands:"
    echo "  setup            - Set up the test environment (create SSH keys, etc.)"
    echo "  start            - Start the development environment"
    echo "  stop             - Stop the development environment"
    echo "  restart          - Restart the API service"
    echo "  test             - Run all tests"
    echo "  test-integration - Run integration tests with mock Windows host"
    echo "  test-windows     - Run test playbook on mock Windows host with PowerShell"
    echo "  shell            - Open a shell in the API container"
    echo "  logs             - Show logs from the API service"
    echo "  model list       - List available models"
    echo "  model download X - Download model X"
    echo "  clean            - Clean up development environment (removes volumes)"
    exit 1
    ;;
esac
