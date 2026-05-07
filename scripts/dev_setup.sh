#!/bin/bash

# AI Hedge Fund Development Environment Setup Script
# This script sets up a complete development environment for the AI Hedge Fund project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Poetry is installed
check_poetry() {
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry is not installed. Please install Poetry first:"
        echo "Visit: https://python-poetry.org/docs/#installation"
        exit 1
    fi
    print_success "Poetry is installed"
}

# Create virtual environment and install dependencies
setup_environment() {
    print_status "Creating virtual environment and installing dependencies..."
    
    # Install main dependencies
    poetry install --no-root
    
    # Install development dependencies
    poetry install --with dev --no-root
    
    print_success "Dependencies installed successfully"
}

# Setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."
    
    if ! command -v pre-commit &> /dev/null; then
        poetry run pip install pre-commit
    fi
    
    poetry run pre-commit install
    print_success "Pre-commit hooks installed"
}

# Create environment configuration
setup_environment_config() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
        else
            print_warning ".env.example not found, creating basic .env file"
            cat > .env << EOF
# AI Hedge Fund Configuration
# Copy this file to .env and modify the values as needed

# Data Configuration
DATA_PROVIDER=yahoo
DATA_CACHE_ENABLED=true
DATA_CACHE_TTL=3600

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_OLLAMA_MODEL=qwen3.5:latest
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/ai_hedge_fund.log
LOG_MAX_SIZE_MB=10
LOG_BACKUP_COUNT=5

# Performance Configuration
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30

# Backtesting Configuration
DEFAULT_INITIAL_CAPITAL=100000.0
DEFAULT_MARGIN_REQUIREMENT=0.0

# API Keys (Optional)
# FINANCIAL_DATASETS_API_KEY=your-api-key-here
# OPENAI_API_KEY=your-api-key-here
# ANTHROPIC_API_KEY=your-api-key-here
# GROQ_API_KEY=your-api-key-here
# DEEPSEEK_API_KEY=your-api-key-here
EOF
            print_success "Created basic .env file"
        fi
    else
        print_success ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p data/cache
    mkdir -p data/samples
    mkdir -p tests/fixtures
    
    print_success "Directories created"
}

# Download sample data (if available)
download_sample_data() {
    print_status "Downloading sample data..."
    
    # Create sample data directory
    mkdir -p data/samples
    
    # Create a simple sample price data file
    cat > data/samples/sample_prices.csv << EOF
date,open,high,low,close,volume
2024-01-01,150.0,155.0,149.0,152.0,1000000
2024-01-02,152.0,156.0,151.0,154.0,1200000
2024-01-03,154.0,158.0,153.0,156.0,1100000
2024-01-04,156.0,160.0,155.0,158.0,1300000
2024-01-05,158.0,162.0,157.0,160.0,1400000
EOF
    
    print_success "Sample data created"
}

# Run initial tests to verify setup
run_initial_tests() {
    print_status "Running initial tests to verify setup..."
    
    if poetry run pytest tests/ -x --tb=short -q; then
        print_success "Initial tests passed"
    else
        print_warning "Some tests failed - this might be expected during initial setup"
    fi
}

# Display completion message
show_completion() {
    echo ""
    echo "========================================="
    echo " AI Hedge Fund Development Setup Complete"
    echo "========================================="
    echo ""
    echo "Next steps:"
    echo "1. Review and edit the .env file for your configuration"
    echo "2. Run 'poetry shell' to activate the virtual environment"
    echo "3. Run 'python src/main.py' to start the application"
    echo "4. Run 'poetry run pytest' to run all tests"
    echo ""
    echo "Available commands:"
    echo "  ./scripts/run_tests.sh    - Run all tests"
    echo "  ./scripts/format_code.sh  - Format code"
    echo "  ./scripts/lint_code.sh    - Lint code"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "Setting up AI Hedge Fund development environment..."
    echo ""
    
    check_poetry
    setup_environment
    setup_pre_commit
    setup_environment_config
    create_directories
    download_sample_data
    run_initial_tests
    show_completion
}

# Run main function
main "$@"