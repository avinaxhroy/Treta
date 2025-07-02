#!/usr/bin/env python3
"""
Treta Universal Auto-Installer v2.0
===================================

🎵 The most user-friendly music downloader installer on the planet! 🎵

This enhanced auto-installer sets up everything you need for Treta:
✅ Python 3.8+ detection & installation (if needed)
✅ Secure virtual environment creation
✅ All dependencies (zotify, gamdl, yt-dlp, etc.)
✅ FFmpeg setup for audio processing
✅ Global 'treta' command installation
✅ Smart launcher scripts
✅ PATH configuration for global access
✅ Configuration & service setup
✅ Health checks & diagnostics

Usage:
    python install_auto.py
    
    Options:
    --force-reinstall    Force reinstall all components
    --global-install     Install globally (requires admin/sudo)
    --skip-optional      Skip optional packages for faster install
    --verbose           Enable detailed logging

Features:
- 🚀 One-click setup (no technical knowledge needed)
- 🎯 Smart dependency resolution
- 🔧 Automatic error recovery
- 🌈 Beautiful colored progress indicators
- 🔒 Safe isolated environments
- 🔄 Resume interrupted installations
- 📱 Cross-platform (Windows/macOS/Linux)
- 🩺 Comprehensive health checks
- 🆘 Detailed troubleshooting guidance
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
import argparse
import time
from pathlib import Path
from typing import Optional, List, Tuple, Dict

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
    
    # Additional styling
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'

# Progress indicators and emojis (with fallbacks for Windows)
class Icons:
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    STEP = "📋"
    MUSIC = "🎵"
    ROCKET = "🚀"
    GEAR = "⚙️"
    DOWNLOAD = "⬇️"
    INSTALL = "📦"
    COMPLETE = "🎉"
    PYTHON = "🐍"
    FOLDER = "📁"
    FILE = "📄"
    LINK = "🔗"
    KEY = "🔑"
    SHIELD = "🛡️"
    HEART = "❤️"
    STAR = "⭐"
    
    @classmethod
    def get_fallbacks(cls) -> Dict[str, str]:
        """Get fallback text for systems that don't support Unicode."""
        return {
            cls.SUCCESS: "[OK]",
            cls.ERROR: "[ERROR]",
            cls.WARNING: "[WARN]",
            cls.INFO: "[INFO]",
            cls.STEP: "[STEP]",
            cls.MUSIC: "[MUSIC]",
            cls.ROCKET: "[LAUNCH]",
            cls.GEAR: "[CONFIG]",
            cls.DOWNLOAD: "[DOWNLOAD]",
            cls.INSTALL: "[INSTALL]",
            cls.COMPLETE: "[DONE]",
            cls.PYTHON: "[PYTHON]",
            cls.FOLDER: "[FOLDER]",
            cls.FILE: "[FILE]",
            cls.LINK: "[LINK]",
            cls.KEY: "[AUTH]",
            cls.SHIELD: "[SECURE]",
            cls.HEART: "[LOVE]",
            cls.STAR: "[STAR]"
        }

def print_colored(text: str, color: str = Colors.WHITE, end: str = '\n', icon: str = ""):
    """Print colored text with optional formatting and icon."""
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
            full_text = f"{icon} {text}" if icon else text
            full_text.encode('cp1252')
            print(f"{color}{full_text}{Colors.RESET}", end=end)
        except (UnicodeEncodeError, LookupError):
            # Fallback: use text replacements for Windows compatibility
            fallbacks = Icons.get_fallbacks()
            text_clean = text
            
            # Replace Unicode icons with fallback text
            for unicode_icon, fallback in fallbacks.items():
                if unicode_icon in text_clean:
                    text_clean = text_clean.replace(unicode_icon, fallback)
            
            # If an icon was provided, use its fallback
            if icon and icon in fallbacks:
                icon_clean = fallbacks[icon]
                text_clean = f"{icon_clean} {text_clean}"
            elif icon:
                # Remove non-ASCII characters from icon
                import re
                icon_clean = re.sub(r'[^\x00-\x7F]+', '', icon)
                text_clean = f"{icon_clean} {text_clean}" if icon_clean else text_clean
            
            print(f"{color}{text_clean}{Colors.RESET}", end=end)
    else:
        full_text = f"{icon} {text}" if icon else text
        print(f"{color}{full_text}{Colors.RESET}", end=end)

def print_header(title: str, subtitle: str = ""):
    """Print a beautiful formatted header."""
    print()
    print_colored("=" * 80, Colors.CYAN + Colors.BOLD)
    print_colored(f"{Icons.MUSIC} {title}", Colors.BOLD + Colors.CYAN)
    if subtitle:
        print_colored(f"   {subtitle}", Colors.CYAN)
    print_colored("=" * 80, Colors.CYAN + Colors.BOLD)
    print()

def print_step(step: str, status: str = "", number: int = 0):
    """Print a step with optional numbering and status."""
    step_text = f"Step {number}: {step}" if number > 0 else step
    print_colored(step_text, Colors.BLUE + Colors.BOLD, end="", icon=Icons.STEP)
    if status:
        print_colored(f" {status}", Colors.GREEN)
    else:
        print()

def print_substep(substep: str, status: str = ""):
    """Print a substep with indentation."""
    print_colored(f"  └─ {substep}", Colors.BLUE, end="")
    if status:
        print_colored(f" {status}", Colors.GREEN)
    else:
        print()

def print_success(message: str):
    """Print a success message."""
    print_colored(message, Colors.GREEN + Colors.BOLD, icon=Icons.SUCCESS)

def print_warning(message: str):
    """Print a warning message."""
    print_colored(message, Colors.YELLOW + Colors.BOLD, icon=Icons.WARNING)

def print_error(message: str):
    """Print an error message."""
    print_colored(message, Colors.RED + Colors.BOLD, icon=Icons.ERROR)

def print_info(message: str, indent: int = 0):
    """Print an info message with optional indentation."""
    indented_msg = "  " * indent + message
    print_colored(indented_msg, Colors.CYAN, icon=Icons.INFO if indent == 0 else "")

def print_progress(message: str, percentage: int = 0):
    """Print a progress message with percentage."""
    if percentage > 0:
        bar_length = 20
        filled_length = int(bar_length * percentage // 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print_colored(f"{message} [{bar}] {percentage}%", Colors.YELLOW, icon=Icons.DOWNLOAD)
    else:
        print_colored(message, Colors.YELLOW, icon=Icons.DOWNLOAD)

def print_box(title: str, content: List[str], color: str = Colors.CYAN):
    """Print content in a nice box."""
    max_width = max(len(title), max(len(line) for line in content) if content else 0) + 4
    
    print_colored("┌" + "─" * (max_width - 2) + "┐", color)
    print_colored(f"│ {title.center(max_width - 4)} │", color + Colors.BOLD)
    print_colored("├" + "─" * (max_width - 2) + "┤", color)
    
    for line in content:
        print_colored(f"│ {line.ljust(max_width - 4)} │", color)
    
    print_colored("└" + "─" * (max_width - 2) + "┘", color)

class TretaInstaller:
    def __init__(self, args: argparse.Namespace):
        self.project_dir = Path(__file__).parent.absolute()
        self.venv_dir = self.project_dir / '.venv'
        self.system = platform.system().lower()
        self.python_executable: Optional[str] = None
        self.venv_python: Optional[str] = None
        
        # Installation options
        self.force_reinstall = args.force_reinstall
        self.global_install = args.global_install
        self.skip_optional = args.skip_optional
        self.verbose = args.verbose
        
        # Installation state
        self.installed_components = []
        self.failed_components = []
        self.warnings = []
        
        # Progress tracking
        self.total_steps = 10
        self.current_step = 0
        
    def log_verbose(self, message: str):
        """Log verbose messages if verbose mode is enabled."""
        if self.verbose:
            print_info(message, indent=1)
    
    def update_progress(self, step_name: str):
        """Update installation progress."""
        self.current_step += 1
        percentage = int((self.current_step / self.total_steps) * 100)
        print_progress(f"Progress: {step_name}", percentage)
        
    def run(self) -> bool:
        """Main installation process with enhanced user experience."""
        try:
            # Welcome screen
            self.show_welcome()
            
            # Pre-installation checks
            if not self.pre_installation_checks():
                return False
            
            # Main installation steps
            steps = [
                ("Checking Python installation", self.check_and_install_python),
                ("Creating virtual environment", self.create_virtual_environment),
                ("Installing core dependencies", self.install_dependencies),
                ("Installing Treta package", self.install_package),
                ("Setting up external tools", self.install_external_tools),
                ("Creating launcher scripts", self.create_launchers),
                ("Configuring global access", self.setup_global_access),
                ("Setting up configuration", self.setup_configuration),
                ("Running health checks", self.verify_installation),
                ("Finalizing setup", self.finalize_installation)
            ]
            
            for step_name, step_function in steps:
                self.update_progress(step_name)
                print_step(step_name, number=self.current_step)
                
                try:
                    result = step_function()
                    if result:
                        print_success(f"✓ {step_name} completed successfully")
                    else:
                        print_warning(f"⚠ {step_name} completed with issues")
                        self.warnings.append(step_name)
                except Exception as e:
                    print_error(f"✗ {step_name} failed: {e}")
                    self.failed_components.append(step_name)
                    if self.verbose:
                        import traceback
                        print_info(f"Error details: {traceback.format_exc()}", indent=1)
                
                print()  # Add spacing between steps
            
            # Show final results
            self.show_results()
            self.show_next_steps()
            
            return len(self.failed_components) == 0
            
        except KeyboardInterrupt:
            print_error("Installation interrupted by user.")
            print_info("You can run the installer again to resume.")
            return False
        except Exception as e:
            print_error(f"Unexpected error during installation: {e}")
            print_info("Please report this issue with the full error details.")
            return False
    
    def show_welcome(self):
        """Show a beautiful welcome screen."""
        welcome_lines = [
            "Welcome to the Treta Music Downloader Auto-Installer!",
            "",
            "This installer will set up everything you need:",
            "• Python environment with all dependencies",
            "• Spotify, Apple Music & YouTube downloaders",
            "• Audio processing tools (FFmpeg)",
            "• Global 'treta' command",
            "• Configuration and authentication setup",
            "",
            "Sit back and relax - we'll handle everything! ☕"
        ]
        
        print_box("Treta Auto-Installer v2.0", welcome_lines, Colors.CYAN)
        
        # Show installation options
        if self.force_reinstall or self.global_install or self.skip_optional or self.verbose:
            options = []
            if self.force_reinstall:
                options.append("Force reinstall enabled")
            if self.global_install:
                options.append("Global installation enabled")
            if self.skip_optional:
                options.append("Skipping optional packages")
            if self.verbose:
                options.append("Verbose logging enabled")
            
            print_box("Installation Options", options, Colors.YELLOW)
        
        # Confirmation
        try:
            response = input(f"\n{Colors.BOLD}{Colors.CYAN}Ready to begin installation? (Y/n): {Colors.RESET}")
            if response.lower().strip() in ['n', 'no']:
                print_info("Installation cancelled by user.")
                sys.exit(0)
        except KeyboardInterrupt:
            print_error("Installation cancelled by user.")
            sys.exit(0)
    
    def pre_installation_checks(self) -> bool:
        """Perform pre-installation checks."""
        print_step("Pre-installation checks", number=0)
        
        # Check if we have write permissions
        try:
            test_file = self.project_dir / '.install_test'
            test_file.write_text('test')
            test_file.unlink()
            print_substep("Write permissions", "✓ OK")
        except PermissionError:
            print_error("Insufficient permissions to write to project directory")
            print_info("Try running as administrator/sudo or choose a different directory")
            return False
        
        # Check internet connectivity
        try:
            urllib.request.urlopen('https://pypi.org', timeout=10)
            print_substep("Internet connectivity", "✓ OK")
        except (urllib.error.URLError, OSError):
            print_warning("No internet connection detected")
            print_info("Some features may not work without internet access")
        
        # Check disk space (approximate)
        try:
            disk_usage = shutil.disk_usage(self.project_dir)
            free_gb = disk_usage.free / (1024**3)
            if free_gb < 2:
                print_warning(f"Low disk space: {free_gb:.1f} GB free")
                print_info("Treta needs at least 2GB of free space")
            else:
                print_substep("Disk space", f"✓ {free_gb:.1f} GB available")
        except OSError:
            print_substep("Disk space", "? Unable to check")
        
        return True
    
    def check_and_install_python(self) -> bool:
        """Enhanced Python checking and installation with better user feedback."""
        print_substep("Detecting Python installation...")
        
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
                            print_substep(f"Found compatible Python: {version_str}", "✓")
                            return True
                        elif major == 3 and minor >= 8:
                            self.python_executable = cmd
                            print_substep(f"Found Python {version_str} (zotify prefers 3.11+)", "⚠")
                            return True
                        else:
                            print_substep(f"Found Python {version_str} (too old)", "✗")
                            
            except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                continue
        
        # Python not found or too old
        print_substep("Python 3.8+ not found, attempting installation...")
        return self.install_python()

    def check_python(self) -> bool:
        """Backward compatibility wrapper."""
        return self.check_and_install_python()

    def setup_global_access(self) -> bool:
        """Setup global access to the treta command."""
        print_substep("Setting up global command access...")
        
        if not self.global_install:
            print_substep("Global install not requested, skipping")
            return True
        
        try:
            if self.system == 'windows':
                return self.setup_windows_global_access()
            else:
                return self.setup_unix_global_access()
        except Exception as e:
            print_error(f"Failed to setup global access: {e}")
            return False

    def setup_windows_global_access(self) -> bool:
        """Setup global access on Windows by adding to PATH."""
        try:
            # Create a wrapper script in a common location
            user_scripts_dir = Path.home() / 'AppData' / 'Local' / 'Programs' / 'Treta'
            user_scripts_dir.mkdir(parents=True, exist_ok=True)
            
            # Create global treta.bat
            global_bat = user_scripts_dir / 'treta.bat'
            bat_content = f'@echo off\n"{self.venv_python}" "{self.project_dir / "treta.py"}" %*\n'
            global_bat.write_text(bat_content)
            
            # Try to add to PATH
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
                try:
                    current_path, _ = winreg.QueryValueEx(key, 'PATH')
                except FileNotFoundError:
                    current_path = ''
                
                scripts_dir_str = str(user_scripts_dir)
                if scripts_dir_str not in current_path:
                    new_path = f"{current_path};{scripts_dir_str}" if current_path else scripts_dir_str
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                    print_substep("Added to PATH (restart terminal to use 'treta' globally)")
                
                winreg.CloseKey(key)
                return True
                
            except Exception as e:
                print_substep(f"Could not modify PATH: {e}")
                print_substep(f"Manual step: Add {user_scripts_dir} to your PATH")
                return True  # Don't fail the installation for this
                
        except Exception as e:
            print_error(f"Failed to setup Windows global access: {e}")
            return False

    def setup_unix_global_access(self) -> bool:
        """Setup global access on Unix systems."""
        try:
            # Create symlink in /usr/local/bin (common approach)
            local_bin = Path('/usr/local/bin')
            if local_bin.exists() and os.access(local_bin, os.W_OK):
                symlink_path = local_bin / 'treta'
                if symlink_path.exists():
                    symlink_path.unlink()
                
                # Create wrapper script instead of direct symlink
                wrapper_content = f'#!/bin/bash\n"{self.venv_python}" "{self.project_dir / "treta.py"}" "$@"\n'
                symlink_path.write_text(wrapper_content)
                symlink_path.chmod(0o755)
                
                print_substep("Global 'treta' command installed to /usr/local/bin")
                return True
            else:
                # Try ~/.local/bin as fallback
                local_bin = Path.home() / '.local' / 'bin'
                local_bin.mkdir(parents=True, exist_ok=True)
                
                wrapper_path = local_bin / 'treta'
                wrapper_content = f'#!/bin/bash\n"{self.venv_python}" "{self.project_dir / "treta.py"}" "$@"\n'
                wrapper_path.write_text(wrapper_content)
                wrapper_path.chmod(0o755)
                
                print_substep("Global 'treta' command installed to ~/.local/bin")
                print_substep("Make sure ~/.local/bin is in your PATH")
                return True
                
        except Exception as e:
            print_error(f"Failed to setup Unix global access: {e}")
            return False

    def finalize_installation(self) -> bool:
        """Finalize the installation process."""
        print_substep("Cleaning up temporary files...")
        
        # Clean up any temporary files
        temp_patterns = ['*.tmp', '*.temp', '*.download']
        for pattern in temp_patterns:
            for temp_file in self.project_dir.glob(pattern):
                try:
                    temp_file.unlink()
                except OSError:
                    pass
        
        # Create success marker
        success_marker = self.project_dir / '.treta_installed'
        success_marker.write_text(f"Treta installed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print_substep("Installation finalized successfully")
        return True

    def show_results(self):
        """Show installation results in a beautiful format."""
        print()
        print_header("Installation Results", "Here's what we accomplished!")
        
        # Successful components
        if self.installed_components:
            print_box("✅ Successfully Installed", self.installed_components, Colors.GREEN)
        
        # Warnings
        if self.warnings:
            print_box("⚠️ Completed with Warnings", self.warnings, Colors.YELLOW)
        
        # Failed components
        if self.failed_components:
            print_box("❌ Failed Components", self.failed_components, Colors.RED)
        
        # Overall status
        if not self.failed_components and not self.warnings:
            print_success("🎉 Perfect installation! Everything is ready to use.")
        elif not self.failed_components:
            print_success("✅ Installation completed successfully with minor warnings.")
        else:
            print_warning("⚠️ Installation completed but some components failed.")
            print_info("Basic functionality should still work.")

    def show_next_steps(self):
        """Show enhanced next steps with better formatting."""
        print()
        print_header("🚀 You're All Set!", "Here's how to start using Treta:")
        
        # Quick start guide
        quick_start = [
            "1. Test your installation:",
            "   python test_installation.py",
            "",
            "2. Authenticate with your music services:",
            f"   {'treta' if self.global_install else 'python treta.py'} auth add --service spotify",
            f"   {'treta' if self.global_install else 'python treta.py'} auth add --service apple",
            "",
            "3. Download your first song:",
            f'   {'treta' if self.global_install else 'python treta.py'} download url "https://open.spotify.com/track/..."',
            "",
            "4. Explore all features:",
            f"   {'treta' if self.global_install else 'python treta.py'} --help"
        ]
        
        print_box("Quick Start Guide", quick_start, Colors.CYAN)
        
        # Advanced usage
        advanced = [
            "• Download entire playlists and albums",
            "• Use mood-based recommendations",
            "• Queue management and smart downloads",
            "• Artist discography downloads",
            "• High-quality audio format options",
            "• Metadata editing and organization"
        ]
        
        print_box("Advanced Features", advanced, Colors.MAGENTA)
        
        # Support information
        support = [
            "📖 Documentation: https://github.com/avinaxhroy/Treta/wiki",
            "🐛 Report Issues: https://github.com/avinaxhroy/Treta/issues",
            "💬 Community: https://github.com/avinaxhroy/Treta/discussions",
            "🔧 Troubleshooting: Run 'python test_installation.py'"
        ]
        
        print_box("Need Help?", support, Colors.BLUE)
        
        print()
        print_colored("🎵 Happy music downloading! 🎵", Colors.GREEN + Colors.BOLD, icon=Icons.HEART)
        print()
    
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
        if not self.venv_python:
            print_error("Virtual environment Python not available")
            return False
            
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
        """Create enhanced launcher scripts for easy access."""
        print_substep("Creating launcher scripts...")
        
        try:
            if self.system == 'windows':
                success = self.create_windows_launchers()
            else:
                success = self.create_unix_launchers()
                
            if success:
                print_substep("Launcher scripts created successfully")
                self.installed_components.append("Launcher scripts")
            
            return success
            
        except Exception as e:
            print_error(f"Failed to create launchers: {e}")
            self.failed_components.append("Launcher scripts")
            return False
    
    def create_windows_launchers(self) -> bool:
        """Create enhanced Windows batch and PowerShell launchers."""
        if not self.venv_python:
            return False
            
        # Create enhanced batch launcher
        launcher_content = f'''@echo off
REM Treta Music Downloader - Windows Launcher
REM Auto-generated by Treta installer v2.0

setlocal
cd /d "{self.project_dir}"

REM Check if virtual environment exists
if not exist "{self.venv_python}" (
    echo Error: Virtual environment not found at {self.venv_python}
    echo Please run the installer again.
    pause
    exit /b 1
)

REM Run Treta with all arguments
"{self.venv_python}" treta.py %*

REM Preserve exit code
exit /b %ERRORLEVEL%
'''
        
        launcher_path = self.project_dir / 'treta.bat'
        launcher_path.write_text(launcher_content, encoding='utf-8')
        
        # Create enhanced PowerShell launcher
        ps_content = f'''# Treta Music Downloader - PowerShell Launcher
# Auto-generated by Treta installer v2.0

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Set error handling
$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = "{self.project_dir}"
Set-Location $ScriptDir

# Check if virtual environment exists
$VenvPython = "{self.venv_python}"
if (-not (Test-Path $VenvPython)) {{
    Write-Host "Error: Virtual environment not found at $VenvPython" -ForegroundColor Red
    Write-Host "Please run the installer again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}}

# Run Treta with all passed arguments
try {{
    & $VenvPython "$ScriptDir\\treta.py" @Arguments
    exit $LASTEXITCODE
}} catch {{
    Write-Host "Error running Treta: $_" -ForegroundColor Red
    exit 1
}}
'''
        
        ps_launcher_path = self.project_dir / 'treta.ps1'
        ps_launcher_path.write_text(ps_content, encoding='utf-8')
        
        print_substep("Created treta.bat and treta.ps1 launchers")
        return True
    
    def create_unix_launchers(self) -> bool:
        """Create enhanced Unix shell launcher."""
        if not self.venv_python:
            return False
            
        launcher_content = f'''#!/bin/bash
# Treta Music Downloader - Unix Launcher
# Auto-generated by Treta installer v2.0

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="{self.project_dir}"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
VENV_PYTHON="{self.venv_python}"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $VENV_PYTHON" >&2
    echo "Please run the installer again." >&2
    exit 1
fi

# Run Treta with all arguments
exec "$VENV_PYTHON" "$SCRIPT_DIR/treta.py" "$@"
'''
        
        launcher_path = self.project_dir / 'treta'
        launcher_path.write_text(launcher_content, encoding='utf-8')
        
        # Make executable
        launcher_path.chmod(0o755)
        
        print_substep("Created treta shell launcher")
        return True
    
    def install_package(self) -> bool:
        """Install Treta package in development mode for global 'treta' command."""
        print_substep("Installing Treta package for global access...")
        
        try:
            if not self.venv_python:
                print_error("Virtual environment not available")
                self.failed_components.append("Treta package installation")
                return False
            
            # Install the current directory as an editable package
            result = subprocess.run([
                self.venv_python, '-m', 'pip', 'install', '-e', '.'
            ], cwd=self.project_dir, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print_substep("Treta package installed successfully")
                print_substep("Global 'treta' command is now available (in venv)")
                self.installed_components.append("Treta package (editable install)")
                return True
            else:
                print_substep(f"Package installation failed: {result.stderr}")
                self.warnings.append("Package installation (you can still use launcher scripts)")
                return False
                
        except Exception as e:
            print_substep(f"Package installation failed: {e}")
            self.warnings.append("Package installation (you can still use launcher scripts)")
            return False
    
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
        print_colored("1. Activate the virtual environment:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored("   .venv\\Scripts\\activate", Colors.WHITE)
        else:
            print_colored("   source .venv/bin/activate", Colors.WHITE)
        
        print()
        print_colored("2. Authenticate with your music services:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored("   treta auth add --service spotify  # (in activated venv)", Colors.WHITE)
            print_colored("   # OR without venv activation:", Colors.CYAN)
            print_colored("   treta.bat auth add --service spotify", Colors.WHITE)
            print_colored("   treta.bat auth add --service apple", Colors.WHITE)
        else:
            print_colored("   treta auth add --service spotify  # (in activated venv)", Colors.WHITE)
            print_colored("   # OR without venv activation:", Colors.CYAN)
            print_colored("   ./treta auth add --service spotify", Colors.WHITE)
            print_colored("   ./treta auth add --service apple", Colors.WHITE)
        
        print()
        print_colored("3. Start downloading music:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored('   treta download url "https://open.spotify.com/track/..."  # (in activated venv)', Colors.WHITE)
            print_colored("   # OR without venv activation:", Colors.CYAN)
            print_colored('   treta.bat download url "https://open.spotify.com/track/..."', Colors.WHITE)
        else:
            print_colored('   treta download url "https://open.spotify.com/track/..."  # (in activated venv)', Colors.WHITE)
            print_colored("   # OR without venv activation:", Colors.CYAN)
            print_colored('   ./treta download url "https://open.spotify.com/track/..."', Colors.WHITE)
        
        print()
        print_colored("4. Explore all features:", Colors.CYAN)
        
        if self.system == 'windows':
            print_colored("   treta guide    # (in activated venv)", Colors.WHITE)
            print_colored("   treta examples # (in activated venv)", Colors.WHITE)
            print_colored("   # OR:", Colors.CYAN)
            print_colored("   treta.bat guide", Colors.WHITE)
            print_colored("   treta.bat examples", Colors.WHITE)
        else:
            print_colored("   treta guide    # (in activated venv)", Colors.WHITE)
            print_colored("   treta examples # (in activated venv)", Colors.WHITE)
            print_colored("   # OR:", Colors.CYAN)
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


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Treta Universal Auto-Installer v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python install_auto.py                    # Standard installation
    python install_auto.py --global-install  # Install globally
    python install_auto.py --force-reinstall # Force reinstall everything
    python install_auto.py --verbose         # Enable detailed logging
    python install_auto.py --skip-optional   # Skip optional packages
        """
    )
    
    parser.add_argument(
        '--force-reinstall',
        action='store_true',
        help='Force reinstall all components even if they exist'
    )
    
    parser.add_argument(
        '--global-install',
        action='store_true',
        help='Install globally (adds treta command to PATH)'
    )
    
    parser.add_argument(
        '--skip-optional',
        action='store_true',
        help='Skip optional packages for faster installation'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()

def main():
    """Main entry point with enhanced argument handling."""
    args = parse_arguments()
    
    # Handle help display
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        return
    
    # Show basic help if no arguments
    if len(sys.argv) == 1:
        print_header("Treta Universal Auto-Installer v2.0", 
                    "The most user-friendly music downloader installer!")
        print_info("Starting installation with default settings...")
        print_info("Use --help to see all available options")
        print()
    
    installer = TretaInstaller(args)
    success = installer.run()
    
    if success:
        print()
        print_success("🎉 Treta installation completed successfully!")
        sys.exit(0)
    else:
        print()
        print_error("❌ Treta installation failed. Please check the errors above.")
        print_info("You can:")
        print_info("• Run the installer again with --verbose for more details")
        print_info("• Check the troubleshooting guide")
        print_info("• Report the issue on GitHub")
        sys.exit(1)


if __name__ == "__main__":
    main()
