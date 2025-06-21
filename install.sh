#!/bin/bash
#
# Treta Music Downloader - Unix/Linux/macOS Auto-Installer
# =======================================================
#
# This script downloads and runs the Treta auto-installer.
# It handles everything automatically: Python, dependencies, FFmpeg, setup.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/treta-team/treta/main/install.sh | bash
#   or
#   ./install.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_header() {
    echo
    print_color $CYAN "=================================================================="
    print_color $CYAN "🎵 Treta Music Downloader - Auto-Installer"
    print_color $CYAN "=================================================================="
    echo
}

print_step() {
    print_color $BLUE "📋 $1"
}

print_success() {
    print_color $GREEN "✅ $1"
}

print_error() {
    print_color $RED "❌ $1"
}

print_warning() {
    print_color $YELLOW "⚠️  $1"
}

print_info() {
    print_color $CYAN "ℹ️  $1"
}

# Main installation function
main() {
    print_header
    
    print_info "Setting up your music downloading environment..."
    echo
    
    # Check if we're running from a cloned repository
    if [[ -f "install_auto.py" && -f "treta.py" ]]; then
        print_step "Running from local repository..."
        python3 install_auto.py
        return $?
    fi
    
    # We need to download the repository first
    print_step "Downloading Treta repository..."
    
    # Check if git is available
    if command -v git >/dev/null 2>&1; then
        # Clone with git
        print_info "Using git to clone repository..."
        git clone https://github.com/treta-team/treta.git
        cd treta
    else
        # Download as zip
        print_info "Downloading repository as archive..."
        
        if command -v curl >/dev/null 2>&1; then
            curl -L -o treta.zip https://github.com/treta-team/treta/archive/main.zip
        elif command -v wget >/dev/null 2>&1; then
            wget -O treta.zip https://github.com/treta-team/treta/archive/main.zip
        else
            print_error "Neither curl nor wget found. Please install one of them or git."
            exit 1
        fi
        
        # Extract archive
        if command -v unzip >/dev/null 2>&1; then
            unzip -q treta.zip
            cd treta-main
        else
            print_error "unzip command not found. Please install unzip or use git to clone the repository."
            exit 1
        fi
    fi
    
    # Run the auto-installer
    print_step "Running Treta auto-installer..."
    
    # Find Python 3
    PYTHON_CMD=""
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            if "$cmd" -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
                PYTHON_CMD="$cmd"
                break
            fi
        fi
    done
    
    if [[ -z "$PYTHON_CMD" ]]; then
        print_error "Python 3.8+ not found. Please install Python first."
        print_info "Visit: https://python.org/downloads/"
        exit 1
    fi
    
    # Run the installer
    "$PYTHON_CMD" install_auto.py
    
    if [[ $? -eq 0 ]]; then
        print_success "Treta installation completed successfully!"
        echo
        print_info "You can now use Treta with: ./treta"
        print_info "Or run 'treta guide' for a complete walkthrough"
    else
        print_error "Installation failed. Please check the error messages above."
        exit 1
    fi
}

# Run main function
main "$@"
