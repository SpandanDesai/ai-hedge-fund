#!/bin/bash

# AI Hedge Fund Code Linter Script
# This script runs linting checks using flake8 and other tools

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

# Check if linting tools are available
check_tools() {
    if ! poetry run flake8 --version &> /dev/null; then
        print_error "flake8 is not available. Please install dev dependencies:"
        echo "  poetry install --with dev"
        exit 1
    fi
    
    if ! poetry run mypy --version &> /dev/null; then
        print_warning "mypy is not available. Type checking will be skipped."
    fi
}

# Run flake8 linting
run_flake8() {
    print_status "Running flake8 linting..."
    
    if poetry run flake8 src/ tests/ app/backend/ --max-line-length=88 --show-source; then
        print_success "flake8 checks passed"
    else
        print_error "flake8 checks failed"
        exit 1
    fi
}

# Run mypy type checking
run_mypy() {
    if poetry run mypy --version &> /dev/null; then
        print_status "Running mypy type checking..."
        
        if poetry run mypy src/ --ignore-missing-imports; then
            print_success "mypy checks passed"
        else
            print_warning "mypy checks found some issues"
        fi
    fi
}

# Run bandit security scanning
run_bandit() {
    if poetry run bandit --version &> /dev/null; then
        print_status "Running bandit security scanning..."
        
        if poetry run bandit -r src/ -s B101; then
            print_success "bandit checks passed"
        else
            print_warning "bandit checks found some issues"
        fi
    else
        print_warning "bandit not available, skipping security scan"
    fi
}

# Run pre-commit hooks
run_pre_commit() {
    if command -v pre-commit &> /dev/null; then
        print_status "Running pre-commit hooks..."
        
        if poetry run pre-commit run --all-files; then
            print_success "pre-commit checks passed"
        else
            print_error "pre-commit checks failed"
            exit 1
        fi
    else
        print_warning "pre-commit not available, skipping"
    fi
}

# Main execution
main() {
    echo ""
    echo "Running AI Hedge Fund code linting..."
    echo ""
    
    check_tools
    run_flake8
    run_mypy
    run_bandit
    run_pre_commit
    
    echo ""
    print_success "All linting checks completed!"
    echo ""
}

# Run main function
main "$@"