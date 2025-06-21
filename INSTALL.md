# Installation Guide

## Quick Start

1. **Install Treta**:
   ```bash
   pip install treta
   ```

2. **Run Treta**:
   ```bash
   treta --help
   ```

## From Source

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Treta**:
   ```bash
   python treta.py --help
   ```

## First Time Setup

### Authentication Setup
Before downloading, you'll need to authenticate with your music services:

```bash
# For Spotify
treta auth add --service spotify

# For Apple Music  
treta auth add --service apple
```

### Download Music
```bash
# Download from any supported URL
treta download url "https://open.spotify.com/track/..."
treta download url "https://music.apple.com/album/..."
treta download url "https://music.youtube.com/watch?v=..."

# Multiple URLs at once
treta download url "url1" "url2" "url3"
```

## Requirements

- Python 3.8 or higher
- ffmpeg (for audio processing)
- Active subscriptions to music services you want to download from

## Platform Support

- Windows
- macOS  
- Linux

## Troubleshooting

If you encounter issues:

1. **Check authentication**: `treta auth status`
2. **Verify subscriptions**: Ensure you have active premium subscriptions
3. **Update dependencies**: `pip install -r requirements.txt --upgrade`

For more help, see the README.md file.
