#!/bin/bash

# AI Hedge Fund Documentation Generation Script
# This script generates comprehensive documentation for the project

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

# Check if documentation tools are available
check_tools() {
    if ! poetry run mkdocs --version &> /dev/null; then
        print_error "MkDocs is not available. Please install documentation dependencies:"
        echo "  poetry install --with docs"
        exit 1
    fi
    
    if ! poetry run pdoc --version &> /dev/null; then
        print_error "pdoc is not available. Please install documentation dependencies:"
        echo "  poetry install --with docs"
        exit 1
    fi
}

# Generate API documentation with pdoc
generate_api_docs() {
    print_status "Generating API documentation with pdoc..."
    
    # Create API documentation directory
    mkdir -p docs/api
    
    # Generate API docs
    poetry run pdoc src --output-dir docs/api --docformat google
    
    print_success "API documentation generated"
}

# Build MkDocs documentation
build_mkdocs() {
    print_status "Building MkDocs documentation..."
    
    # Build the documentation site
    poetry run mkdocs build
    
    print_success "MkDocs documentation built"
}

# Serve documentation locally
serve_docs() {
    print_status "Serving documentation locally..."
    echo ""
    echo "Documentation will be available at:"
    echo "  http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Serve the documentation
    poetry run mkdocs serve
}

# Deploy documentation to GitHub Pages
deploy_docs() {
    print_status "Deploying documentation to GitHub Pages..."
    
    # Deploy to GitHub Pages
    poetry run mkdocs gh-deploy --force
    
    print_success "Documentation deployed to GitHub Pages"
}

# Clean documentation build artifacts
clean_docs() {
    print_status "Cleaning documentation build artifacts..."
    
    # Remove built documentation
    rm -rf site/
    rm -rf docs/api/
    
    print_success "Documentation artifacts cleaned"
}

# Main execution
main() {
    local command="build"
    local serve=false
    local deploy=false
    local clean=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            serve)
                serve=true
                shift
                ;;
            deploy)
                deploy=true
                shift
                ;;
            clean)
                clean=true
                shift
                ;;
            --help|-h)
                echo "Usage: ./scripts/generate_docs.sh [COMMAND]"
                echo ""
                echo "Commands:"
                echo "  serve       Serve documentation locally"
                echo "  deploy      Deploy to GitHub Pages"
                echo "  clean       Clean build artifacts"
                echo "  (default)   Build documentation"
                echo ""
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    echo ""
    echo "Generating AI Hedge Fund Documentation..."
    echo "=========================================="
    echo ""
    
    check_tools
    
    if [ "$clean" = true ]; then
        clean_docs
        exit 0
    fi
    
    # Generate API documentation
    generate_api_docs
    
    # Build documentation
    build_mkdocs
    
    if [ "$deploy" = true ]; then
        deploy_docs
    elif [ "$serve" = true ]; then
        serve_docs
    else
        print_success "Documentation generated successfully!"
        echo ""
        echo "The documentation is available in the 'site/' directory"
        echo ""
        echo "To view locally:"
        echo "  ./scripts/generate_docs.sh serve"
        echo ""
        echo "To deploy to GitHub Pages:"
        echo "  ./scripts/generate_docs.sh deploy"
        echo ""
    fi
}

# Run main function
main "$@"