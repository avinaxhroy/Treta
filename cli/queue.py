"""
Queue CLI commands for Treta.
Manages smart music queues and playback.
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from core.smart_queue import SmartQueue
from db.manager import DatabaseManager
from db.models import MOOD_CATEGORIES, Track

# Initialize Rich console
console = Console()

# Create Typer app
queue_app = typer.Typer(help="Manage smart music queues")

@queue_app.command()
def create(
    queue_type: str = typer.Argument(..., help="Type of queue (mood/artist/discovery/favorites/mixed)"),
    name: str = typer.Argument(..., help="Queue name or mood/artist name"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of tracks"),
    save_as: Optional[str] = typer.Option(None, "--save-as", "-s", help="Save queue with custom name")
):
    """Create a smart queue based on criteria."""
    
    smart_queue = SmartQueue()
    
    console.print(f"🎵 [bold blue]Creating {queue_type} queue: {name}[/bold blue]")
    
    try:
        if queue_type == "mood":
            if name.lower() not in MOOD_CATEGORIES:
                console.print(f"❌ [red]Invalid mood. Available: {', '.join(MOOD_CATEGORIES)}[/red]")
                raise typer.Exit(1)
            tracks = smart_queue.generate_mood_queue(name.lower(), limit)
            
        elif queue_type == "artist":
            tracks = smart_queue.generate_artist_queue(name, limit)
            
        elif queue_type == "discovery":
            tracks = smart_queue.generate_discovery_queue(limit)
            
        elif queue_type == "favorites":
            tracks = smart_queue.generate_favorites_queue(limit)
            
        elif queue_type == "mixed":
            tracks = smart_queue.generate_mixed_queue(limit)
            
        else:
            console.print("❌ [red]Invalid queue type. Use: mood, artist, discovery, favorites, or mixed[/red]")
            raise typer.Exit(1)
        
        if tracks:
            console.print(f"✅ [green]Created queue with {len(tracks)} tracks[/green]")
            _show_queue_preview(tracks[:10])  # Show first 10 tracks
            
            if len(tracks) > 10:
                console.print(f"📋 [cyan]... and {len(tracks) - 10} more tracks[/cyan]")
        else:
            console.print("❌ [red]No tracks found for the specified criteria[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error creating queue: {e}[/red]")
        raise typer.Exit(1)

@queue_app.command()
def show(
    queue_type: str = typer.Option("default", "--type", "-t", help="Queue type to show"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of tracks to show")
):
    """Show current queue."""
    
    db_manager = DatabaseManager()
    tracks = db_manager.get_smart_queue(queue_type)
    
    if not tracks:
        console.print(f"📭 [yellow]No tracks in {queue_type} queue[/yellow]")
        console.print("💡 [cyan]Create a queue with: treta queue create <type> <name>[/cyan]")
        return
    
    console.print(f"🎵 [bold blue]Current Queue: {queue_type}[/bold blue]")
    _show_queue_table(tracks[:limit])
    
    if len(tracks) > limit:
        console.print(f"📋 [cyan]... and {len(tracks) - limit} more tracks[/cyan]")

@queue_app.command()
def next(
    queue_type: str = typer.Option("default", "--type", "-t", help="Queue type"),
    play: bool = typer.Option(False, "--play", "-p", help="Mark as played and increment play count")
):
    """Get next track from queue."""
    
    smart_queue = SmartQueue()
    track = smart_queue.get_next_track(queue_type)
    
    if not track:
        console.print(f"📭 [yellow]No more tracks in {queue_type} queue[/yellow]")
        return
    
    # Show track info
    track_info = f"""
🎵 Next Track:

Title: {track.title or 'Unknown'}
Artist: {track.artist or 'Unknown'}
Album: {track.album or 'Unknown'}
Mood: {track.mood or 'Unknown'}
Source: {track.source.title()}
File: {track.file_path or 'Unknown'}
"""
    
    console.print(Panel(track_info.strip(), title="🎵 Now Playing", border_style="green"))
    
    if play:
        # Mark as played
        db_manager = DatabaseManager()
        if track.id:
            db_manager.increment_play_count(track.id)
            console.print("✅ [green]Marked as played[/green]")
            
            # Remove from queue
            smart_queue.remove_from_queue(track.id, queue_type)
            console.print("⏭️  [cyan]Moved to next track in queue[/cyan]")
        else:
            console.print("⚠️  [yellow]Cannot mark track as played - no database ID[/yellow]")

@queue_app.command()
def remove(
    track_id: int = typer.Argument(..., help="Track ID to remove from queue"),
    queue_type: str = typer.Option("default", "--type", "-t", help="Queue type")
):
    """Remove a track from the queue."""
    
    smart_queue = SmartQueue()
    
    try:
        smart_queue.remove_from_queue(track_id, queue_type)
        console.print(f"✅ [green]Removed track {track_id} from {queue_type} queue[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error removing track: {e}[/red]")
        raise typer.Exit(1)

@queue_app.command()
def clear(
    queue_type: str = typer.Option("default", "--type", "-t", help="Queue type to clear"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clear all tracks from a queue."""
    
    if not confirm:
        confirm = typer.confirm(f"Are you sure you want to clear the {queue_type} queue?")
        if not confirm:
            console.print("❌ [yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0)
    
    db_manager = DatabaseManager()
    
    try:
        # Clear by creating empty queue
        db_manager.create_smart_queue([], queue_type)
        console.print(f"✅ [green]Cleared {queue_type} queue[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error clearing queue: {e}[/red]")
        raise typer.Exit(1)

@queue_app.command()
def list():
    """List all available queues."""
    
    # This would require tracking queue types in database
    console.print("📋 [bold blue]Available Queue Types[/bold blue]")
    
    queue_types = [
        ("mood", "Queue based on mood (happy, sad, energetic, etc.)"),
        ("artist", "Queue based on specific artist and similar artists"),
        ("discovery", "Queue with less-played tracks for discovery"),
        ("favorites", "Queue with most played and recently played tracks"),
        ("mixed", "Mixed queue with variety from different categories"),
        ("default", "Default/custom queue")
    ]
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Queue Type", style="magenta")
    table.add_column("Description", style="cyan")
    
    for queue_type, description in queue_types:
        table.add_row(queue_type, description)
    
    console.print(table)
    
    console.print("\n💡 [cyan]Usage examples:[/cyan]")
    console.print("  treta queue create mood happy --limit 30")
    console.print("  treta queue create artist \"Taylor Swift\" --limit 25")
    console.print("  treta queue create discovery --limit 20")

def _show_queue_preview(tracks: List[Track]) -> None:
    """Show a preview of queue tracks."""
    
    if not tracks:
        return
    
    table = Table(title="🎵 Queue Preview", show_header=True, header_style="bold cyan")
    table.add_column("#", style="yellow")
    table.add_column("Title", style="cyan")
    table.add_column("Artist", style="magenta")
    table.add_column("Mood", style="green")
    
    for i, track in enumerate(tracks, 1):
        table.add_row(
            str(i),
            track.title or "Unknown",
            track.artist or "Unknown",
            track.mood or "Unknown"
        )
    
    console.print(table)

def _show_queue_table(tracks: List[Track]) -> None:
    """Show queue tracks in a detailed table."""
    
    if not tracks:
        return
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Position", style="yellow")
    table.add_column("Title", style="cyan")
    table.add_column("Artist", style="magenta")
    table.add_column("Album", style="blue")
    table.add_column("Mood", style="green")
    table.add_column("Plays", style="red")
    table.add_column("Source", style="white")
    
    for i, track in enumerate(tracks, 1):
        table.add_row(
            str(i),
            track.title or "Unknown",
            track.artist or "Unknown",
            track.album or "Unknown",
            track.mood or "Unknown",
            str(track.play_count),
            track.source.title()
        )
    
    console.print(table)
