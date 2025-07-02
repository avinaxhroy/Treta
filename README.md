# 🎵 Treta Music Downloader

<div align="center">

[![Release](https://img.shields.io/github/v/release/avinaxhroy/treta?style=for-the-badge&logo=github)](https://github.com/avinaxhroy/treta/releases)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/github/license/avinaxhroy/treta?style=for-the-badge)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/avinaxhroy/treta/total?style=for-the-badge)](https://github.com/avinaxhroy/treta/releases)

**A powerful, AI-enhanced music downloader with support for Spotify, Apple Music, and YouTube Music**

[🚀 **Quick Install**](#-installation) • [📖 **Documentation**](#-usage) • [�️ **Features**](#-features) • [❓ **Support**](https://github.com/avinaxhroy/treta/issues)

</div>

---

## ⚠️ Important Disclaimer

**This tool is for educational and personal use only.** Please respect copyright laws and platform terms of service. Premium subscriptions are required for premium services. The developers are not responsible for any misuse of this software.

---

## 🚀 Installation

### One-Click Installation (Recommended)

Get up and running in seconds with our automated installers:

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.ps1 | iex"
```

**Linux/macOS (Bash):**
```bash
curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
```

### Manual Installation

For advanced users who want more control:

```bash
# Clone the repository
git clone https://github.com/avinaxhroy/treta.git
cd treta

# Run the installer with global setup
python install_auto.py --global-install
```

### What the Installer Does

Our smart installer automatically handles everything:

- ✅ **Python Environment**: Detects and configures Python 3.8+
- ✅ **Dependencies**: Installs all required packages
- ✅ **FFmpeg**: Downloads and configures audio processing tools
- ✅ **Virtual Environment**: Creates isolated Python environment
- ✅ **Global Command**: Sets up `treta` command system-wide
- ✅ **PATH Configuration**: Adds to system PATH automatically

---

## 🛠️ Features

### 🎧 Supported Platforms

| Platform | Audio Quality | Formats | Requirements |
|----------|---------------|---------|--------------|
| **Spotify** | FLAC, 320kbps MP3 | FLAC, OGG | Premium Account |
| **Apple Music** | AAC 256kbps | M4A, AAC | Active Subscription |
| **YouTube Music** | Up to FLAC | FLAC, WEBM, MP3 | None (Free) |

### ⭐ Key Features

- 🤖 **AI Mood Detection**: Automatically categorizes music by mood and energy
- 📁 **Smart Organization**: Auto-sorts downloads by service/artist/album
- 🔄 **Batch Processing**: Download entire playlists and albums
- 🎯 **High Quality**: Premium audio formats with complete metadata
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux
- 🎨 **Interactive CLI**: Beautiful command-line interface with progress bars
- 📊 **Statistics**: Track your download history and library stats
- 🔍 **Smart Search**: Find and download music efficiently

---

## 📖 Usage

### Getting Started

After installation, simply run:
```bash
treta
```

This launches the interactive menu where you can:
- Download individual tracks or playlists
- Manage authentication for different services
- View your download statistics
- Analyze mood patterns in your library

### Quick Commands

**Download a single track:**
```bash
treta download url "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
```

**Download multiple URLs:**
```bash
treta download url "url1" "url2" "url3"
```

**Download from a file:**
```bash
treta download batch --file my_playlist.txt
```

**Download with specific quality:**
```bash
treta download url "spotify_url" --quality flac
```

### Authentication Setup

Before downloading from premium services, set up authentication:

**Spotify:**
```bash
treta auth add --service spotify
# Follow the prompts to log in
```

**Apple Music:**
```bash
treta auth add --service apple
# Enter your Apple ID credentials
```

**Check authentication status:**
```bash
treta auth status
```

### Advanced Features

**Mood Analysis:**
```bash
# Analyze your music library
treta mood analyze

# Create mood-based playlists
treta mood playlist --mood "energetic" --count 25
```

**Library Statistics:**
```bash
# View download statistics
treta stats overview

# Top artists in your library
treta stats artists --top 10

# Storage usage breakdown
treta stats storage
```

**Queue Management:**
```bash
# View download queue
treta queue list

# Pause/resume downloads
treta queue pause
treta queue resume

# Clear completed downloads
treta queue clear
```

---

## 📁 File Organization

Treta organizes your downloads in a clean, logical structure:

```
downloads/
├── spotify/
│   ├── Artist Name/
│   │   ├── Album Name/
│   │   │   ├── 01 - Track Name.flac
│   │   │   ├── 02 - Track Name.flac
│   │   │   └── cover.jpg
│   │   └── Singles/
│   └── Playlists/
├── apple/
│   └── [Similar structure]
├── youtube/
│   └── [Similar structure]
└── metadata/
    ├── downloads.db
    └── mood_analysis.json
```

---

## 🔧 Troubleshooting

### Health Check & Diagnostics

Run our built-in diagnostic tool:
```bash
python test_installation.py --verbose
```

**Auto-fix common issues:**
```bash
python test_installation.py --fix-issues
```

### Common Issues & Solutions

**❌ Installation Failed**
```bash
# Force reinstall with verbose output
python install_auto.py --force-reinstall --verbose

# Manual dependency install
pip install -r requirements.txt
```

**❌ Authentication Issues**
```bash
# Reset authentication
treta auth remove --service spotify
treta auth add --service spotify

# Clear auth cache
treta auth clear-cache
```

**❌ Global Command Not Found**
```bash
# Test global command setup
python test_global_command.py

# Manual PATH configuration (if needed)
# Windows: Add install directory to System PATH
# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
```

**❌ Download Failures**
```bash
# Retry failed downloads
treta download retry

# Update downloaders
treta update components

# Check service status
treta status check
```

### Getting Help

- 📖 **Full Documentation**: See `TROUBLESHOOTING.md`
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/avinaxhroy/treta/issues)
- 💬 **Community Support**: [Discussions](https://github.com/avinaxhroy/treta/discussions)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/avinaxhroy/treta.git
cd treta
python install_auto.py --verbose

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_downloader.py -v
pytest tests/test_mood_detector.py -v

# Run tests with coverage
pytest --cov=treta tests/
```

### Contribution Guidelines

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. ✨ **Make** your changes with tests
4. ✅ **Test** thoroughly (`pytest tests/`)
5. 📝 **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. 🚀 **Push** to your branch (`git push origin feature/amazing-feature`)
7. 🔄 **Submit** a Pull Request

---

## 🙏 Acknowledgments

Treta builds upon the excellent work of these projects:

- **[Zotify](https://github.com/DraftKinner/zotify)** - Spotify downloading engine
- **[GAMDL](https://github.com/glomatico/gamdl)** - Apple Music downloader
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - YouTube downloading
- **[librosa](https://librosa.org)** - Audio analysis and mood detection
- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal output
- **[Typer](https://typer.tiangolo.com)** - Modern CLI framework

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🎵 Made with ❤️ for music lovers everywhere 🎵**

[⬇️ Download Latest](https://github.com/avinaxhroy/treta/releases/latest) • [📝 Report Bug](https://github.com/avinaxhroy/treta/issues/new) • [💡 Request Feature](https://github.com/avinaxhroy/treta/issues/new)

---

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=avinaxhroy/treta&type=Date)](https://star-history.com/#avinaxhroy/treta&Date)

</div>