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
    # Extract major and minor version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [[ $PYTHON_MAJOR -lt 3 || ($PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8) ]]; then
        print_error "Python version must be 3.8 or higher. Current version: $PYTHON_VERSION"
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

# Clone repository if not already cloned
clone_repository() {
    if [[ ! -d "BooImagine" ]]; then
        print_message "Cloning BooImagine repository..."
        if ! command_exists git; then
            print_error "Git is not installed. Please install Git first."
            exit 1
        fi
        git clone https://github.com/Bhuvanesh1729/BooImagine.git
        cd BooImagine
    elif [[ ! -f "requirements.txt" && ! -d ".git" ]]; then
        cd ..
        print_message "Cloning BooImagine repository..."
        if ! command_exists git; then
            print_error "Git is not installed. Please install Git first."
            exit 1
        fi
        git clone https://github.com/Bhuvanesh1729/BooImagine.git
        cd BooImagine
    fi
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
    
    # Clone repository if running via curl
    if [[ ! -f "requirements.txt" ]]; then
        clone_repository
    elif [[ "$(basename "$(pwd)")" == "scripts" ]]; then
        cd ..
    fi
    
    # Verify we're in the correct directory
    if [[ ! -f "requirements.txt" ]]; then
        print_error "Could not find requirements.txt. Please ensure you're in the BooImagine directory."
        exit 1
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
