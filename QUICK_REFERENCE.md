# 🎵 Treta Quick Reference Card

## 🚀 One-Command Installation

### Windows (Super Easy)
```cmd
# Just double-click:
install_easy.bat

# OR run:
python install_auto.py --global-install
```

### Linux/macOS (Super Easy)
```bash
# Just run:
./install_easy.sh

# OR run:
python3 install_auto.py --global-install
```

## 🩺 Health Check
```bash
python test_installation.py              # Basic check
python test_installation.py --verbose    # Detailed diagnostics  
python test_installation.py --fix-issues # Auto-fix problems
```

## 🌍 Global Setup
```bash
python setup_global.py                   # Add global 'treta' command
python setup_global.py --desktop         # Add desktop shortcuts
python setup_global.py --shell-alias     # Add shell aliases
```

## 🎯 Usage After Installation

### Authentication (Do This First!)
```bash
treta auth add --service spotify     # Spotify login
treta auth add --service apple       # Apple Music login  
treta auth list                      # View saved accounts
```

### Download Music
```bash
# Single track
treta download url "https://open.spotify.com/track/..."

# Playlist  
treta download url "https://open.spotify.com/playlist/..."

# Album
treta download url "https://open.spotify.com/album/..."

# Artist discography
treta artist download "Artist Name"
```

### Smart Features
```bash
treta mood analyze                   # Analyze your music mood
treta queue smart --mood happy       # Generate happy playlist
treta stats                          # View download statistics
treta --help                         # View all commands
```

## 🔧 Troubleshooting

### Installation Issues
```bash
python install_auto.py --force-reinstall --verbose
```

### Missing Dependencies
```bash
# In virtual environment:
.venv\Scripts\activate           # Windows  
source .venv/bin/activate        # Linux/macOS
pip install -r requirements.txt
```

### Permission Issues
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo or check file permissions
```

## 📁 File Structure
```
Treta/
├── install_auto.py          # Main installer
├── install_easy.bat         # Windows easy installer  
├── install_easy.sh          # Unix easy installer
├── test_installation.py     # Health check tool
├── setup_global.py          # Global setup tool
├── treta.py                 # Main application
├── treta.bat               # Windows launcher
├── treta.ps1               # PowerShell launcher  
├── requirements.txt         # Dependencies
└── .venv/                  # Virtual environment
```

## 🆘 Getting Help

1. **Run diagnostics**: `python test_installation.py --verbose`
2. **Check documentation**: Read `README.md`
3. **Report issues**: https://github.com/avinaxhroy/Treta/issues
4. **Community**: https://github.com/avinaxhroy/Treta/discussions

## ⚡ Pro Tips

- Use `--global-install` for easiest setup
- Run health check after installation
- Use PowerShell on Windows for best experience
- Keep your virtual environment activated for development
- Use `treta --help` to discover all features

## 🎵 Happy Music Downloading!

Enjoy your perfectly configured Treta installation! 🎉
