#!/bin/bash
# Setup script for Video Converter GUI

echo "=================================="
echo "Video Converter GUI - Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if python3-venv is installed
echo ""
echo "Checking for python3-venv..."
if ! dpkg -l | grep -q python3.*-venv; then
    echo "python3-venv is not installed."
    echo "Installing python3-venv..."
    sudo apt install python3-venv -y
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

# Check FFmpeg installation
echo ""
echo "Checking FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg is installed"
    ffmpeg -version | head -1
else
    echo "✗ FFmpeg is NOT installed"
    echo ""
    echo "Please install FFmpeg:"
    echo "  sudo apt install ffmpeg"
fi

echo ""
echo "=================================="
echo "Setup completed successfully!"
echo "=================================="
echo ""
echo "To run the application:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python src/main.py"
echo ""
echo "Or use the run.sh script:"
echo "  ./run.sh"
echo ""
