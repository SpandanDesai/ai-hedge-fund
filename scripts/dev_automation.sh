#!/bin/bash

# AI Hedge Fund Development Automation Script
# This script provides a menu-driven interface for common development tasks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${CYAN}=========================================${NC}"
    echo -e "${CYAN}  AI Hedge Fund Development Automation  ${NC}"
    echo -e "${CYAN}=========================================${NC}"
    echo ""
}

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

# Check if script is being run from project root
check_project_root() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
}

# Display menu options
show_menu() {
    echo ""
    echo -e "${CYAN}Development Tasks:${NC}"
    echo "1. Setup Development Environment"
    echo "2. Run Tests"
    echo "3. Format Code"
    echo "4. Lint Code"
    echo "5. Run Application (CLI)"
    echo "6. Run Web Application"
    echo "7. Run All Checks (Test + Format + Lint)"
    echo "8. Generate Performance Report"
    echo "9. Clean Project"
    echo "0. Exit"
    echo ""
    echo -n "Enter your choice (0-9): "
}

# Setup development environment
setup_environment() {
    print_status "Setting up development environment..."
    ./scripts/dev_setup.sh
}

# Run tests
run_tests() {
    print_status "Running tests..."
    ./scripts/run_tests.sh "$@"
}

# Format code
format_code() {
    print_status "Formatting code..."
    ./scripts/format_code.sh
}

# Lint code
lint_code() {
    print_status "Linting code..."
    ./scripts/lint_code.sh
}

# Run CLI application
run_cli_app() {
    print_status "Running CLI application..."
    ./scripts/run_app.sh --mode cli "$@"
}

# Run web application
run_web_app() {
    print_status "Running web application..."
    ./scripts/run_app.sh --mode web
}

# Run all checks
run_all_checks() {
    print_status "Running all code quality checks..."
    echo ""
    
    print_status "1. Formatting code..."
    ./scripts/format_code.sh
    echo ""
    
    print_status "2. Linting code..."
    ./scripts/lint_code.sh
    echo ""
    
    print_status "3. Running tests..."
    ./scripts/run_tests.sh
    echo ""
    
    print_success "All checks completed successfully!"
}

# Generate performance report
generate_performance_report() {
    print_status "Generating performance report..."
    poetry run python -c "
from src.utils.performance import log_performance_report
log_performance_report()
print('Performance report generated and logged')
"
}

# Clean project
clean_project() {
    print_status "Cleaning project..."
    
    # Remove Python cache files
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete
    find . -name "*.pyo" -delete
    find . -name "*.pyd" -delete
    
    # Remove coverage files
    rm -rf .coverage htmlcov coverage.xml
    
    # Remove build artifacts
    rm -rf build/ dist/ *.egg-info
    
    # Remove test artifacts
    rm -rf .pytest_cache
    
    print_success "Project cleaned successfully"
}

# Main execution
main() {
    check_project_root
    
    while true; do
        print_header
        show_menu
        
        read choice
        case $choice in
            1)
                setup_environment
                ;;
            2)
                echo -n "Enter test options (e.g., -v for verbose, -c for coverage): "
                read test_options
                run_tests $test_options
                ;;
            3)
                format_code
                ;;
            4)
                lint_code
                ;;
            5)
                echo -n "Enter application options (e.g., --tickers AAPL,MSFT): "
                read app_options
                run_cli_app $app_options
                ;;
            6)
                run_web_app
                ;;
            7)
                run_all_checks
                ;;
            8)
                generate_performance_report
                ;;
            9)
                clean_project
                ;;
            0)
                echo ""
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter a number between 0-9."
                ;;
        esac
        
        echo ""
        echo -n "Press Enter to continue..."
        read
    done
}

# Show help if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    print_header
    echo "Usage: ./scripts/dev_automation.sh"
    echo ""
    echo "This script provides a menu-driven interface for common development tasks."
    echo ""
    echo "Available options:"
    echo "  --help, -h    Show this help message"
    echo ""
    exit 0
fi

# Run main function
main "$@"