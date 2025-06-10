# Ansible-TinyLlama Integration

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Ansible 2.14+](https://img.shields.io/badge/ansible-2.14%2B-brightgreen.svg)](https://docs.ansible.com/)

This project integrates TinyLlama 3, a compact large language model (LLM), with the Ansible automation engine to enhance automation capabilities with AI-driven decision making, natural language processing for playbook generation, and intelligent automation workflows.

## Features

- **Natural Language to Playbook**: Convert natural language descriptions into Ansible playbooks
- **Playbook Analysis**: Analyze and suggest improvements for existing playbooks
- **Intelligent Error Handling**: Get AI-powered suggestions when playbooks fail
- **Windows over SSH**: Special focus on Windows automation using SSH instead of WinRM
- **Local LLM Processing**: Run the LLM locally without external API dependencies

## Architecture

### Component Diagram

```mermaid
graph TB
    subgraph "Ansible Integration"
        AP[Ansible Playbooks]
        ACB[Callback Plugins]
        AM[Custom Modules]
        AF[Filter Plugins]
    end
    
    subgraph "TinyLlama Engine"
        ML[Model Loader]
        RP[Response Processor]
        PT[Prompt Templates]
        WP[Windows Processor]
    end
    
    subgraph "API Layer"
        CLI[CLI Interface]
        REST[REST API]
    end
    
    subgraph "Data Storage"
        MOD[Model Files]
        CONF[Configuration]
        LOGS[Logs]
    end
    
    AM -->|Uses| ML
    ACB -->|Analyzes| RP
    AF -->|Processes| RP
    CLI -->|Interacts| ML
    CLI -->|Interacts| PT
    REST -->|Exposes| ML
    ML -->|Loads| MOD
    RP -->|Uses| PT
    RP -->|Specialized| WP
    CLI -->|Reads| CONF
    REST -->|Reads| CONF
    ACB -->|Writes| LOGS
    AP -->|Uses| AM
    AP -->|Triggers| ACB
    AP -->|Uses| AF
```

### Sequence Diagram for Playbook Generation

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI Interface
    participant TE as TinyLlama Engine
    participant RP as Response Processor
    participant Ansible as Ansible Engine

    User->>CLI: Requests playbook generation
    CLI->>TE: Sends natural language prompt
    TE->>TE: Processes with LLM
    TE->>RP: Returns raw response
    RP->>RP: Extracts & validates YAML
    RP->>CLI: Returns formatted playbook
    CLI->>User: Displays or saves playbook
    User->>Ansible: Executes generated playbook
    Ansible->>CLI: Triggers callback for analysis
    CLI->>TE: Sends execution results
    TE->>CLI: Returns insights
    CLI->>User: Displays recommendations
```

### Deployment Diagram

```mermaid
graph TB
    subgraph "Local Development Environment"
        PY[Python 3.12]
        VE[Virtual Environment]
        GIT[Git Repository]
        VS[VS Code / Editor]
    end
    
    subgraph "Production Server"
        subgraph "Container / VM"
            API[API Server]
            ANS[Ansible Controller]
            TL[TinyLlama Engine]
            CONF[Configuration]
        end
        VOL[(Model Storage)]
        LOG[(Log Storage)]
    end
    
    subgraph "Target Infrastructure"
        WS[Windows Servers w/ SSH]
        LX[Linux Servers]
    end
    
    PY -->|Supports| VE
    VE -->|Contains| GIT
    VS -->|Edits| GIT
    GIT -->|Deployed to| API
    API -->|Uses| TL
    API -->|Uses| ANS
    TL -->|Reads| VOL
    API -->|Writes| LOG
    ANS -->|Configures| WS
    ANS -->|Configures| LX
    CONF -->|Configures| ANS
    CONF -->|Configures| TL
```

## Requirements

- Python 3.12+
- Ansible Core 2.14+
- PyTorch 2.0+ or ONNX Runtime
- SSH access to Windows hosts (OpenSSH Server installed)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/ansible-llm.git
   cd ansible-llm
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies and CLI tools:
   ```bash
   pip install -e .
   ```
   This will make the `ansible-llm` command available in your environment.

4. Download a TinyLlama model:
   ```bash
   python -m src.main model download TinyLlama-1.1B-Chat-v1.0
   ```
   See the [Model Management Guide](docs/model_management.md) for more options.

5. (Optional) Set up Windows SSH examples:
   ```bash
   ansible-llm cli setup-examples --windows
   ```
   
   After installation, you can use either the module form `python -m src.main` or the installed command `ansible-llm`.

## Quick Start

### CLI Usage Examples

```bash
# Starting the CLI Interface (shows available commands)
cd ansible-llm
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m src.main cli
```

### Available CLI Commands

```bash
# Generate an Ansible playbook from natural language
python -m src.main cli generate-playbook "Install and configure Nginx on all web servers with rate limiting"

# Save the generated playbook to a file
python -m src.main cli generate-playbook "Install and configure Nginx with SSL on web servers" -o nginx_ssl.yml

# Analyze an existing Ansible playbook
python -m src.main cli analyze-playbook path/to/playbook.yml

# Analyze an Ansible inventory file
python -m src.main cli analyze-inventory path/to/inventory.ini

# Set up Windows SSH automation examples
python -m src.main cli setup-examples --windows
```

### Starting the API Server

```bash
cd ansible-llm
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m src.main api --host 0.0.0.0 --port 8000
```

### Managing Models

```bash
# List available models
python -m src.main model list

# Download a specific model
python -m src.main model download TinyLlama-1.1B-Chat-v1.0

# Download and quantize a model to reduce memory usage
python -m src.main model download TinyLlama-1.1B-Chat-v1.0 --quantize 8bit
```

### Using Windows SSH Examples

1. Ensure your Windows hosts have OpenSSH Server installed and configured
2. Review the setup guide in `examples/windows_ssh/setup_guide.md`
3. Update the inventory file with your Windows hosts
4. Run the example playbook:
   ```bash
   ansible-playbook -i examples/windows_ssh/inventory.ini examples/windows_ssh/example_playbook.yml
   ```

## Project Structure

```
ansible-llm/
├── config/               # Configuration directory
│   └── config.toml       # Main configuration file
├── docs/                 # Documentation
│   └── ansible-llm-integration-spec.md
├── examples/             # Example playbooks for users
│   └── windows_ssh/      # Windows SSH examples
├── logs/                 # Log files directory
├── models/               # TinyLlama model files directory
├── src/                  # Source code
│   ├── ansible_plugins/  # Custom Ansible plugins
│   │   ├── callbacks/    # Callback plugins
│   │   ├── filters/      # Filter plugins
│   │   └── modules/      # Custom modules
│   ├── api/              # API interfaces
│   │   ├── cli.py        # Command line interface
│   │   └── rest_api.py   # REST API
│   ├── llm_engine/       # TinyLlama integration
│   │   ├── model_loader.py
│   │   ├── prompt_templates.py
│   │   ├── response_processor.py
│   │   └── windows_processor.py
│   ├── main.py           # Main entry point
│   └── utils/            # Utilities
│       └── logger.py     # Logging setup
└── setup.py              # Setup script

## Docker Development Environment

A Docker-based development environment is available for easy testing across platforms (Linux, macOS, Windows).

### Prerequisites

- Docker and Docker Compose installed on your system
- Git to clone the repository

### Getting Started with Docker

1. **Setup the development environment**:
   ```bash
   # Clone the repository if you haven't already
   git clone https://github.com/yourusername/ansible-llm.git
   cd ansible-llm
   
   # Make the dev script executable
   chmod +x dev.sh
   
   # Setup test environment (creates SSH keys for mock hosts)
   ./dev.sh setup
   ```

2. **Start the development environment**:
   ```bash
   # Start the API server in development mode
   ./dev.sh start
   ```

3. **Download a model**:
   ```bash
   # List available models
   ./dev.sh model list
   
   # Download a TinyLlama model
   ./dev.sh model download TinyLlama-1.1B-Chat-v1.0
   ```

4. **Run tests**:
   ```bash
   # Run all tests
   ./dev.sh test
   
   # Run integration tests with mock Windows host
   ./dev.sh test-integration
   ```

5. **Access container shell**:
   ```bash
   # Get an interactive shell in the container
   ./dev.sh shell
   ```

6. **Other useful commands**:
   ```bash
   # View logs
   ./dev.sh logs
   
   # Restart the API service
   ./dev.sh restart
   
   # Stop the environment
   ./dev.sh stop
   
   # Clean up everything (including volumes)
   ./dev.sh clean
   ```

### Cross-Platform Considerations

- **Windows**: Use PowerShell or WSL2 to run Docker commands
- **File Permissions**: The container runs as root to avoid permission issues with mounted volumes
- **SSH Keys**: SSH keys for mock hosts are generated in `tests/mock_windows_host/`

### Testing with Mock Windows Host

The development environment includes a mock Windows host with PowerShell Core for testing Windows automation:

```bash
# Quick Start with Mock Windows testing
# 1. Build containers with sshpass support
docker-compose -f docker-compose.dev.yml build test_runner ansible_llm_api

# 2. Start all necessary containers
docker-compose -f docker-compose.dev.yml up -d test_runner ansible_llm_api mock_windows_host

# 3. Run the sample test playbook
docker-compose -f docker-compose.dev.yml exec -u root -e ANSIBLE_HOST_KEY_CHECKING=False test_runner ansible-playbook -i tests/mock_windows_host/inventory.ini tests/mock_windows_host/raw_test_playbook.yml -v

# Run your own custom playbook
docker-compose -f docker-compose.dev.yml exec -u root -e ANSIBLE_HOST_KEY_CHECKING=False test_runner ansible-playbook -i tests/mock_windows_host/inventory.ini your_playbook.yml -v
```

#### Mock Windows Host Features

- Runs PowerShell Core 7.x in a Linux container
- Provides SSH access with username 'ansible_user' and password 'ansible_password'
- Simulates a Windows-like environment with PowerShell
- Has Windows-like directory structures (C:\Windows, C:\Program Files, etc.)
- Allows testing of PowerShell scripts via Ansible
- Supports password-based SSH authentication using sshpass

#### Direct SSH Access

You can directly SSH into the mock Windows host for testing:

```bash
# From the test_runner container using password authentication
docker-compose -f docker-compose.dev.yml exec test_runner sshpass -p ansible_password ssh -o StrictHostKeyChecking=no ansible_user@mock_windows_host

# Run PowerShell commands directly
docker-compose -f docker-compose.dev.yml exec test_runner sshpass -p ansible_password ssh -o StrictHostKeyChecking=no ansible_user@mock_windows_host /opt/microsoft/powershell/7/pwsh -Command "Write-Output 'Hello from PowerShell!'"
```

> **Note**: The PowerShell executable in the mock Windows host is located at `/opt/microsoft/powershell/7/pwsh`. Always specify the full path when running PowerShell commands.

#### Complete Testing Example

A ready-to-use test playbook is included in the repository at `tests/mock_windows_host/raw_test_playbook.yml`. This is the recommended approach for testing PowerShell commands with Ansible:

```yaml
# tests/mock_windows_host/raw_test_playbook.yml
---
- name: Test PowerShell Execution on Mock Windows Host using Raw module
  hosts: windows
  gather_facts: false
  
  tasks:
    - name: Test PowerShell with raw module
      ansible.builtin.raw: /opt/microsoft/powershell/7/pwsh -Command "Write-Output 'Hello from PowerShell on mock Windows host'; Get-Process | Select-Object -First 5"
      register: raw_output
    
    - name: Show raw output
      ansible.builtin.debug:
        var: raw_output.stdout_lines
```

You can run this test playbook with:

```bash
docker-compose -f docker-compose.dev.yml exec -u root -e ANSIBLE_HOST_KEY_CHECKING=False test_runner ansible-playbook -i tests/mock_windows_host/inventory.ini tests/mock_windows_host/raw_test_playbook.yml -v
```

> **Important**: Using the `raw` module is recommended for Windows SSH targets as it doesn't rely on Python being available on the target host. For Windows environments, PowerShell is the preferred scripting language.

#### Troubleshooting Mock Windows Host

If you encounter issues with the mock Windows host, try these troubleshooting steps:

1. **Rebuild the containers with the latest updates**:
   ```bash
   docker-compose -f docker-compose.dev.yml build test_runner ansible_llm_api mock_windows_host
   ```

2. **Check if sshpass is correctly installed in the test_runner container**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec test_runner which sshpass
   ```
   If sshpass is not found, it means there might be an issue with the container build. Check the `Dockerfile.dev` to ensure sshpass is included in the apt-get install commands.

3. **Verify the PowerShell path in the mock Windows host**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec mock_windows_host find / -name pwsh -type f 2>/dev/null
   ```
   The path should be `/opt/microsoft/powershell/7/pwsh`. Make sure your inventory files and playbooks use this path.

4. **Test SSH connectivity manually**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec test_runner ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ansible_user@mock_windows_host
   # Password: ansible_password
   ```

5. **Verify PowerShell works in the mock host**:
   ```bash
   docker-compose -f docker-compose.dev.yml exec mock_windows_host /opt/microsoft/powershell/7/pwsh -Command "Write-Output 'Test'"
   ```

6. **Check inventory file configuration**:
   Ensure the inventory file for the mock Windows host has the correct settings:
   ```ini
   [windows]
   mock_windows ansible_host=mock_windows_host ansible_port=22 ansible_user=ansible_user ansible_password=ansible_password
   
   [windows:vars]
   ansible_connection=ssh
   ansible_shell_type=powershell
   ansible_shell_executable=/opt/microsoft/powershell/7/pwsh
   ansible_become=false
   ```

## Recent Updates

### June 2025

- Added sshpass to the test_runner container to support password-based SSH authentication with Ansible
- Fixed PowerShell path in mock Windows host and inventory files (/opt/microsoft/powershell/7/pwsh)
- Added support for raw module in playbooks to execute PowerShell commands without Python requirements 
- Enhanced documentation for working with the mock Windows host
- Added example playbooks for quick testing and validation
- Created raw_test_playbook.yml for easy testing of the mock Windows host
- Updated troubleshooting steps for common SSH connection issues

## Development

This project is in active development. The implementation follows the phases outlined in the specification document:

1. **Phase 1: Foundation** (Current Phase)
   - Basic integration between Ansible and TinyLlama 3
   - Simple playbook generation from natural language
   - Initial template library

2. **Phase 2: Enhancement** (Upcoming)
   - Advanced decision-making during playbook execution
   - Infrastructure analysis and recommendations
   - Performance optimizations

3. **Phase 3: Advanced Features** (Planned)
   - Learning from execution results to improve future automations
   - Multi-model support (alternative LLMs)
   - Advanced security features and compliance checking

## Security Considerations

- The LLM never has direct access to Ansible Vault or credentials
- All LLM processing happens locally by default
- Comprehensive logging of all LLM-generated content
- Optional human approval for LLM-generated playbooks before execution

## License

GNU General Public License v3.0

## Development Workflow

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/ansible-llm.git
   cd ansible-llm
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes and Test**
   ```bash
   # Implement your changes
   # Run tests (to be implemented)
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add your detailed commit message"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Open a PR against the main branch
   - Describe your changes in detail
   - Link any related issues

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
