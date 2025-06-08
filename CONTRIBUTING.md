# Contributing to Ansible-TinyLlama Integration

Thank you for your interest in contributing to the Ansible-TinyLlama Integration project! This document provides guidelines and best practices for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please be respectful and considerate of others when contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```
   git clone https://github.com/yourusername/ansible-llm.git
   cd ansible-llm
   ```
3. Add the original repository as a remote:
   ```
   git remote add upstream https://github.com/original-owner/ansible-llm.git
   ```
4. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Development Environment

- Python 3.12+
- Ansible 2.14+
- PyTorch 2.0+ or ONNX Runtime
- Git

## Branch Naming Convention

Please use the following naming convention for branches:

- `feature/your-feature-name` - For new features
- `bugfix/issue-description` - For bug fixes
- `docs/documentation-update` - For documentation updates
- `refactor/component-name` - For code refactoring

## Commit Message Guidelines

Follow these guidelines for commit messages:

- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Reference issues in the body, not the title
- Separate the title from the body with a blank line
- Use the body to explain what and why, not how

Example:
```
Add Windows SSH module processor

This adds a specialized processor for Windows SSH playbooks that ensures
proper connection settings and module usage.

Fixes #123
```

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate
2. Update the CHANGELOG.md with details of changes
3. Make sure all tests pass
4. Ensure your code follows the project's coding standards
5. Get at least one review from a maintainer
6. You may merge the Pull Request once it has been approved

## Coding Standards

- Follow PEP 8 for Python code style
- Use type hints where appropriate
- Document all functions, classes, and modules with docstrings
- Keep line length to a maximum of 100 characters
- Use 4 spaces for indentation (no tabs)

## Testing Guidelines

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage

## Documentation

- Update documentation for any feature changes
- Document all public APIs
- Use Markdown for documentation files
- Include examples where appropriate

Thank you for contributing!
