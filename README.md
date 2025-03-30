# BooImagine

A user-friendly GUI application for browsing, selecting, and utilizing Hugging Face models for image generation.

![BooImagine Logo](docs/logo.png)

## Features

- **Model Selection**: Browse and search for image generation models from Hugging Face Hub
- **Image Generation**: Generate images based on text prompts
- **Style Application**: Apply various artistic styles to your generated images
- **Prompt Management**: Save and reuse your favorite prompts
- **Image Editing**: Basic AI-powered image editing capabilities

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Quick Install

Option 1: One-line installation (macOS/Linux):
```bash
# Download and run the deployment script directly
curl -sSL https://raw.githubusercontent.com/Bhuvanesh1729/BooImagine/main/scripts/deployment.sh | bash
```

Option 2: Clone and install:
```bash
# Clone the repository
git clone https://github.com/Bhuvanesh1729/BooImagine.git
cd BooImagine

# Run the deployment script
# For macOS/Linux:
bash scripts/deployment.sh
# For Windows:
.\scripts\deployment.bat
```

For detailed installation instructions, see [deployment.md](deployment.md).

## Usage

### Starting the Application

After installation, run the application:

```bash
# Activate the virtual environment if not already activated
# For Windows:
.\venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate

# Run the application
cd src
python main.py
```

### Basic Workflow

1. **Select a Model**:
   - Browse the available models in the left panel
   - Use the search bar to find specific models
   - Click on a model to view its details
   - Click "Load Selected Model" to load it

2. **Create a Prompt**:
   - Enter your text prompt in the prompt area
   - Optionally use the style buttons for quick prompts
   - Click "Generate Image" to create your image

3. **Save and Manage Prompts**:
   - Click "Save Prompt" to save your current prompt
   - Click "Load Prompt" to use a previously saved prompt

4. **Edit Images**:
   - Use the image editing buttons to modify your generated image
   - Options include background removal, enhancement, and more

## Architecture

BooImagine follows a simple MVC-inspired architecture:

- **Model**: Handles interaction with Hugging Face API and models
- **View**: Tkinter-based GUI components
- **Controller**: Application logic connecting the model and view

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for their amazing models and API
- All the open-source contributors who make their models available
- The Python and Tkinter communities for their excellent documentation

## Contact

Bhuvanesh - [@Bhuvanesh1729](https://github.com/Bhuvanesh1729)

Project Link: [https://github.com/Bhuvanesh1729/BooImagine](https://github.com/Bhuvanesh1729/BooImagine)
