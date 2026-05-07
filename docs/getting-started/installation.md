# Installation Guide

This guide will help you install and set up the AI Hedge Fund project on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+**: [Download Python](https://www.python.org/downloads/)
- **Poetry**: Python dependency management tool
- **Ollama** (optional): For local LLM inference
- **Redis** (optional): For enhanced caching

### Installing Poetry

```bash
# On macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# On Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# Add Poetry to your PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Installing Ollama

```bash
# On macOS
brew install ollama

# On Linux
curl -fsSL https://ollama.ai/install.sh | sh

# On Windows
# Download from https://ollama.ai/download
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-hedge-fund.git
cd ai-hedge-fund
```

### 2. Set Up Development Environment

The project includes an automated setup script:

```bash
# Run the setup script
./scripts/dev_setup.sh
```

This script will:
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks
- Create configuration files
- Download sample data

### 3. Manual Installation (Alternative)

If you prefer to install manually:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\\Scripts\\activate

# Install dependencies
pip install -e .
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install
```

### 4. Configuration

Create a `.env` file for configuration:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your favorite editor
```

### 5. Verify Installation

Run a quick test to verify everything is working:

```bash
# Run basic tests
./scripts/run_tests.sh tests/test_data_providers.py

# Test the application
./scripts/run_app.sh --tickers AAPL --start-date 2024-01-01 --end-date 2024-01-10
```

## Docker Installation

If you prefer using Docker:

### 1. Install Docker

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Docker Engine](https://docs.docker.com/engine/install/)

### 2. Build and Run

```bash
# Build the Docker image
docker build -t ai-hedge-fund .

# Run the application
docker run -it --rm -p 8000:8000 ai-hedge-fund
```

### 3. Docker Compose

```bash
# Using Docker Compose
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

## Platform-Specific Instructions

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python poetry ollama redis
```

### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and tools
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### Windows

1. Install Python from [python.org](https://python.org)
2. Install Chocolatey package manager
3. Use Chocolatey to install dependencies:

```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install poetry ollama redis
```

## Troubleshooting

### Common Issues

1. **Python Version Issues**
   ```bash
   # Check Python version
   python --version
   
   # If wrong version, use python3 explicitly
   python3 -m venv .venv
   ```

2. **Permission Errors**
   ```bash
   # On Linux/macOS, you might need sudo for some installations
   sudo apt install python3.11-venv
   ```

3. **Ollama Connection Issues**
   ```bash
   # Start Ollama service
   ollama serve
   
   # Pull a model
   ollama pull qwen3.5:latest
   ```

4. **Redis Connection Issues**
   ```bash
   # Start Redis server
   redis-server
   
   # Or use Docker
   docker run --name redis -d -p 6379:6379 redis
   ```

### Getting Help

If you encounter issues:

1. Check the [FAQ](../getting-started/faq.md)
2. Search existing [issues](https://github.com/your-username/ai-hedge-fund/issues)
3. Create a new issue with details about your problem

## Next Steps

After installation, check out:

- [Configuration Guide](./configuration.md) - Learn how to configure the system
- [Quick Start Guide](./quick-start.md) - Get started with basic usage
- [API Reference](../api/data-models.md) - Explore the available APIs