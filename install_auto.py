#!/usr/bin/env python3
"""
Treta Universal Auto-Installer
=============================

This script automatically installs and sets up everything needed to run Treta:
- Python 3.8+ (if not present)
- Virtual environment creation
- All required dependencies (including zotify, gamdl, yt-dlp)
- FFmpeg download and installation (Windows)
- Launcher script creation
- Configuration setup
- Service authentication guidance

Usage:
    python install_auto.py

Features:
- Cross-platform (Windows, macOS, Linux)
- Automatic dependency detection and installation
- Safe isolated environment creation
- Colored output with progress indicators
- Error handling and recovery
- Comprehensive setup verification
"""

import sys
import os
import subprocess
import platform
import urllib.request
import urllib.error
import zipfile
import shutil
import json
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple

# ANSI color codes for cross-platform colored output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

def print_colored(text: str, color: str = Colors.WHITE, end: str = '\n'):
    """Print colored text with optional formatting."""
    if os.name == 'nt':
        # Enable ANSI colors on Windows
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except:
            pass
        
        # Handle Unicode encoding issues on Windows
        try:
            # Try to encode with the current console encoding
            text.encode('cp1252')
            print(f"{color}{text}{Colors.RESET}", end=end)
        except (UnicodeEncodeError, LookupError):
            # Fallback: remove emoji and non-ASCII characters for Windows compatibility
            import re
            # Remove emoji and other Unicode symbols
            text_clean = re.sub(r'[^\x00-\x7F]+', '', text)
            # Clean up extra spaces
            text_clean = re.sub(r'\s+', ' ', text_clean).strip()
            # Add fallback symbols
            if '🎵' in text:
                text_clean = f"[Music] {text_clean}"
            elif '❌' in text:
                text_clean = f"[Error] {text_clean}"
            elif '✅' in text:
                text_clean = f"[Success] {text_clean}"
            elif '📋' in text:
                text_clean = f"[Step] {text_clean}"
            elif '⚠️' in text:
                text_clean = f"[Warning] {text_clean}"
            elif 'ℹ️' in text:
                text_clean = f"[Info] {text_clean}"
            
            print(f"{color}{text_clean}{Colors.RESET}", end=end)
    else:
        print(f"{color}{text}{Colors.RESET}", end=end)

def print_header(title: str):
    """Print a formatted header."""
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"🎵 {title}", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)

def print_step(step: str, status: str = ""):
    """Print a step with status."""
    print_colored(f"📋 {step}", Colors.BLUE, end="")
    if status:
        print_colored(f" {status}", Colors.GREEN)
    else:
        print()

def print_success(message: str):
    """Print a success message."""
    print_colored(f"✅ {message}", Colors.GREEN)

def print_warning(message: str):
    """Print a warning message."""
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_error(message: str):
    """Print an error message."""
    print_colored(f"❌ {message}", Colors.RED)

def print_info(message: str):
    """Print an info message."""
    print_colored(f"ℹ️  {message}", Colors.CYAN)

class TretaInstaller:
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.project_dir / '.venv'
        self.system = platform.system().lower()
        self.python_executable = None
        self.venv_python = None
        
    def run(self):
        """Main installation process."""
        try:
            print_header("Treta Auto-Installer")
            print_info("Setting up your music downloading environment...")
            print()
            
            # Step 1: Check Python installation
            if not self.check_python():
                print_error("Python installation failed. Please install Python 3.8+ manually.")
                return False
                
            # Step 2: Create virtual environment
            if not self.create_virtual_environment():
                print_error("Virtual environment creation failed.")
                return False
                
            # Step 3: Install dependencies
            if not self.install_dependencies():
                print_error("Dependency installation failed.")
                return False
                
            # Step 4: Install external tools (FFmpeg, etc.)
            if not self.install_external_tools():
                print_warning("Some external tools may not be available. Treta will still work with limited functionality.")
                
            # Step 5: Create launcher scripts
            if not self.create_launchers():
                print_warning("Launcher script creation failed. You can still run Treta manually.")
                
            # Step 6: Setup configuration
            if not self.setup_configuration():
                print_warning("Configuration setup incomplete. You can configure manually later.")
                
            # Step 7: Final verification
            if not self.verify_installation():
                print_warning("Installation verification had issues, but Treta should still work.")
                
            self.print_next_steps()
            return True
            
        except KeyboardInterrupt:
            print_error("Installation interrupted by user.")
            return False
        except Exception as e:
            print_error(f"Unexpected error during installation: {e}")
            return False
    
    def check_python(self) -> bool:
        """Check if Python 3.8+ is available."""
        print_step("Checking Python installation...")
        
        # Try to find existing Python
        python_commands = ['python3', 'python', 'py']
        
        for cmd in python_commands:
            try:
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_str = result.stdout.strip()
                    if 'Python 3.' in version_str:
                        version_parts = version_str.split()[1].split('.')
                        major, minor = int(version_parts[0]), int(version_parts[1])
                        if major == 3 and minor >= 8:
                            self.python_executable = cmd
                            print_success(f"Found Python {version_str}")
                            return True
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                continue
        
        # Python not found or too old
        print_warning("Python 3.8+ not found. Attempting to install...")
        return self.install_python()
    
    def install_python(self) -> bool:
        """Install Python if not present (platform-specific)."""
        if self.system == 'windows':
            return self.install_python_windows()
        elif self.system == 'darwin':  # macOS
            return self.install_python_macos()
        elif self.system == 'linux':
            return self.install_python_linux()
        else:
            print_error(f"Unsupported platform: {self.system}")
            return False
    
    def install_python_windows(self) -> bool:
        """Install Python on Windows."""
        print_step("Installing Python on Windows...")
        
        # Try using winget first (Windows 10 1709+)
        try:
            result = subprocess.run(['winget', 'install', 'Python.Python.3.11'], 
                                  capture_output=True, timeout=300)
            if result.returncode == 0:
                print_success("Python installed via winget")
                # Update PATH and retry detection
                os.environ['PATH'] = os.environ['PATH'] + ';' + os.path.expanduser('~\\AppData\\Local\\Programs\\Python\\Python311')
                return self.check_python()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback: guide user to manual installation
        print_info("Please download and install Python from: https://python.org/downloads/")
        print_info("Make sure to check 'Add Python to PATH' during installation")
        input("Press Enter after installing Python...")
        return self.check_python()
    
    def install_python_macos(self) -> bool:
        """Install Python on macOS."""
        print_step("Installing Python on macOS...")
        
        # Try Homebrew first
        try:
            subprocess.run(['brew', 'install', 'python@3.11'], 
                          capture_output=True, timeout=300)
            print_success("Python installed via Homebrew")
            return self.check_python()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print_info("Please install Python 3.8+ from https://python.org or using Homebrew:")
        print_info("brew install python@3.11")
        input("Press Enter after installing Python...")
        return self.check_python()
    
    def install_python_linux(self) -> bool:
        """Install Python on Linux."""
        print_step("Installing Python on Linux...")
        
        # Try different package managers
        managers = [
            (['apt', 'update'], ['apt', 'install', '-y', 'python3.11', 'python3.11-venv', 'python3.11-pip']),
            (['yum', 'install', '-y', 'python311', 'python311-pip']),
            (['dnf', 'install', '-y', 'python3.11', 'python3.11-pip']),
            (['pacman', '-S', '--noconfirm', 'python']),
        ]
        
        for update_cmd, install_cmd in managers:
            try:
                if update_cmd:
                    subprocess.run(update_cmd, capture_output=True, timeout=60)
                subprocess.run(install_cmd, capture_output=True, timeout=300)
                if self.check_python():
                    print_success("Python installed via package manager")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        print_info("Please install Python 3.8+ using your system's package manager")
        input("Press Enter after installing Python...")
        return self.check_python()

    def create_virtual_environment(self) -> bool:
        """Create a virtual environment for Treta."""
        print_step("Creating virtual environment...")
        
        try:
            if not self.python_executable:
                print_error("No Python executable found")
                return False
                
            # Remove existing venv if it exists
            if self.venv_dir.exists():
                shutil.rmtree(self.venv_dir)
            
            # Create new virtual environment
            subprocess.run([self.python_executable, '-m', 'venv', str(self.venv_dir)], 
                          check=True, timeout=120)
            
            # Set venv python path
            if self.system == 'windows':
                self.venv_python = str(self.venv_dir / 'Scripts' / 'python.exe')
            else:
                self.venv_python = str(self.venv_dir / 'bin' / 'python')
            
            print_success("Virtual environment created")
            return True
            
        except Exception as e:
            print_error(f"Failed to create virtual environment: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install all required dependencies."""
        print_step("Installing dependencies...")
        
        try:
            if not self.venv_python:
                print_error("Virtual environment not available")
                return False
                
            # Upgrade pip first
            subprocess.run([self.venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                          check=True, timeout=120)
            
            # Install requirements from requirements.txt
            req_file = self.project_dir / 'requirements.txt'
            if req_file.exists():
                subprocess.run([self.venv_python, '-m', 'pip', 'install', '-r', str(req_file)], 
                              check=True, timeout=600)
            else:
                # Install essential packages directly
                essential_packages = [
                    'typer[all]>=0.9.0',
                    'rich>=13.0.0',
                    'requests>=2.31.0',
                    'yt-dlp>=2023.12.0',
                    'mutagen>=1.47.0',
                    'librosa>=0.10.0',
                    'sqlalchemy>=2.0.0',
                    'cryptography>=41.0.0'
                ]
                
                for package in essential_packages:
                    subprocess.run([self.venv_python, '-m', 'pip', 'install', package], 
                                  check=True, timeout=120)
            
            print_success("Dependencies installed successfully")
            return True
            
        except Exception as e:
            print_error(f"Failed to install dependencies: {e}")
            return False
    
    def install_external_tools(self) -> bool:
        """Install external tools like FFmpeg."""
        print_step("Installing external tools...")
        
        success = True
        
        # Install FFmpeg
        if not self.install_ffmpeg():
            print_warning("FFmpeg installation failed - some audio processing features may not work")
            success = False
        
        return success
    
    def install_ffmpeg(self) -> bool:
        """Install FFmpeg based on the platform."""
        print_step("Installing FFmpeg...")
        
        if self.system == 'windows':
            return self.install_ffmpeg_windows()
        elif self.system == 'darwin':
            return self.install_ffmpeg_macos()
        elif self.system == 'linux':
            return self.install_ffmpeg_linux()
        
        return False
    
    def install_ffmpeg_windows(self) -> bool:
        """Install FFmpeg on Windows."""
        try:
            ffmpeg_dir = self.project_dir / 'ffmpeg'
            ffmpeg_bin = ffmpeg_dir / 'bin'
            
            if (ffmpeg_bin / 'ffmpeg.exe').exists():
                print_success("FFmpeg already installed")
                return True
            
            # Download FFmpeg
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            temp_file = tempfile.mktemp(suffix='.zip')
            
            print_info("Downloading FFmpeg...")
            urllib.request.urlretrieve(ffmpeg_url, temp_file)
            
            # Extract FFmpeg
            with zipfile.ZipFile(temp_file, 'r') as zip_ref:
                zip_ref.extractall(self.project_dir)
            
            # Move to proper location
            extracted_dir = None
            for item in self.project_dir.iterdir():
                if item.is_dir() and item.name.startswith('ffmpeg-master'):
                    extracted_dir = item
                    break
            
            if extracted_dir:
                if ffmpeg_dir.exists():
                    shutil.rmtree(ffmpeg_dir)
                shutil.move(str(extracted_dir), str(ffmpeg_dir))
            
            os.unlink(temp_file)
            
            if (ffmpeg_bin / 'ffmpeg.exe').exists():
                print_success("FFmpeg installed successfully")
                return True
            else:
                print_error("FFmpeg installation failed")
                return False
                
        except Exception as e:
            print_error(f"FFmpeg installation failed: {e}")
            return False
    
    def install_ffmpeg_macos(self) -> bool:
        """Install FFmpeg on macOS."""
        try:
            subprocess.run(['brew', 'install', 'ffmpeg'], 
                          capture_output=True, timeout=300)
            print_success("FFmpeg installed via Homebrew")
            return True
        except:
            print_info("Please install FFmpeg: brew install ffmpeg")
            return False
    
    def install_ffmpeg_linux(self) -> bool:
        """Install FFmpeg on Linux."""
        managers = [
            ['apt', 'install', '-y', 'ffmpeg'],
            ['yum', 'install', '-y', 'ffmpeg'],
            ['dnf', 'install', '-y', 'ffmpeg'],
            ['pacman', '-S', '--noconfirm', 'ffmpeg'],
        ]
        
        for cmd in managers:
            try:
                subprocess.run(cmd, capture_output=True, timeout=300)
                print_success("FFmpeg installed via package manager")
                return True
            except:
                continue
        
        print_info("Please install FFmpeg using your system's package manager")
        return False
    
    def create_launchers(self) -> bool:
        """Create launcher scripts for easy access."""
        print_step("Creating launcher scripts...")
        
        try:
            if self.system == 'windows':
                self.create_windows_launcher()
            else:
                self.create_unix_launcher()
            
            print_success("Launcher scripts created")
            return True
            
        except Exception as e:
            print_error(f"Failed to create launchers: {e}")
            return False
    
    def create_windows_launcher(self):
        """Create Windows batch launcher."""
        launcher_content = f'''@echo off
cd /d "{self.project_dir}"
"{self.venv_python}" treta.py %*
'''
        
        launcher_path = self.project_dir / 'treta.bat'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
    
    def create_unix_launcher(self):
        """Create Unix shell launcher."""
        launcher_content = f'''#!/bin/bash
cd "{self.project_dir}"
"{self.venv_python}" treta.py "$@"
'''
        
        launcher_path = self.project_dir / 'treta'
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        # Make executable
        os.chmod(launcher_path, 0o755)
    
    def setup_configuration(self) -> bool:
        """Setup initial configuration."""
        print_step("Setting up configuration...")
        
        try:
            # Create data directory
            data_dir = self.project_dir / 'data'
            data_dir.mkdir(exist_ok=True)
            
            # Create downloads directory
            downloads_dir = self.project_dir / 'downloads'
            downloads_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            for service in ['spotify', 'apple', 'youtube']:
                (downloads_dir / service).mkdir(exist_ok=True)            
            print_success("Configuration setup completed")
            return True
            
        except Exception as e:
            print_error(f"Configuration setup failed: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that the installation was successful."""
        print_step("Verifying installation...")
        
        try:
            # Test that Treta can be imported and run
            if not self.venv_python:
                print_error("Virtual environment Python not available")
                return False
                
            result = subprocess.run([self.venv_python, 'treta.py', '--help'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print_success("Installation verification successful")
                return True
            else:
                print_error(f"Installation verification failed: {result.stderr}")
                return False
                
        except Exception as e:
            print_error(f"Installation verification failed: {e}")
            return False
    
    def print_next_steps(self):
        """Print next steps for the user."""
        print()
        print_header("🎉 Installation Complete!")
        print()
        print_success("Treta has been successfully installed!")
        print()
        print_info("Next steps:")
        print_colored("1. Authenticate with your music services:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored("   treta.bat auth add --service spotify", Colors.WHITE)
            print_colored("   treta.bat auth add --service apple", Colors.WHITE)
        else:
            print_colored("   ./treta auth add --service spotify", Colors.WHITE)
            print_colored("   ./treta auth add --service apple", Colors.WHITE)
        
        print()
        print_colored("2. Start downloading music:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored('   treta.bat download url "https://open.spotify.com/track/..."', Colors.WHITE)
        else:
            print_colored('   ./treta download url "https://open.spotify.com/track/..."', Colors.WHITE)
        
        print()
        print_colored("3. Explore all features:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored("   treta.bat guide", Colors.WHITE)
            print_colored("   treta.bat examples", Colors.WHITE)
        else:
            print_colored("   ./treta guide", Colors.WHITE)
            print_colored("   ./treta examples", Colors.WHITE)
        
        print()
        print_colored("📖 For full documentation, visit: https://github.com/avinaxhroy/Treta", Colors.BLUE)
        print_colored("🐛 Report issues at: https://github.com/avinaxhroy/Treta/issues", Colors.BLUE)
        print()
        print_colored("Happy downloading! 🎵", Colors.GREEN + Colors.BOLD)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("Treta Universal Auto-Installer")
        print()
        print("This script automatically sets up everything needed to run Treta:")
        print("- Python 3.8+ installation (if needed)")
        print("- Virtual environment creation")
        print("- All dependencies installation")
        print("- FFmpeg setup")
        print("- Launcher script creation")
        print()
        print("Usage: python install_auto.py")
        return
    
    installer = TretaInstaller()
    success = installer.run()
    
    if success:
        print()
        print_success("🎉 Treta installation completed successfully!")
        sys.exit(0)
    else:
        print()
        print_error("❌ Treta installation failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
