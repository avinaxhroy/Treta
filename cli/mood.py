"""
Mood CLI commands for Treta.
Handles mood analysis and classification of music tracks.
"""

import typer
import os
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

from core.mood_detector import MoodDetector
from db.manager import DatabaseManager
from db.models import MOOD_CATEGORIES

# Initialize Rich console
console = Console()

# Create Typer app
mood_app = typer.Typer(help="Analyze and manage music moods")

@mood_app.command()
def analyze(
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="Analyze specific audio file"),
    track_id: Optional[int] = typer.Option(None, "--track-id", help="Analyze specific track by database ID"),
    all_tracks: bool = typer.Option(False, "--all", help="Analyze all tracks in database"),
    retrain: bool = typer.Option(False, "--retrain", help="Retrain model after analysis")
):
    """Analyze mood of audio files."""
    
    if not any([file_path, track_id, all_tracks]):
        console.print("❌ [red]Please specify --file, --track-id, or --all[/red]")
        raise typer.Exit(1)
    
    mood_detector = MoodDetector()
    db_manager = DatabaseManager()
    
    if file_path:
        _analyze_single_file(mood_detector, file_path)
    
    elif track_id:
        _analyze_single_track(mood_detector, db_manager, track_id)
    
    elif all_tracks:
        _analyze_all_tracks(mood_detector, db_manager)
    
    if retrain:
        console.print("\n🧠 [blue]Retraining mood classification model...[/blue]")
        success = mood_detector.train_model()
        if success:
            console.print("✅ [green]Model retrained successfully![/green]")
        else:
            console.print("❌ [red]Failed to retrain model[/red]")

@mood_app.command()
def train(
    use_existing: bool = typer.Option(True, "--use-existing/--no-existing", help="Use existing mood labels from database")
):
    """Train mood classification model."""
    
    console.print("🧠 [bold blue]Training Mood Classification Model[/bold blue]")
    
    mood_detector = MoodDetector()
    
    with console.status("[bold green]Training model..."):
        success = mood_detector.train_model(use_existing_data=use_existing)
    
    if success:
        console.print("✅ [green]Mood classification model trained successfully![/green]")
        
        # Show model info
        distribution = mood_detector.get_mood_distribution()
        if distribution:
            _show_mood_distribution(distribution)
    else:
        console.print("❌ [red]Failed to train mood model[/red]")
        console.print("💡 [cyan]Try analyzing some tracks first to build training data[/cyan]")

@mood_app.command()
def stats():
    """Show mood statistics and distribution."""
    
    console.print("📊 [bold blue]Mood Statistics[/bold blue]")
    
    db_manager = DatabaseManager()
    stats = db_manager.get_stats()
    
    mood_breakdown = stats.get('mood_breakdown', {})
    
    if not mood_breakdown:
        console.print("📭 [yellow]No mood data available[/yellow]")
        console.print("💡 [cyan]Run 'treta mood analyze --all' to analyze your tracks[/cyan]")
        return
    
    _show_mood_distribution(mood_breakdown)
    
    # Show tracks without mood
    total_tracks = stats.get('total_tracks', 0)
    tracks_with_mood = sum(mood_breakdown.values())
    tracks_without_mood = total_tracks - tracks_with_mood
    
    if tracks_without_mood > 0:
        console.print(f"\n📝 [yellow]{tracks_without_mood} tracks don't have mood analysis yet[/yellow]")
        console.print("💡 [cyan]Run 'treta mood analyze --all' to analyze them[/cyan]")

@mood_app.command()
def set(
    track_id: int = typer.Argument(..., help="Track ID to set mood for"),
    mood: str = typer.Argument(..., help="Mood to set")
):
    """Manually set mood for a track."""
    
    if mood.lower() not in MOOD_CATEGORIES:
        console.print(f"❌ [red]Invalid mood. Available moods: {', '.join(MOOD_CATEGORIES)}[/red]")
        raise typer.Exit(1)
    
    db_manager = DatabaseManager()
    
    try:
        # Check if track exists
        tracks = db_manager.get_all_tracks()
        track = next((t for t in tracks if t.id == track_id), None)
        
        if not track:
            console.print(f"❌ [red]Track with ID {track_id} not found[/red]")
            raise typer.Exit(1)
        
        # Update mood
        db_manager.update_track_mood(track_id, mood.lower())
        
        console.print(f"✅ [green]Set mood '{mood}' for track: {track.title} - {track.artist}[/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Error setting mood: {e}[/red]")
        raise typer.Exit(1)

@mood_app.command()
def search(
    mood: str = typer.Argument(..., help="Mood to search for"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results")
):
    """Search tracks by mood."""
    
    if mood.lower() not in MOOD_CATEGORIES:
        console.print(f"❌ [red]Invalid mood. Available moods: {', '.join(MOOD_CATEGORIES)}[/red]")
        raise typer.Exit(1)
    
    db_manager = DatabaseManager()
    
    try:
        # Get all tracks and filter by mood
        all_tracks = db_manager.get_all_tracks()
        mood_tracks = [t for t in all_tracks if t.mood and t.mood.lower() == mood.lower()]
        
        if not mood_tracks:
            console.print(f"📭 [yellow]No tracks found with mood '{mood}'[/yellow]")
            return
        
        # Sort by play count
        mood_tracks.sort(key=lambda x: x.play_count, reverse=True)
        mood_tracks = mood_tracks[:limit]
        
        # Display results
        table = Table(title=f"🎵 Tracks with mood: {mood}", show_header=True, header_style="bold cyan")
        table.add_column("Title", style="cyan")
        table.add_column("Artist", style="magenta")
        table.add_column("Album", style="yellow")
        table.add_column("Plays", style="green")
        table.add_column("Source", style="blue")
        
        for track in mood_tracks:
            table.add_row(
                track.title or "Unknown",
                track.artist or "Unknown",
                track.album or "Unknown",
                str(track.play_count),
                track.source.title()
            )
        
        console.print(table)
        console.print(f"\n📊 [cyan]Found {len(mood_tracks)} tracks (showing {min(limit, len(mood_tracks))})[/cyan]")
        
    except Exception as e:
        console.print(f"❌ [red]Error searching tracks: {e}[/red]")
        raise typer.Exit(1)

def _analyze_single_file(mood_detector: MoodDetector, file_path: str):
    """Analyze mood of a single file."""
    
    if not os.path.exists(file_path):
        console.print(f"❌ [red]File not found: {file_path}[/red]")
        raise typer.Exit(1)
    
    console.print(f"🔍 [blue]Analyzing: {Path(file_path).name}[/blue]")
    
    with console.status("[bold green]Extracting audio features..."):
        features = mood_detector.extract_features(file_path)
    
    if not features:
        console.print("❌ [red]Failed to extract audio features[/red]")
        return
    
    # Predict mood
    mood, confidence = mood_detector.predict_mood(file_path)
    
    if mood:
        console.print(f"🎭 [green]Predicted mood: {mood} (confidence: {confidence:.2f})[/green]")
    else:
        # Use heuristic suggestion
        suggested_mood = mood_detector.suggest_mood_for_features(features)
        console.print(f"🎭 [yellow]Suggested mood: {suggested_mood} (heuristic)[/yellow]")
    
    # Show some features
    console.print("\n📊 [cyan]Audio Features:[/cyan]")
    key_features = ['tempo', 'spectral_centroid_mean', 'rmse_mean', 'zero_crossing_rate_mean']
    for feature in key_features:
        if feature in features:
            console.print(f"  {feature}: {features[feature]:.3f}")

def _analyze_single_track(mood_detector: MoodDetector, db_manager: DatabaseManager, track_id: int):
    """Analyze mood of a single track from database."""
    
    tracks = db_manager.get_all_tracks()
    track = next((t for t in tracks if t.id == track_id), None)
    
    if not track:
        console.print(f"❌ [red]Track with ID {track_id} not found[/red]")
        raise typer.Exit(1)
    
    console.print(f"🔍 [blue]Analyzing: {track.title} - {track.artist}[/blue]")
    
    success = mood_detector.analyze_track(track)
    
    if success:
        console.print("✅ [green]Mood analysis completed[/green]")
        if track.mood:
            console.print(f"🎭 [cyan]Mood: {track.mood}[/cyan]")
    else:
        console.print("❌ [red]Failed to analyze track[/red]")

def _analyze_all_tracks(mood_detector: MoodDetector, db_manager: DatabaseManager):
    """Analyze mood for all tracks in database."""
    
    tracks = db_manager.get_all_tracks()
    
    if not tracks:
        console.print("📭 [yellow]No tracks found in database[/yellow]")
        return
    
    # Filter tracks that need analysis
    tracks_to_analyze = [t for t in tracks if not t.mood and t.file_path and os.path.exists(t.file_path)]
    
    if not tracks_to_analyze:
        console.print("✅ [green]All tracks already have mood analysis[/green]")
        return
    
    console.print(f"🔍 [blue]Analyzing {len(tracks_to_analyze)} tracks...[/blue]")
    
    analyzed_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        task = progress.add_task("Analyzing tracks...", total=len(tracks_to_analyze))
        
        for track in tracks_to_analyze:
            progress.update(task, description=f"Analyzing: {track.title[:30]}...")
            
            try:
                success = mood_detector.analyze_track(track)
                if success:
                    analyzed_count += 1
                    
            except Exception as e:
                console.print(f"❌ [red]Error analyzing {track.title}: {e}[/red]")
            
            progress.advance(task)
    
    console.print(f"✅ [green]Analyzed {analyzed_count}/{len(tracks_to_analyze)} tracks[/green]")

def _show_mood_distribution(mood_breakdown: dict):
    """Show mood distribution in a table."""
    
    if not mood_breakdown:
        return
    
    table = Table(title="🎭 Mood Distribution", show_header=True, header_style="bold cyan")
    table.add_column("Mood", style="magenta")
    table.add_column("Count", style="green")
    table.add_column("Percentage", style="yellow")
    
    total = sum(mood_breakdown.values())
    
    # Sort by count
    sorted_moods = sorted(mood_breakdown.items(), key=lambda x: x[1], reverse=True)
    
    for mood, count in sorted_moods:
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(mood.title(), str(count), f"{percentage:.1f}%")
    
    console.print(table)
