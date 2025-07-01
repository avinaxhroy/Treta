# Treta Installation Troubleshooting Guide

## Python 3.12 `imp` Module Error

If you get this error:
```
ModuleNotFoundError: No module named 'imp'
```

This is a Python 3.12 compatibility issue with librespot-python. Here are the solutions:

### Solution 1: Manual Compatible Installation (Recommended)

```bash
# Activate your virtual environment first
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install DraftKinner's librespot-python (more compatible)
pip install git+https://github.com/DraftKinner/librespot-python

# Install zotify without dependencies to avoid conflicts
pip install --no-deps git+https://github.com/DraftKinner/zotify.git@v1.0.1

# Install zotify's other dependencies manually
pip install requests Pillow protobuf tabulate tqdm pycryptodome music-tag
```

### Solution 2: Use Python 3.11 (Most Reliable)

1. **Download Python 3.11** from [python.org](https://www.python.org/downloads/release/python-3118/)
2. **Install it** (make sure to check "Add Python to PATH")
3. **Create a new virtual environment:**
   ```bash
   python3.11 -m venv .venv
   ```
4. **Run the installer again**

### Solution 3: Alternative librespot Installation

Try installing a specific commit that doesn't have the `imp` issue:

```bash
# Remove existing librespot if installed
pip uninstall -y librespot

# Install compatible version
pip install git+https://github.com/kokarare1212/librespot-python.git@6f88a73b59baaeb3c6e1e8c87cd1b9b57b42b8e0

# Then install zotify without deps
pip install --no-deps git+https://github.com/DraftKinner/zotify.git@v1.0.1
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
