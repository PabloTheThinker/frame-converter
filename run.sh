#!/bin/bash
# Run script for Video Converter GUI

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run setup.sh first:"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
echo "Starting Video Converter GUI..."
python src/main.py
