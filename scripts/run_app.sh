#!/bin/bash

# AI Hedge Fund Application Runner Script
# This script runs the main application with various configurations

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
MODE="cli"
TICKERS="AAPL,MSFT,GOOGL"
START_DATE="2024-01-01"
END_DATE="2024-03-01"
INITIAL_CASH="100000.0"
MODEL="qwen3.5:latest"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --tickers)
            TICKERS="$2"
            shift 2
            ;;
        --start-date)
            START_DATE="$2"
            shift 2
            ;;
        --end-date)
            END_DATE="$2"
            shift 2
            ;;
        --initial-cash)
            INITIAL_CASH="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --web)
            MODE="web"
            shift
            ;;
        --help)
            echo "Usage: ./run_app.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mode MODE          Execution mode: cli or web (default: cli)"
            echo "  --tickers TICKERS    Comma-separated ticker symbols (default: AAPL,MSFT,GOOGL)"
            echo "  --start-date DATE    Start date in YYYY-MM-DD format (default: 2024-01-01)"
            echo "  --end-date DATE      End date in YYYY-MM-DD format (default: 2024-03-01)"
            echo "  --initial-cash AMT   Initial cash amount (default: 100000.0)"
            echo "  --model MODEL        LLM model to use (default: qwen3.5:latest)"
            echo "  --web                Run web application (same as --mode web)"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the application based on mode
run_application() {
    case "$MODE" in
        "cli")
            print_status "Running CLI application..."
            print_status "Tickers: $TICKERS"
            print_status "Date range: $START_DATE to $END_DATE"
            print_status "Initial cash: $INITIAL_CASH"
            print_status "Model: $MODEL"
            echo ""
            
            poetry run python src/main.py \
                --tickers "$TICKERS" \
                --start-date "$START_DATE" \
                --end-date "$END_DATE" \
                --initial-cash "$INITIAL_CASH" \
                --model "$MODEL"
            ;;
        "web")
            print_status "Starting web application..."
            echo ""
            echo "Web application will be available at:"
            echo "  Frontend: http://localhost:5173"
            echo "  Backend API: http://localhost:8000"
            echo ""
            echo "Press Ctrl+C to stop the application"
            echo ""
            
            # Start the web application
            poetry run python app/backend/main.py
            ;;
        *)
            print_error "Unknown mode: $MODE"
            echo "Available modes: cli, web"
            exit 1
            ;;
    esac
}

# Main execution
main() {
    echo ""
    echo "Starting AI Hedge Fund Application..."
    echo "===================================="
    echo ""
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        print_warning ".env file not found. Using default configuration."
        echo "Run ./scripts/dev_setup.sh to create a proper .env file"
    fi
    
    run_application
}

# Run main function
main "$@"