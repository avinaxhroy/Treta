"""
Fixed Download CLI commands for Treta - bypasses caching issues.
Handles downloading music from Spotify, Apple Music, and YouTube Music.
"""

import typer
import re
from typing import Optional, List
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
from rich.panel import Panel
from rich.table import Table
import subprocess
import sys
import os
import glob
import re
from urllib.parse import urlparse

from core.downloader.spotify import SpotifyDownloader
from core.downloader.apple import AppleDownloader
from core.downloader.youtube import YouTubeDownloader
from core.auth_store import AuthStore
from db.manager import DatabaseManager
from db.models import Track

console = Console()

def detect_source_fixed(url: str) -> str:
    """Detect music source from URL - FIXED VERSION."""
    console.print(f"🔍 [cyan]Detecting source for: {url}[/cyan]")
    
    if "spotify.com" in url:
        console.print("✅ [green]Detected: Spotify[/green]")
        return "spotify"
    elif "music.apple.com" in url:
        console.print("✅ [green]Detected: Apple Music[/green]")
        return "apple"
    elif any(pattern in url for pattern in ["music.youtube.com", "youtube.com", "youtu.be"]):
        console.print("✅ [green]Detected: YouTube Music[/green]")
        return "youtube"
    else:
        console.print("❌ [red]Unknown source[/red]")
        return "unknown"

def _download_spotify_track_simple(url: str) -> List[Track]:
    """Download a single Spotify track using the SpotifyDownloader class with progress bar."""
    try:
        console.print("🎵 [bold blue]Starting Spotify download...[/bold blue]")
        console.print("🎼 [cyan]Quality: FLAC (Very High) | Organization: By Artist[/cyan]")
        
        # Use the proper SpotifyDownloader class
        downloader = SpotifyDownloader()
        
        # Check authentication first (before progress bar)
        if not downloader.is_authenticated():
            console.print("🔑 [yellow]Spotify authentication required[/yellow]")
            console.print("🚀 [cyan]Starting Spotify authentication setup...[/cyan]")
            try:
                result = subprocess.run([
                    sys.executable, "treta.py", "auth", "add", "--service", "spotify"
                ], cwd=os.getcwd(), capture_output=False)
                if result.returncode == 0:
                    downloader = SpotifyDownloader()  # Create fresh instance
                    if downloader.is_authenticated():
                        console.print("✅ [green]Spotify authentication successful![/green]")
                    else:
                        console.print("❌ [red]Authentication may have failed. Please verify.[/red]")
                        return []
                else:
                    console.print("❌ [red]Authentication setup was cancelled or failed.[/red]")
                    console.print("📋 [cyan]You can try again with: python treta.py auth add --service spotify[/cyan]")
                    return []
            except Exception as e:
                console.print(f"❌ [red]Auto-authentication failed: {e}[/red]")
                console.print("📋 [cyan]Please run manually: python treta.py auth add --service spotify[/cyan]")
                return []
        # Now start the progress bar for the download attempt
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("🔐 Connecting to Spotify...", total=100)
            progress.update(task, description="🔐 Authenticating with Spotify...", completed=10)
            progress.update(task, description="🔍 Processing URL...", completed=20)
            progress.update(task, description="📥 Fetching track information...", completed=30)
            progress.update(task, description="⬇️ Downloading...", completed=50)
            track = downloader.download_track(url)
            if track:
                progress.update(task, description="✅ Download completed!", completed=100)
                console.print("✅ [green]Spotify download completed successfully![/green]")
                console.print("📁 [blue]Files organized by artist in downloads/spotify/[/blue]")
                return [track]
            else:
                progress.update(task, description="❌ Download failed", completed=100)
                console.print("❌ [red]Spotify download failed[/red]")
        # If download failed, offer to refresh authentication (outside progress bar)
        console.print("🔑 [yellow]This might be due to expired credentials.[/yellow]")
        console.print("🚀 [cyan]Attempting to refresh Spotify authentication...[/cyan]")
        try:
            result = subprocess.run([
                sys.executable, "treta.py", "auth", "add", "--service", "spotify"
            ], cwd=os.getcwd(), capture_output=False)
            if result.returncode == 0:
                console.print("✅ [green]Authentication refreshed! Retrying download...[/green]")
                fresh_downloader = SpotifyDownloader()
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    console=console
                ) as progress:
                    task = progress.add_task("🔐 Connecting to Spotify...", total=100)
                    progress.update(task, description="🔐 Authenticating with Spotify...", completed=10)
                    progress.update(task, description="🔍 Processing URL...", completed=20)
                    progress.update(task, description="📥 Fetching track information...", completed=30)
                    progress.update(task, description="⬇️ Downloading...", completed=50)
                    retry_track = fresh_downloader.download_track(url)
                    if retry_track:
                        progress.update(task, description="✅ Download completed!", completed=100)
                        console.print("✅ [green]Spotify download completed successfully![/green]")
                        console.print("📁 [blue]Files organized by artist in downloads/spotify/[/blue]")
                        return [retry_track]
                    else:
                        progress.update(task, description="❌ Download failed", completed=100)
                        console.print("❌ [red]Download still failed after authentication refresh[/red]")
                        console.print("💡 [yellow]Please check your Spotify Premium subscription and network connection[/yellow]")
            else:
                console.print("❌ [red]Authentication refresh was cancelled or failed[/red]")
                console.print("📋 [cyan]You can try manually: python treta.py auth add --service spotify[/cyan]")
        except Exception as e:
            console.print(f"❌ [red]Failed to refresh authentication: {e}[/red]")
            console.print("📋 [cyan]Please run manually: python treta.py auth add --service spotify[/cyan]")
        return []
    except Exception as e:
        error_msg = str(e).lower()
        if any(keyword in error_msg for keyword in ["authentication", "credential", "login", "premium"]):
            console.print("🔑 [yellow]Authentication issue detected![/yellow]")
            console.print("📋 [cyan]Please run: python treta.py auth add --service spotify[/cyan]")
        else:
            console.print(f"❌ [red]Error during Spotify download: {e}[/red]")
        return []

def _download_youtube_track_simple(url: str) -> List[Track]:
    """Download a single YouTube Music track with progress bar."""
    try:
        console.print("🎵 [bold blue]Starting YouTube Music download...[/bold blue]")
        console.print("🎼 [cyan]Quality: FLAC (Highest) | Organization: By Artist[/cyan]")
        
        # Create artist directory structure
        downloads_dir = Path("downloads/youtube")
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to use yt-dlp for YouTube Music download with highest quality
        cmd = [
            "yt-dlp",
            "--extract-audio",
            "--audio-format", "flac",  # FLAC for highest quality
            "--audio-quality", "0",    # Best quality available
            "--output", str(downloads_dir / "%(uploader)s/%(title)s.%(ext)s"),  # Organize by artist
            "--embed-thumbnail",       # Add album art
            "--add-metadata",         # Add metadata
            "--prefer-ffmpeg",        # Use ffmpeg for best quality
            "--no-playlist",          # Single track only
            url
        ]
        
        console.print(f"🔧 [cyan]Downloading in FLAC quality...[/cyan]")        # Use rich progress bar with download progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("🔍 Starting download...", total=100)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'  # Replace problematic characters
            )
            
            # Stream output and update progress
            output_lines = []
            if process.stdout:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        line = output.strip()
                        output_lines.append(line)
                          # Update progress based on yt-dlp output
                        if '[download]' in line and '%' in line:
                            # Extract percentage from yt-dlp output
                            # Format: "[download]  50.0% of 4.5MiB at 1.2MiB/s ETA 00:03"
                            try:
                                # Find percentage in the line
                                parts = line.split()
                                for part in parts:
                                    if '%' in part:
                                        percent_str = part.replace('%', '').strip()
                                        percent = float(percent_str)
                                        # Extract speed if available
                                        speed = ""
                                        size = ""
                                        if ' at ' in line and 'iB/s' in line:
                                            speed_part = line.split(' at ')[1].split(' ')[0]
                                            speed = f"Speed: {speed_part}"
                                        if ' of ' in line and 'iB' in line:
                                            size_part = line.split(' of ')[1].split(' ')[0]
                                            size = f"Size: {size_part}"
                                        
                                        desc = f"📥 Downloading... {percent:.1f}%"
                                        if speed and size:
                                            desc += f" ({speed}, {size})"
                                        elif speed:
                                            desc += f" ({speed})"
                                        
                                        progress.update(task, description=desc, completed=min(percent, 90))
                                        break
                            except:
                                progress.update(task, description=f"📥 {line}", completed=50)
                        elif 'Extracting audio' in line:
                            progress.update(task, description="🎶 Extracting audio...", completed=95)
                        elif 'Adding metadata' in line:
                            progress.update(task, description="📝 Adding metadata...", completed=98)
                        elif 'has already been downloaded' in line:
                            progress.update(task, description="✅ Already downloaded!", completed=100)
        
        rc = process.poll()
        
        if rc == 0:
            console.print("✅ [green]YouTube Music download completed successfully![/green]")
            # Create a basic Track object
            track = Track(
                title="Downloaded YouTube Track",
                artist="Unknown Artist",
                url=url,
                source="youtube",
                file_path="downloaded"
            )
            return [track]
        else:
            console.print(f"❌ [red]YouTube Music download failed with exit code {rc}[/red]")
            console.print("💡 [yellow]Make sure yt-dlp is installed: pip install yt-dlp[/yellow]")
            return []
            
    except FileNotFoundError:
        console.print("❌ [red]yt-dlp not found. Please install it: pip install yt-dlp[/red]")
        return []
    except Exception as e:
        console.print(f"❌ [red]Error during YouTube download: {e}[/red]")
        return []

def download_track_fixed(url: str, source: Optional[str] = None) -> List[Track]:
    """Download a single track from URL - FIXED VERSION."""
    detected_source = detect_source_fixed(url)
    final_source = source or detected_source
    console.print(f"🎯 [cyan]Using source: {final_source}[/cyan]")
    
    if final_source == "spotify":
        return _download_spotify_track_simple(url)
    elif final_source == "apple":
        console.print("🍎 [green]Processing Apple Music URL...[/green]")
        console.print("🎼 [cyan]Quality: AAC 256kbps (High Quality) | Organization: By Artist[/cyan]")
        
        try:
            # Use the Apple Music downloader directly
            downloader = AppleDownloader()            # Check authentication
            if not downloader.is_authenticated():
                console.print("🔑 [yellow]Apple Music authentication required[/yellow]")
                console.print("🚀 [cyan]Starting Apple Music authentication setup...[/cyan]")
                
                try:
                    # Use subprocess to run the auth command
                    import subprocess
                    result = subprocess.run([
                        sys.executable, "treta.py", "auth", "add", "--service", "apple"
                    ], cwd=os.getcwd(), capture_output=False)
                    
                    if result.returncode == 0:
                        # Re-check authentication after setup
                        downloader = AppleDownloader()  # Create fresh instance
                        if downloader.is_authenticated():
                            console.print("✅ [green]Apple Music authentication successful![/green]")
                        else:
                            console.print("❌ [red]Authentication may have failed. Please verify.[/red]")
                            return []
                    else:
                        console.print("❌ [red]Authentication setup was cancelled or failed.[/red]")
                        console.print("📋 [cyan]You can try again with: python treta.py auth add --service apple[/cyan]")
                        return []
                        
                except Exception as e:
                    console.print(f"❌ [red]Auto-authentication failed: {e}[/red]")
                    console.print("📋 [cyan]Please run manually: python treta.py auth add --service apple[/cyan]")
                    return []
            
            # Check if already downloaded
            db_manager = DatabaseManager()
            if db_manager.is_already_downloaded(url):
                console.print("⏩ [yellow]Track already downloaded (found in database)[/yellow]")
                # Return a success indicator
                return [Track(
                    title="Already Downloaded",
                    artist="Already Downloaded", 
                    album="Already Downloaded",
                    source="apple",
                    url=url,
                    file_path="",
                    file_hash="",
                    track_id=""
                )]            # Download with progress indication
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                DownloadColumn(),
                TransferSpeedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("🍎 Starting Apple Music download...", total=100)
                progress.update(task, description="🍎 Connecting to Apple Music...", completed=10)
                
                # Create progress callback for Apple downloader
                def apple_progress_callback(description, percent):
                    progress.update(task, description=description, completed=percent)
                
                track = downloader.download_track(url, progress_callback=apple_progress_callback)
                
                if track:
                    progress.update(task, description="✅ Download completed!")
                    console.print("✅ [green]Apple Music download completed![/green]")
                    console.print("📁 [blue]Files organized by artist in downloads/apple/[/blue]")
                    return [track]
                else:
                    progress.update(task, description="❌ Download failed")
                    console.print("❌ [red]Apple Music download failed[/red]")
                    console.print("💡 [yellow]Possible reasons:[/yellow]")
                    console.print("   • Track not available in your region")
                    console.print("   • Subscription/licensing restrictions")
                    console.print("   • DRM protection preventing download")
                    console.print("   • Network connectivity issues")
                    console.print("🔄 [cyan]You could try a different track or check your Apple Music subscription[/cyan]")
                    return []
                
        except Exception as e:
            console.print(f"❌ [red]Error downloading from Apple Music: {e}[/red]")
            return []
    elif final_source == "youtube":
        return _download_youtube_track_simple(url)
    else:
        console.print(f"❌ [red]Unsupported URL: {url}[/red]")
        return []

# Alias for compatibility with main download command
_download_track_UNIQUE_NAME = download_track_fixed

# Also create the debug version that the main download expects
def _detect_source(url: str) -> str:
    """Detect music source from URL - WORKING VERSION."""
    print(f"DEBUG: _detect_source called with URL: {url}", flush=True)
    if "spotify.com" in url:
        print("DEBUG: _detect_source - Detected Spotify", flush=True)
        return "spotify"
    elif "music.apple.com" in url:
        print("DEBUG: _detect_source - Detected Apple Music", flush=True)
        return "apple"
    elif any(pattern in url for pattern in ["music.youtube.com", "youtube.com", "youtu.be"]):
        print("DEBUG: _detect_source - Detected YouTube", flush=True)
        return "youtube"
    else:
        print("DEBUG: _detect_source - Unknown source", flush=True)
        return "unknown"

# Create download app
download_app = typer.Typer(help="Download music from various sources")

@download_app.command("url")
def download_url(
    urls: List[str] = typer.Argument(..., help="Music URLs to download"),
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Force source (spotify/apple/youtube)"),
    album: bool = typer.Option(False, "--album", "-a", help="Treat URLs as albums"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
):
    """Download music from URLs."""
    console.print(Panel.fit(
        f"🎵 [bold blue]Treta Music Downloader[/bold blue]\n"
        f"📥 Downloading {len(urls)} URL(s)",
        title="Download Started"
    ))
      # Download each URL
    all_tracks = []
    for i, url in enumerate(urls, 1):
        console.print(f"\n📦 [bold cyan]Processing URL {i}/{len(urls)}[/bold cyan]")
        console.print(f"🔗 {url}")
        
        try:
            tracks = _download_track_UNIQUE_NAME(url, source)
            if tracks:
                all_tracks.extend(tracks)
                console.print(f"✅ [green]Successfully processed {len(tracks)} track(s)[/green]")
            else:
                console.print(f"⚠️  [yellow]No tracks downloaded from this URL[/yellow]")
        except Exception as e:
            console.print(f"❌ [red]Error downloading from {url}: {e}[/red]")
    
    # Final summary
    if all_tracks:
        console.print(Panel.fit(
            f"🎉 [bold green]Download Complete![/bold green]\n"
            f"📥 Downloaded {len(all_tracks)} track(s) successfully\n"
            f"📁 Check your downloads folder for the files",
            title="Success"
        ))
    else:
        console.print(Panel.fit(
            f"❌ [bold red]Download Failed[/bold red]\n"
            f"No tracks were downloaded successfully",
            title="Error"
        ))
        raise typer.Exit(1)

# Export the main function for compatibility with existing imports
url = download_url
