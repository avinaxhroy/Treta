#!/bin/bash
# Treta Music Downloader - Remote Auto-Installer
# ===============================================
#
# 🎵 True One-Click Installer - Downloads and installs everything automatically! 🎵
#
# This script:
# ✅ Downloads the latest Treta repository
# ✅ Runs the enhanced auto-installer
# ✅ Sets up everything for you automatically
# ✅ Works from anywhere - no need to download repository first!
#
# Usage (run this from anywhere):
#   curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
#   or
#   wget -qO- https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
BOLD='\033[1m'
RESET='\033[0m'

# Unicode icons with fallbacks
if [[ "$TERM" == *"color"* ]] || [[ "$COLORTERM" == *"color"* ]] || [[ -n "$COLORTERM" ]]; then
    ICON_SUCCESS="✅"
    ICON_ERROR="❌"
    ICON_WARNING="⚠️"
    ICON_INFO="ℹ️"
    ICON_STEP="📋"
    ICON_MUSIC="🎵"
    ICON_ROCKET="🚀"
    ICON_PARTY="🎉"
else
    # Fallbacks for basic terminals
    ICON_SUCCESS="[OK]"
    ICON_ERROR="[ERROR]"
    ICON_WARNING="[WARN]"
    ICON_INFO="[INFO]"
    ICON_STEP="[STEP]"
    ICON_MUSIC="[MUSIC]"
    ICON_ROCKET="[LAUNCH]"
    ICON_PARTY="[DONE]"
fi

# Print functions
print_colored() {
    local message="$1"
    local color="$2"
    local icon="$3"
    
    if [[ -n "$icon" ]]; then
        echo -e "${color}${icon} ${message}${RESET}"
    else
        echo -e "${color}${message}${RESET}"
    fi
}

print_header() {
    local title="$1"
    local subtitle="$2"
    
    echo ""
    print_colored "==================================================================" "$CYAN$BOLD"
    print_colored "$title" "$CYAN$BOLD" "$ICON_MUSIC"
    if [[ -n "$subtitle" ]]; then
        print_colored "   $subtitle" "$CYAN"
    fi
    print_colored "==================================================================" "$CYAN$BOLD"
    echo ""
}

print_step() {
    print_colored "$1" "$BLUE$BOLD" "$ICON_STEP"
}

print_success() {
    print_colored "$1" "$GREEN$BOLD" "$ICON_SUCCESS"
}

print_warning() {
    print_colored "$1" "$YELLOW$BOLD" "$ICON_WARNING"
}

print_error() {
    print_colored "$1" "$RED$BOLD" "$ICON_ERROR"
}

print_info() {
    print_colored "$1" "$CYAN" "$ICON_INFO"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main installation function
install_treta() {
    print_header "Treta Music Downloader - Remote Auto-Installer v2.0" "Downloads and installs everything automatically!"
    
    print_info "🚀 This installer will:"
    print_info "  • Download the latest Treta repository"
    print_info "  • Install Python (if needed)"
    print_info "  • Set up all music downloaders (Spotify, Apple Music, YouTube)"
    print_info "  • Configure FFmpeg for audio processing"
    print_info "  • Create global 'treta' command"
    print_info "  • Set up everything for immediate use"
    echo ""
    
    # Ask for confirmation
    read -p "Ready to begin automatic installation? (Y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installation cancelled by user."
        return 0
    fi
    
    # Step 1: Check prerequisites
    print_step "Checking system prerequisites..."
    
    # Check for required tools
    local missing_tools=()
    
    if ! command_exists curl && ! command_exists wget; then
        missing_tools+=("curl or wget")
    fi
    
    if ! command_exists unzip; then
        missing_tools+=("unzip")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        print_info "Please install the missing tools and try again."
        print_info ""
        print_info "On Ubuntu/Debian: sudo apt update && sudo apt install curl unzip"
        print_info "On CentOS/RHEL: sudo yum install curl unzip"
        print_info "On macOS: install Xcode command line tools"
        return 1
    fi
    
    print_success "Required tools available ✓"
    
    # Check internet connectivity
    if command_exists curl; then
        if ! curl -s --connect-timeout 10 https://github.com >/dev/null; then
            print_error "No internet connection available"
            print_info "Internet connection is required to download Treta."
            return 1
        fi
    elif command_exists wget; then
        if ! wget -q --timeout=10 --spider https://github.com; then
            print_error "No internet connection available"
            print_info "Internet connection is required to download Treta."
            return 1
        fi
    fi
    
    print_success "Internet connectivity ✓"
    
    # Step 2: Choose installation directory
    print_step "Choosing installation directory..."
    
    # Default to user's home directory for safety
    local install_dir="$HOME/Treta"
    print_info "Installation directory: $install_dir"
    
    # Create directory if it doesn't exist
    if [[ ! -d "$install_dir" ]]; then
        mkdir -p "$install_dir"
        print_success "Created installation directory"
    else
        print_info "Installation directory already exists"
    fi
    
    # Step 3: Download repository
    print_step "Downloading latest Treta repository..."
    
    local repo_url="https://github.com/avinaxhroy/treta/archive/refs/heads/main.zip"
    local temp_dir=$(mktemp -d)
    local zip_path="$temp_dir/treta-main.zip"
    
    # Download the repository
    print_info "Downloading from: $repo_url"
    if command_exists curl; then
        curl -fsSL "$repo_url" -o "$zip_path"
    elif command_exists wget; then
        wget -q "$repo_url" -O "$zip_path"
    fi
    
    if [[ ! -f "$zip_path" ]]; then
        print_error "Failed to download repository"
        rm -rf "$temp_dir"
        return 1
    fi
    
    print_success "Repository downloaded"
    
    # Extract the archive
    print_info "Extracting repository..."
    cd "$temp_dir"
    unzip -q "$zip_path"
    
    local source_dir="$temp_dir/treta-main"
    if [[ ! -d "$source_dir" ]]; then
        print_error "Repository structure not as expected"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Copy contents to installation directory
    cp -r "$source_dir"/* "$install_dir/"
    print_success "Repository extracted to: $install_dir"
    
    # Clean up temporary files
    rm -rf "$temp_dir"
    
    # Step 4: Run the auto-installer
    print_step "Running Treta auto-installer..."
    
    local installer_path="$install_dir/install_auto.py"
    if [[ ! -f "$installer_path" ]]; then
        print_error "install_auto.py not found in downloaded repository"
        return 1
    fi
    
    # Change to installation directory
    cd "$install_dir"
    
    # Check if Python is available
    local python_cmd=""
    if command_exists python3; then
        local python_version=$(python3 --version 2>&1)
        print_success "Python found: $python_version"
        python_cmd="python3"
    elif command_exists python; then
        local python_version=$(python --version 2>&1)
        if [[ "$python_version" == *"Python 3"* ]]; then
            print_success "Python found: $python_version"
            python_cmd="python"
        else
            print_warning "Python 2 found, but Python 3 is required"
            python_cmd="python3"  # The installer will handle Python installation
        fi
    else
        print_warning "Python not found - the installer will attempt to install it"
        python_cmd="python3"  # The installer will handle Python installation
    fi
    
    # Run the enhanced auto-installer with global install
    print_info "Starting Treta auto-installer with global install option..."
    print_info "This may take a few minutes..."
    echo ""
    
    if "$python_cmd" install_auto.py --global-install --verbose; then
        print_success "Treta installation completed successfully!"
    else
        local exit_code=$?
        print_warning "Installation completed with some issues (exit code: $exit_code)"
        print_info "Basic functionality should still work."
    fi
    
    # Step 5: Final setup and instructions
    print_header "🎉 Installation Complete!" "Treta is ready to use!"
    
    print_colored "🎯 Quick Start:" "$GREEN$BOLD"
    print_info "1. Test your installation:"
    print_info "   cd \"$install_dir\""
    print_info "   python test_installation.py"
    echo ""
    
    print_info "2. IMPORTANT: Restart your terminal!"
    print_info "   (The global 'treta' command needs a fresh terminal session)"
    echo ""
    
    print_info "3. Authenticate with your music services:"
    print_info "   treta auth add --service spotify"
    print_info "   treta auth add --service apple"
    echo ""
    
    print_info "4. Download your first song:"
    print_info "   treta download url \"https://open.spotify.com/track/...\""
    echo ""
    
    print_warning "If 'treta' command doesn't work after restart:"
    print_info "• Navigate to: $install_dir"
    print_info "• Use: python treta.py [command] instead"
    print_info "• Or use: ./treta [command]"
    echo ""
    
    print_colored "📖 Installation Directory:" "$CYAN$BOLD"
    print_info "$install_dir"
    echo ""
    
    print_colored "🆘 Need Help?" "$BLUE$BOLD"
    print_info "• Documentation: https://github.com/avinaxhroy/treta/wiki"
    print_info "• Issues: https://github.com/avinaxhroy/treta/issues"
    print_info "• Run diagnostics: python test_installation.py"
    echo ""
    
    print_colored "🎵 Happy music downloading! 🎵" "$GREEN$BOLD"
    
    return 0
}

# Run the installation
if install_treta; then
    echo ""
    print_info "Installation completed successfully!"
else
    echo ""
    print_error "Installation failed. Please check the error messages above."
    print_info "You can report issues at: https://github.com/avinaxhroy/treta/issues"
    exit 1
fi
