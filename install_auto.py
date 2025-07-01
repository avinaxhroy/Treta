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
                print_error("Python installation failed. Please install Python 3.8-3.11 manually.")
                print_info("Download from: https://www.python.org/downloads/release/python-3118/")
                return False
                
            # Step 2: Create virtual environment
            if not self.create_virtual_environment():
                print_error("Virtual environment creation failed.")
                return False
                
            # Step 3: Install dependencies (allow partial success)
            deps_success = self.install_dependencies()
            if not deps_success:
                print_warning("Some dependencies failed to install. Treta may have limited functionality.")
                print_info("You can run 'python test_installation.py' to check what's missing")
                
            # Step 4: Install external tools (FFmpeg, etc.)
            if not self.install_external_tools():
                print_warning("Some external tools may not be available. Audio processing features may be limited.")
                
            # Step 5: Create launcher scripts
            if not self.create_launchers():
                print_warning("Launcher script creation failed. You can still run Treta manually.")
                
            # Step 6: Setup configuration
            if not self.setup_configuration():
                print_warning("Configuration setup incomplete. You can configure manually later.")
                
            # Step 7: Final verification
            verification_success = self.verify_installation()
            if not verification_success:
                print_warning("Installation verification had issues.")
                print_info("Run 'python test_installation.py' to diagnose problems")
                
            # Show results
            if deps_success and verification_success:
                print_success("✅ Installation completed successfully!")
            else:
                print_warning("⚠️  Installation completed with some issues")
                print_info("Basic functionality should work, but some features may be limited")
                
            self.print_next_steps()
            return True
            
        except KeyboardInterrupt:
            print_error("Installation interrupted by user.")
            return False
        except Exception as e:
            print_error(f"Unexpected error during installation: {e}")
            print_info("Try running the installer again, or install manually")
            return False
    
    def check_python(self) -> bool:
        """Check if Python 3.11+ is available (as required by zotify)."""
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
                        if major == 3 and minor >= 11:
                            self.python_executable = cmd
                            print_success(f"Found Python {version_str}")
                            return True
                        elif major == 3 and minor >= 8:
                            print_warning(f"Found Python {version_str}, but zotify requires Python 3.11+")
                            print_info("Some features may not work correctly")
                            self.python_executable = cmd
                            return True
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                continue
        
        # Python not found or too old
        print_warning("Python 3.11+ not found. Attempting to install...")
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
        """Install all required dependencies with special handling for zotify."""
        print_step("Installing dependencies...")
        
        try:
            if not self.venv_python:
                print_error("Virtual environment not available")
                return False
                
            # Upgrade pip first
            subprocess.run([self.venv_python, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                          check=True, timeout=120)
            
            # Install requirements with special zotify handling
            req_file = self.project_dir / 'requirements.txt'
            if req_file.exists():
                # Create a temporary requirements file without zotify
                temp_req_content = []
                zotify_line = None
                
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if 'zotify' in line.lower() and line.startswith('git+'):
                            zotify_line = line
                            print_info(f"Skipping zotify for separate installation: {line}")
                            continue
                        elif line and not line.startswith('#'):
                            temp_req_content.append(line)
                
                # Install non-zotify requirements first
                if temp_req_content:
                    temp_req_file = self.project_dir / 'temp_requirements.txt'
                    try:
                        with open(temp_req_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(temp_req_content))
                        
                        print_info("Installing core dependencies (excluding zotify)...")
                        subprocess.run([self.venv_python, '-m', 'pip', 'install', '-r', str(temp_req_file)], 
                                      check=True, timeout=600)
                        print_success("Core dependencies installed successfully")
                        
                        # Clean up temp file
                        temp_req_file.unlink()
                        
                    except Exception as e:
                        print_warning(f"Core dependencies installation had issues: {e}")
                        if temp_req_file.exists():
                            temp_req_file.unlink()
                        # Try individual installation as fallback
                        return self._install_with_fixes()
                
                # Now handle zotify separately
                zotify_success = True
                if zotify_line:
                    zotify_success = self._install_zotify_with_fixes()
                
                return zotify_success  # Return overall success
                
            else:
                # Install essential packages directly
                return self._install_with_fixes()
            
        except Exception as e:
            print_error(f"Failed to install dependencies: {e}")
            print_info("Trying individual package installation...")
            return self._install_with_fixes()
    
    def _install_with_fixes(self) -> bool:
        """Install packages with specific fixes for Python 3.12 compatibility."""
        print_info("Attempting installation with Python 3.12 compatibility fixes...")
        
        # Install packages in order of dependency
        packages_order = [
            # Core packages first
            ('typer>=0.9.0', 'Command-line interface framework'),
            ('rich>=13.0.0', 'Rich text formatting'),
            ('requests>=2.31.0', 'HTTP requests'),
            ('mutagen>=1.47.0', 'Audio metadata'),
            ('cryptography>=41.0.0', 'Encryption'),
            ('yt-dlp>=2023.12.30', 'YouTube downloader'),
            ('gamdl>=2.4.0', 'Apple Music downloader'),
            
            # Audio processing
            ('librosa>=0.10.0', 'Audio analysis'),
            ('scikit-learn>=1.3.0', 'Machine learning'),
            ('matplotlib>=3.7.0', 'Plotting'),
            ('soundfile>=0.12.0', 'Audio file handling'),
            ('numba>=0.57.0', 'Performance optimization'),
            ('resampy>=0.4.0', 'Audio resampling'),
            ('joblib>=1.3.0', 'Parallel processing'),
        ]
        
        success_count = 0
        for package, description in packages_order:
            if self._install_single_package(package, description):
                success_count += 1
        
        # Now try to install zotify with special handling
        zotify_success = self._install_zotify_with_fixes()
        if zotify_success:
            success_count += 1
        
        total_packages = len(packages_order) + 1  # +1 for zotify
        print_info(f"Successfully installed {success_count}/{total_packages} packages")
        
        # Consider it successful if we got most packages
        return success_count >= (total_packages * 0.7)  # 70% success rate
    
    def _install_zotify_with_fixes(self) -> bool:
        """Install DraftKinner's zotify with careful dependency management."""
        print_info("Installing zotify with dependency conflict resolution...")
        
        if not self.venv_python:
            return False
        
        # Method 1: Try installing zotify directly (might work if pip resolves dependencies correctly)
        try:
            print_info("Attempting direct zotify installation...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install', 
                          'git+https://github.com/DraftKinner/zotify.git@v1.0.1'], 
                          check=True, timeout=300)
            
            print_success("Zotify v1.0.1 installed successfully (direct method)")
            return True
            
        except subprocess.CalledProcessError:
            print_warning("Direct installation failed due to dependency conflicts. Trying manual resolution...")
        
        # Method 2: Install without dependencies and handle manually
        try:
            print_info("Installing zotify without dependencies...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install', '--no-deps',
                          'git+https://github.com/DraftKinner/zotify.git@v1.0.1'], 
                          check=True, timeout=180)
            
            # Install zotify's dependencies manually (excluding librespot)
            print_info("Installing zotify dependencies manually...")
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
                    subprocess.run([self.venv_python, '-m', 'pip', 'install', dep], 
                                  check=True, timeout=60)
                    print_info(f"✓ {dep}")
                except subprocess.CalledProcessError:
                    print_warning(f"Failed to install {dep}")
            
            # Now try to install a compatible librespot
            print_info("Installing compatible librespot-python...")
            librespot_success = False
            
            # Try DraftKinner's version first
            try:
                subprocess.run([self.venv_python, '-m', 'pip', 'install', 
                              'git+https://github.com/DraftKinner/librespot-python'], 
                              check=True, timeout=240)
                print_success("DraftKinner's librespot-python installed")
                librespot_success = True
            except subprocess.CalledProcessError:
                print_warning("DraftKinner's librespot failed, trying alternatives...")
                
                # Try installing just the librespot package without git dependencies
                try:
                    subprocess.run([self.venv_python, '-m', 'pip', 'install', 'librespot'], 
                                  check=True, timeout=120)
                    print_success("Standard librespot package installed")
                    librespot_success = True
                except subprocess.CalledProcessError:
                    print_warning("Standard librespot failed too")
            
            if librespot_success:
                print_success("Zotify installed with manual dependency resolution")
                return True
            else:
                print_warning("Zotify installed but librespot may not work - limited functionality")
                return True  # Still consider it a success as zotify is installed
            
        except subprocess.CalledProcessError:
            print_warning("Manual installation failed. Trying development version...")
        
        # Method 3: Try development version
        try:
            print_info("Trying zotify development version...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install', '--no-deps',
                          'git+https://github.com/DraftKinner/zotify.git@dev'], 
                          check=True, timeout=180)
            
            print_success("Zotify (dev) installed - may have better compatibility")
            return True
            
        except subprocess.CalledProcessError:
            print_error("All zotify installation methods failed")
            print_info("")
            print_info("🔧 To fix this manually, run the fix script:")
            print_info("   python fix_zotify.py")
            print_info("")
            print_info("Or try these manual steps:")
            if self.system == 'windows':
                print_info("   .venv\\Scripts\\activate")
            else:
                print_info("   source .venv/bin/activate")
            print_info("   pip uninstall -y librespot zotify")
            print_info("   pip install --no-deps git+https://github.com/DraftKinner/zotify.git@v1.0.1")
            print_info("   pip install requests Pillow protobuf tabulate tqdm pycryptodome music-tag")
            print_info("   pip install git+https://github.com/DraftKinner/librespot-python")
            print_info("")
            print_info("Treta will work without zotify, but Spotify downloading won't be available.")
            return False
    
    def _install_librespot_with_fixes(self) -> bool:
        """Install librespot-python with Python 3.12 compatibility fixes."""
        if not self.venv_python:
            return False
            
        try:
            # First try DraftKinner's fork which should be compatible with their zotify
            print_info("Installing DraftKinner's librespot-python (compatible with their zotify)...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install', 
                          'git+https://github.com/DraftKinner/librespot-python'], 
                          check=True, timeout=180)
            print_success("DraftKinner's librespot-python installed successfully")
            return True
        except subprocess.CalledProcessError:
            print_warning("DraftKinner's librespot-python failed, trying original...")
            # If that fails, try the original
            try:
                subprocess.run([self.venv_python, '-m', 'pip', 'install', 
                              'git+https://github.com/kokarare1212/librespot-python'], 
                              check=True, timeout=180)
                print_success("Original librespot-python installed")
                return True
            except subprocess.CalledProcessError:
                # If that fails, try with specific commit that might be more compatible
                try:
                    subprocess.run([self.venv_python, '-m', 'pip', 'install', 
                                  'git+https://github.com/kokarare1212/librespot-python.git@v0.1.0'], 
                                  check=True, timeout=180)
                    print_success("Compatible librespot-python version installed")
                    return True
                except subprocess.CalledProcessError:
                    print_error("All librespot-python installation attempts failed")
                    return False
    
    def _install_single_package(self, package: str, description: str) -> bool:
        """Install a single package with error handling."""
        try:
            print_info(f"Installing {description}...")
            subprocess.run([self.venv_python, '-m', 'pip', 'install', package], 
                          check=True, timeout=120)
            return True
        except subprocess.CalledProcessError:
            print_warning(f"Failed to install {package}")
            return False
    
    def _install_essential_packages(self) -> bool:
        """Install essential packages individually with error handling."""
        if not self.venv_python:
            print_error("Virtual environment not available for package installation")
            return False
            
        essential_packages = [
            'typer>=0.9.0',  # Remove [all] as it's causing issues
            'rich>=13.0.0',
            'requests>=2.31.0',
            'yt-dlp>=2023.12.0',
            'mutagen>=1.47.0',
            'cryptography>=41.0.0',
            'gamdl>=2.4.0'
        ]
        
        # Optional packages that might fail
        optional_packages = [
            'librosa>=0.10.0',
            'scikit-learn>=1.3.0',
            'matplotlib>=3.7.0',
            'soundfile>=0.12.0'
        ]
        
        success_count = 0
        
        # Install essential packages
        for package in essential_packages:
            try:
                print_info(f"Installing {package}...")
                subprocess.run([self.venv_python, '-m', 'pip', 'install', package], 
                              check=True, timeout=120)
                success_count += 1
            except subprocess.CalledProcessError:
                print_warning(f"Failed to install {package} - continuing with other packages")
        
        # Install optional packages (don't fail if these don't work)
        for package in optional_packages:
            try:
                print_info(f"Installing optional package {package}...")
                subprocess.run([self.venv_python, '-m', 'pip', 'install', package], 
                              check=True, timeout=180)
            except subprocess.CalledProcessError:
                print_warning(f"Optional package {package} failed to install - skipping")
        
        # Return True if we got at least 70% of essential packages
        return success_count >= (len(essential_packages) * 0.7)
    
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
        print_success("Treta has been successfully set up!")
        print()
        
        # Test command first
        print_colored("🧪 First, test your installation:", Colors.CYAN)
        print_colored("   python test_installation.py", Colors.WHITE)
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
        print_colored("🔧 Troubleshooting:", Colors.YELLOW)
        print_colored("   • If you have issues, run: python test_installation.py", Colors.WHITE)
        print_colored("   • For Python 3.12 compatibility issues, use Python 3.11", Colors.WHITE)
        print_colored("   • Missing dependencies can be installed individually with pip", Colors.WHITE)
        
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
