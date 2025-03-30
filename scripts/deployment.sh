#!/bin/bash
# BooImagine Deployment Script
# This script automates the setup process for BooImagine on macOS, Linux, and Windows (via Git Bash)

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[BooImagine Setup]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[Warning]${NC} $1"
}

print_error() {
    echo -e "${RED}[Error]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macOS" ;;
        Linux*)     OS="Linux" ;;
        MINGW*|MSYS*|CYGWIN*) OS="Windows" ;;
        *)          OS="Unknown" ;;
    esac
    print_message "Detected operating system: $OS"
}

# Check Python version
check_python() {
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_message "Python version: $PYTHON_VERSION"

    # Check if Python version is at least 3.8
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]]; then
        print_error "Python version must be 3.8 or higher. Please upgrade Python."
        exit 1
    fi
}

# Check pip installation
check_pip() {
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
    print_message "pip is installed."
}

# Create and activate virtual environment
setup_venv() {
    print_message "Setting up virtual environment..."
    
    # Create virtual environment
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment based on OS
    if [[ "$OS" == "Windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    print_message "Virtual environment created and activated."
}

# Install dependencies
install_dependencies() {
    print_message "Installing dependencies..."
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    python -m pip install -r requirements.txt
    
    print_message "Dependencies installed successfully."
}

# Create necessary directories if they don't exist
create_directories() {
    print_message "Creating necessary directories..."
    
    # Create assets directory
    mkdir -p src/assets
    
    print_message "Directories created."
}

# Main function
main() {
    print_message "Starting BooImagine setup..."
    
    # Detect OS
    detect_os
    
    # Check Python
    check_python
    
    # Check pip
    check_pip
    
    # Navigate to project root (assuming script is run from scripts directory)
    if [[ "$(basename "$(pwd)")" == "scripts" ]]; then
        cd ..
    fi
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Create directories
    create_directories
    
    print_message "Setup completed successfully!"
    print_message "To run BooImagine:"
    if [[ "$OS" == "Windows" ]]; then
        echo "   1. Activate the virtual environment: .\\venv\\Scripts\\activate"
    else
        echo "   1. Activate the virtual environment: source venv/bin/activate"
    fi
    echo "   2. Run the application: cd src && python main.py"
}

# Execute main function
main
