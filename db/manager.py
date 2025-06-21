"""
Database manager for Treta music downloader.
Handles SQLite database operations, initialization, and queries.
"""

import sqlite3
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager

from .models import Track, Artist, Album, Playlist, AuthToken


class DatabaseManager:
    """Manages SQLite database operations for Treta."""
    
    def __init__(self, db_path: str = None):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. Defaults to data/downloads.db
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'downloads.db')
        
        self.db_path = os.path.abspath(db_path)
        self.schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """Initialize database with schema if it doesn't exist."""
        try:
            with self.get_connection() as conn:
                # Read and execute schema
                with open(self.schema_path, 'r') as f:
                    schema_sql = f.read()
                
                conn.executescript(schema_sql)
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    # Track operations
    def add_track(self, track: Track) -> int:
        """Add a track to the database.
        
        Args:
            track: Track object to add
            
        Returns:
            Track ID of inserted record
        """
        query = """
        INSERT INTO tracks (title, artist, album, source, url, file_path, 
                          mood, duration, file_hash, track_id, album_id, 
                          artist_id, audio_features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (
                track.title, track.artist, track.album, track.source,
                track.url, track.file_path, track.mood, track.duration,
                track.file_hash, track.track_id, track.album_id,
                track.artist_id, json.dumps(track.audio_features) if track.audio_features else None
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_track_by_hash(self, file_hash: str) -> Optional[Track]:
        """Get track by file hash."""
        query = "SELECT * FROM tracks WHERE file_hash = ?"
        
        with self.get_connection() as conn:
            row = conn.execute(query, (file_hash,)).fetchone()
            return Track.from_db_row(row) if row else None
    
    def get_track_by_id(self, track_id: str, source: str) -> Optional[Track]:
        """Get track by external ID and source."""
        query = "SELECT * FROM tracks WHERE track_id = ? AND source = ?"
        
        with self.get_connection() as conn:
            row = conn.execute(query, (track_id, source)).fetchone()
            return Track.from_db_row(row) if row else None
    
    def get_all_tracks(self, limit: int = None) -> List[Track]:
        """Get all tracks from database."""
        query = "SELECT * FROM tracks ORDER BY downloaded_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [Track.from_db_row(row) for row in rows]
    
    def search_tracks(self, query: str) -> List[Track]:
        """Search tracks by title, artist, or album."""
        sql_query = """
        SELECT * FROM tracks 
        WHERE title LIKE ? OR artist LIKE ? OR album LIKE ?
        ORDER BY downloaded_at DESC
        """
        search_term = f"%{query}%"
        
        with self.get_connection() as conn:
            rows = conn.execute(sql_query, (search_term, search_term, search_term)).fetchall()
            return [Track.from_db_row(row) for row in rows]
    
    def update_track_mood(self, track_id: int, mood: str):
        """Update track mood."""
        query = "UPDATE tracks SET mood = ? WHERE id = ?"
        
        with self.get_connection() as conn:
            conn.execute(query, (mood, track_id))
            conn.commit()
    
    def increment_play_count(self, track_id: int):
        """Increment play count and update last played timestamp."""
        query = """
        UPDATE tracks 
        SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP 
        WHERE id = ?
        """
        
        with self.get_connection() as conn:
            conn.execute(query, (track_id,))
            conn.commit()
    
    # Artist operations
    def add_artist(self, artist: Artist) -> int:
        """Add an artist to followed artists."""
        query = """
        INSERT OR IGNORE INTO artists (name, artist_id, source)
        VALUES (?, ?, ?)
        """
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (artist.name, artist.artist_id, artist.source))
            conn.commit()
            return cursor.lastrowid
    
    def get_followed_artists(self) -> List[Artist]:
        """Get all followed artists."""
        query = "SELECT * FROM artists ORDER BY followed_at DESC"
        
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [Artist.from_db_row(row) for row in rows]
    
    def remove_artist(self, artist_id: str, source: str):
        """Remove artist from followed list."""
        query = "DELETE FROM artists WHERE artist_id = ? AND source = ?"
        
        with self.get_connection() as conn:
            conn.execute(query, (artist_id, source))
            conn.commit()
    
    # Authentication operations
    def store_auth_token(self, token: AuthToken):
        """Store authentication token."""
        query = """
        INSERT OR REPLACE INTO auth_tokens (service, token_type, token_data, expires_at)
        VALUES (?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            conn.execute(query, (
                token.service, token.token_type, token.token_data, token.expires_at
            ))
            conn.commit()
    
    def get_auth_token(self, service: str, token_type: str = 'bearer') -> Optional[AuthToken]:
        """Get authentication token for service."""
        query = """
        SELECT * FROM auth_tokens 
        WHERE service = ? AND token_type = ? AND is_active = TRUE
        """
        
        with self.get_connection() as conn:
            row = conn.execute(query, (service, token_type)).fetchone()
            return AuthToken.from_db_row(row) if row else None
    
    def revoke_auth_token(self, service: str):
        """Revoke authentication token for service."""
        query = "UPDATE auth_tokens SET is_active = FALSE WHERE service = ?"
        
        with self.get_connection() as conn:
            conn.execute(query, (service,))
            conn.commit()
    
    # Download history operations
    def add_download_history(self, url: str, file_hash: str = None, 
                           success: bool = True, error_message: str = None):
        """Add download history entry."""
        query = """
        INSERT INTO download_history (url, file_hash, success, error_message)
        VALUES (?, ?, ?, ?)
        """
        
        with self.get_connection() as conn:
            conn.execute(query, (url, file_hash, success, error_message))
            conn.commit()
    
    def is_already_downloaded(self, url: str) -> bool:
        """Check if URL was already successfully downloaded."""
        query = "SELECT COUNT(*) FROM download_history WHERE url = ? AND success = TRUE"
        
        with self.get_connection() as conn:
            count = conn.execute(query, (url,)).fetchone()[0]
            return count > 0
    
    # Statistics operations
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive download statistics."""
        with self.get_connection() as conn:
            stats = {}
            
            # Total tracks
            stats['total_tracks'] = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
            
            # Total artists
            stats['total_artists'] = conn.execute(
                "SELECT COUNT(DISTINCT artist) FROM tracks"
            ).fetchone()[0]
            
            # Total albums
            stats['total_albums'] = conn.execute(
                "SELECT COUNT(DISTINCT album) FROM tracks WHERE album IS NOT NULL"
            ).fetchone()[0]
            
            # By source
            source_stats = conn.execute("""
                SELECT source, COUNT(*) as count 
                FROM tracks 
                GROUP BY source
            """).fetchall()
            stats['by_source'] = {row[0]: row[1] for row in source_stats}
            
            # Top artists
            top_artists = conn.execute("""
                SELECT artist, COUNT(*) as track_count 
                FROM tracks 
                GROUP BY artist 
                ORDER BY track_count DESC 
                LIMIT 10
            """).fetchall()
            stats['top_artists'] = [{'artist': row[0], 'tracks': row[1]} for row in top_artists]
            
            # Mood breakdown
            mood_stats = conn.execute("""
                SELECT mood, COUNT(*) as count 
                FROM tracks 
                WHERE mood IS NOT NULL 
                GROUP BY mood
            """).fetchall()
            stats['mood_breakdown'] = {row[0]: row[1] for row in mood_stats}
            
            # Most played
            most_played = conn.execute("""
                SELECT title, artist, play_count 
                FROM tracks 
                WHERE play_count > 0 
                ORDER BY play_count DESC 
                LIMIT 10
            """).fetchall()
            stats['most_played'] = [
                {'title': row[0], 'artist': row[1], 'plays': row[2]} 
                for row in most_played
            ]
            
            return stats
    
    # Smart queue operations
    def create_smart_queue(self, track_ids: List[int], queue_type: str = 'default'):
        """Create a smart queue from track IDs."""
        # Clear existing queue
        with self.get_connection() as conn:
            conn.execute("DELETE FROM smart_queue WHERE queue_type = ?", (queue_type,))
            
            # Insert new queue
            for position, track_id in enumerate(track_ids):
                conn.execute("""
                    INSERT INTO smart_queue (track_id, position, queue_type)
                    VALUES (?, ?, ?)
                """, (track_id, position, queue_type))
            
            conn.commit()
    
    def get_smart_queue(self, queue_type: str = 'default') -> List[Track]:
        """Get tracks from smart queue."""
        query = """
        SELECT t.* FROM tracks t
        JOIN smart_queue sq ON t.id = sq.track_id
        WHERE sq.queue_type = ?
        ORDER BY sq.position
        """
        
        with self.get_connection() as conn:
            rows = conn.execute(query, (queue_type,)).fetchall()
            return [Track.from_db_row(row) for row in rows]
    
    def get_next_in_queue(self, queue_type: str = 'default') -> Optional[Track]:
        """Get next track in queue."""
        queue = self.get_smart_queue(queue_type)
        return queue[0] if queue else None
    
    def remove_from_queue(self, track_id: int, queue_type: str = 'default'):
        """Remove track from queue and reorder."""
        with self.get_connection() as conn:
            # Remove the track
            conn.execute("""
                DELETE FROM smart_queue 
                WHERE track_id = ? AND queue_type = ?
            """, (track_id, queue_type))
            
            # Reorder remaining tracks
            conn.execute("""
                UPDATE smart_queue 
                SET position = position - 1 
                WHERE queue_type = ? AND position > (
                    SELECT MIN(position) FROM smart_queue 
                    WHERE track_id = ? AND queue_type = ?
                )
            """, (queue_type, track_id, queue_type))
            
            conn.commit()
