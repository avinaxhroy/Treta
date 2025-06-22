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

[🚀 **Auto-Install Now**](#-one-click-installation--setup) • [📖 **Documentation**](#-complete-command-reference) • [💬 **Community (Coming Soon)**]() • [🐛 **Issues**](https://github.com/avinaxhroy/treta/issues)

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


## ⚡ One-Click Installation & Setup

### 🖥️ Windows (Automatic Setup)

Simply run our auto-installer that handles **EVERYTHING** for you:

```powershell
# Download and run the auto-installer
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install.ps1 | iex"
```

**What the auto-installer does:**
- ✅ Installs Python (if not present)
- ✅ Creates isolated virtual environment
- ✅ Installs all dependencies automatically
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

### 🚨 **Common Issues & Solutions**

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

### [⬇️ Download Treta](https://github.com/avinaxhroy/treta/releases/latest) | [📖 Documentation](https://docs.treta.app) | [💬 Community(Coming soon)]() | [🐛 Report Issues](https://github.com/avinaxhroy/treta/issues)

**Made with ❤️ by music lovers, for music lovers**

*Happy downloading! 🎧*

</div>
