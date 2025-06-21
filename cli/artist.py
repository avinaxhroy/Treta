"""
Artist CLI commands for Treta.
Manages artist following and new release tracking.
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from db.manager import DatabaseManager
from db.models import Artist

# Initialize Rich console
console = Console()

# Create Typer app
artist_app = typer.Typer(help="Follow artists and manage releases")

@artist_app.command()
def follow(
    artist_name: str = typer.Argument(..., help="Artist name to follow"),
    artist_id: Optional[str] = typer.Option(None, "--id", help="Artist ID from service"),
    source: str = typer.Option("spotify", "--source", "-s", help="Music service (spotify/apple)")
):
    """Follow an artist for new release notifications."""
    
    if source not in ["spotify", "apple"]:
        console.print("❌ [red]Invalid source. Use 'spotify' or 'apple'[/red]")
        raise typer.Exit(1)
    
    db_manager = DatabaseManager()
    
    try:
        # If no artist ID provided, try to find from existing tracks
        if not artist_id:
            tracks = db_manager.get_all_tracks()
            artist_tracks = [t for t in tracks if t.artist.lower() == artist_name.lower() and t.source == source]
            
            if artist_tracks:
                artist_id = artist_tracks[0].artist_id
                console.print(f"🔍 [blue]Found artist ID from existing tracks: {artist_id}[/blue]")
            else:
                console.print("❗ [yellow]No artist ID provided and no existing tracks found[/yellow]")
                console.print("💡 [cyan]Download some tracks from this artist first, or provide --id[/cyan]")
                raise typer.Exit(1)        
        # Create artist object
        artist = Artist(
            name=artist_name,
            artist_id=artist_id or "",  # Provide default empty string if None
            source=source
        )
        
        # Add to database
        artist_db_id = db_manager.add_artist(artist)
        
        if artist_db_id:
            console.print(f"✅ [green]Now following {artist_name} on {source.title()}[/green]")
            console.print(f"🆔 [cyan]Artist ID: {artist_id}[/cyan]")
        else:
            console.print(f"⚠️  [yellow]Already following {artist_name} on {source.title()}[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [red]Error following artist: {e}[/red]")
        raise typer.Exit(1)

@artist_app.command()
def unfollow(
    artist_name: str = typer.Argument(..., help="Artist name to unfollow"),
    source: str = typer.Option("spotify", "--source", "-s", help="Music service (spotify/apple)"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Unfollow an artist."""
    
    if source not in ["spotify", "apple"]:
        console.print("❌ [red]Invalid source. Use 'spotify' or 'apple'[/red]")
        raise typer.Exit(1)
    
    db_manager = DatabaseManager()
    
    try:
        # Find artist
        followed_artists = db_manager.get_followed_artists()
        artist = next(
            (a for a in followed_artists 
             if a.name.lower() == artist_name.lower() and a.source == source),
            None
        )
        
        if not artist:
            console.print(f"❌ [red]Not currently following {artist_name} on {source.title()}[/red]")
            raise typer.Exit(1)
        
        if not confirm:
            confirm = typer.confirm(f"Unfollow {artist_name} on {source.title()}?")
            if not confirm:
                console.print("❌ [yellow]Operation cancelled[/yellow]")
                raise typer.Exit(0)
        
        # Remove from database
        db_manager.remove_artist(artist.artist_id, source)
        console.print(f"✅ [green]Unfollowed {artist_name} on {source.title()}[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error unfollowing artist: {e}[/red]")
        raise typer.Exit(1)

@artist_app.command()
def list(
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Filter by source (spotify/apple)")
):
    """List all followed artists."""
    
    db_manager = DatabaseManager()
    
    try:
        followed_artists = db_manager.get_followed_artists()
        
        if source:
            followed_artists = [a for a in followed_artists if a.source == source]
        
        if not followed_artists:
            filter_text = f" on {source.title()}" if source else ""
            console.print(f"📭 [yellow]No followed artists{filter_text}[/yellow]")
            console.print("💡 [cyan]Follow an artist with: treta artist follow <artist_name>[/cyan]")
            return
        
        # Group by source
        by_source = {}
        for artist in followed_artists:
            if artist.source not in by_source:
                by_source[artist.source] = []
            by_source[artist.source].append(artist)
        
        for source_name, artists in by_source.items():
            console.print(f"\n🎵 [bold blue]{source_name.title()} Artists[/bold blue]")
            
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Artist", style="magenta")
            table.add_column("Artist ID", style="cyan")
            table.add_column("Followed Since", style="yellow")
            table.add_column("Tracks", style="green")
            
            for artist in artists:
                # Count tracks from this artist
                all_tracks = db_manager.get_all_tracks()
                track_count = len([
                    t for t in all_tracks 
                    if t.artist.lower() == artist.name.lower() and t.source == artist.source
                ])
                
                followed_date = artist.followed_at.strftime("%Y-%m-%d") if artist.followed_at else "Unknown"
                
                table.add_row(
                    artist.name,
                    artist.artist_id or "Unknown",
                    followed_date,
                    str(track_count)
                )
            
            console.print(table)
        
        console.print(f"\n📊 [cyan]Total: {len(followed_artists)} followed artists[/cyan]")
        
    except Exception as e:
        console.print(f"❌ [red]Error listing artists: {e}[/red]")
        raise typer.Exit(1)

@artist_app.command()
def info(
    artist_name: str = typer.Argument(..., help="Artist name to get info for"),
    source: Optional[str] = typer.Option(None, "--source", "-s", help="Specific source (spotify/apple)")
):
    """Show detailed information about an artist."""
    
    db_manager = DatabaseManager()
    
    try:
        # Get all tracks from this artist
        all_tracks = db_manager.get_all_tracks()
        artist_tracks = [
            t for t in all_tracks 
            if t.artist.lower() == artist_name.lower()
        ]
        
        if source:
            artist_tracks = [t for t in artist_tracks if t.source == source]
        
        if not artist_tracks:
            filter_text = f" on {source.title()}" if source else ""
            console.print(f"❌ [red]No tracks found for {artist_name}{filter_text}[/red]")
            raise typer.Exit(1)
          # Calculate stats
        total_tracks = len(artist_tracks)
        total_plays = sum(t.play_count for t in artist_tracks)
        albums = sorted(set(t.album for t in artist_tracks if t.album))
        sources = sorted(set(t.source for t in artist_tracks))
        moods = [t.mood for t in artist_tracks if t.mood]
        mood_distribution = {}
        for mood in moods:
            mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
        
        # Most played track
        most_played = max(artist_tracks, key=lambda x: x.play_count) if artist_tracks else None
        
        # Show info panel
        info_text = f"""
🎤 Artist: {artist_name}
📀 Total Tracks: {total_tracks}
🔥 Total Plays: {total_plays}
💿 Albums: {len(albums)}
🎵 Sources: {', '.join(s.title() for s in sources)}
"""
        
        if most_played:
            info_text += f"\n🏆 Most Played: {most_played.title} ({most_played.play_count} plays)"
        
        console.print(Panel(info_text.strip(), title=f"🎤 {artist_name}", border_style="blue"))
          # Show albums
        if albums:
            console.print("\n💿 [bold cyan]Albums[/bold cyan]")
            album_table = Table(show_header=True, header_style="bold cyan")
            album_table.add_column("Album", style="yellow")
            album_table.add_column("Tracks", style="green")
            album_table.add_column("Source", style="blue")
            
            for album in sorted(albums):
                album_tracks = [t for t in artist_tracks if t.album == album]
                sources_for_album = sorted(set(t.source for t in album_tracks))
                
                album_table.add_row(
                    album,
                    str(len(album_tracks)),
                    ', '.join(s.title() for s in sources_for_album)
                )
            
            console.print(album_table)
        
        # Show mood distribution
        if mood_distribution:
            console.print("\n🎭 [bold cyan]Mood Distribution[/bold cyan]")
            mood_table = Table(show_header=True, header_style="bold cyan")
            mood_table.add_column("Mood", style="magenta")
            mood_table.add_column("Tracks", style="green")
            mood_table.add_column("Percentage", style="yellow")
            
            for mood, count in sorted(mood_distribution.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(moods) * 100) if moods else 0
                mood_table.add_row(mood.title(), str(count), f"{percentage:.1f}%")
            
            console.print(mood_table)
        
        # Check if following
        followed_artists = db_manager.get_followed_artists()
        is_following = any(
            a.name.lower() == artist_name.lower() 
            for a in followed_artists
        )
        
        if is_following:
            console.print("\n✅ [green]You are following this artist[/green]")
        else:
            console.print("\n💡 [cyan]Follow this artist with: treta artist follow \"" + artist_name + "\"[/cyan]")
        
    except Exception as e:
        console.print(f"❌ [red]Error getting artist info: {e}[/red]")
        raise typer.Exit(1)

@artist_app.command()
def releases(
    check_all: bool = typer.Option(False, "--all", help="Check releases for all followed artists")
):
    """Check for new releases from followed artists."""
    
    console.print("🔍 [bold blue]Checking for New Releases[/bold blue]")
    
    # This feature would require implementing API calls to check for new releases
    console.print("❗ [yellow]New release checking not yet implemented[/yellow]")
    console.print("💡 [cyan]This feature will check for new albums/songs from followed artists[/cyan]")
    console.print("\n📋 [cyan]Planned features:[/cyan]")
    console.print("  • Automatic checking for new releases")
    console.print("  • Notifications when new music is available")
    console.print("  • Auto-download option for new releases")
    console.print("  • Release history tracking")

@artist_app.command()
def download(
    artist_name: str = typer.Argument(..., help="Artist name to download all tracks from"),
    source: str = typer.Option("spotify", "--source", "-s", help="Music service (spotify/apple)"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum tracks to download")
):
    """Download all available tracks from an artist."""
    
    console.print(f"🎵 [bold blue]Downloading tracks from {artist_name}[/bold blue]")
    
    # This would require implementing artist search and download
    console.print("❗ [yellow]Artist download not yet implemented[/yellow]")
    console.print("💡 [cyan]Use artist URLs instead:[/cyan]")
    console.print(f"  Spotify: https://open.spotify.com/artist/...")
    console.print(f"  Apple Music: https://music.apple.com/.../artist/...")
    console.print("\n📖 [cyan]Usage:[/cyan] treta download url <artist_url>")
