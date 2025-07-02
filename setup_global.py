#!/usr/bin/env python3
"""
Treta Global Installation Script
===============================

This script sets up global access to the 'treta' command by:
- Adding Treta to your system PATH
- Creating global wrapper scripts
- Setting up shell aliases (optional)
- Configuring desktop shortcuts (optional)

Usage:
    python setup_global.py
    python setup_global.py --uninstall     # Remove global access
    python setup_global.py --desktop       # Add desktop shortcuts
    python setup_global.py --shell-alias   # Add shell aliases
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path
import argparse

# Color support
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_colored(text: str, color: str = Colors.WHITE):
    """Print colored text."""
    print(f"{color}{text}{Colors.RESET}")

def print_success(message: str):
    print_colored(f"✅ {message}", Colors.GREEN)

def print_error(message: str):
    print_colored(f"❌ {message}", Colors.RED)

def print_warning(message: str):
    print_colored(f"⚠️  {message}", Colors.YELLOW)

def print_info(message: str):
    print_colored(f"ℹ️  {message}", Colors.CYAN)

class GlobalSetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.system = platform.system().lower()
        self.venv_python = self.find_venv_python()
        
    def find_venv_python(self) -> str:
        """Find the virtual environment Python executable."""
        venv_paths = [self.project_dir / '.venv', self.project_dir / 'venv']
        
        for venv_path in venv_paths:
            if self.system == 'windows':
                python_exe = venv_path / 'Scripts' / 'python.exe'
            else:
                python_exe = venv_path / 'bin' / 'python'
            
            if python_exe.exists():
                return str(python_exe)
        
        # Fallback to system Python
        return sys.executable
    
    def install_global(self, desktop: bool = False, shell_alias: bool = False) -> bool:
        """Install global access."""
        print_colored("🚀 Setting up global Treta access...", Colors.CYAN + Colors.BOLD)
        print()
        
        success = True
        
        if self.system == 'windows':
            success &= self.install_windows_global()
        else:
            success &= self.install_unix_global()
        
        if desktop:
            success &= self.create_desktop_shortcuts()
        
        if shell_alias:
            success &= self.setup_shell_aliases()
        
        return success
    
    def install_windows_global(self) -> bool:
        """Install global access on Windows."""
        try:
            # Create user programs directory
            user_programs = Path.home() / 'AppData' / 'Local' / 'Programs' / 'Treta'
            user_programs.mkdir(parents=True, exist_ok=True)
            
            # Create global treta.bat
            global_bat = user_programs / 'treta.bat'
            bat_content = f'''@echo off
REM Treta Global Launcher
cd /d "{self.project_dir}"
"{self.venv_python}" "{self.project_dir}\\treta.py" %*
'''
            global_bat.write_text(bat_content)
            
            # Create global treta.cmd (alternative name)
            global_cmd = user_programs / 'treta.cmd'
            global_cmd.write_text(bat_content)
            
            print_success(f"Global launcher created at {user_programs}")
            
            # Try to add to PATH
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
                
                try:
                    current_path, _ = winreg.QueryValueEx(key, 'PATH')
                except FileNotFoundError:
                    current_path = ''
                
                user_programs_str = str(user_programs)
                if user_programs_str not in current_path:
                    new_path = f"{current_path};{user_programs_str}" if current_path else user_programs_str
                    winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                    print_success("Added to PATH - restart your terminal to use 'treta' globally")
                else:
                    print_info("Already in PATH")
                
                winreg.CloseKey(key)
                
                # Notify system of PATH change
                try:
                    import ctypes
                    from ctypes import wintypes
                    
                    HWND_BROADCAST = 0xFFFF
                    WM_SETTINGCHANGE = 0x001A
                    SMTO_ABORTIFHUNG = 0x0002
                    
                    result = ctypes.c_long()
                    SendMessageTimeout = ctypes.windll.user32.SendMessageTimeoutW
                    SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
                except:
                    pass  # Not critical if this fails
                
                return True
                
            except Exception as e:
                print_warning(f"Could not modify PATH automatically: {e}")
                print_info(f"Please manually add {user_programs} to your PATH")
                return True  # Still successful, just requires manual step
                
        except Exception as e:
            print_error(f"Failed to setup Windows global access: {e}")
            return False
    
    def install_unix_global(self) -> bool:
        """Install global access on Unix systems."""
        try:
            # Try /usr/local/bin first (system-wide)
            local_bin = Path('/usr/local/bin')
            if local_bin.exists() and os.access(local_bin, os.W_OK):
                target_dir = local_bin
                scope = "system-wide"
            else:
                # Use ~/.local/bin as fallback
                target_dir = Path.home() / '.local' / 'bin'
                target_dir.mkdir(parents=True, exist_ok=True)
                scope = "user"
            
            # Create wrapper script
            wrapper_path = target_dir / 'treta'
            wrapper_content = f'''#!/bin/bash
# Treta Global Launcher
exec "{self.venv_python}" "{self.project_dir}/treta.py" "$@"
'''
            wrapper_path.write_text(wrapper_content)
            wrapper_path.chmod(0o755)
            
            print_success(f"Global 'treta' command installed ({scope})")
            
            if scope == "user":
                print_info("Make sure ~/.local/bin is in your PATH")
                print_info("Add this to your shell profile if needed:")
                print_colored('  export PATH="$HOME/.local/bin:$PATH"', Colors.WHITE)
            
            return True
            
        except Exception as e:
            print_error(f"Failed to setup Unix global access: {e}")
            return False
    
    def create_desktop_shortcuts(self) -> bool:
        """Create desktop shortcuts."""
        try:
            if self.system == 'windows':
                return self.create_windows_shortcuts()
            else:
                return self.create_unix_shortcuts()
        except Exception as e:
            print_error(f"Failed to create desktop shortcuts: {e}")
            return False
    
    def create_windows_shortcuts(self) -> bool:
        """Create Windows desktop shortcuts."""
        try:
            import winshell
            desktop = winshell.desktop()
        except ImportError:
            print_warning("winshell not available - creating basic shortcuts")
            desktop = Path.home() / 'Desktop'
        
        # Create desktop shortcut
        shortcut_path = desktop / 'Treta Music Downloader.lnk'
        
        try:
            # Try with winshell first
            import winshell
            with winshell.shortcut(str(shortcut_path)) as link:
                link.path = str(self.venv_python)
                link.arguments = f'"{self.project_dir}\\treta.py"'
                link.description = "Treta Music Downloader"
                link.working_directory = str(self.project_dir)
            
            print_success("Desktop shortcut created")
            return True
            
        except ImportError:
            # Fallback: create batch file
            shortcut_bat = desktop / 'Treta Music Downloader.bat'
            bat_content = f'''@echo off
title Treta Music Downloader
cd /d "{self.project_dir}"
"{self.venv_python}" treta.py %*
pause
'''
            shortcut_bat.write_text(bat_content)
            print_success("Desktop launcher created (batch file)")
            return True
    
    def create_unix_shortcuts(self) -> bool:
        """Create Unix desktop shortcuts."""
        desktop_dirs = [
            Path.home() / 'Desktop',
            Path.home() / '.local' / 'share' / 'applications'
        ]
        
        desktop_entry = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=Treta Music Downloader
Comment=Download music from Spotify, Apple Music, and YouTube
Exec="{self.venv_python}" "{self.project_dir}/treta.py"
Icon=audio-x-generic
Terminal=true
Categories=AudioVideo;Audio;
'''
        
        for desktop_dir in desktop_dirs:
            if desktop_dir.exists():
                shortcut_path = desktop_dir / 'treta.desktop'
                shortcut_path.write_text(desktop_entry)
                shortcut_path.chmod(0o755)
                print_success(f"Desktop entry created in {desktop_dir}")
        
        return True
    
    def setup_shell_aliases(self) -> bool:
        """Setup shell aliases."""
        try:
            if self.system == 'windows':
                return self.setup_windows_aliases()
            else:
                return self.setup_unix_aliases()
        except Exception as e:
            print_error(f"Failed to setup shell aliases: {e}")
            return False
    
    def setup_windows_aliases(self) -> bool:
        """Setup Windows PowerShell aliases."""
        try:
            # PowerShell profile path
            profile_path = Path.home() / 'Documents' / 'PowerShell' / 'Microsoft.PowerShell_profile.ps1'
            profile_path.parent.mkdir(parents=True, exist_ok=True)
            
            alias_content = f'''
# Treta Music Downloader Aliases
function treta {{ & "{self.venv_python}" "{self.project_dir}\\treta.py" @args }}
function treta-auth {{ & "{self.venv_python}" "{self.project_dir}\\treta.py" auth @args }}
function treta-download {{ & "{self.venv_python}" "{self.project_dir}\\treta.py" download @args }}
function treta-queue {{ & "{self.venv_python}" "{self.project_dir}\\treta.py" queue @args }}
'''
            
            # Append to profile if it doesn't already contain treta aliases
            if profile_path.exists():
                existing_content = profile_path.read_text()
                if 'treta' not in existing_content:
                    profile_path.write_text(existing_content + alias_content)
            else:
                profile_path.write_text(alias_content)
            
            print_success("PowerShell aliases added to profile")
            print_info("Restart PowerShell to use aliases")
            return True
            
        except Exception as e:
            print_warning(f"Could not setup PowerShell aliases: {e}")
            return False
    
    def setup_unix_aliases(self) -> bool:
        """Setup Unix shell aliases."""
        shell_profiles = [
            Path.home() / '.bashrc',
            Path.home() / '.zshrc',
            Path.home() / '.profile'
        ]
        
        alias_content = f'''
# Treta Music Downloader Aliases
alias treta='"{self.venv_python}" "{self.project_dir}/treta.py"'
alias treta-auth='"{self.venv_python}" "{self.project_dir}/treta.py" auth'
alias treta-download='"{self.venv_python}" "{self.project_dir}/treta.py" download'
alias treta-queue='"{self.venv_python}" "{self.project_dir}/treta.py" queue'
'''
        
        added_to_profiles = []
        
        for profile in shell_profiles:
            if profile.exists():
                try:
                    existing_content = profile.read_text()
                    if 'treta' not in existing_content:
                        profile.write_text(existing_content + alias_content)
                        added_to_profiles.append(profile.name)
                except:
                    continue
        
        if added_to_profiles:
            print_success(f"Shell aliases added to: {', '.join(added_to_profiles)}")
            print_info("Restart your shell or run 'source ~/.bashrc' to use aliases")
            return True
        else:
            print_warning("No shell profiles found to add aliases")
            return False
    
    def uninstall_global(self) -> bool:
        """Remove global access."""
        print_colored("🗑️  Removing global Treta access...", Colors.YELLOW + Colors.BOLD)
        print()
        
        success = True
        
        if self.system == 'windows':
            success &= self.uninstall_windows_global()
        else:
            success &= self.uninstall_unix_global()
        
        return success
    
    def uninstall_windows_global(self) -> bool:
        """Remove Windows global access."""
        try:
            # Remove from Programs directory
            user_programs = Path.home() / 'AppData' / 'Local' / 'Programs' / 'Treta'
            if user_programs.exists():
                shutil.rmtree(user_programs)
                print_success("Removed global launcher directory")
            
            # Note: We don't automatically remove from PATH to avoid breaking other software
            print_info("Note: You may want to remove Treta from your PATH manually")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to remove Windows global access: {e}")
            return False
    
    def uninstall_unix_global(self) -> bool:
        """Remove Unix global access."""
        try:
            # Remove from possible locations
            possible_locations = [
                Path('/usr/local/bin/treta'),
                Path.home() / '.local' / 'bin' / 'treta'
            ]
            
            removed = []
            for location in possible_locations:
                if location.exists():
                    location.unlink()
                    removed.append(str(location))
            
            if removed:
                print_success(f"Removed global launchers: {', '.join(removed)}")
            else:
                print_info("No global launchers found to remove")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to remove Unix global access: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Treta Global Installation Setup")
    parser.add_argument('--uninstall', action='store_true', help='Remove global access')
    parser.add_argument('--desktop', action='store_true', help='Create desktop shortcuts')
    parser.add_argument('--shell-alias', action='store_true', help='Setup shell aliases')
    
    args = parser.parse_args()
    
    setup = GlobalSetup()
    
    if args.uninstall:
        success = setup.uninstall_global()
    else:
        success = setup.install_global(desktop=args.desktop, shell_alias=args.shell_alias)
    
    if success:
        if args.uninstall:
            print_success("Global access removed successfully!")
        else:
            print_success("Global access installed successfully!")
            print_info("You can now use 'treta' command from anywhere!")
    else:
        print_error("Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
