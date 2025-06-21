"""
YouTube Music downloader wrapper using yt-dlp.
Handles downloading from YouTube Music URLs with proper audio extraction.
"""

import os
import subprocess
import logging
import hashlib
import json
import shutil
import sys
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs

from db.manager import DatabaseManager
from db.models import Track
from core.auth_store import AuthStore


class YouTubeDownloader:
    """Wrapper for yt-dlp to download YouTube Music."""
    
    def __init__(self, download_dir: Optional[str] = None, auth_store: Optional[AuthStore] = None, 
                 db_manager: Optional[DatabaseManager] = None):
        """Initialize YouTube Music downloader.
        
        Args:
            download_dir: Directory to save downloads. Defaults to downloads/youtube
            auth_store: Authentication store instance  
            db_manager: Database manager instance
        """
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'downloads', 'youtube')
        
        self.download_dir = os.path.abspath(download_dir)
        self.auth_store = auth_store or AuthStore()
        self.db_manager = db_manager or DatabaseManager()
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(c for c in filename if ord(c) >= 32)
        
        # Trim whitespace and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename
    
    def _run_ytdlp(self, url: str, output_format: str = "flac") -> subprocess.CompletedProcess:
        """Run yt-dlp command for YouTube Music download.
        
        Args:
            url: YouTube Music URL
            output_format: Audio format (flac, mp3, m4a)
            
        Returns:
            CompletedProcess result
        """
        
        # Build yt-dlp command for high-quality audio extraction
        cmd = [
            sys.executable, '-m', 'yt_dlp',
            '--extract-audio',
            '--audio-format', output_format,
            '--audio-quality', '0',  # Best quality
            '--add-metadata',
            '--embed-thumbnail',
            '--output', os.path.join(self.download_dir, '%(uploader)s', '%(title)s.%(ext)s'),
            '--no-playlist',  # Download single track only
            '--quiet',
            url
        ]
        
        self.logger.info(f"Running yt-dlp: {' '.join(cmd[:-1])} [URL_HIDDEN]")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=self.download_dir
            )
            return result
        except subprocess.TimeoutExpired:
            self.logger.error("yt-dlp command timed out")
            raise
    
    def download_track(self, url: str, format: str = "flac") -> Optional[Track]:
        """Download a single track from YouTube Music.
        
        Args:
            url: YouTube Music track URL
            format: Audio format (flac, mp3, m4a)
            
        Returns:
            Track object if successful, None otherwise
        """
        try:
            self.logger.info(f"Starting YouTube Music track download: {url}")
            
            # Get video info first
            info_cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--print-json',
                '--no-download',
                url
            ]
            
            info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=30)
            
            if info_result.returncode != 0:
                self.logger.error(f"Failed to get track info: {info_result.stderr}")
                return None
            
            # Parse track metadata
            track_info = json.loads(info_result.stdout)
            title = track_info.get('title', 'Unknown Title')
            artist = track_info.get('artist') or track_info.get('uploader', 'Unknown Artist')
            album = track_info.get('album', 'Unknown Album')
            duration = track_info.get('duration', 0)
            
            # Sanitize metadata
            title = self._sanitize_filename(title)
            artist = self._sanitize_filename(artist)
            album = self._sanitize_filename(album)
            
            self.logger.info(f"Track metadata: {artist} - {title} ({album})")
            
            # Run download
            result = self._run_ytdlp(url, format)
            
            if result.returncode != 0:
                error_msg = f"yt-dlp failed: {result.stderr}"
                self.logger.error(error_msg)
                return None
            
            # Find downloaded file
            expected_filename = f"{artist} - {title}.{format}"
            file_path = os.path.join(self.download_dir, expected_filename)
            
            # Search for downloaded file if exact name doesn't exist
            if not os.path.exists(file_path):
                # Look for any file with similar name
                pattern = f"*{title}*.{format}"
                matches = list(Path(self.download_dir).glob(pattern))
                if matches:
                    file_path = str(matches[0])
                else:
                    self.logger.error(f"Downloaded file not found: {expected_filename}")
                    return None
            
            # Verify file exists and get hash
            if not os.path.exists(file_path):
                self.logger.error(f"Downloaded file not found: {file_path}")
                return None
            
            file_hash = self._get_file_hash(file_path)
            
            # Create Track object
            track = Track(
                title=title,
                artist=artist,
                album=album,
                source="youtube",
                url=url,
                file_path=file_path,
                file_hash=file_hash,
                track_id=track_info.get('id', ''),
                duration=duration
            )
            
            # Save to database
            self.db_manager.add_track(track)
            
            self.logger.info(f"Successfully downloaded: {artist} - {title}")
            return track
            
        except Exception as e:
            self.logger.error(f"Error downloading YouTube Music track: {e}")
            return None
    
    def download_playlist(self, url: str, format: str = "flac") -> List[Track]:
        """Download all tracks from a YouTube Music playlist.
        
        Args:
            url: YouTube Music playlist URL
            format: Audio format (flac, mp3, m4a)
            
        Returns:
            List of successfully downloaded Track objects
        """
        tracks = []
        
        try:
            self.logger.info(f"Starting YouTube Music playlist download: {url}")
            
            # Get playlist info
            info_cmd = [
                sys.executable, '-m', 'yt_dlp',
                '--flat-playlist',
                '--print-json',
                '--no-download',
                url
            ]
            
            info_result = subprocess.run(info_cmd, capture_output=True, text=True, timeout=60)
            
            if info_result.returncode != 0:
                self.logger.error(f"Failed to get playlist info: {info_result.stderr}")
                return tracks
            
            # Parse playlist entries
            playlist_entries = []
            for line in info_result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        entry = json.loads(line)
                        if entry.get('_type') == 'url':
                            playlist_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            self.logger.info(f"Found {len(playlist_entries)} tracks in playlist")
            
            # Download each track
            for i, entry in enumerate(playlist_entries, 1):
                track_url = entry.get('url')
                if track_url:
                    self.logger.info(f"Downloading track {i}/{len(playlist_entries)}")
                    track = self.download_track(track_url, format)
                    if track:
                        tracks.append(track)
                    else:
                        self.logger.warning(f"Failed to download track {i}: {track_url}")
            
            self.logger.info(f"Successfully downloaded {len(tracks)}/{len(playlist_entries)} tracks")
            return tracks
            
        except Exception as e:
            self.logger.error(f"Error downloading YouTube Music playlist: {e}")
            return tracks
    
    def download_album(self, url: str, format: str = "flac") -> List[Track]:
        """Download all tracks from a YouTube Music album.
        
        Note: YouTube Music doesn't have dedicated album URLs like Spotify/Apple Music.
        This method treats album URLs the same as playlist URLs.
        
        Args:
            url: YouTube Music album/playlist URL  
            format: Audio format (flac, mp3, m4a)
            
        Returns:
            List of successfully downloaded Track objects
        """
        return self.download_playlist(url, format)
    
    def is_youtube_music_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube Music URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if valid YouTube Music URL
        """
        youtube_patterns = [
            r'music\.youtube\.com',
            r'youtube\.com/watch\?.*list=',
            r'youtube\.com/playlist\?list=',
            r'youtu\.be/',
            r'youtube\.com/watch\?v='
        ]
        
        return any(re.search(pattern, url) for pattern in youtube_patterns)
