"""
Statistics CLI commands for Treta.
Shows download statistics, listening habits, and analytics.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import tempfile
import os

# Optional matplotlib for visualizations
try:
    import matplotlib.pyplot as plt
    import matplotlib
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from db.manager import DatabaseManager

# Use non-interactive backend for matplotlib
matplotlib.use('Agg')

# Initialize Rich console
console = Console()

# Create Typer app
stats_app = typer.Typer(help="View download and listening statistics")

@stats_app.command()
def show(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed statistics"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export charts to directory")
):
    """Show comprehensive download and listening statistics."""
    
    console.print("📊 [bold blue]Treta Statistics[/bold blue]")
    
    db_manager = DatabaseManager()
    stats = db_manager.get_stats()
    
    # Basic stats
    _show_basic_stats(stats)
    
    if detailed:
        _show_detailed_stats(stats)
    
    # Generate charts if requested
    if export:
        _generate_charts(stats, export)

@stats_app.command()
def top(
    category: str = typer.Argument("artists", help="Category to show (artists/tracks/albums)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of items to show"),
    by: str = typer.Option("tracks", "--by", help="Sort by (tracks/plays) for artists")
):
    """Show top artists, tracks, or albums."""
    
    db_manager = DatabaseManager()
    
    if category == "artists":
        _show_top_artists(db_manager, limit, by)
    elif category == "tracks":
        _show_top_tracks(db_manager, limit)
    elif category == "albums":
        _show_top_albums(db_manager, limit)
    else:
        console.print("❌ [red]Invalid category. Use: artists, tracks, or albums[/red]")
        raise typer.Exit(1)

@stats_app.command()
def mood():
    """Show mood-based statistics."""
    
    console.print("🎭 [bold blue]Mood Statistics[/bold blue]")
    
    db_manager = DatabaseManager()
    stats = db_manager.get_stats()
    
    mood_breakdown = stats.get('mood_breakdown', {})
    
    if not mood_breakdown:
        console.print("📭 [yellow]No mood data available[/yellow]")
        console.print("💡 [cyan]Run 'treta mood analyze --all' to analyze your tracks[/cyan]")
        return
    
    # Create mood table
    table = Table(title="🎭 Mood Distribution", show_header=True, header_style="bold cyan")
    table.add_column("Mood", style="magenta")
    table.add_column("Count", style="green")
    table.add_column("Percentage", style="yellow")
    table.add_column("Bar", style="blue")
    
    total = sum(mood_breakdown.values())
    max_count = max(mood_breakdown.values()) if mood_breakdown else 1
    
    # Sort by count
    sorted_moods = sorted(mood_breakdown.items(), key=lambda x: x[1], reverse=True)
    
    for mood, count in sorted_moods:
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int((count / max_count) * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        table.add_row(mood.title(), str(count), f"{percentage:.1f}%", bar)
    
    console.print(table)

@stats_app.command()
def sources():
    """Show statistics by music source."""
    
    console.print("🎵 [bold blue]Statistics by Source[/bold blue]")
    
    db_manager = DatabaseManager()
    stats = db_manager.get_stats()
    
    by_source = stats.get('by_source', {})
    
    if not by_source:
        console.print("📭 [yellow]No tracks found[/yellow]")
        return
    
    table = Table(title="🎵 Downloads by Source", show_header=True, header_style="bold cyan")
    table.add_column("Source", style="magenta")
    table.add_column("Tracks", style="green")
    table.add_column("Percentage", style="yellow")
    table.add_column("Bar", style="blue")
    
    total = sum(by_source.values())
    max_count = max(by_source.values()) if by_source else 1
    
    for source, count in by_source.items():
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int((count / max_count) * 20)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        
        table.add_row(source.title(), str(count), f"{percentage:.1f}%", bar)
    
    console.print(table)

@stats_app.command()
def activity(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to show activity for")
):
    """Show download activity over time."""
    
    console.print(f"📈 [bold blue]Download Activity (Last {days} days)[/bold blue]")
    
    # This would require implementing date-based queries
    console.print("❗ [yellow]Activity tracking not yet implemented[/yellow]")
    console.print("💡 [cyan]This feature will show download patterns over time[/cyan]")

def _show_basic_stats(stats: dict):
    """Show basic statistics."""
    
    basic_info = f"""
📀 Total Tracks: {stats.get('total_tracks', 0)}
🎤 Total Artists: {stats.get('total_artists', 0)}
💿 Total Albums: {stats.get('total_albums', 0)}
"""
    
    # Add source breakdown
    by_source = stats.get('by_source', {})
    if by_source:
        basic_info += "\n🎵 By Source:\n"
        for source, count in by_source.items():
            basic_info += f"   {source.title()}: {count}\n"
    
    console.print(Panel(basic_info.strip(), title="📊 Overview", border_style="blue"))

def _show_detailed_stats(stats: dict):
    """Show detailed statistics."""
    
    # Top artists
    top_artists = stats.get('top_artists', [])
    if top_artists:
        console.print("\n🌟 [bold cyan]Top Artists[/bold cyan]")
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Artist", style="magenta")
        table.add_column("Tracks", style="green")
        
        for artist_info in top_artists[:10]:
            table.add_row(artist_info['artist'], str(artist_info['tracks']))
        
        console.print(table)
    
    # Most played
    most_played = stats.get('most_played', [])
    if most_played:
        console.print("\n🔥 [bold cyan]Most Played[/bold cyan]")
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Title", style="cyan")
        table.add_column("Artist", style="magenta")
        table.add_column("Plays", style="green")
        
        for track_info in most_played[:10]:
            table.add_row(
                track_info['title'],
                track_info['artist'],
                str(track_info['plays'])
            )
        
        console.print(table)

def _show_top_artists(db_manager: DatabaseManager, limit: int, sort_by: str):
    """Show top artists."""
    
    console.print(f"🌟 [bold blue]Top {limit} Artists[/bold blue]")
    
    stats = db_manager.get_stats()
    top_artists = stats.get('top_artists', [])
    
    if not top_artists:
        console.print("📭 [yellow]No artists found[/yellow]")
        return
    
    table = Table(title=f"🌟 Top Artists (by {sort_by})", show_header=True, header_style="bold cyan")
    table.add_column("Rank", style="yellow")
    table.add_column("Artist", style="magenta")
    table.add_column("Tracks", style="green")
    
    for i, artist_info in enumerate(top_artists[:limit], 1):
        table.add_row(
            str(i),
            artist_info['artist'],
            str(artist_info['tracks'])
        )
    
    console.print(table)

def _show_top_tracks(db_manager: DatabaseManager, limit: int):
    """Show top tracks by play count."""
    
    console.print(f"🔥 [bold blue]Top {limit} Tracks[/bold blue]")
    
    stats = db_manager.get_stats()
    most_played = stats.get('most_played', [])
    
    if not most_played:
        console.print("📭 [yellow]No played tracks found[/yellow]")
        return
    
    table = Table(title="🔥 Most Played Tracks", show_header=True, header_style="bold cyan")
    table.add_column("Rank", style="yellow")
    table.add_column("Title", style="cyan")
    table.add_column("Artist", style="magenta")
    table.add_column("Plays", style="green")
    
    for i, track_info in enumerate(most_played[:limit], 1):
        table.add_row(
            str(i),
            track_info['title'],
            track_info['artist'],
            str(track_info['plays'])
        )
    
    console.print(table)

def _show_top_albums(db_manager: DatabaseManager, limit: int):
    """Show top albums by track count."""
    
    console.print(f"💿 [bold blue]Top {limit} Albums[/bold blue]")
    
    # Get all tracks and group by album
    tracks = db_manager.get_all_tracks()
    
    if not tracks:
        console.print("📭 [yellow]No tracks found[/yellow]")
        return
    
    # Group by album
    album_counts = {}
    for track in tracks:
        if track.album:
            key = f"{track.artist} - {track.album}"
            album_counts[key] = album_counts.get(key, 0) + 1
    
    # Sort and limit
    sorted_albums = sorted(album_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    table = Table(title="💿 Albums by Track Count", show_header=True, header_style="bold cyan")
    table.add_column("Rank", style="yellow")
    table.add_column("Album", style="cyan")
    table.add_column("Tracks", style="green")
    
    for i, (album, count) in enumerate(sorted_albums, 1):
        table.add_row(str(i), album, str(count))
    
    console.print(table)

def _generate_charts(stats: dict, export_dir: str):
    """Generate and save charts."""
    
    if not MATPLOTLIB_AVAILABLE:
        console.print("⚠️  [yellow]Matplotlib not available. Install it to generate charts:[/yellow]")
        console.print("   [cyan]pip install matplotlib[/cyan]")
        return
    
    console.print(f"📊 [blue]Generating charts in: {export_dir}[/blue]")
    
    export_path = Path(export_dir)
    export_path.mkdir(exist_ok=True)
    
    try:
        # Sources pie chart
        by_source = stats.get('by_source', {})
        if by_source:
            plt.figure(figsize=(10, 8))
            plt.pie(by_source.values(), labels=[s.title() for s in by_source.keys()], autopct='%1.1f%%')
            plt.title('Downloads by Source')
            plt.savefig(export_path / 'sources.png', dpi=300, bbox_inches='tight')
            plt.close()
            console.print("✅ [green]Sources chart saved[/green]")
        
        # Mood distribution chart
        mood_breakdown = stats.get('mood_breakdown', {})
        if mood_breakdown:
            plt.figure(figsize=(12, 8))
            moods = list(mood_breakdown.keys())
            counts = list(mood_breakdown.values())
            
            plt.bar(moods, counts, color='skyblue')
            plt.title('Mood Distribution')
            plt.xlabel('Mood')
            plt.ylabel('Number of Tracks')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(export_path / 'moods.png', dpi=300, bbox_inches='tight')
            plt.close()
            console.print("✅ [green]Mood chart saved[/green]")
        
        # Top artists chart
        top_artists = stats.get('top_artists', [])
        if top_artists:
            plt.figure(figsize=(12, 8))
            artists = [a['artist'] for a in top_artists[:10]]
            track_counts = [a['tracks'] for a in top_artists[:10]]
            
            plt.barh(artists, track_counts, color='lightgreen')
            plt.title('Top 10 Artists by Track Count')
            plt.xlabel('Number of Tracks')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(export_path / 'top_artists.png', dpi=300, bbox_inches='tight')
            plt.close()
            console.print("✅ [green]Top artists chart saved[/green]")
        
        console.print(f"📊 [green]All charts saved to: {export_path}[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error generating charts: {e}[/red]")
