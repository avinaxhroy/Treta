# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-21

### 🎉 Initial Release

#### Added
- **Multi-platform music downloading** from Spotify, Apple Music, and YouTube Music
- **High-quality audio** with FLAC support for Spotify and YouTube, AAC for Apple Music
- **Smart authentication** system with secure credential storage
- **Intelligent duplicate detection** to avoid re-downloading existing tracks
- **Mood-based playlist generation** using AI analysis
- **Artist and download statistics** tracking
- **Rich command-line interface** with progress bars and beautiful output
- **Automatic file organization** by artist and source
- **Comprehensive database** tracking all downloads
- **Cross-platform support** (Windows, macOS, Linux)

#### Features
- Download individual tracks or entire albums
- Batch downloading of multiple URLs
- Automatic metadata embedding
- Album artwork downloading
- Real-time download progress
- Authentication status checking
- Download history and statistics
- Mood detection for smart queuing

#### Supported Services
- **Spotify** (Premium subscription required)
- **Apple Music** (Subscription required)  
- **YouTube Music** (Free tier supported)

#### Command Line Interface
- `treta download url` - Download from URLs
- `treta auth` - Manage service authentication
- `treta queue` - Smart playlist management
- `treta stats` - View download statistics
- `treta mood` - Mood-based recommendations

### Technical Details
- Built with Python 3.8+ support
- Uses typer for CLI framework
- Rich library for beautiful terminal output
- SQLite database for local storage
- FFmpeg integration for audio processing
- Secure credential management with cryptography

---

*For installation instructions, see INSTALL.md*
*For usage examples, see README.md*
