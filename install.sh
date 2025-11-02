#!/bin/bash

# FrameConverter Installation Script
# This script installs FrameConverter as a desktop application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FrameConverter Installation Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Python 3 is installed
echo -e "${YELLOW}[1/6]${NC} Checking for Python 3..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check if pip is installed
echo -e "${YELLOW}[2/6]${NC} Checking for pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    echo "Please install pip3: sudo apt install python3-pip"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip3 found"

# Check if FFmpeg is installed
echo -e "${YELLOW}[3/6]${NC} Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: FFmpeg is not installed${NC}"
    echo "Please install FFmpeg: sudo apt install ffmpeg"
    exit 1
fi
FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
echo -e "${GREEN}✓${NC} FFmpeg ${FFMPEG_VERSION} found"

# Install Python dependencies
echo -e "${YELLOW}[4/6]${NC} Installing Python dependencies..."
pip3 install --user -r "$PROJECT_DIR/requirements.txt" --quiet
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create .desktop file for applications menu
echo -e "${YELLOW}[5/6]${NC} Creating desktop application entry..."
DESKTOP_FILE="$HOME/.local/share/applications/frameconverter.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=FrameConverter
Comment=Convert MP4 videos to MOV format optimized for DaVinci Resolve
Exec=/usr/bin/env bash -c 'export PYTHONPATH="$HOME/.local/lib/python3.10/site-packages:\$PYTHONPATH" && cd "$PROJECT_DIR" && /usr/bin/python3 src/main.py'
Icon=$PROJECT_DIR/src/resources/app_icon.png
Terminal=false
Categories=AudioVideo;Video;AudioVideoEditing;
Keywords=video;converter;ffmpeg;resolve;davinci;mov;mp4;
StartupNotify=true
StartupWMClass=FrameConverter
DESKTOP_EOF

chmod +x "$DESKTOP_FILE"
echo -e "${GREEN}✓${NC} Desktop entry created"

# Create desktop shortcut (optional)
echo -e "${YELLOW}[6/6]${NC} Creating desktop shortcut..."
DESKTOP_SHORTCUT="$HOME/Desktop/frameconverter.desktop"
if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_FILE" "$DESKTOP_SHORTCUT"
    chmod +x "$DESKTOP_SHORTCUT"
    
    # For Ubuntu/GNOME - mark as trusted
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_SHORTCUT" "metadata::trusted" true 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓${NC} Desktop shortcut created"
else
    echo -e "${YELLOW}⚠${NC} Desktop folder not found, skipping desktop shortcut"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "You can now launch FrameConverter by:"
echo -e "  1. ${BLUE}Searching for 'FrameConverter' in your applications menu${NC}"
echo -e "  2. ${BLUE}Clicking the desktop icon (if created)${NC}"
echo -e "  3. ${BLUE}Running: python3 $PROJECT_DIR/src/main.py${NC}"
echo ""
echo -e "Enjoy converting videos! 🎬"
echo ""
