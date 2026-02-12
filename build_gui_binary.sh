#!/bin/bash
#
# Build WOPR GUI as a standalone binary using PyInstaller
#
# Not used

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Building WOPR GUI Binary...${NC}"

# Navigate to frontend directory
cd "$(dirname "$0")/frontend/src"

# Create/activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo -e "${BLUE}Cleaning previous builds...${NC}"
rm -rf build dist *.spec

# Build the binary
echo -e "${BLUE}Building binary with PyInstaller...${NC}"
pyinstaller \
    --onefile \
    --windowed \
    --name wopr-control \
    --add-data "wopr-icon.png:." \
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtGui \
    --hidden-import=PySide6.QtWidgets \
    --collect-all PySide6 \
    wopr_gui.py

echo -e "${GREEN}✓ Binary built successfully!${NC}"
echo -e "${BLUE}Location: frontend/src/dist/wopr-control${NC}"

# Get binary size
SIZE=$(du -h dist/wopr-control | cut -f1)
echo -e "${BLUE}Binary size: ${SIZE}${NC}"

# Test the binary
echo -e "${YELLOW}Testing binary...${NC}"
if ./dist/wopr-control --help 2>/dev/null || [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Binary appears functional${NC}"
else
    echo -e "${YELLOW}⚠ Could not test binary (may need X display)${NC}"
fi

echo ""
echo -e "${GREEN}Build complete!${NC}"
echo ""
echo "To install the binary system-wide:"
echo "  sudo cp dist/wopr-control /usr/local/bin/"
echo ""
echo "To test the binary:"
echo "  ./dist/wopr-control"

deactivate