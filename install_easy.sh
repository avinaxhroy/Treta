#!/bin/bash
# Treta Easy Installer for Unix/Linux/macOS
# ========================================
#
# This script runs the Treta auto-installer with sensible defaults.
# Run this script to install Treta automatically!

set -e  # Exit on error

echo
echo "==============================================="
echo "   Treta Music Downloader - Easy Installer"
echo "==============================================="
echo
echo "This will automatically install everything you need:"
echo "  - Python environment setup"
echo "  - All music downloaders (Spotify, Apple, YouTube)"
echo "  - Audio processing tools"
echo "  - Global 'treta' command"
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR"
echo

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if install_auto.py exists
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
