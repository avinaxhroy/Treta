# 🔧 Treta Installation Troubleshooting Guide

## 🚨 Common Installation Issues and Solutions

### Issue 1: "install_auto.py not found"
**Error:** `python: can't open file 'install_auto.py': [Errno 2] No such file or directory`

**Solution:**
1. Make sure you're running the installer from the correct directory
2. Use the updated `install_easy.bat` (Windows) or `install_easy.sh` (Unix/Linux)
3. Or manually navigate to the Treta directory first:
   ```cmd
   cd path\to\treta
   python install_auto.py --global-install
   ```

### Issue 2: Python Not Found
**Error:** `Python not found` or `'python' is not recognized`

**Solutions:**
1. **Install Python 3.8+** from https://python.org/downloads/
2. **During installation, check "Add Python to PATH"**
3. **Test installation:**
   ```cmd
   python --version
   ```
4. **Alternative commands to try:**
   ```cmd
   python3 --version
   py --version
   ```

### Issue 3: Permission Denied
**Error:** `Permission denied` or `Access is denied`

**Solutions:**
1. **Windows:** Run Command Prompt as Administrator
2. **Linux/macOS:** Use `sudo` or check directory permissions
3. **Alternative:** Install to a user directory instead

### Issue 4: Virtual Environment Creation Fails
**Error:** `Failed to create virtual environment`

**Solutions:**
1. **Install venv module:**
   ```cmd
   python -m pip install --user virtualenv
   ```
2. **Try alternative creation:**
   ```cmd
   python -m virtualenv .venv
   ```
3. **Check Python installation integrity**

### Issue 5: Dependency Installation Fails
**Error:** Package installation timeouts or conflicts

**Solutions:**
1. **Try with increased timeout:**
   ```cmd
   python install_auto.py --verbose --global-install
   ```
2. **Skip optional packages:**
   ```cmd
   python install_auto.py --skip-optional --global-install
   ```
3. **Force reinstall:**
   ```cmd
   python install_auto.py --force-reinstall --global-install
   ```

### Issue 6: Zotify Installation Problems
**Error:** Zotify dependency conflicts

**Solutions:**
1. **Manual zotify installation:**
   ```cmd
   .venv\Scripts\activate
   pip uninstall -y zotify librespot
   pip install --no-deps git+https://github.com/DraftKinner/zotify.git@v1.0.1
   pip install requests Pillow protobuf tabulate tqdm pycryptodome music-tag
   pip install git+https://github.com/DraftKinner/librespot-python
   ```

### Issue 7: FFmpeg Download Fails
**Error:** FFmpeg installation issues

**Solutions:**
1. **Windows:** Download manually from https://ffmpeg.org/download.html
2. **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian)
3. **macOS:** `brew install ffmpeg`

### Issue 8: Global Command Not Working
**Error:** `'treta' is not recognized as an internal or external command`

**Solutions:**
1. **Run the global setup:**
   ```cmd
   python setup_global.py
   ```
2. **Restart your terminal/command prompt**
3. **Add to PATH manually (Windows):**
   - Search "Environment Variables" in Start menu
   - Edit system PATH
   - Add the Treta installation directory
4. **Use launcher scripts instead:**
   ```cmd
   treta.bat [commands]  # Windows
   ./treta [commands]    # Unix/Linux
   ```

## 🩺 Diagnostic Commands

### Quick Health Check
```cmd
python test_installation.py
```

### Detailed Diagnostics
```cmd
python test_installation.py --verbose
```

### Auto-Fix Common Issues
```cmd
python test_installation.py --fix-issues
```

## 🔄 Reset Installation

### Complete Reset
```cmd
# Delete virtual environment
rmdir /s .venv          # Windows
rm -rf .venv            # Unix/Linux

# Delete installed markers
del .treta_installed    # Windows
rm .treta_installed     # Unix/Linux

# Reinstall
python install_auto.py --force-reinstall --global-install
```

## 📞 Getting Additional Help

### 1. Check System Requirements
- **Python:** 3.8 or higher (3.11+ recommended)
- **Operating System:** Windows 10+, macOS 10.15+, or modern Linux
- **Disk Space:** At least 2GB free
- **Internet:** Required for downloading dependencies

### 2. Collect Diagnostic Information
Before reporting issues, run:
```cmd
python test_installation.py --verbose > diagnostic.txt 2>&1
```

### 3. Report Issues
- **GitHub Issues:** https://github.com/avinaxhroy/Treta/issues
- **Include:** Error messages, system info, and diagnostic output
- **Use:** The issue template for faster resolution

### 4. Community Support
- **Discussions:** https://github.com/avinaxhroy/Treta/discussions
- **Documentation:** Check the README.md and wiki

## 💡 Pro Tips

1. **Always use `--verbose` flag** when troubleshooting
2. **Run health check after every installation** attempt
3. **Keep Python updated** to the latest stable version
4. **Use PowerShell on Windows** for better Unicode support
5. **Close and reopen terminal** after PATH changes
6. **Don't run multiple installations** simultaneously

## 🎯 Success Indicators

A successful installation should show:
- ✅ All 10 installation steps completed
- ✅ Virtual environment created in `.venv/`
- ✅ Launcher scripts (`treta.bat`, `treta.ps1`)
- ✅ Health check passes all tests
- ✅ `treta --help` works (in venv or globally)

## 🔒 Clean Installation Process

For a guaranteed clean installation:

1. **Download fresh copy** of Treta
2. **Open terminal as admin** (Windows) or with `sudo` access (Unix)
3. **Navigate to Treta directory**
4. **Run:** `python install_auto.py --force-reinstall --global-install --verbose`
5. **Test:** `python test_installation.py --verbose`
6. **Verify:** `treta --help`

---

**Remember:** The installer is designed to be resilient and provide helpful error messages. Most issues can be resolved by following the specific guidance provided during installation failure.
