#!/bin/bash

# Exit on error
set -e

# Detect OS
OS="$(uname)"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Setting up BooImagine..."

# Create src directory if it doesn't exist
mkdir -p src

# Check Python installation
if ! command_exists python3; then
    echo "Python 3 is required but not installed."
    if [ "$OS" = "Darwin" ]; then
        echo "Please install Python 3 using Homebrew: brew install python3"
    elif [ "$OS" = "Linux" ]; then
        echo "Please install Python 3 using your package manager"
        echo "For Ubuntu/Debian: sudo apt-get install python3"
        echo "For Fedora: sudo dnf install python3"
    else
        echo "Please install Python 3 from https://www.python.org/downloads/"
    fi
    exit 1
fi

# Check pip installation
if ! command_exists pip3; then
    echo "pip3 is required but not installed."
    if [ "$OS" = "Darwin" ]; then
        echo "Please install pip3 using Homebrew: brew install python3"
    elif [ "$OS" = "Linux" ]; then
        echo "Please install pip3 using your package manager"
        echo "For Ubuntu/Debian: sudo apt-get install python3-pip"
        echo "For Fedora: sudo dnf install python3-pip"
    else
        echo "Please install pip3 from https://pip.pypa.io/en/stable/installation/"
    fi
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if CUDA is available for PyTorch
if python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
    echo "CUDA is available. PyTorch will use GPU acceleration."
else
    echo "CUDA is not available. PyTorch will run on CPU only."
    echo "For better performance, consider installing CUDA if you have a compatible NVIDIA GPU."
fi

echo "Setup complete! You can now run the application with:"
echo "source venv/bin/activate && cd src && python main.py"
