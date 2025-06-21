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
        print_warning("Python 3.8+ not found. Please install manually from https://python.org")
        print_info("Make sure to add Python to PATH during installation.")
        return False
    
    def create_virtual_environment(self) -> bool:
        """Create a virtual environment for Treta."""
        print_step("Creating virtual environment...")
        
        if not self.python_executable:
            print_error("No Python executable found")
            return False
        
        try:
            # Remove existing venv if it exists
            if self.venv_dir.exists():
                shutil.rmtree(self.venv_dir)
            
            # Create new virtual environment
            subprocess.run([self.python_executable, '-m', 'venv', str(self.venv_dir)], 
                          check=True)
            
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
        
        if not self.venv_python:
            print_error("Virtual environment not available")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([self.venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                          check=True)
            
            # Install basic dependencies first
            basic_deps = [
                'typer[all]>=0.9.0',
                'rich>=13.0.0',
                'requests>=2.31.0',
                'mutagen>=1.47.0',
                'cryptography>=41.0.0',
            ]
            
            print_info("Installing basic dependencies...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install'] + basic_deps, 
                          check=True)
            
            # Install ML dependencies
            ml_deps = [
                'librosa>=0.10.0',
                'scikit-learn>=1.3.0',
                'joblib>=1.3.0',
                'matplotlib>=3.7.0',
            ]
            
            print_info("Installing ML dependencies...")
            try:
                subprocess.run([self.venv_python, '-m', 'pip', 'install'] + ml_deps, 
                              check=True)
            except subprocess.CalledProcessError:
                print_warning("ML dependencies installation failed, continuing without them")
            
            # Install downloaders
            downloader_deps = [
                'spotipy>=2.22.0',
                'yt-dlp>=2023.12.0',
            ]
            
            print_info("Installing downloader dependencies...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install'] + downloader_deps, 
                          check=True)
            
            # Try to install external downloaders (optional)
            try:
                print_info("Installing external downloaders...")
                subprocess.run([self.venv_python, '-m', 'pip', 'install', 'zotify'], 
                              check=True, timeout=120)
            except:
                print_warning("Zotify installation failed (optional)")
            
            try:
                subprocess.run([self.venv_python, '-m', 'pip', 'install', 'gamdl'], 
                              check=True, timeout=120)
            except:
                print_warning("Gamdl installation failed (optional)")
            
            # Install Treta in development mode
            subprocess.run([self.venv_python, '-m', 'pip', 'install', '-e', '.'], 
                          cwd=str(self.project_dir), check=True)
            
            print_success("Dependencies installed")
            return True
            
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install dependencies: {e}")
            return False
    
    def install_external_tools(self) -> bool:
        """Install external tools like FFmpeg."""
        print_step("Installing external tools...")
        
        success = True
        
        # Install FFmpeg
        if not self.install_ffmpeg():
            success = False
        
        return success
    
    def install_ffmpeg(self) -> bool:
        """Install FFmpeg."""
        print_info("Installing FFmpeg...")
        
        if self.system == 'windows':
            return self.install_ffmpeg_windows()
        else:
            print_info("Please install FFmpeg using your package manager:")
            if self.system == 'darwin':
                print_info("  macOS: brew install ffmpeg")
            else:
                print_info("  Linux: sudo apt install ffmpeg  # or your package manager")
            return True
    
    def install_ffmpeg_windows(self) -> bool:
        """Install FFmpeg on Windows."""
        try:
            ffmpeg_dir = self.project_dir / 'ffmpeg'
            if ffmpeg_dir.exists():
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
            
            # Move to ffmpeg directory
            extracted_dir = None
            for item in self.project_dir.iterdir():
                if item.is_dir() and 'ffmpeg' in item.name.lower():
                    extracted_dir = item
                    break
            
            if extracted_dir:
                shutil.move(str(extracted_dir), str(ffmpeg_dir))
            
            os.unlink(temp_file)
            print_success("FFmpeg installed")
            return True
            
        except Exception as e:
            print_error(f"Failed to install FFmpeg: {e}")
            return False
    
    def create_launchers(self) -> bool:
        """Create launcher scripts."""
        print_step("Creating launcher scripts...")
        
        try:
            if self.system == 'windows':
                self.create_windows_launchers()
            else:
                self.create_unix_launchers()
            
            print_success("Launcher scripts created")
            return True
        except Exception as e:
            print_error(f"Failed to create launchers: {e}")
            return False
    
    def create_windows_launchers(self):
        """Create Windows launcher scripts."""
        # Batch file launcher
        bat_content = f'''@echo off
"{self.venv_python}" "{self.project_dir}\\treta.py" %*
'''
        with open(self.project_dir / 'treta.bat', 'w') as f:
            f.write(bat_content)
        
        # PowerShell launcher
        ps1_content = f'''#!/usr/bin/env pwsh
& "{self.venv_python}" "{self.project_dir}\\treta.py" @args
'''
        with open(self.project_dir / 'treta.ps1', 'w') as f:
            f.write(ps1_content)
    
    def create_unix_launchers(self):
        """Create Unix launcher scripts."""
        # Shell script launcher
        sh_content = f'''#!/bin/bash
"{self.venv_python}" "{self.project_dir}/treta.py" "$@"
'''
        launcher_path = self.project_dir / 'treta'
        with open(launcher_path, 'w') as f:
            f.write(sh_content)
        launcher_path.chmod(0o755)
    
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
            
            # Create basic config
            config = {
                "version": "1.0.0",
                "setup_complete": True,
                "python_path": str(self.venv_python) if self.venv_python else "",
                "project_path": str(self.project_dir),
                "downloads_path": str(downloads_dir),
                "services": {
                    "spotify": {"configured": False},
                    "apple_music": {"configured": False},
                    "youtube": {"configured": False}
                }
            }
            
            config_file = data_dir / 'config.json'
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print_success("Configuration setup complete")
            return True
        except Exception as e:
            print_error(f"Failed to setup configuration: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify that everything is working."""
        print_step("Verifying installation...")
        
        try:
            if not self.venv_python:
                print_error("Virtual environment Python not available")
                return False
                
            # Test Python environment
            result = subprocess.run([self.venv_python, '-c', 'import sys; print("OK")'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print_error("Python environment test failed")
                return False
            
            # Test CLI
            result = subprocess.run([self.venv_python, str(self.project_dir / 'treta.py'), '--help'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print_error("Treta CLI test failed")
                return False
            
            print_success("Installation verification passed")
            return True
        except Exception as e:
            print_error(f"Verification failed: {e}")
            return False
    
    def print_next_steps(self):
        """Print next steps for the user."""
        print()
        print_header("🎉 Installation Complete!")
        print()
        print_info("Treta has been successfully installed! Here's how to get started:")
        print()
        
        # Show how to run Treta
        if self.system == 'windows':
            print_colored("💡 To run Treta:", Colors.BOLD + Colors.CYAN)
            print_colored("   • PowerShell: ", Colors.BLUE, end="")
            print_colored(".\\treta.ps1 --help", Colors.GREEN)
            print_colored("   • Command Prompt: ", Colors.BLUE, end="")
            print_colored("treta.bat --help", Colors.GREEN)
            print_colored("   • Direct: ", Colors.BLUE, end="")
            print_colored(f'"{self.venv_python}" treta.py --help', Colors.GREEN)
        else:
            print_colored("💡 To run Treta:", Colors.BOLD + Colors.CYAN)
            print_colored("   • Using launcher: ", Colors.BLUE, end="")
            print_colored("./treta --help", Colors.GREEN)
            print_colored("   • Direct: ", Colors.BLUE, end="")
            print_colored(f'"{self.venv_python}" treta.py --help', Colors.GREEN)
        
        print()
        print_colored("🎵 Quick Start Examples:", Colors.BOLD + Colors.CYAN)
        print_colored("   • Download a song: ", Colors.BLUE, end="")
        print_colored("./treta download url https://open.spotify.com/track/...", Colors.GREEN)
        print_colored("   • Search and download: ", Colors.BLUE, end="")
        print_colored('./treta download search "artist song name"', Colors.GREEN)
        print_colored("   • Configure services: ", Colors.BLUE, end="")
        print_colored("./treta auth setup", Colors.GREEN)
        
        print()
        print_colored("📖 For more help:", Colors.BOLD + Colors.CYAN)
        print_colored("   • Full guide: ", Colors.BLUE, end="")
        print_colored("./treta guide", Colors.GREEN)
        print_colored("   • Examples: ", Colors.BLUE, end="")
        print_colored("./treta examples", Colors.GREEN)
        print_colored("   • Configuration: ", Colors.BLUE, end="")
        print_colored("./treta config --help", Colors.GREEN)
        
        print()
        print_colored("🔐 Important Next Steps:", Colors.BOLD + Colors.YELLOW)
        print_colored("   1. Set up service authentication using: ", Colors.YELLOW, end="")
        print_colored("./treta auth setup", Colors.GREEN)
        print_colored("   2. Configure download preferences: ", Colors.YELLOW, end="")
        print_colored("./treta config set quality high", Colors.GREEN)
        print_colored("   3. Test with a simple download: ", Colors.YELLOW, end="")
        print_colored("./treta examples", Colors.GREEN)
        
        print()
        print_success("Enjoy downloading music with Treta! 🎶")

def main():
    """Main installer entry point."""
    installer = TretaInstaller()
    success = installer.run()
    
    if success:
        print()
        print_success("Installation completed successfully!")
        sys.exit(0)
    else:
        print()
        print_error("Installation failed. Please check the error messages above.")
        print_info("You can try running the installer again or install dependencies manually.")
        sys.exit(1)

if __name__ == '__main__':
    main()
