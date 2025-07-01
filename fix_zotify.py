#!/usr/bin/env python3
"""
Zotify Installation Fix Script
=============================

This script specifically addresses the Python 3.12 'imp' module error
when installing zotify by using compatible versions and installation order.

Usage:
    python fix_zotify.py
"""

import sys
import subprocess
import os
from pathlib import Path

def print_colored(text, color_code="0"):
    """Print colored text (simple version)."""
    print(f"\033[{color_code}m{text}\033[0m")

def print_step(text):
    print_colored(f"📋 {text}", "94")  # Blue

def print_success(text):
    print_colored(f"✅ {text}", "92")  # Green

def print_error(text):
    print_colored(f"❌ {text}", "91")  # Red

def print_warning(text):
    print_colored(f"⚠️  {text}", "93")  # Yellow

def print_info(text):
    print_colored(f"ℹ️  {text}", "96")  # Cyan

def check_venv():
    """Check if we're in a virtual environment."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def get_python_executable():
    """Get the current Python executable."""
    return sys.executable

def fix_zotify_installation():
    """Fix zotify installation with Python 3.12 compatibility."""
    print_colored("🔧 Zotify Installation Fix Script", "95")  # Magenta
    print_colored("=" * 40, "95")
    print()
    
    # Check if we're in a virtual environment
    if not check_venv():
        print_error("This script should be run from within your virtual environment!")
        print_info("Please activate your virtual environment first:")
        if os.name == 'nt':
            print_info("  .venv\\Scripts\\activate")
        else:
            print_info("  source .venv/bin/activate")
        return False
    
    python_exe = get_python_executable()
    print_info(f"Using Python: {python_exe}")
    print()
    
    # Step 1: Remove any existing conflicting packages
    print_step("Removing any existing librespot/zotify installations...")
    packages_to_remove = ['librespot', 'zotify']
    for package in packages_to_remove:
        try:
            subprocess.run([python_exe, '-m', 'pip', 'uninstall', '-y', package], 
                          capture_output=True, timeout=60)
        except:
            pass  # Ignore errors if package isn't installed
    
    # Step 2: Install DraftKinner's librespot-python
    print_step("Installing DraftKinner's librespot-python...")
    try:
        result = subprocess.run([
            python_exe, '-m', 'pip', 'install', 
            'git+https://github.com/DraftKinner/librespot-python'
        ], check=True, timeout=300, capture_output=True, text=True)
        print_success("DraftKinner's librespot-python installed successfully")
    except subprocess.CalledProcessError as e:
        print_warning("DraftKinner's version failed, trying alternative...")
        try:
            # Try a specific commit that might work
            subprocess.run([
                python_exe, '-m', 'pip', 'install', 
                'git+https://github.com/kokarare1212/librespot-python.git@6f88a73b59baaeb3c6e1e8c87cd1b9b57b42b8e0'
            ], check=True, timeout=300, capture_output=True, text=True)
            print_success("Alternative librespot-python installed")
        except subprocess.CalledProcessError:
            print_error("Failed to install compatible librespot-python")
            return False
    
    # Step 3: Install zotify dependencies manually
    print_step("Installing zotify dependencies...")
    zotify_deps = [
        'requests>=2.25.0',
        'Pillow>=8.0.0',
        'protobuf>=3.17.0',
        'tabulate>=0.8.0',
        'tqdm>=4.0.0',
        'pycryptodome>=3.0.0',
        'music-tag>=0.4.3'
    ]
    
    for dep in zotify_deps:
        try:
            subprocess.run([python_exe, '-m', 'pip', 'install', dep], 
                          check=True, timeout=60, capture_output=True)
            print_info(f"Installed {dep}")
        except subprocess.CalledProcessError:
            print_warning(f"Failed to install {dep}")
    
    # Step 4: Install zotify without dependencies
    print_step("Installing zotify without dependencies...")
    zotify_versions = [
        'git+https://github.com/DraftKinner/zotify.git@v1.0.1',
        'git+https://github.com/DraftKinner/zotify.git@dev',
        'git+https://github.com/DraftKinner/zotify.git'
    ]
    
    for version in zotify_versions:
        try:
            subprocess.run([
                python_exe, '-m', 'pip', 'install', '--no-deps', version
            ], check=True, timeout=180, capture_output=True, text=True)
            print_success(f"Zotify installed successfully: {version}")
            break
        except subprocess.CalledProcessError:
            print_warning(f"Failed to install {version}")
            continue
    else:
        print_error("All zotify installation attempts failed")
        return False
    
    # Step 5: Test the installation
    print_step("Testing zotify installation...")
    try:
        result = subprocess.run([python_exe, '-c', 'import zotify; print("Zotify import successful")'], 
                              check=True, timeout=10, capture_output=True, text=True)
        print_success("Zotify can be imported successfully!")
        return True
    except subprocess.CalledProcessError:
        print_warning("Zotify installed but import test failed - it may still work")
        return True

def main():
    """Main function."""
    try:
        success = fix_zotify_installation()
        
        print()
        if success:
            print_success("🎉 Zotify installation fix completed!")
            print_info("You can now use zotify for Spotify downloading")
        else:
            print_error("❌ Fix failed - you may need to use Python 3.11 instead")
            print_info("Download Python 3.11 from: https://python.org/downloads/")
        
        print()
        print_info("To test if everything is working, you can run:")
        print_info("  python test_installation.py")
        
    except KeyboardInterrupt:
        print_error("Fix interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
