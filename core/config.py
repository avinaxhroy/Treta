"""
Configuration settings for Treta music downloader.
"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration."""
    
    # Default paths
    DEFAULT_CONFIG_DIR = Path.home() / ".treta"
    DEFAULT_MUSIC_DIR = Path.home() / "Music" / "Treta"
    DEFAULT_DATABASE = DEFAULT_CONFIG_DIR / "treta.db"
    DEFAULT_LOG_DIR = DEFAULT_CONFIG_DIR / "logs"
    
    # Audio settings
    DEFAULT_AUDIO_FORMAT = "mp3"
    DEFAULT_AUDIO_QUALITY = "320"  # kbps
    
    # Mood detection settings
    MOOD_MODEL_PATH = DEFAULT_CONFIG_DIR / "models" / "mood_model.joblib"
    MOOD_FEATURES_PATH = DEFAULT_CONFIG_DIR / "models" / "mood_features.joblib"
    
    # Download settings
    MAX_CONCURRENT_DOWNLOADS = 3
    RETRY_ATTEMPTS = 3
    TIMEOUT_SECONDS = 300
    
    # Queue settings
    DEFAULT_QUEUE_SIZE = 50
    MAX_DISCOVERY_TRACKS = 20
    
    def __init__(self):
        """Initialize configuration."""
        # Create default directories
        self.config_dir = Path(os.getenv("TRETA_CONFIG_DIR", self.DEFAULT_CONFIG_DIR))
        self.music_dir = Path(os.getenv("TRETA_MUSIC_DIR", self.DEFAULT_MUSIC_DIR))
        self.database_path = Path(os.getenv("TRETA_DATABASE", self.DEFAULT_DATABASE))
        self.log_dir = Path(os.getenv("TRETA_LOG_DIR", self.DEFAULT_LOG_DIR))
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "models").mkdir(parents=True, exist_ok=True)
        
        # Audio settings
        self.audio_format = os.getenv("TRETA_AUDIO_FORMAT", self.DEFAULT_AUDIO_FORMAT)
        self.audio_quality = os.getenv("TRETA_AUDIO_QUALITY", self.DEFAULT_AUDIO_QUALITY)
        
        # Other settings
        self.max_concurrent_downloads = int(os.getenv("TRETA_MAX_DOWNLOADS", self.MAX_CONCURRENT_DOWNLOADS))
        self.retry_attempts = int(os.getenv("TRETA_RETRY_ATTEMPTS", self.RETRY_ATTEMPTS))
        self.timeout_seconds = int(os.getenv("TRETA_TIMEOUT", self.TIMEOUT_SECONDS))


# Global configuration instance
config = Config()
