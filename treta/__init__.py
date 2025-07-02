#!/usr/bin/env python3
"""
Treta - Music Downloader and Library Manager
Main CLI entry point.

HOW TO RUN THIS APPLICATION:
---------------------------
Option 1 - Run with Python directly:
   python treta.py [command] [options]
   Example: python treta.py download url https://open.spotify.com/track/...

Option 2 - Use wrapper scripts:
   - PowerShell: .\treta.ps1 [command] [options]
   - CMD: treta.bat [command] [options]

Option 3 - Install as a package:
   pip install -e .
   Then: treta [command] [options]
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util

# Auto-activate virtual environment if it exists and we're not already in it
def ensure_venv():
    """Automatically activate virtual environment if available and needed."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return  # Already in a virtual environment
    
    script_dir = Path(__file__).parent
    
    # Check for common virtual environment directories
    for venv_name in ['.venv', 'venv', 'env']:
        venv_path = script_dir / venv_name
        if venv_path.exists():
            if sys.platform == "win32":
                activate_script = venv_path / "Scripts" / "activate.bat"
                python_exe = venv_path / "Scripts" / "python.exe"
            else:
                activate_script = venv_path / "bin" / "activate"
                python_exe = venv_path / "bin" / "python"
            
            if python_exe.exists():
                # Re-run this script with the venv Python
                try:
                    result = subprocess.run([str(python_exe)] + sys.argv, 
                                          cwd=script_dir, 
                                          check=False)
                    sys.exit(result.returncode)
                except Exception:
                    # If venv activation fails, continue with system Python
                    break

# Only activate venv if we're running this script directly
if __name__ == "__main__":
    ensure_venv()

# Import required modules
import typer
from pathlib import Path
from typing import Optional, List
import time

# Import rich for better formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Check for zotify availability
try:
    import zotify
    ZOTIFY_AVAILABLE = True
except ImportError:
    ZOTIFY_AVAILABLE = False

# Initialize console for better output formatting
if RICH_AVAILABLE:
    console = Console()
else:
    # Provide a dummy console with print method for non-rich environments
    class DummyConsole:
        def print(self, *args, **kwargs):
            print(*args)
        def input(self, prompt):
            return input(prompt.replace("[bold cyan]", "").replace("[/bold cyan]", ""))
    
    console = DummyConsole()

# Always initialize Typer app at module level (required for entry point)
app = typer.Typer(
    name="treta",
    help="🎵 Treta - Music Downloader and Library Manager",
    add_completion=False,
    no_args_is_help=True
)

# Setup function to configure the app
def setup_app():
    """Configure the Typer app with commands and sub-applications."""
    try:
        # Import configuration and logging
        from core.config import config
        from core.logging_config import setup_logging, get_logger
        
        # Import CLI modules
        from cli.download import download_app
        from cli.auth import auth_app
        from cli.mood import mood_app
        from cli.stats import stats_app
        from cli.queue import queue_app
        from cli.artist import artist_app
        
        # Add sub-applications
        app.add_typer(download_app, name="download", help="Download music from various sources")
        app.add_typer(auth_app, name="auth", help="Manage authentication for music services")
        app.add_typer(mood_app, name="mood", help="Analyze and manage music moods")
        app.add_typer(stats_app, name="stats", help="View download and listening statistics")
        app.add_typer(queue_app, name="queue", help="Manage download queue")
        app.add_typer(artist_app, name="artist", help="Artist-specific operations")
        
        # Add version command
        @app.command()
        def version():
            """Show Treta version information."""
            if RICH_AVAILABLE:
                console.print(Panel(
                    "[bold cyan]Treta Music Downloader[/bold cyan]\n"
                    "Version: 1.2.0\n"
                    "Python: " + sys.version.split()[0] + "\n"
                    f"Rich UI: {'✓' if RICH_AVAILABLE else '✗'}\n"
                    f"Zotify: {'✓' if ZOTIFY_AVAILABLE else '✗'}",
                    title="🎵 Version Info",
                    border_style="cyan"
                ))
            else:
                print("Treta Music Downloader v1.2.0")
                print(f"Python: {sys.version.split()[0]}")
                print(f"Rich UI: {'Available' if RICH_AVAILABLE else 'Not Available'}")
                print(f"Zotify: {'Available' if ZOTIFY_AVAILABLE else 'Not Available'}")
        
        # Add initialization command
        @app.command()
        def init():
            """Initialize Treta workspace and database."""
            from db.manager import DatabaseManager
            
            try:
                console.print("[bold green]Initializing Treta workspace...[/bold green]")
                
                # Initialize database
                db = DatabaseManager()
                db.initialize_database()
                
                # Create directories
                downloads_dir = Path("downloads")
                downloads_dir.mkdir(exist_ok=True)
                (downloads_dir / "spotify").mkdir(exist_ok=True)
                (downloads_dir / "apple").mkdir(exist_ok=True)
                (downloads_dir / "youtube").mkdir(exist_ok=True)
                
                console.print("[bold green]✓[/bold green] Treta workspace initialized successfully!")
                console.print(f"[dim]Database: {db.db_path}[/dim]")
                console.print(f"[dim]Downloads: {downloads_dir.absolute()}[/dim]")
                
            except Exception as e:
                console.print(f"[bold red]✗[/bold red] Failed to initialize workspace: {str(e)}")
                raise typer.Exit(1)
        
        # Add guide command
        @app.command()
        def guide():
            """Show a detailed guide on how to use Treta."""
            guide_text = """
# Treta Music Downloader Guide

## Getting Started

1. **Initialize your workspace:**
   ```
   treta init
   ```

2. **Set up authentication for services:**
   ```
   treta auth setup spotify
   treta auth setup apple
   ```

## Downloading Music

### From URLs:
```
treta download url "https://open.spotify.com/track/..."
treta download url "https://music.apple.com/album/..."
treta download url "https://music.youtube.com/watch?v=..."
```

### Batch download from file:
```
treta download batch urls.txt
```

### Download entire albums:
```
treta download url --album "https://open.spotify.com/album/..."
```

## Queue Management

```
treta queue add "https://open.spotify.com/track/..."
treta queue list
treta queue download
```

## Statistics and Analytics

```
treta stats overview
treta mood analyze
```

For more help on any command, use: `treta [command] --help`
            """
            
            if RICH_AVAILABLE:
                console.print(Markdown(guide_text))
            else:
                print(guide_text)
        
        # Add examples command
        @app.command()
        def examples():
            """Show command examples for common use cases."""
            examples_text = """
# Common Treta Usage Examples

## Single Track Downloads
```bash
# Spotify track
treta download url "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"

# Apple Music track  
treta download url "https://music.apple.com/us/song/example/123456"

# YouTube Music
treta download url "https://music.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Album Downloads
```bash
# Download entire Spotify album
treta download url --album "https://open.spotify.com/album/4m2880jivSbbyEGAKfITCa"

# Download to specific directory
treta download url --output ~/Music/Albums "https://open.spotify.com/album/..."
```

## Batch Operations
```bash
# Download multiple URLs from file
treta download batch my_playlist.txt

# Add multiple tracks to queue
treta queue add-batch urls.txt
treta queue download
```

## Authentication
```bash
# Setup Spotify (required for Spotify downloads)
treta auth setup spotify

# Check authentication status
treta auth status
```
            """
            
            if RICH_AVAILABLE:
                console.print(Markdown(examples_text))
            else:
                print(examples_text)
        
        # Add status command
        @app.command()
        def status():
            """Show Treta system status."""
            if RICH_AVAILABLE:
                # Check various system components
                python_version = sys.version.split()[0]
                
                # Check if ffmpeg is available
                ffmpeg_available = False
                try:
                    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                    ffmpeg_available = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
                
                # Check if yt-dlp is available
                ytdlp_available = False
                try:
                    import yt_dlp
                    ytdlp_available = True
                except ImportError:
                    pass
                
                status_panel = Panel(
                    f"[bold green]System Status[/bold green]\n\n"
                    f"Python: {python_version} {'✓' if sys.version_info >= (3, 8) else '✗'}\n"
                    f"Rich UI: {'✓' if RICH_AVAILABLE else '✗'}\n"
                    f"Zotify (Spotify): {'✓' if ZOTIFY_AVAILABLE else '✗'}\n"
                    f"yt-dlp (YouTube): {'✓' if ytdlp_available else '✗'}\n"
                    f"FFmpeg: {'✓' if ffmpeg_available else '✗'}\n\n"
                    f"[dim]Working Directory: {Path.cwd()}[/dim]\n"
                    f"[dim]Script Location: {Path(__file__).parent}[/dim]",
                    title="🎵 Treta Status",
                    border_style="green" if all([RICH_AVAILABLE, ZOTIFY_AVAILABLE, ytdlp_available]) else "yellow"
                )
                
                console.print(status_panel)
            else:
                print("Treta System Status:")
                print(f"Python: {sys.version.split()[0]}")
                print(f"Rich UI: {'Available' if RICH_AVAILABLE else 'Not Available'}")
                print(f"Zotify: {'Available' if ZOTIFY_AVAILABLE else 'Not Available'}")
        
        # Main callback for global options
        @app.callback()
        def main(
            verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
            debug: bool = typer.Option(False, "--debug", help="Enable debug logging")
        ):
            """
            🎵 Treta - Music Downloader and Library Manager
            
            A powerful CLI tool for downloading and managing music from various sources.
            """
            # Setup logging based on verbosity
            if debug:
                setup_logging("DEBUG")
            elif verbose:
                setup_logging("INFO")
            else:
                setup_logging("WARNING")
        
        return True
        
    except ImportError as e:
        # If core modules fail to import, show helpful error
        if not ZOTIFY_AVAILABLE:
            console.print("\n⚠️  [yellow]Zotify not found. Spotify downloads will not work.[/yellow]")
            console.print("\n[bold]Recommended installation methods:[/bold]")
            console.print("Option 1: Install Git first (recommended)")
            console.print("   - Run: install_git.bat (CMD) or .\\install_git.ps1 (PowerShell)")
            console.print("   - Then: pip install git+https://github.com/zotify-dev/zotify.git")
            console.print("\nOption 2: Install without Git")
            console.print("   - Run: python install_zotify_no_git.py (guided installation)\n")
        
        console.print(f"[red]Import error: {str(e)}[/red]")
        console.print("[yellow]Some features may not be available.[/yellow]")
        return False

# Setup the app when module is imported
setup_app()

# Entry point for direct script execution
if __name__ == "__main__":
    app()
