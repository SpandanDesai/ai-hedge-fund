#!/bin/bash

# AI Hedge Fund Test Runner Script
# This script runs tests with various configurations and options

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

# Default values
TEST_PATH="tests/"
VERBOSE=false
COVERAGE=false
FAIL_FAST=false
INTEGRATION=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -x|--fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -i|--integration)
            INTEGRATION=true
            shift
            ;;
        --*|-*)
            print_error "Unknown option $1"
            exit 1
            ;;
        *)
            TEST_PATH="$1"
            shift
            ;;
    esac
done

# Build pytest arguments
PYTEST_ARGS=""

if [ "$VERBOSE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -v"
else
    PYTEST_ARGS="$PYTEST_ARGS -q"
fi

if [ "$FAIL_FAST" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -x"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS --cov=src --cov-report=term --cov-report=html"
fi

if [ "$INTEGRATION" = false ]; then
    PYTEST_ARGS="$PYTEST_ARGS -m 'not integration'"
fi

# Run tests
print_status "Running tests in $TEST_PATH..."
print_status "pytest args: $PYTEST_ARGS"

if poetry run pytest $TEST_PATH $PYTEST_ARGS; then
    print_success "All tests passed!"
    exit 0
else
    print_error "Some tests failed"
    exit 1
fi