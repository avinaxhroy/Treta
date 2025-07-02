# 🎵 Complete Guide: Downloading an Entire Artist Catalog with Treta

## Quick Summary
Treta supports downloading entire artist catalogs from Spotify, Apple Music, and YouTube. Here are the main methods:

### Method 1: Direct Artist URL (Recommended)
```powershell
# Download entire artist catalog from Spotify
python treta.py download url "https://open.spotify.com/artist/4q3ewBCX7sLwd24euuV69X"

# Download from Apple Music
python treta.py download url "https://music.apple.com/us/artist/bad-bunny/1126808565"
```

### Method 2: Artist Command (Future Feature)
```powershell
# This feature is planned but not yet fully implemented
python treta.py artist download "Taylor Swift" --source spotify --limit 100
```

## Step-by-Step Instructions

### 1. First-Time Setup
Before downloading, ensure Treta is properly configured:

```powershell
# Initialize Treta workspace
python treta.py init

# Set up Spotify authentication (required for Spotify downloads)
python treta.py auth add --service spotify
```

### 2. Finding Artist URLs

#### Spotify Artist URLs:
1. Open Spotify (web or app)
2. Search for the artist
3. Go to the artist's main page
4. Copy the URL from the address bar
   - Format: `https://open.spotify.com/artist/[ARTIST_ID]`
   - Example: `https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02` (Taylor Swift)

#### Apple Music Artist URLs:
1. Open Apple Music (web or app)
2. Search for the artist
3. Go to the artist's main page
4. Copy the URL
   - Format: `https://music.apple.com/us/artist/[ARTIST_NAME]/[ARTIST_ID]`
   - Example: `https://music.apple.com/us/artist/taylor-swift/159260351`

### 3. Download Commands

#### Download Entire Artist Catalog from Spotify:
```powershell
# Basic download (all available albums and singles)
python treta.py download url "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"

# With verbose output to see progress
python treta.py --verbose download url "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
```

#### Download from Apple Music:
```powershell
python treta.py download url "https://music.apple.com/us/artist/taylor-swift/159260351"
```

#### Download from YouTube Music:
```powershell
# YouTube artist channel or music page
python treta.py download url "https://music.youtube.com/channel/[CHANNEL_ID]"
```

## 🎯 Popular Artist Examples

### Taylor Swift (Spotify)
```powershell
python treta.py download url "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
```

### Bad Bunny (Spotify)
```powershell
python treta.py download url "https://open.spotify.com/artist/4q3ewBCX7sLwd24euuV69X"
```

### Kendrick Lamar (Spotify)
```powershell
python treta.py download url "https://open.spotify.com/artist/2YZyLoL8N0Wb9xBt1NhZWg"
```

### Dua Lipa (Apple Music)
```powershell
python treta.py download url "https://music.apple.com/us/artist/dua-lipa/1065981054"
```

## 📁 File Organization

Downloads are automatically organized by source and artist:

```
downloads/
├── spotify/
│   ├── Taylor Swift/
│   │   ├── 1989/
│   │   │   ├── 01 - Welcome To New York.flac
│   │   │   ├── 02 - Blank Space.flac
│   │   │   └── ...
│   │   ├── folklore/
│   │   │   ├── 01 - the 1.flac
│   │   │   └── ...
│   │   └── Midnights/
│   └── Bad Bunny/
├── apple/
│   └── [Apple Music downloads]
└── youtube/
    └── [YouTube downloads]
```

## 🔧 Advanced Options

### Monitor Download Progress
```powershell
# Enable verbose output for detailed progress information
python treta.py --verbose download url "[ARTIST_URL]"

# Enable debug logging for troubleshooting
python treta.py --debug download url "[ARTIST_URL]"
```

### Manage Downloaded Music
```powershell
# View download statistics
python treta.py stats

# Get detailed artist information
python treta.py artist info "Taylor Swift"

# Follow an artist for new release notifications
python treta.py artist follow "Taylor Swift"
```

## 🚨 Important Notes

### Quality and Format
- **Spotify**: Downloads in FLAC format (highest quality) when using Zotify
- **Apple Music**: Quality depends on gamdl settings
- **YouTube**: MP3 format using yt-dlp

### Legal Considerations
- Only download music you have legal access to
- Respect artists' and platforms' terms of service
- Consider supporting artists through official purchases and streaming

### Spotify Premium Required
- Spotify downloads require a Spotify Premium subscription
- Free accounts will not work for downloading

## 🔧 Troubleshooting

### Authentication Issues
```powershell
# Refresh Spotify credentials
python treta.py auth add --service spotify

# Check authentication status
python treta.py auth status
```

### Download Failures
```powershell
# Check system status
python treta.py status

# Run with debug output
python treta.py --debug download url "[ARTIST_URL]"
```

### Missing Dependencies
```powershell
# Run the automated installer
python install_auto.py

# Or fix zotify specifically
python fix_zotify.py
```

## 📖 Examples of Complete Workflows

### Download Taylor Swift's Complete Catalog
```powershell
# 1. Set up authentication
python treta.py auth add --service spotify

# 2. Download entire catalog
python treta.py --verbose download url "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"

# 3. Follow for new releases
python treta.py artist follow "Taylor Swift"

# 4. Check what was downloaded
python treta.py artist info "Taylor Swift"
```

### Multi-Platform Download
```powershell
# Download from Spotify
python treta.py download url "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"

# Also download from Apple Music (different tracks/versions)
python treta.py download url "https://music.apple.com/us/artist/taylor-swift/159260351"

# Compare downloads
python treta.py stats
```

## ⚡ Tips for Large Downloads

1. **Start with a test**: Download a single album first to verify everything works
2. **Use verbose mode**: Monitor progress with `--verbose` flag
3. **Stable internet**: Ensure reliable connection for large downloads
4. **Disk space**: Artist catalogs can be several GB (Taylor Swift ~3-4GB)
5. **Time**: Complete artist downloads can take 30-60+ minutes depending on catalog size

## 🎵 What Gets Downloaded

When you download an artist's complete catalog, Treta will typically include:
- All studio albums
- All singles and EPs
- Compilation albums
- Live albums (if available)
- Featured tracks (depending on platform)

The exact content depends on what's available on the specific platform and the artist's catalog size.

## Next Steps

After downloading an artist's catalog:
1. Use `python treta.py artist info "Artist Name"` to see statistics
2. Create mood-based playlists with `python treta.py mood create`
3. Explore smart queues with `python treta.py queue smart`
4. Check out all available commands with `python treta.py --help`
