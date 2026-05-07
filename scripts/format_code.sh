#!/bin/bash

# AI Hedge Fund Code Formatter Script
# This script formats code using black and isort

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if formatting tools are available
check_tools() {
    if ! poetry run black --version &> /dev/null; then
        print_error "black is not available. Please install dev dependencies:"
        echo "  poetry install --with dev"
        exit 1
    fi
    
    if ! poetry run isort --version &> /dev/null; then
        print_error "isort is not available. Please install dev dependencies:"
        echo "  poetry install --with dev"
        exit 1
    fi
}

# Format Python code
format_python() {
    print_status "Formatting Python code with black..."
    poetry run black src/ tests/ app/backend/
    
    print_status "Sorting imports with isort..."
    poetry run isort src/ tests/ app/backend/
    
    print_success "Python code formatted successfully"
}

# Format other files (if needed)
format_other() {
    print_status "Checking for other files to format..."
    
    # Add formatting for other file types here if needed
    # For example: JSON, YAML, Markdown files
    
    print_success "Other files processed"
}

# Main execution
main() {
    echo ""
    echo "Formatting AI Hedge Fund code..."
    echo ""
    
    check_tools
    format_python
    format_other
    
    echo ""
    print_success "Code formatting complete!"
    echo ""
}

# Run main function
main "$@"