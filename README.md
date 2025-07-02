# 🎵 Treta Music Downloader

<div align="center">

![Treta Logo](http://avinas.me/wp-content/uploads/2025/06/TRETA.png)

[![Release](https://img.shields.io/github/v/release/avinaxhroy/treta?style=flat-square)](https://github.com/avinaxhroy/treta/releases)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/github/license/avinaxhroy/treta?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/avinaxhroy/treta?style=flat-square)](https://github.com/avinaxhroy/treta/stargazers)
[![Downloads](https://img.shields.io/github/downloads/avinaxhroy/treta/total?style=flat-square)](https://github.com/avinaxhroy/treta/releases)

**🚀 The Ultimate Multi-Platform Music Downloader | 🎯 Zero Configuration Required | 🎶 Premium Quality Audio**

*A feature-rich, AI-powered music downloader supporting Spotify, Apple Music, and YouTube Music with intelligent mood detection, smart playlists, and completely automated setup.*

### 🆕 **NEW v2.0: One-Click "No-Brainer" Installation!**
*✨ Enhanced auto-installer with beautiful UI, smart error handling, and global command setup*

[🚀 **Auto-Install Now**](#-one-click-installation--setup-new-v20) • [📖 **Documentation**](#-complete-command-reference) • [💬 **Community (Coming Soon)**]() • [🐛 **Issues**](https://github.com/avinaxhroy/treta/issues)

</div>

---

## ⚖️ Disclaimer

Treta Music Downloader is intended for **educational and personal use only**. Users must ensure compliance with the terms of service of the platforms they access and respect all applicable copyright laws. The software does not circumvent DRM protections and requires valid subscriptions or accounts for premium services. 

**Key Points:**
- ✅ This project is only made for education purpose.
- ✅ Use downloads for personal, non-commercial purposes only.
- ✅ Ensure you have the legal right to access and download content.
- ✅ The developers are not responsible for misuse of this software.

By using Treta, you agree to take full responsibility for adhering to local laws and regulations regarding music downloads and intellectual property rights.


## ⚡ One-Click Installation & Setup (NEW v2.0!)

**🎉 Introducing the most user-friendly installer on the planet!** Our enhanced auto-installer v2.0 is now even smarter, faster, and more reliable with beautiful colored progress bars, intelligent error recovery, and zero-configuration setup.

> **💡 Pro Tip**: The installer automatically handles Python detection, dependency management, FFmpeg setup, and global command installation. Just run it and you're ready to download music in under 2 minutes!

### 🖥️ Windows - Super Easy Installation

**🏆 Option 1: Ultimate Easy Mode (Recommended)**
```powershell
# Just double-click this file after cloning/downloading:
install_easy.bat
```
*This downloads the repository and runs the installer automatically - perfect for beginners!*

**🏆 Option 2: Remote One-Liner (Ultimate Convenience)**
```powershell
# Download and run the auto-installer from anywhere
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.ps1 | iex"
```
*Downloads the repository and installs everything automatically - works from any directory!*

**Option 3: PowerShell One-Liner (Alternative)**
```powershell
# Download and run the auto-installer
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install.ps1 | iex"
```

**Option 4: Manual with Enhanced Features**
```cmd
# Clone the repository
git clone https://github.com/avinaxhroy/treta.git
cd treta

# Run the enhanced auto-installer
python install_auto.py --global-install
```

### 🐧 Linux/macOS - One Command Installation

**🏆 Option 1: Ultimate Easy Mode (Recommended)**
```bash
# Just run this after cloning:
./install_easy.sh
```
*Automatically handles everything including Python, dependencies, and global setup!*

**🏆 Option 2: Remote One-Liner (Ultimate Convenience)**
```bash
# Download and install from anywhere
curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
```
*Downloads the repository and installs everything automatically - works from any directory!*

**Option 3: Direct Installation**
```bash
# Clone and install in one go
git clone https://github.com/avinaxhroy/treta.git && cd treta && python3 install_auto.py --global-install
```

### 🚀 What the Enhanced Auto-Installer v2.0 Does

**🎨 Beautiful User Experience:**
- ✨ **Colored Progress Bars**: Beautiful Unicode progress indicators with Windows fallbacks
- 🎯 **Smart Error Recovery**: Automatically detects and fixes common installation issues
- 📊 **Real-time Status**: Step-by-step progress with detailed status messages
- 🔍 **Health Diagnostics**: Comprehensive pre and post-installation checks

**🔧 Technical Setup (No User Action Required):**
- ✅ **Smart Python Detection**: Finds and validates Python 3.8+ installation
- ✅ **Auto Python Install**: Downloads and installs Python if missing
- ✅ **Virtual Environment**: Creates isolated `.venv` for clean dependencies
- ✅ **Dependency Resolution**: Installs all required packages with smart conflict resolution
- ✅ **FFmpeg Integration**: Downloads and configures FFmpeg for audio processing
- ✅ **Global Command Setup**: Installs `treta` command globally in your PATH

**🎵 Music Service Integration:**
- ✅ **Spotify Support**: zotify with DraftKinner's enhanced version
- ✅ **Apple Music Support**: gamdl with full M4A support
- ✅ **YouTube Music Support**: yt-dlp with premium quality extraction
- ✅ **AI Mood Detection**: librosa-powered mood analysis
- ✅ **Smart Playlists**: Intelligent recommendation system

**🎯 User Experience Enhancements:**
- ✅ **Zero Configuration**: Works out-of-the-box with intelligent defaults
- ✅ **Cross-Platform**: Perfect compatibility on Windows, macOS, and Linux
- ✅ **Multiple Launchers**: Batch files, PowerShell scripts, and shell scripts
- ✅ **Desktop Integration**: Optional desktop shortcuts and shell aliases
- ✅ **Rollback Support**: Easy uninstall and cleanup if needed

### 🆕 NEW Installation Options & Features

```bash
# Standard installation (recommended for most users)
python install_auto.py

# Install with global command access (use 'treta' from anywhere)
python install_auto.py --global-install

# Force reinstall everything (if you encounter issues)
python install_auto.py --force-reinstall

# Speed up installation by skipping optional packages
python install_auto.py --skip-optional

# Verbose logging for troubleshooting
python install_auto.py --verbose

# All options combined for power users
python install_auto.py --global-install --verbose
```

### 🩺 Installation Health Check

After installation, verify everything works:

```bash
# Comprehensive health check
python test_installation.py

# Verbose diagnostics
python test_installation.py --verbose

# Auto-fix simple issues
python test_installation.py --fix-issues
```

### 🌍 Global Access Setup

Want to use `treta` command from anywhere? Run the global setup:

```bash
# Add global command access
python setup_global.py

# Add desktop shortcuts
python setup_global.py --desktop

# Add shell aliases
python setup_global.py --shell-alias

# Remove global access
python setup_global.py --uninstall
```

### 🏆 Why Choose Treta's Auto-Installer?

| Traditional Setup | 😴 | Treta Auto-Installer v2.0 | 🚀 |
|-------------------|----|-----------------------------|-----|
| Manual repo download | 📥 | **Auto-downloads latest repo** | ✅ |
| Manual Python setup | ❌ | **Auto-detects & installs Python** | ✅ |
| Dependency conflicts | 😵 | **Smart conflict resolution** | ✅ |
| Missing FFmpeg errors | 💥 | **Auto-downloads FFmpeg** | ✅ |
| Complex PATH setup | 🤯 | **Global command installation** | ✅ |
| Cryptic error messages | 😖 | **Beautiful progress & clear errors** | ✅ |
| Hours of troubleshooting | ⏰ | **2 minutes to working setup** | ⚡ |
| **Works from repo only** | 📁 | **Works from anywhere** | 🌍 |

> **💪 Result**: Go from zero to downloading your favorite music in under 2 minutes, with a beautiful installation experience that works from any directory!
- ✅ Downloads and sets up FFmpeg
- ✅ Installs Treta as a global command
- ✅ Guides you through service authentication
- ✅ Ready to use in under 2 minutes!

### 🐧 Linux/macOS (Automatic Setup)

```bash
# Download and run the auto-installer
curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install.sh | bash
```

### 📦 Manual Installation (If needed)

<details>
<summary>Click to expand manual installation steps</summary>

```bash
# 1. Clone the repository
git clone https://github.com/avinaxhroy/treta.git
cd treta

# 2. Run the local auto-installer
python install_auto.py

# 3. Follow the interactive setup
```

</details>

---

## 🌟 Features Overview

### 🎵 **Multi-Platform Downloads**
| Service | Quality | Format | Requirements |
|---------|---------|--------|--------------|
| **Spotify** | FLAC/320kbps | FLAC/OGG | Premium Account |
| **Apple Music** | AAC 256kbps | M4A/AAC | Active Subscription |
| **YouTube Music** | Up to FLAC | FLAC/WEBM | Free (No account needed) |

### 🚀 **Smart Features**
- **🧠 AI Mood Detection**: Automatically categorize music by mood and energy
- **🔄 Smart Duplicate Detection**: Never download the same song twice
- **📊 Download Statistics**: Track your library growth and analytics
- **🎯 Intelligent Queue**: Generate playlists based on mood and preferences
- **⚡ Batch Downloads**: Process multiple URLs simultaneously
- **🔐 Secure Authentication**: Encrypted credential storage

### 💎 **Quality & Organization**
- **🎧 Premium Audio Quality**: FLAC, 320kbps, AAC 256kbps
- **📁 Smart Organization**: Auto-sorted by service/artist/album
- **🖼️ Rich Metadata**: Album art, lyrics, complete tags
- **🎼 Multiple Formats**: Support for all major audio formats
- **📱 Cross-Platform**: Windows, macOS, Linux support

---

## 🎯 Quick Start (After Installation)

### 1️⃣ **Launch Treta**
```bash
treta
```
*Opens interactive menu with all options*

### 2️⃣ **Download Your First Song**
```bash
# Just paste any music URL!
treta download url "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
treta download url "https://music.apple.com/album/nevermind/1440783608"
treta download url "https://music.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 3️⃣ **Batch Download Multiple Songs**
```bash
# Multiple URLs at once
treta download url "url1" "url2" "url3"

# Or from a text file
treta download batch --file urls.txt
```

---

## 📋 Complete Command Reference

### 🎵 **Download Commands**

```bash
# Single downloads
treta download url "https://spotify.com/track/..."
treta download url "https://music.apple.com/album/..."
treta download url "https://music.youtube.com/watch?v=..."

# Batch downloads
treta download url "url1" "url2" "url3"
treta download batch --file urls.txt

# Search and download
treta download search --query "artist song name"
treta download album --name "Album Name" --artist "Artist"
```

### 🔐 **Authentication Setup**

```bash
# Setup service authentication (interactive)
treta auth add --service spotify
treta auth add --service apple

# Check authentication status
treta auth status

# Remove authentication
treta auth remove --service spotify
```

### 🎭 **Mood & Smart Features**

```bash
# Analyze mood of your library
treta mood analyze

# Create mood-based playlists
treta mood playlist --mood "energetic" --count 20
treta mood playlist --mood "chill" --count 15

# Smart queue management
treta queue add-by-mood "happy" --count 10
treta queue add-by-artist "Artist Name"
treta queue play
```

### 📊 **Statistics & Analytics**

```bash
# View library statistics
treta stats overview
treta stats artists --top 10
treta stats mood-distribution

# Detailed artist statistics
treta stats artist --name "Artist Name"

# Download history
treta stats downloads --recent 30
```

### ⚙️ **System & Configuration**

```bash
# System status and health check
treta status

# Show comprehensive user guide
treta guide

# Show usage examples
treta examples

# Update Treta
treta update
```

---

## 🎨 Advanced Usage Examples

### 🎵 **Downloading Full Discographies**

```bash
# Download entire artist catalog
treta artist download --name "Pink Floyd" --albums all

# Download top tracks only
treta artist download --name "The Beatles" --top 20

# Download specific albums
treta album download --artist "Queen" --album "A Night at the Opera"
```

### 🎭 **Mood-Based Music Management**

```bash
# Create different mood playlists
treta mood create-playlist --name "Workout" --energy high --tempo fast
treta mood create-playlist --name "Study" --energy low --focus high
treta mood create-playlist --name "Party" --energy high --valence high

# Discover new music by mood
treta mood discover --mood "melancholic" --limit 10
```

### 📊 **Analytics & Insights**

```bash
# Generate detailed reports
treta analytics generate --type "monthly-report"
treta analytics mood-trends --period "last-year"
treta analytics listening-patterns --export csv

# Find least played tracks
treta analytics underplayed --limit 20
```

### 🔄 **Automation & Scheduling**

```bash
# Setup auto-download for new releases
treta auto follow-artist --name "Artist Name"
treta auto check-releases --frequency daily

# Bulk operations
treta bulk download --playlist-file playlists.txt
treta bulk organize --by-mood
treta bulk tag-update --source musicbrainz
```

---

## 🎵 Music Quality & Formats

### 📻 **Spotify Downloads**
- **Quality**: Up to FLAC (Premium required)
- **Fallback**: 320kbps OGG (Premium), 160kbps (Free)
- **Metadata**: Complete tags, lyrics, album art
- **Organization**: `downloads/spotify/artist/album/`

### 🍎 **Apple Music Downloads**
- **Quality**: AAC 256kbps (High Quality)
- **Format**: M4A with rich metadata
- **Features**: Spatial Audio info, complete artwork
- **Organization**: `downloads/apple/artist/album/`

### 📺 **YouTube Music Downloads**
- **Quality**: Up to FLAC (Best available)
- **Formats**: FLAC, WEBM, MP4
- **Advantage**: No subscription required
- **Organization**: `downloads/youtube/artist/album/`

---

## 🧠 AI-Powered Features

### 🎭 **Mood Detection System**

Treta uses advanced AI to analyze your music and categorize it:

| Mood Category | Description | Energy Level | Use Case |
|---------------|-------------|--------------|----------|
| **Energetic** | High-energy, intense tracks | High | Workouts, motivation |
| **Happy** | Upbeat, positive vibes | Medium-High | Daily activities, parties |
| **Chill** | Relaxed, laid-back | Low-Medium | Study, relaxation |
| **Melancholic** | Emotional, introspective | Low | Reflection, evening |
| **Romantic** | Love songs, intimate | Variable | Date nights, emotions |
| **Intense** | Powerful, dramatic | High | Focus, high-energy tasks |
| **Calm** | Peaceful, soothing | Low | Sleep, meditation |
| **Upbeat** | Cheerful, lively | Medium-High | Morning, positive vibes |

### 🎯 **Smart Recommendations**

```bash
# Get recommendations based on listening history
treta recommend similar --to "Song Name"
treta recommend mood --based-on "current-listening"
treta recommend discover --genre "alternative rock"
```

---

## ⚙️ Configuration & Customization

### 📁 **Directory Structure**

```
Treta/
├── downloads/           # Downloaded music files
│   ├── spotify/        # Spotify downloads
│   ├── apple/          # Apple Music downloads
│   └── youtube/        # YouTube Music downloads
├── data/               # Application data
│   ├── downloads.db    # SQLite database
│   └── auth/          # Encrypted credentials
├── config/             # Configuration files
└── logs/              # Application logs
```

### 🔧 **Environment Variables**

```bash
# Custom paths
export TRETA_DOWNLOAD_DIR="/path/to/downloads"
export TRETA_DATA_DIR="/path/to/data"

# Quality settings
export TRETA_SPOTIFY_QUALITY="FLAC"
export TRETA_APPLE_QUALITY="256"
export TRETA_YOUTUBE_QUALITY="best"

# Behavior settings
export TRETA_AUTO_ORGANIZE="true"
export TRETA_DUPLICATE_ACTION="skip"
export TRETA_LOG_LEVEL="INFO"
```

### ⚡ **Performance Tuning**

```bash
# Advanced configuration
treta config set max-concurrent-downloads 4
treta config set retry-attempts 3
treta config set download-timeout 300
treta config set analysis-threads 2
```

---

## 🔧 Troubleshooting & Support

### 🩺 **Quick Health Check**

If you experience any issues, start with our comprehensive health check:

```bash
# Run the installation health check
python test_installation.py

# Verbose diagnostics with auto-fix
python test_installation.py --verbose --fix-issues

# Fresh reinstall if needed
python install_auto.py --force-reinstall --verbose
```

### 🚨 **Common Issues & Solutions**

<details>
<summary><b>❌ Installation Failed</b></summary>

```bash
# Try the enhanced auto-installer with verbose logging
python install_auto.py --force-reinstall --verbose

# Or run the health check for specific diagnostics
python test_installation.py --verbose --fix-issues

# For Windows permission issues, run as Administrator
# For Unix permission issues: chmod +x install_easy.sh
```
</details>

<details>
<summary><b>❌ Authentication Failed</b></summary>

```bash
# Re-authenticate with service
treta auth remove --service spotify
treta auth add --service spotify

# Check authentication status
treta auth status
```
</details>

<details>
<summary><b>❌ Download Failed</b></summary>

```bash
# Check system status
treta status

# Retry with verbose logging
treta download url "url" --verbose

# Update dependencies
treta update --check-deps
```
</details>

<details>
<summary><b>❌ FFmpeg Not Found</b></summary>

```bash
# Auto-install FFmpeg
treta install ffmpeg

# Or manually specify path
treta config set ffmpeg-path "/path/to/ffmpeg"
```
</details>

<details>
<summary><b>❌ Permission Issues</b></summary>

```bash
# Fix permissions (Linux/macOS)
chmod +x treta
sudo chown -R $USER:$USER ~/.treta

# Windows: Run as Administrator
```
</details>

### 📞 **Getting Help**

```bash
# Built-in help system
treta help
treta command --help
treta guide

# System diagnostics
treta diagnostics
treta logs --tail 50

# Community support
treta support --create-issue
```

---

## 🚀 Advanced Features

### 🔄 **Automation & Scripting**

```bash
# Setup automated workflows
treta automation create --name "daily-new-music" \
  --trigger "new-releases" \
  --action "download" \
  --artists-file followed.txt

# Batch processing
treta batch process --script download-playlists.py
treta batch analyze --directory "downloads/" --mood-update
```

### 🎮 **Plugin System**

```bash
# Install community plugins
treta plugins install lastfm-scrobbler
treta plugins install discord-integration
treta plugins install plex-sync

# Create custom plugins
treta plugins create --template downloader --name "custom-service"
```

### 📊 **Data Export & Import**

```bash
# Export your library data
treta export library --format json --file my-library.json
treta export playlists --format m3u --directory exports/

# Import from other services
treta import spotify-playlists --file playlists.json
treta import itunes-library --file "iTunes Music Library.xml"
```

---

## 🏗️ Development & Contribution

### 🛠️ **Development Setup**

```bash
# Clone repository
git clone https://github.com/avinaxhroy/treta.git
cd treta

# Setup development environment
python dev-setup.py

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Code formatting
black . && isort .

# Type checking
mypy treta/
```

### 🧪 **Testing**

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Performance testing
pytest tests/performance/ --benchmark
```

### 📝 **Contributing Guidelines**

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

---

## ⚖️ Legal & Compliance

### 📜 **Important Legal Notice**

**Treta is designed for personal use only. Users must:**

- ✅ Own active subscriptions to services they download from
- ✅ Comply with all terms of service
- ✅ Respect copyright and intellectual property rights
- ✅ Use downloads for personal, non-commercial purposes only
- ✅ Understand that circumventing DRM may violate local laws

**The developers are not responsible for misuse of this software.**

### 🛡️ **Privacy & Security**

- 🔐 **Local Storage**: All data stays on your device
- 🔒 **Encrypted Credentials**: Authentication tokens encrypted at rest
- 🚫 **No Telemetry**: We don't collect any usage data
- 🏠 **Offline Capable**: Core features work without internet

---

## 🙏 Acknowledgments & Credits

### 🎵 **Core Technologies**
- **[Zotify](https://github.com/DraftKinner/zotify)** - Spotify downloading engine
- **[GAMDL](https://github.com/glomatico/gamdl)** - Apple Music downloading functionality
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - YouTube downloading capabilities
- **[librosa](https://librosa.org)** - Audio analysis and processing
- **[Typer](https://typer.tiangolo.com)** - CLI framework
- **[Rich](https://rich.readthedocs.io)** - Beautiful terminal interface

### 🌟 **Special Thanks**
- All contributors and beta testers
- The open-source music community
- Everyone who provided feedback and bug reports

### 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

## 🎵 Start Your Musical Journey Today!

### ⚡ Three Ways to Get Started:
1. **🏆 Ultimate Easy**: Run one PowerShell/bash command from anywhere (auto-downloads everything)
2. **🎯 Easy Mode**: Download and double-click `install_easy.bat` (Windows) or `./install_easy.sh` (Unix)  
3. **⚙️ Advanced**: Clone repo and run `python install_auto.py --global-install`

**All methods give you the same beautiful, error-free installation experience in under 2 minutes!**

#### Windows (choose one):
```powershell
# Option 1: Remote installer (works from anywhere)
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.ps1 | iex"

# Option 2: Download repo first, then double-click install_easy.bat
```

#### Unix/Linux/macOS (choose one):
```bash
# Option 1: Remote installer (works from anywhere)  
curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash

# Option 2: Download repo first, then run ./install_easy.sh
```

### [⬇️ Download Treta](https://github.com/avinaxhroy/treta/releases/latest) | [📖 Documentation](https://docs.treta.app) | [💬 Community(Coming soon)]() | [🐛 Report Issues](https://github.com/avinaxhroy/treta/issues)

**Made with ❤️ by music lovers, for music lovers**

*Happy downloading! 🎧*

</div>