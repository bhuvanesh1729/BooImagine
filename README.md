# BooImagine

A user-friendly GUI application for browsing, selecting, and utilizing Hugging Face models for image generation. Built with Python and CustomTkinter, BooImagine provides an intuitive interface to interact with state-of-the-art AI image generation models.

## Features

### Core Functionality
- Browse and select pre-trained image generation models from Hugging Face Hub
- Search functionality to find specific models
- Generate images based on text prompts
- Support for image-to-image transformations
- Basic AI-powered image editing capabilities
- Save and load custom prompts

### User Interface
- **Model Selection Panel (Left Side)**
  - Browse and select models from Hugging Face
  - View model information and statistics
  - Search for specific models
  - Track locally downloaded models

- **Generation Panel (Right Side)**
  - Text prompt input
  - Image display area
  - Style presets for quick modifications
  - Progress tracking and context window
  - Save/load prompts and generated images

### Model Types Support
- Text-to-Image generation
- Image-to-Image transformation
- Text-to-Video generation (for supported models)
- Style transfer and image enhancement

### Technical Features
- Multi-threaded model loading and image generation
- GPU acceleration support (when available)
- Automatic model pipeline selection
- Token usage tracking
- Memory usage monitoring

## Requirements

- Python 3.8 or higher
- pip3
- Virtual environment (recommended)
- CUDA-compatible GPU (optional, for better performance)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Bhuvanesh1729/BooImagine.git
cd BooImagine
```

2. Make the deployment script executable:
```bash
chmod +x scripts/deployment.sh
```

3. Run the deployment script:
```bash
./scripts/deployment.sh
```

The script will:
- Check for required dependencies
- Create a virtual environment
- Install required packages
- Check for CUDA availability
- Set up the application

## Running the Application

After installation, you can run the application using:

```bash
source venv/bin/activate
cd src
python main.py
```

## Usage Guide

1. **Selecting a Model**
   - Use the search bar to find specific models
   - Browse the list of available models
   - Click on a model to view its details
   - Click "Load Selected Model" to load it

2. **Generating Images**
   - Enter your prompt in the text area
   - Click "Generate" to create an image
   - Use style presets to modify the generation
   - Save generated images using the "Save Image" button

3. **Managing Prompts**
   - Save frequently used prompts with "Save Prompt"
   - Load saved prompts using "Load Prompt"
   - Apply style presets to enhance prompts

4. **Image Editing**
   - Upload images for transformation
   - Apply various AI-powered enhancements
   - Save edited images

## Troubleshooting

### Common Issues

1. **Model Loading Fails**
   - Ensure you have enough disk space
   - Check your internet connection
   - Try a different model

2. **CUDA/GPU Issues**
   - Verify CUDA is properly installed
   - Update GPU drivers
   - Check CUDA compatibility with PyTorch

3. **Memory Issues**
   - Close other resource-intensive applications
   - Try smaller models
   - Reduce batch size or image resolution

### Error Logs

The application logs errors and information to `booimagine.log`. Check this file if you encounter issues.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for their amazing models and infrastructure
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI components
- The open-source AI community for their contributions
