"""Tests for database functionality."""

import pytest
import sqlite3
from pathlib import Path

from db.manager import DatabaseManager
from db.models import Track, Artist, Album


class TestDatabaseManager:
    """Test database manager functionality."""
    
    def test_init_database(self, test_database):
        """Test database initialization."""
        db_manager = DatabaseManager(test_database)
        db_manager.init_database()
        
        # Check that tables were created
        conn = sqlite3.connect(test_database)
        cursor = conn.cursor()
        
        # Check if tracks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracks'")
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_add_track(self, test_database):
        """Test adding a track to the database."""
        db_manager = DatabaseManager(test_database)
        db_manager.init_database()
        
        track = Track(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration=180,
            file_path="/path/to/test.mp3",
            source="spotify"
        )
        
        track_id = db_manager.add_track(track)
        assert track_id is not None
        
        # Verify the track was added
        retrieved_track = db_manager.get_track(track_id)
        assert retrieved_track is not None
        assert retrieved_track.title == "Test Song"
    
    def test_get_tracks_by_artist(self, test_database):
        """Test retrieving tracks by artist."""
        db_manager = DatabaseManager(test_database)
        db_manager.init_database()
        
        # Add test tracks
        track1 = Track(
            title="Song 1",
            artist="Test Artist",
            album="Album 1",
            duration=180,
            file_path="/path/to/song1.mp3",
            source="spotify"
        )
        
        track2 = Track(
            title="Song 2",
            artist="Test Artist",
            album="Album 2",
            duration=200,
            file_path="/path/to/song2.mp3",
            source="apple"
        )
        
        db_manager.add_track(track1)
        db_manager.add_track(track2)
        
        # Get tracks by artist
        tracks = db_manager.get_tracks_by_artist("Test Artist")
        assert len(tracks) == 2
        assert all(track.artist == "Test Artist" for track in tracks)
