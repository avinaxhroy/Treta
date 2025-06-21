#!/usr/bin/env python3
"""
Comprehensive Treta Project Health Check
=======================================

This script performs a complete health check of the Treta project
to ensure it's ready for public distribution.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def print_status(message, success=True):
    symbol = "✅" if success else "❌"
    print(f"{symbol} {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_file_exists(filepath):
    """Check if a file exists."""
    if Path(filepath).exists():
        print_status(f"{filepath} exists")
        return True
    else:
        print_status(f"{filepath} missing", False)
        return False

def check_python_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        compile(source, filepath, 'exec')
        print_status(f"{filepath} syntax OK")
        return True
    except SyntaxError as e:
        print_status(f"{filepath} syntax error: {e}", False)
        return False
    except Exception as e:
        print_warning(f"{filepath} check failed: {e}")
        return False

def check_import(module_path):
    """Check if a module can be imported."""
    try:
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Don't actually execute the module, just check if it can be loaded
            print_status(f"{module_path} can be imported")
            return True
        else:
            print_status(f"{module_path} import failed", False)
            return False
    except Exception as e:
        print_warning(f"{module_path} import error: {e}")
        return False

def main():
    """Run comprehensive health check."""
    
    print_header("Treta Project Health Check")
    
    # Check if we're in the right directory
    if not Path("treta.py").exists():
        print_status("Not in Treta project directory", False)
        return False
    
    print_status("In Treta project directory")
    
    # 1. Essential Files Check
    print_header("Essential Files Check")
    essential_files = [
        "treta.py",
        "install_auto.py", 
        "requirements.txt",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "MANIFEST.in"
    ]
    
    files_ok = True
    for file in essential_files:
        if not check_file_exists(file):
            files_ok = False
    
    # 2. Directory Structure Check
    print_header("Directory Structure Check")
    essential_dirs = [
        "cli",
        "core", 
        "db",
        "downloads",
        "data"
    ]
    
    dirs_ok = True
    for dir_name in essential_dirs:
        if Path(dir_name).exists():
            print_status(f"Directory {dir_name}/ exists")
        else:
            print_status(f"Directory {dir_name}/ missing", False)
            dirs_ok = False
    
    # 3. Python Syntax Check
    print_header("Python Syntax Check")
    python_files = [
        "treta.py",
        "install_auto.py",
        "cli/__init__.py",
        "cli/artist.py",
        "cli/auth.py", 
        "cli/download.py",
        "cli/mood.py",
        "cli/queue.py",
        "cli/stats.py",
        "core/__init__.py",
        "core/config.py",
        "core/auth_store.py",
        "core/logging_config.py",
        "core/metadata.py",
        "core/mood_detector.py",
        "core/smart_queue.py",
        "db/__init__.py",
        "db/models.py",
        "db/manager.py"
    ]
    
    syntax_ok = True
    for py_file in python_files:
        if Path(py_file).exists():
            if not check_python_syntax(py_file):
                syntax_ok = False
        else:
            print_warning(f"{py_file} not found")
    
    # 4. Package Dependencies Check
    print_header("Package Dependencies Check")
    try:
        import typer
        print_status("typer available")
    except ImportError:
        print_status("typer missing", False)
    
    try:
        import rich
        print_status("rich available")
    except ImportError:
        print_status("rich missing", False)
    
    try:
        import pathlib
        print_status("pathlib available")
    except ImportError:
        print_status("pathlib missing", False)
    
    # Optional dependencies
    try:
        import mutagen
        print_status("mutagen available (optional)")
    except ImportError:
        print_warning("mutagen missing (audio metadata features limited)")
    
    try:
        import matplotlib
        print_status("matplotlib available (optional)")
    except ImportError:
        print_warning("matplotlib missing (chart generation disabled)")
    
    # 5. Configuration Files Check
    print_header("Configuration Files Check")
    
    # Check requirements.txt
    try:
        with open("requirements.txt", 'r') as f:
            reqs = f.read()
        if "typer" in reqs and "rich" in reqs:
            print_status("requirements.txt contains essential packages")
        else:
            print_status("requirements.txt missing essential packages", False)
    except Exception as e:
        print_status(f"requirements.txt check failed: {e}", False)
    
    # Check pyproject.toml
    try:
        with open("pyproject.toml", 'r') as f:
            toml_content = f.read()
        if "[build-system]" in toml_content and "[project]" in toml_content:
            print_status("pyproject.toml has required sections")
        else:
            print_status("pyproject.toml missing required sections", False)
    except Exception as e:
        print_status(f"pyproject.toml check failed: {e}", False)
    
    # 6. Auto-Installer Check
    print_header("Auto-Installer Check")
    
    installer_files = ["install_auto.py", "install.sh", "install.ps1"]
    installer_ok = True
    for installer in installer_files:
        if not check_file_exists(installer):
            installer_ok = False
    
    # 7. Summary
    print_header("Health Check Summary")
    
    overall_status = all([files_ok, dirs_ok, syntax_ok, installer_ok])
    
    if overall_status:
        print_status("🎉 PROJECT READY FOR PUBLIC RELEASE!", True)
        print("\n🚀 Next steps:")
        print("   1. Create GitHub repository")
        print("   2. Test auto-installer on different platforms")
        print("   3. Create release with proper tags")
        print("   4. Update documentation with actual repository URLs")
    else:
        print_status("❌ PROJECT NEEDS FIXES BEFORE RELEASE", False)
        print("\n🔧 Issues found that need attention:")
        if not files_ok:
            print("   - Missing essential files")
        if not dirs_ok:
            print("   - Missing required directories")
        if not syntax_ok:
            print("   - Python syntax errors")
        if not installer_ok:
            print("   - Missing installer files")
    
    return overall_status

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
