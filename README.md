# Treta Music Downloader

<div align="center">

[![Release](https://img.shields.io/github/v/release/avinaxhroy/treta?style=flat-square)](https://github.com/avinaxhroy/treta/releases)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square)](https://python.org)
[![License](https://img.shields.io/github/license/avinaxhroy/treta?style=flat-square)](LICENSE)

A feature-rich music downloader supporting Spotify, Apple Music, and YouTube Music with AI-powered mood detection and automated setup.

[🚀 **Quick Install**](#installation) • [📖 **Documentation**](#usage) • [🐛 **Issues**](https://github.com/avinaxhroy/treta/issues)

</div>

## Disclaimer

**Educational and personal use only.** Users must comply with platform terms of service and copyright laws. Requires valid subscriptions for premium services. The developers are not responsible for misuse of this software.

## Installation

### One-Click Installation

**Windows:**
```powershell
# Remote installer (recommended)
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.ps1 | iex"
```

**Linux/macOS:**
```bash
# Remote installer (recommended)
curl -fsSL https://raw.githubusercontent.com/avinaxhroy/treta/main/install_remote.sh | bash
```

### Manual Installation

```bash
# Clone and install
git clone https://github.com/avinaxhroy/treta.git
cd treta
python install_auto.py --global-install
```

The installer automatically handles:
- Python detection and installation
- Virtual environment setup
- Dependency management
- FFmpeg installation
- Global command setup

## Features

### Supported Services
| Service | Quality | Format | Requirements |
|---------|---------|--------|--------------|
| **Spotify** | FLAC/320kbps | FLAC/OGG | Premium Account |
| **Apple Music** | AAC 256kbps | M4A | Active Subscription |
| **YouTube Music** | Up to FLAC | FLAC/WEBM | None |

### Key Features
- **AI Mood Detection**: Automatic music categorization
- **Smart Organization**: Auto-sorted by service/artist/album
- **Batch Downloads**: Process multiple URLs simultaneously
- **Quality Control**: Premium audio formats with metadata
- **Cross-Platform**: Windows, macOS, Linux support

## Usage

### Basic Commands

```bash
# Launch interactive menu
treta

# Download single track
treta download url "https://open.spotify.com/track/..."

# Download multiple tracks
treta download url "url1" "url2" "url3"

# Download from file
treta download batch --file urls.txt
```

### Authentication

```bash
# Setup service authentication
treta auth add --service spotify
treta auth add --service apple

# Check authentication status
treta auth status
```

### Mood Analysis

```bash
# Analyze mood of library
treta mood analyze

# Create mood-based playlist
treta mood playlist --mood "energetic" --count 20
```

### Statistics

```bash
# View library statistics
treta stats overview

# View top artists
treta stats artists --top 10
```

## Directory Structure

```
downloads/
├── spotify/        # Spotify downloads
├── apple/          # Apple Music downloads
└── youtube/        # YouTube Music downloads
```

## Troubleshooting

### Health Check
```bash
# Run diagnostics
python test_installation.py --verbose

# Auto-fix issues
python test_installation.py --fix-issues
```

### Common Issues

**Installation Failed:**
```bash
python install_auto.py --force-reinstall --verbose
```

**Authentication Failed:**
```bash
treta auth remove --service spotify
treta auth add --service spotify
```

**Global Command Not Found:**
Restart your terminal after installation, or manually add the installation directory to your PATH.

## Contributing

### Development Setup
```bash
git clone https://github.com/avinaxhroy/treta.git
cd treta
python install_auto.py --verbose
pip install -r requirements-dev.txt
```

### Running Tests
```bash
pytest tests/ -v
```

### Contributing Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Acknowledgments

**Core Technologies:**
- [Zotify](https://github.com/DraftKinner/zotify) - Spotify downloading
- [GAMDL](https://github.com/glomatico/gamdl) - Apple Music downloading
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [librosa](https://librosa.org) - Audio analysis
- [Typer](https://typer.tiangolo.com) - CLI framework

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for music lovers**

[Download](https://github.com/avinaxhroy/treta/releases) • [Report Issues](https://github.com/avinaxhroy/treta/issues)

</div>

## Features

### Supported Services
| Service | Quality | Format | Requirements |
|---------|---------|--------|--------------|
| **Spotify** | FLAC/320kbps | FLAC/OGG | Premium Account |
| **Apple Music** | AAC 256kbps | M4A | Active Subscription |
| **YouTube Music** | Up to FLAC | FLAC/WEBM | None |

### Key Features
- **AI Mood Detection**: Automatic music categorization
- **Smart Organization**: Auto-sorted by service/artist/album
- **Batch Downloads**: Process multiple URLs simultaneously
- **Quality Control**: Premium audio formats with metadata
- **Cross-Platform**: Windows, macOS, Linux support

## Usage

### Basic Commands

```bash
# Launch interactive menu
treta

# Download single track
treta download url "https://open.spotify.com/track/..."

# Download multiple tracks
treta download url "url1" "url2" "url3"

# Download from file
treta download batch --file urls.txt
```

### Authentication

```bash
# Setup service authentication
treta auth add --service spotify
treta auth add --service apple

# Check authentication status
treta auth status
```

### Mood Analysis

```bash
# Analyze mood of library
treta mood analyze

# Create mood-based playlist
treta mood playlist --mood "energetic" --count 20
```

### Statistics

```bash
# View library statistics
treta stats overview

# View top artists
treta stats artists --top 10
```

## Directory Structure

```
downloads/
├── spotify/        # Spotify downloads
├── apple/          # Apple Music downloads
└── youtube/        # YouTube Music downloads
```

## Troubleshooting

### Health Check
```bash
# Run diagnostics
python test_installation.py --verbose

# Auto-fix issues
python test_installation.py --fix-issues
```

### Common Issues

**Installation Failed:**
```bash
python install_auto.py --force-reinstall --verbose
```

**Authentication Failed:**
```bash
treta auth remove --service spotify
treta auth add --service spotify
```

**Global Command Not Found:**
Restart your terminal after installation, or manually add the installation directory to your PATH.