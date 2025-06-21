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
        # Already in a virtual environment
        return
    
    venv_path = Path(__file__).parent / '.venv'
    if venv_path.exists():
        if os.name == 'nt':  # Windows
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:  # Unix/Linux/Mac
            python_exe = venv_path / 'bin' / 'python'
        
        if python_exe.exists():
            # Re-run the script with the virtual environment Python
            cmd = [str(python_exe)] + sys.argv
            sys.exit(subprocess.call(cmd))

# Ensure we're using the virtual environment
ensure_venv()

# Initialize availability flags
RICH_AVAILABLE = False
ZOTIFY_AVAILABLE = False

try:
    # First try to import from the installed package
    from treta.cli_app import run_cli, app
    print("Using installed treta package...")
    
    # When using installed package, we still need to check for rich and zotify
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown
        from rich import box
        RICH_AVAILABLE = True
    except ImportError:
        RICH_AVAILABLE = False
    
    try:
        import zotify
        ZOTIFY_AVAILABLE = True
    except ImportError:
        ZOTIFY_AVAILABLE = False
        
    # Use the app from the installed package
    USING_INSTALLED_PACKAGE = True
    
    # FIX: Import typer for installed package mode
    import typer
    from core.logging_config import setup_logging, get_logger
except ImportError:
    # If that fails, try to use local modules
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
        
    try:
        import zotify
        ZOTIFY_AVAILABLE = True
    except ImportError:
        ZOTIFY_AVAILABLE = False
        print("\n⚠️  Zotify not found. Spotify downloads will not work.")
        print("\nRecommended installation methods:")
        print("Option 1: Install Git first (recommended)")
        print("   - Run: install_git.bat (CMD) or .\\install_git.ps1 (PowerShell)")
        print("   - Then: pip install git+https://github.com/zotify-dev/zotify.git")
        print("\nOption 2: Install without Git")
        print("   - Run: python install_zotify_no_git.py (guided installation)\n")

    from core.config import config
    from core.logging_config import setup_logging, get_logger
    
    USING_INSTALLED_PACKAGE = False

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

# Only set up the local app if we're not using the installed package
if not USING_INSTALLED_PACKAGE:    # Initialize Typer app
    app = typer.Typer(
        name="treta",
        help="🎵 Treta - Music Downloader and Library Manager",
        add_completion=False,
        no_args_is_help=True  # Show help when no command is provided
    )
    
    # Import CLI modules (no override needed - authentication handled in download logic)
    from cli.download import download_app, url as download_url_cmd
    from cli.auth import auth_app
    from cli.mood import mood_app
    from cli.stats import stats_app
    from cli.queue import queue_app
    from cli.artist import artist_app
    import cli.download

    # Add sub-applications
    app.add_typer(download_app, name="download", help="Download music from various sources")
    app.add_typer(auth_app, name="auth", help="Manage authentication for music services")
    app.add_typer(mood_app, name="mood", help="Analyze and manage music moods")
    app.add_typer(stats_app, name="stats", help="View download and listening statistics")
    app.add_typer(queue_app, name="queue", help="Manage smart music queues")
    app.add_typer(artist_app, name="artist", help="Follow artists and manage releases")

    # Add direct download command    @app.command()
    def download(
        url: str = typer.Option(..., "--url", "-u", help="URL to download from Spotify or Apple Music"),
        source: Optional[str] = typer.Option(None, "--source", "-s", help="Force source (spotify/apple)"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory")
    ):
        """Download music directly from a URL (shortcut for 'download url')."""
        # Call the download url command with the provided URL
        return download_url_cmd([url], source, False, output)

    @app.callback()
    def main(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
        debug: bool = typer.Option(False, "--debug", help="Enable debug logging")
    ):
        """
        🎵 Treta - Music Downloader and Library Manager
        
        A powerful CLI tool for downloading and managing music from Spotify and Apple Music.
        """
        # Setup logging based on verbosity
        log_level = "DEBUG" if debug else "INFO" if verbose else "WARNING"
        logger = setup_logging(level=log_level)
        
        if debug:
            logger.info("Debug logging enabled")
        elif verbose:
            logger.info("Verbose logging enabled")

    @app.command()
    def version():
        """Show Treta version information."""
        typer.echo("🎵 Treta v1.0.0")
        typer.echo("Music Downloader and Library Manager")
        typer.echo("Built with Python, Typer, and ❤️")

    @app.command()
    def init():
        """Initialize Treta workspace and database."""
        try:
            from db.manager import DatabaseManager
            
            logger = get_logger()
            
            if RICH_AVAILABLE:
                console.print("[bold cyan]🔧 Initializing Treta workspace...[/bold cyan]")
            else:
                typer.echo("🔧 Initializing Treta workspace...")
            
            # Initialize database
            db_manager = DatabaseManager(str(config.database_path))
            
            if RICH_AVAILABLE:
                console.print("[green]✅ Database initialized[/green]")
            else:
                typer.echo("✅ Database initialized")
            
            # Create directories (using config)
            directories = [config.music_dir, config.log_dir, config.config_dir / "models"]
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                
                if RICH_AVAILABLE:
                    console.print(f"[green]📁 Created directory: {directory}[/green]")
                else:
                    typer.echo(f"📁 Created directory: {directory}")
            
            if RICH_AVAILABLE:
                console.print("\n[bold green]🎉 Treta workspace initialized successfully![/bold green]")
                console.print(f"\n[blue]📂 Configuration directory:[/blue] {config.config_dir}")
                console.print(f"[blue]🎵 Music directory:[/blue] {config.music_dir}")
                console.print(f"[blue]🗄️ Database:[/blue] {config.database_path}")
                
                console.print("\n[bold yellow]📝 Next steps:[/bold yellow]")
                console.print("[cyan]1. Add authentication:[/cyan] treta auth add --service spotify")
                console.print("[cyan]2. Download music:[/cyan] treta download url <spotify/apple_url>")
                console.print("[cyan]3. View stats:[/cyan] treta stats show")
            else:
                typer.echo("\n🎉 Treta workspace initialized successfully!")
                typer.echo(f"\n📂 Configuration directory: {config.config_dir}")
                typer.echo(f"🎵 Music directory: {config.music_dir}")
                typer.echo(f"🗄️ Database: {config.database_path}")
                
                typer.echo("\n📝 Next steps:")
                typer.echo("1. Add authentication: treta auth add --service spotify")
                typer.echo("2. Download music: treta download url <spotify/apple_url>")
                typer.echo("3. View stats: treta stats show")
            
            logger.info("Treta workspace initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Treta: {e}")
            if RICH_AVAILABLE:
                console.print(f"[bold red]❌ Failed to initialize Treta: {e}[/bold red]")
            else:
                typer.echo(f"❌ Failed to initialize Treta: {e}")
            raise typer.Exit(1)

def display_welcome():
    """Display a welcome message with quick start instructions."""
    if not USING_INSTALLED_PACKAGE:
        welcome_text = """
# 🎵 Welcome to Treta! 

**Treta** is a powerful Music Downloader and Library Manager for your personal music collection.

## 🚀 Quick Start Guide:

1. **Initialize workspace**: `treta init`
2. **Set up authentication**: `treta auth add --service spotify`
3. **Download music**: `treta download url https://spotify.com/album/...`
4. **Create a mood-based queue**: `treta mood create --name "Chill" --energy low --valence high`

## 📚 Available Commands:
- `download`: Download music from Spotify or Apple Music
- `auth`: Manage music service authentication
- `mood`: Create and manage mood-based playlists
- `stats`: View your library statistics
- `queue`: Manage your smart music queue
- `artist`: Follow artists and get notified about new releases

Type `treta --help` for more information or `treta COMMAND --help` for help on a specific command.    """
        if RICH_AVAILABLE:
            console.print(Panel(Markdown(welcome_text), 
                           title="[bold cyan]Treta Music Manager[/bold cyan]",
                           border_style="cyan",
                           box=box.DOUBLE_EDGE))
            
            console.print("\n[bold green]Would you like to:[/bold green]")
            console.print("1. Initialize Treta workspace (first-time setup)")
            console.print("2. View full command list")
            console.print("3. Run a specific command")
            console.print("4. Exit")
    else:
        print("🎵 Welcome to Treta! 🎵")
        print("=" * 50)
        print("\nQuick Start Guide:")
        print("1. Initialize workspace: treta init")
        print("2. Set up authentication: treta auth add --service spotify")
        print("3. Download music: treta download url <spotify/apple_url>")
        
        print("\nWhat would you like to do?")
        print("1. Initialize Treta workspace (first-time setup)")
        print("2. View full command list")
        print("3. Run a specific command")
        print("4. Exit")
    
    return get_user_choice()

def get_user_choice():
    """Get the user's menu choice."""
    if USING_INSTALLED_PACKAGE:
        return ["--help"]  # Default to help for installed package
        
    try:
        if RICH_AVAILABLE:
            choice = console.input("\n[bold cyan]Enter your choice (1-4):[/bold cyan] ")
        else:
            choice = input("\nEnter your choice (1-4): ")
            
        if choice == "1":
            return ["init"]
        elif choice == "2":
            return ["--help"]
        elif choice == "3":
            if RICH_AVAILABLE:
                cmd = console.input("[bold cyan]Enter Treta command (e.g., 'download url https://spotify.com/track/...'):[/bold cyan] ")
            else:
                cmd = input("Enter Treta command (e.g., 'download url https://spotify.com/track/...'): ")
            return cmd.split()
        elif choice == "4":
            if RICH_AVAILABLE:
                console.print("[yellow]Exiting Treta. Goodbye![/yellow]")
            else:
                print("Exiting Treta. Goodbye!")
            sys.exit(0)
        else:
            if RICH_AVAILABLE:
                console.print("[bold red]Invalid choice. Please enter 1, 2, 3 or 4.[/bold red]")
            else:
                print("Invalid choice. Please enter 1, 2, 3 or 4.")
            return get_user_choice()
    except KeyboardInterrupt:
        if RICH_AVAILABLE:
            console.print("[yellow]\nExiting Treta. Goodbye![/yellow]")
        else:
            print("\nExiting Treta. Goodbye!")
        sys.exit(0)

@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging")
):
    """
    🎵 Treta - Music Downloader and Library Manager
    
    A powerful CLI tool for downloading and managing music from Spotify and Apple Music.
    """
    # Setup logging based on verbosity
    log_level = "DEBUG" if debug else "INFO" if verbose else "WARNING"
    logger = setup_logging(level=log_level)
    
    if debug:
        logger.info("Debug logging enabled")
    elif verbose:
        logger.info("Verbose logging enabled")

@app.command()
def version():
    """Show Treta version information."""
    typer.echo("🎵 Treta v1.0.0")
    typer.echo("Music Downloader and Library Manager")
    typer.echo("Built with Python, Typer, and ❤️")

@app.command()
def init():
    """Initialize Treta workspace and database."""
    try:
        from db.manager import DatabaseManager
        
        logger = get_logger()
        
        if RICH_AVAILABLE:
            console.print("[bold cyan]🔧 Initializing Treta workspace...[/bold cyan]")
        else:
            typer.echo("🔧 Initializing Treta workspace...")
        
        # Initialize database
        db_manager = DatabaseManager(str(config.database_path))
        
        if RICH_AVAILABLE:
            console.print("[green]✅ Database initialized[/green]")
        else:
            typer.echo("✅ Database initialized")
        
        # Create directories (using config)
        directories = [config.music_dir, config.log_dir, config.config_dir / "models"]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
            if RICH_AVAILABLE:
                console.print(f"[green]📁 Created directory: {directory}[/green]")
            else:
                typer.echo(f"📁 Created directory: {directory}")
        
        if RICH_AVAILABLE:
            console.print("\n[bold green]🎉 Treta workspace initialized successfully![/bold green]")
            console.print(f"\n[blue]📂 Configuration directory:[/blue] {config.config_dir}")
            console.print(f"[blue]🎵 Music directory:[/blue] {config.music_dir}")
            console.print(f"[blue]🗄️ Database:[/blue] {config.database_path}")
            
            console.print("\n[bold yellow]📝 Next steps:[/bold yellow]")
            console.print("[cyan]1. Add authentication:[/cyan] treta auth add --service spotify")
            console.print("[cyan]2. Download music:[/cyan] treta download url <spotify/apple_url>")
            console.print("[cyan]3. View stats:[/cyan] treta stats show")
        else:
            typer.echo("\n🎉 Treta workspace initialized successfully!")
            typer.echo(f"\n📂 Configuration directory: {config.config_dir}")
            typer.echo(f"🎵 Music directory: {config.music_dir}")
            typer.echo(f"🗄️ Database: {config.database_path}")
            
            typer.echo("\n📝 Next steps:")
            typer.echo("1. Add authentication: treta auth add --service spotify")
            typer.echo("2. Download music: treta download url <spotify/apple_url>")
            typer.echo("3. View stats: treta stats show")
        
        logger.info("Treta workspace initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Treta: {e}")
        if RICH_AVAILABLE:
            console.print(f"[bold red]❌ Failed to initialize Treta: {e}[/bold red]")
        else:
            typer.echo(f"❌ Failed to initialize Treta: {e}")
        raise typer.Exit(1)

@app.command()
def guide():
    """Show a detailed guide on how to use Treta."""
    guide_text = """
# 📚 Treta User Guide

## 🏁 Getting Started

### First-time setup:
```
treta init
```
This creates the necessary folders and database for Treta to work.

### Authentication:
```
treta auth add --service spotify
treta auth add --service apple
```
Follow the prompts to authenticate with your music services.

## 📥 Downloading Music

### Download from URL:
```
# Direct download command:
treta download --url https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3

# Or using the url subcommand:
treta download url https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3
treta download url https://music.apple.com/us/album/1234567890

# Download multiple URLs at once:
treta download url https://open.spotify.com/track/... https://open.spotify.com/album/...
```

### Download by artist:
```
treta artist download --name "Taylor Swift" --limit 5
```

### Download an album:
```
treta download --album "Folklore" --artist "Taylor Swift"
```

## 🎭 Mood Features

### Create a mood-based playlist:
```
treta mood create --name "Workout" --energy high --tempo fast
treta mood create --name "Relaxing" --energy low --valence high
```

### Play by mood:
```
treta queue add-by-mood "Relaxing" --count 10
```

## 📊 Statistics

### View your library stats:
```
treta stats show
```

### View artist statistics:
```
treta stats artist --name "The Weeknd"
```

## 🧠 Smart Queue

### Add tracks to queue:
```
treta queue add --track "Song Name" --artist "Artist Name"
```

### Play the queue:
```
treta queue play
```

### Show the current queue:
```
treta queue show
```

## 🔍 Need more help?

For detailed help on any command:
```
treta COMMAND --help
```

For example:
```
treta download --help
```
"""
    if RICH_AVAILABLE:
        console.print(Panel(Markdown(guide_text),
                       title="[bold cyan]Treta User Guide[/bold cyan]",
                       border_style="cyan",
                       box=box.DOUBLE_EDGE))
    else:
        typer.echo("📚 TRETA USER GUIDE")
        typer.echo("=" * 50)
        
        typer.echo("\n🏁 Getting Started")
        
        typer.echo("\nFirst-time setup:")
        typer.echo("  treta init")
        
        typer.echo("\nAuthentication:")
        typer.echo("  treta auth add --service spotify")
        typer.echo("  treta auth add --service apple")
        
        typer.echo("\n📥 Downloading Music")
        
        typer.echo("\nDownload from URL:")
        typer.echo("  treta download --url https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3")
        typer.echo("  treta download url https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3")
        
        typer.echo("\nFor more detailed instructions, run 'treta guide' with Rich installed.")

@app.command()
def examples():
    """Show command examples for common use cases."""
    examples_text = """
# 📝 Treta Command Examples

## Basic Examples

### Download a Spotify album:
```
treta download url https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3
```

### Download an Apple Music playlist:
```
treta download url https://music.apple.com/us/playlist/pl.u-6mo4lGGtJ6Gz5K
```

### Follow an artist:
```
treta artist follow --name "Kendrick Lamar"
```

### Create a mood playlist:
```
treta mood create --name "Focus" --energy medium --valence low --acousticness high
```

## Advanced Examples

### Download all albums from an artist (last 5 years):
```
treta artist download --name "Dua Lipa" --albums-only --since 2018
```

### Create a smart queue based on your current mood:
```
treta queue smart --energy high --valence high --limit 20
```

### Get detailed statistics:
```
treta stats detailed --from 2023-01-01 --to 2023-12-31
```

### Export your library metadata:
```
treta stats export --format json --output library_export.json
```
"""
    if RICH_AVAILABLE:
        console.print(Panel(Markdown(examples_text),
                       title="[bold cyan]Treta Command Examples[/bold cyan]",
                       border_style="cyan",
                       box=box.DOUBLE_EDGE))
    else:
        typer.echo("📝 TRETA COMMAND EXAMPLES")
        typer.echo("=" * 50)
        
        typer.echo("\nBasic Examples:")
        
        typer.echo("\nDownload a Spotify album:")
        typer.echo("  treta download url https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3")
        
        typer.echo("\nFollow an artist:")
        typer.echo("  treta artist follow --name \"Kendrick Lamar\"")
        
        typer.echo("\nFor more examples, run 'treta examples' with Rich installed.")

@app.command()
def status():
    """Show Treta system status."""
    try:
        from db.manager import DatabaseManager
        from core.auth_store import AuthStore
        
        if RICH_AVAILABLE:
            console.print("[bold cyan]📊 Treta System Status[/bold cyan]")
            console.print("=" * 40)
        else:
            typer.echo("📊 Treta System Status")
            typer.echo("=" * 40)
        
        # Database status
        try:
            db_manager = DatabaseManager()
            stats = db_manager.get_stats()
            
            if RICH_AVAILABLE:
                console.print(f"[blue]📀 Total tracks:[/blue] {stats['total_tracks']}")
                console.print(f"[blue]🎤 Total artists:[/blue] {stats['total_artists']}")
                console.print(f"[blue]💿 Total albums:[/blue] {stats['total_albums']}")
            else:
                typer.echo(f"📀 Total tracks: {stats['total_tracks']}")
                typer.echo(f"🎤 Total artists: {stats['total_artists']}")
                typer.echo(f"💿 Total albums: {stats['total_albums']}")
            
            # By source
            if stats['by_source']:
                if RICH_AVAILABLE:
                    console.print("\n[bold blue]🎵 By source:[/bold blue]")
                else:
                    typer.echo("\n🎵 By source:")
                    
                for source, count in stats['by_source'].items():
                    if RICH_AVAILABLE:
                        console.print(f"  [green]{source}:[/green] {count} tracks")
                    else:
                        typer.echo(f"  {source}: {count} tracks")
            
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]❌ Database error: {e}[/bold red]")
            else:
                typer.echo(f"❌ Database error: {e}")
        
        # Authentication status
        if RICH_AVAILABLE:
            console.print("\n[bold blue]🔐 Authentication Status:[/bold blue]")
        else:
            typer.echo("\n🔐 Authentication Status:")
            
        try:
            auth_store = AuthStore()
            auth_status = auth_store.get_auth_status()
            
            for service, is_auth in auth_status.items():
                status_icon = "✅" if is_auth else "❌"
                if RICH_AVAILABLE:
                    status_color = "green" if is_auth else "red"
                    console.print(f"  [{status_color}]{service.title()}: {status_icon}[/{status_color}]")
                else:
                    typer.echo(f"  {service.title()}: {status_icon}")
                
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]❌ Auth error: {e}[/bold red]")
            else:
                typer.echo(f"❌ Auth error: {e}")
        
        # Storage info
        if RICH_AVAILABLE:
            console.print("\n[bold blue]💾 Storage:[/bold blue]")
        else:
            typer.echo("\n💾 Storage:")
            
        try:
            downloads_dir = Path("downloads")
            if downloads_dir.exists():
                total_size = sum(f.stat().st_size for f in downloads_dir.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                
                if RICH_AVAILABLE:
                    console.print(f"  [green]Downloads:[/green] {size_mb:.1f} MB")
                else:
                    typer.echo(f"  Downloads: {size_mb:.1f} MB")
            else:
                if RICH_AVAILABLE:
                    console.print("  [yellow]Downloads: No downloads directory[/yellow]")
                else:
                    typer.echo("  Downloads: No downloads directory")
        except Exception as e:
            if RICH_AVAILABLE:
                console.print(f"[bold red]❌ Storage error: {e}[/bold red]")
            else:
                typer.echo(f"❌ Storage error: {e}")
            
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"[bold red]❌ Failed to get status: {e}[/bold red]")
        else:
            typer.echo(f"❌ Failed to get status: {e}")
        raise typer.Exit(1)

if __name__ == "__main__":
    # Check if we're using the installed package or local implementation
    if USING_INSTALLED_PACKAGE:
        # We successfully imported from the package
        run_cli()
    else:
        # If run directly with no arguments, show the interactive welcome screen
        if len(sys.argv) == 1:
            args = display_welcome()
            sys.argv.extend(args)
        
        # Run the Typer app
        app()
