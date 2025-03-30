# Local Environment Setup Guide

This guide provides step-by-step instructions for setting up BooImagine in your local environment.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Quick Install

You can quickly install and set up BooImagine using our deployment script:

```bash
# Download and run the deployment script directly
curl -sSL https://raw.githubusercontent.com/Bhuvanesh1729/BooImagine/main/scripts/deployment.sh | bash
```

This command downloads and executes the deployment script, which will set up the entire environment for you.

## Manual Setup Instructions

1. **Create and Activate Virtual Environment**

   ```bash
   # Navigate to the project directory
   cd BooImagine

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # For Windows:
   .\venv\Scripts\activate
   # For macOS/Linux:
   source venv/bin/activate
   ```

2. **Install Dependencies**

   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

3. **Hugging Face Authentication (Optional)**

   If you want to use private models or have higher rate limits:
   ```bash
   # Install Hugging Face CLI
   pip install --upgrade huggingface_hub

   # Login to Hugging Face
   huggingface-cli login
   ```

4. **Run the Application**

   ```bash
   # Navigate to the src directory
   cd src

   # Run the application
   python main.py
   ```

## Troubleshooting

1. **GPU Support**
   - If you have a CUDA-compatible GPU, ensure you have the appropriate CUDA toolkit installed
   - The application will automatically use GPU if available, otherwise will fall back to CPU

2. **Common Issues**

   a. **Package Installation Errors**
   ```bash
   # Try upgrading pip
   python -m pip install --upgrade pip

   # Install packages one by one if there are conflicts
   pip install torch
   pip install transformers
   pip install -r requirements.txt
   ```

   b. **Memory Issues**
   - If you encounter memory errors while loading models:
     - Try closing other applications
     - Use smaller models
     - Reduce batch size if applicable

   c. **Model Download Issues**
   - Check your internet connection
   - Ensure you have enough disk space
   - Try using a VPN if you're having regional access issues

3. **Environment Issues**

   If you encounter environment-related issues:
   ```bash
   # Deactivate and remove existing environment
   deactivate
   rm -rf venv

   # Create new environment and reinstall dependencies
   python -m venv venv
   source venv/bin/activate  # or .\venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

## Additional Configuration

1. **Custom Model Directory**
   - By default, models are downloaded to the Hugging Face cache directory
   - To use a custom directory, set the environment variable:
     ```bash
     # For Windows:
     set HF_HOME=path/to/custom/directory
     # For macOS/Linux:
     export HF_HOME=path/to/custom/directory
     ```

2. **Proxy Configuration**
   If you're behind a proxy:
   ```bash
   # For Windows:
   set HTTPS_PROXY=http://proxy.example.com:port
   # For macOS/Linux:
   export HTTPS_PROXY=http://proxy.example.com:port
   ```

## System Requirements

- **Minimum Requirements:**
  - CPU: Any modern multi-core processor
  - RAM: 8GB minimum, 16GB recommended
  - Storage: 10GB free space
  - Python 3.8 or higher

- **Recommended for GPU Usage:**
  - NVIDIA GPU with CUDA support
  - CUDA Toolkit 11.0 or higher
  - 8GB+ GPU memory for larger models

## Support

If you encounter any issues not covered in this guide:
1. Check the GitHub repository issues section
2. Ensure all prerequisites are properly installed
3. Try creating a fresh virtual environment
4. Update all dependencies to their latest compatible versions
