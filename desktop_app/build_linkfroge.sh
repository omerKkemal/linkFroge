#!/bin/bash
# 🐸 linkFroge - Build Script with Icon
# "Because running Python scripts is so last decade. Let's make a binary."
# Usage: ./build_linkfroge.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🐸 FrogLink - Binary Builder${NC}"
echo -e "${YELLOW}Warning: This script may contain traces of sarcasm and coffee.${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python3 not found.${NC}"
    exit 1
fi
echo -e "${GREEN}[+] Python3 found.${NC}"

# Check pip
if ! command -v pip3 &> /dev/null; then
    python3 -m ensurepip --upgrade || { echo -e "${RED}[!] Failed to install pip.${NC}"; exit 1; }
fi

# Install PyInstaller if missing
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo -e "${YELLOW}[*] Installing PyInstaller...${NC}"
    pip3 install pyinstaller pillow
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f "linkFroge.py" ]; then
    echo -e "${RED}[!] linkFroge.py not found.${NC}"
    exit 1
fi

# Icon paths
JPG_ICON="/home/omerkemal/Desktop/linkFroge/webApp/static/img/cute.jpg"
ICO_ICON="/tmp/linkfroge.ico"

# Convert JPG to ICO if needed (for Windows builds)
if [ -f "$JPG_ICON" ]; then
    echo -e "${GREEN}[+] Icon found at: $JPG_ICON${NC}"
    echo -e "${YELLOW}[*] Converting JPG to ICO...${NC}"
    python3 -c "
from PIL import Image
img = Image.open('$JPG_ICON')
img = img.resize((256, 256), Image.Resampling.LANCZOS)
img.save('$ICO_ICON', format='ICO', sizes=[(256, 256)])
" 2>/dev/null || echo -e "${YELLOW}[!] PIL not installed. Skipping ICO conversion.${NC}"
    
    if [ -f "$ICO_ICON" ]; then
        echo -e "${GREEN}[+] ICO created: $ICO_ICON${NC}"
        ICON_FLAG="--icon $ICO_ICON"
    else
        ICON_FLAG=""
    fi
else
    echo -e "${YELLOW}[!] Icon not found. Building without icon.${NC}"
    ICON_FLAG=""
fi

# Clean previous builds
rm -rf dist build *.spec

# Build
echo -e "${BLUE}[*] Building binary...${NC}"
pyinstaller \
    --onefile \
    --name linkfroge \
    --console \
    $ICON_FLAG \
    --add-data "linkFroge.py:." \
    linkFroge.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Build successful!${NC}"
    echo -e "${GREEN}[+] Binary: ${SCRIPT_DIR}/dist/linkfroge${NC}"
    echo -e "${YELLOW}Run: ./dist/linkfroge --help${NC}"
    chmod +x dist/linkfroge
    echo -e "${BLUE}🐸 Done!${NC}"
else
    echo -e "${RED}[!] Build failed.${NC}"
    exit 1
fi