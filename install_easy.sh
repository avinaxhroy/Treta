#!/bin/bash
# Treta Easy Installer for Unix - Remote Version
# ==============================================
#
# This script downloads and installs Treta automatically!
# Works from anywhere - no need to download repository first!

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

echo
echo -e "${CYAN}===============================================${RESET}"
echo -e "${CYAN}   Treta Music Downloader - Remote Installer${RESET}"
echo -e "${CYAN}===============================================${RESET}"
echo
echo "This will automatically download and install everything you need:"
echo "  - Latest Treta repository from GitHub"
echo "  - Python environment setup"
echo "  - All music downloaders (Spotify, Apple, YouTube)"
echo "  - Audio processing tools"
echo "  - Global 'treta' command"
echo
echo -e "${BLUE}Working from: $(pwd)${RESET}"
echo

# Check for required tools
echo -e "${BLUE}Checking prerequisites...${RESET}"

if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
    echo -e "${RED}Error: Neither curl nor wget is available${RESET}"
    echo
    echo "Please install curl or wget:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install curl"
    echo "  CentOS/RHEL: sudo yum install curl"
    echo "  macOS: curl is pre-installed"
    echo
    exit 1
fi

echo -e "${GREEN}Prerequisites check passed!${RESET}"
echo

# Download and run the remote installer
echo -e "${BLUE}Starting remote installation...${RESET}"
echo

if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
elif command -v wget >/dev/null 2>&1; then
    wget -qO- https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
fi

echo
echo -e "${CYAN}Remote installation process completed.${RESET}"
echo "Check the output above for any instructions or next steps."
echo
if [ ! -f "install_auto.py" ]; then
    echo "Error: install_auto.py not found in current directory!"
    echo "Current directory: $(pwd)"
    echo
    echo "Please make sure you're running this from the Treta directory."
    echo
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python not found!"
    echo
    echo "Please install Python 3.8+ first:"
    echo "  - Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  - CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  - macOS: brew install python3"
    echo "  - Or download from: https://www.python.org/downloads/"
    echo
    exit 1
fi

# Find Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo "Python found! Starting installation..."
echo "Working directory: $(pwd)"
echo

# Run the installer with global install option
$PYTHON_CMD install_auto.py --global-install

echo
if [ $? -eq 0 ]; then
    echo "==============================================="
    echo "   Installation Complete!"
    echo "==============================================="
    echo
    echo "You can now use Treta in several ways:"
    echo "  1. Type 'treta' in any terminal (if in PATH)"
    echo "  2. Use ./treta in this folder"
    echo "  3. Run: $PYTHON_CMD treta.py"
    echo
    echo "Next steps:"
    echo "  1. Run: treta auth add --service spotify"
    echo "  2. Run: treta download url \"YOUR_MUSIC_URL\""
    echo
    echo "For help: treta --help"
    echo
else
    echo "==============================================="
    echo "   Installation Had Issues"
    echo "==============================================="
    echo
    echo "Some components may not have installed correctly."
    echo "You can still use Treta with: $PYTHON_CMD treta.py"
    echo
    echo "For troubleshooting:"
    echo "  - Run: $PYTHON_CMD test_installation.py"
    echo "  - Check the documentation"
    echo "  - Report issues on GitHub"
    echo
fi

echo "Installation script finished."
