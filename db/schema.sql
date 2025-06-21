-- Treta Music Database Schema

-- Tracks table to store downloaded music metadata
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    source TEXT NOT NULL CHECK(source IN ('spotify', 'apple')),
    url TEXT NOT NULL,
    file_path TEXT,
    mood TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER, -- in seconds
    file_hash TEXT UNIQUE,
    track_id TEXT, -- Spotify/Apple Music track ID
    album_id TEXT,
    artist_id TEXT,
    is_favorite BOOLEAN DEFAULT FALSE,
    play_count INTEGER DEFAULT 0,
    last_played TIMESTAMP,
    audio_features TEXT, -- JSON string of librosa features
    UNIQUE(track_id, source)
);

-- Artists table for tracking followed artists
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    artist_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('spotify', 'apple')),
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    UNIQUE(artist_id, source)
);

-- Albums table
CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('spotify', 'apple')),
    release_date TEXT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(album_id, source)
);

-- Playlists table
CREATE TABLE IF NOT EXISTS playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    playlist_id TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('spotify', 'apple')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(playlist_id, source)
);

-- Smart queue table for generated playlists
CREATE TABLE IF NOT EXISTS smart_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER REFERENCES tracks(id),
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    queue_type TEXT DEFAULT 'default' -- 'mood-based', 'artist-based', etc.
);

-- Authentication tokens table
CREATE TABLE IF NOT EXISTS auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL CHECK(service IN ('spotify', 'apple')),
    token_type TEXT NOT NULL, -- 'bearer', 'cookie', etc.
    token_data TEXT NOT NULL, -- encrypted token/cookie data
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(service, token_type)
);

-- Mood detection training data
CREATE TABLE IF NOT EXISTS mood_training (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id INTEGER REFERENCES tracks(id),
    user_mood TEXT NOT NULL,
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Download history for avoiding duplicates
CREATE TABLE IF NOT EXISTS download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    file_hash TEXT,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tracks_source ON tracks(source);
CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks(artist);
CREATE INDEX IF NOT EXISTS idx_tracks_downloaded_at ON tracks(downloaded_at);
CREATE INDEX IF NOT EXISTS idx_tracks_file_hash ON tracks(file_hash);
CREATE INDEX IF NOT EXISTS idx_artists_source ON artists(source);
CREATE INDEX IF NOT EXISTS idx_smart_queue_position ON smart_queue(position);
CREATE INDEX IF NOT EXISTS idx_download_history_url ON download_history(url);
