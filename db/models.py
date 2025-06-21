"""
Data models for Treta music downloader.
Represents tracks, artists, albums, playlists, and authentication tokens.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlite3 import Row


@dataclass
class Track:
    """Represents a music track."""
    title: str
    artist: str
    source: str  # 'spotify' or 'apple'
    url: str
    album: Optional[str] = None
    file_path: Optional[str] = None
    mood: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    file_hash: Optional[str] = None
    track_id: Optional[str] = None  # External service ID
    album_id: Optional[str] = None
    artist_id: Optional[str] = None
    is_favorite: bool = False
    play_count: int = 0
    downloaded_at: Optional[datetime] = None
    last_played: Optional[datetime] = None
    audio_features: Optional[Dict[str, Any]] = None
    id: Optional[int] = None  # Database ID
    
    @classmethod
    def from_db_row(cls, row: Row) -> 'Track':
        """Create Track from database row."""
        audio_features = None
        if row['audio_features']:
            try:
                audio_features = json.loads(row['audio_features'])
            except json.JSONDecodeError:
                audio_features = None
        
        return cls(
            id=row['id'],
            title=row['title'],
            artist=row['artist'],
            album=row['album'],
            source=row['source'],
            url=row['url'],
            file_path=row['file_path'],
            mood=row['mood'],
            duration=row['duration'],
            file_hash=row['file_hash'],
            track_id=row['track_id'],
            album_id=row['album_id'],
            artist_id=row['artist_id'],
            is_favorite=bool(row['is_favorite']),
            play_count=row['play_count'],
            downloaded_at=datetime.fromisoformat(row['downloaded_at']) if row['downloaded_at'] else None,
            last_played=datetime.fromisoformat(row['last_played']) if row['last_played'] else None,
            audio_features=audio_features
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert track to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.downloaded_at:
            data['downloaded_at'] = self.downloaded_at.isoformat()
        if self.last_played:
            data['last_played'] = self.last_played.isoformat()
        return data


@dataclass
@dataclass
class Artist:
    """Represents a music artist."""
    name: str
    artist_id: str  # External service ID
    source: str  # 'spotify' or 'apple'
    followed_at: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    id: Optional[int] = None  # Database ID
    
    @classmethod
    def from_db_row(cls, row: Row) -> 'Artist':
        """Create Artist from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            artist_id=row['artist_id'],
            source=row['source'],
            followed_at=datetime.fromisoformat(row['followed_at']) if row['followed_at'] else None,
            last_checked=datetime.fromisoformat(row['last_checked']) if row['last_checked'] else None
        )


@dataclass
class Album:
    """Represents a music album."""
    title: str
    artist: str
    album_id: str  # External service ID
    source: str  # 'spotify' or 'apple'
    release_date: Optional[str] = None
    added_at: Optional[datetime] = None
    id: Optional[int] = None  # Database ID
    
    @classmethod
    def from_db_row(cls, row: Row) -> 'Album':
        """Create Album from database row."""
        return cls(
            id=row['id'],
            title=row['title'],
            artist=row['artist'],
            album_id=row['album_id'],
            source=row['source'],
            release_date=row['release_date'],
            added_at=datetime.fromisoformat(row['added_at']) if row['added_at'] else None
        )


@dataclass
class Playlist:
    """Represents a music playlist."""
    name: str
    playlist_id: str  # External service ID
    source: str  # 'spotify' or 'apple'
    created_at: Optional[datetime] = None
    id: Optional[int] = None  # Database ID
    
    @classmethod
    def from_db_row(cls, row: Row) -> 'Playlist':
        """Create Playlist from database row."""
        return cls(
            id=row['id'],
            name=row['name'],
            playlist_id=row['playlist_id'],
            source=row['source'],
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )


@dataclass
class AuthToken:
    """Represents authentication token/cookie."""
    service: str  # 'spotify' or 'apple'
    token_type: str  # 'bearer', 'cookie', etc.
    token_data: str  # Actual token/cookie data
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    is_active: bool = True
    id: Optional[int] = None  # Database ID
    
    @classmethod
    def from_db_row(cls, row: Row) -> 'AuthToken':
        """Create AuthToken from database row."""
        return cls(
            id=row['id'],
            service=row['service'],
            token_type=row['token_type'],
            token_data=row['token_data'],
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            is_active=bool(row['is_active'])
        )
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at


# Mood classification constants
MOOD_CATEGORIES = [
    'happy',
    'sad',
    'energetic',
    'calm',
    'angry',
    'romantic',
    'melancholic',
    'upbeat',
    'chill',
    'intense'
]

# Supported audio formats
SUPPORTED_FORMATS = [
    '.mp3',
    '.m4a',
    '.aac',
    '.ogg',
    '.wav',
    '.flac'
]

# Service configuration
SPOTIFY_CONFIG = {
    'name': 'spotify',
    'base_url': 'https://open.spotify.com',
    'api_url': 'https://api.spotify.com/v1'
}

APPLE_CONFIG = {
    'name': 'apple',
    'base_url': 'https://music.apple.com',
    'api_url': 'https://api.music.apple.com/v1'
}
