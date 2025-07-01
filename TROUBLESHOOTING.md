# Treta Installation Troubleshooting Guide

## Python Version Requirements

**Important:** Zotify requires **Python 3.11 or greater**. If you encounter installation issues, this is likely the cause.

### Quick Python Version Check

```bash
python --version
# Should show Python 3.11.x or higher
```

### Installing Python 3.11+

If you have an older Python version:

1. **Download Python 3.11+** from [python.org](https://www.python.org/downloads/)
2. **During installation:** Make sure to check "Add Python to PATH"
3. **Verify installation:** `python --version`

## Zotify Installation Issues

### Quick Fix - Manual Zotify Installation

If the auto-installer fails with zotify, try installing it manually:

```bash
# Activate your virtual environment first
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install stable version (recommended)
pip install git+https://github.com/DraftKinner/zotify.git@v1.0.1

# Or try development version if stable fails
pip install git+https://github.com/DraftKinner/zotify.git@dev
```

### Manual Installation Steps

If the auto-installer fails, try installing manually:

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   # macOS/Linux  
   source .venv/bin/activate
   ```

3. **Install core dependencies first:**
   ```bash
   pip install --upgrade pip
   pip install typer rich requests mutagen cryptography yt-dlp
   ```

4. **Install music downloaders:**
   ```bash
   # Apple Music
   pip install gamdl
   
   # Spotify (zotify) - use compatible versions
   pip install git+https://github.com/DraftKinner/librespot-python
   pip install git+https://github.com/DraftKinner/zotify.git
   ```

5. **Install optional audio processing libraries:**
   ```bash
   pip install librosa scikit-learn matplotlib soundfile
   ```

### Common Error Solutions

#### `ModuleNotFoundError: No module named 'imp'`
- This happens with Python 3.12+ and older dependencies
- Solution: Use DraftKinner's forks as shown above

#### `error: subprocess-exited-with-error` during wheel building
- Try installing individual packages instead of using requirements.txt
- Update pip: `pip install --upgrade pip`
- Install build tools: `pip install setuptools wheel`

#### `librespot-python` installation fails
- Make sure you're using DraftKinner's fork: 
  `pip install git+https://github.com/DraftKinner/librespot-python`
- If that fails, try without optional dependencies:
  `pip install --no-deps git+https://github.com/DraftKinner/librespot-python`

#### FFmpeg not found
- **Windows:** The installer should download FFmpeg automatically
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent

### Testing Your Installation

Run the test script to verify everything is working:

```bash
python test_installation.py
```

This will show you:
- Python version compatibility
- Which dependencies are installed correctly
- Which music downloaders are available
- Suggestions for fixing any issues

### Getting Help

If you're still having issues:

1. **Check the test results:** Run `python test_installation.py` first
2. **Report the issue:** Include the full error message and test results
3. **GitHub Issues:** [https://github.com/avinaxhroy/Treta/issues](https://github.com/avinaxhroy/Treta/issues)

### Advanced: Development Installation

For development or if you want the latest features:

```bash
git clone https://github.com/avinaxhroy/Treta.git
cd Treta
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .
```

This installs Treta in "editable" mode so you can modify the code and see changes immediately.
