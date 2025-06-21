"""
Apple Music downloader wrapper using GAMDL.
Handles downloading from Apple Music URLs with proper authentication.
"""

import os
import subprocess
import tempfile
import logging
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from db.manager import DatabaseManager
from db.models import Track
from core.auth_store import AuthStore


class AppleDownloader:
    """Wrapper for GAMDL to download Apple Music."""
    
    def __init__(self, download_dir: Optional[str] = None, auth_store: Optional[AuthStore] = None, 
                 db_manager: Optional[DatabaseManager] = None):
        """Initialize Apple Music downloader.
        
        Args:
            download_dir: Directory to save downloads. Defaults to downloads/apple
            auth_store: Authentication store instance
            db_manager: Database manager instance
        """
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'downloads', 'apple')
        
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
    
    def _parse_apple_url(self, url: str) -> Dict[str, Any]:
        """Parse Apple Music URL to extract type and ID.
        
        Args:
            url: Apple Music URL
            
        Returns:
            Dictionary with 'type' and 'id' keys
        """
        try:
            # Format: https://music.apple.com/us/album/album-name/1234567890?i=1234567891
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            if len(path_parts) >= 3:
                region = path_parts[0]  # 'us', 'gb', etc.
                content_type = path_parts[1]  # 'album', 'song', 'artist', etc.
                content_id = path_parts[3] if len(path_parts) > 3 else None
                
                # For individual tracks, check for 'i' parameter
                if content_type == 'album' and 'i=' in url:
                    return {'type': 'track', 'id': url.split('i=')[1].split('&')[0]}
                
                return {'type': content_type, 'id': content_id}
            
            raise ValueError("Invalid Apple Music URL format")
            
        except Exception as e:
            self.logger.error(f"Failed to parse Apple Music URL {url}: {e}")
            raise ValueError(f"Invalid Apple Music URL: {url}")
    
    def _setup_cookies_file(self) -> str:
        """Setup cookies file for GAMDL.
        
        Returns:
            Path to cookies file
        """
        cookies_data = self.auth_store.get_apple_cookies()
        if not cookies_data:
            raise ValueError("No Apple Music cookies found. Please run 'treta auth add --service apple' first.")
        
        # Create temporary cookies file
        cookies_file = os.path.join(tempfile.gettempdir(), 'treta_apple_cookies.txt')
        with open(cookies_file, 'w') as f:
            f.write(cookies_data)
        
        return cookies_file
    
    def _get_mp4decrypt_path(self) -> str:
        """Get the path to mp4decrypt binary.
        
        Returns:
            Path to mp4decrypt executable
        """
        # Check if mp4decrypt is in the project binaries directory
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        local_mp4decrypt = os.path.join(project_dir, 'binaries', 'mp4decrypt.exe')
        
        if os.path.exists(local_mp4decrypt):
            return local_mp4decrypt
        
        # Fallback to system PATH
        return 'mp4decrypt'
    
    def _run_gamdl(self, url: str, cookies_file: str) -> subprocess.CompletedProcess:
        """Run GAMDL command with proper authentication.
        
        Args:
            url: Apple Music URL to download
            cookies_file: Path to cookies file
              Returns:
            Subprocess result
        """
        cmd = [
            sys.executable, '-m', 'gamdl',
            '--cookies-path', cookies_file,
            '--output-path', self.download_dir,
            '--codec-song', 'aac-legacy',  # Use stable AAC codec instead of experimental ALAC
            '--save-cover',
            '--no-config-file',
            '--mp4decrypt-path', self._get_mp4decrypt_path(),  # Add mp4decrypt path
            '--template-folder-album', '{artist}',  # Organize by artist only
            '--template-folder-no-album', '{artist}',  # For tracks not in albums
            '--template-file-single-disc', '{title}.m4a',  # Single disc albums
            '--template-file-multi-disc', '{track_num:02d} {title}.m4a',  # Multi disc albums
            '--template-file-no-album', '{title}.m4a',  # Tracks not in albums
            url
        ]
        self.logger.info(f"Running GAMDL: {' '.join(cmd[:-1])} [URL_HIDDEN]")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for Apple Music
        )
        
        return result
    
    def _run_gamdl_with_progress(self, url: str, cookies_file: str, progress_callback=None) -> subprocess.CompletedProcess:
        """Run GAMDL command with real-time progress updates.
        
        Args:
            url: Apple Music URL to download
            cookies_file: Path to cookies file
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Subprocess result
        """
        cmd = [
            sys.executable, '-m', 'gamdl',
            '--cookies-path', cookies_file,
            '--output-path', self.download_dir,
            '--codec-song', 'aac-legacy',  # Use stable AAC codec
            '--save-cover',
            '--no-config-file',
            '--mp4decrypt-path', self._get_mp4decrypt_path(),
            '--template-folder-album', '{artist}',
            '--template-folder-no-album', '{artist}',
            '--template-file-single-disc', '{title}.m4a',
            '--template-file-multi-disc', '{track_num:02d} {title}.m4a',
            '--template-file-no-album', '{title}.m4a',
            url
        ]
        
        self.logger.info(f"Running GAMDL with progress: {' '.join(cmd[:-1])} [URL_HIDDEN]")
        
        # Use Popen for real-time output streaming
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        output_lines = []
        if process.stdout:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    output_lines.append(line)
                    
                    # Update progress based on GAMDL output
                    if progress_callback:
                        if 'Starting Gamdl' in line:
                            progress_callback("🍎 Initializing...", 30)
                        elif 'Checking' in line and 'URL' in line:
                            progress_callback("🔍 Validating URL...", 40)
                        elif 'Downloading' in line and 'Track' in line:
                            progress_callback("📥 Downloading track...", 50)
                        elif 'Converting' in line or 'Remuxing' in line:
                            progress_callback("🎶 Processing audio...", 80)
                        elif 'Done' in line:
                            progress_callback("✅ Download completed!", 100)
          # Wait for process to complete
        process.wait()
        
        # Create a result object similar to subprocess.run
        result = subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout='\n'.join(output_lines),
            stderr='\n'.join(output_lines)  # GAMDL outputs to stdout
        )
        
        return result
    
    def download_track(self, url: str, progress_callback=None) -> Optional[Track]:
        """Download a single track from Apple Music.
        
        Args:
            url: Apple Music track URL
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Track object if download successful, None otherwise
        """
        try:
            # Check if already downloaded
            if self.db_manager.is_already_downloaded(url):
                self.logger.info(f"Track already downloaded: {url}")
                return None
            
            # Parse URL
            url_info = self._parse_apple_url(url)
            if url_info['type'] not in ['track', 'song']:
                raise ValueError(f"Expected track URL, got {url_info['type']}")
            
            # Setup cookies
            cookies_file = self._setup_cookies_file()
            
            try:
                # Get files before download
                files_before = set(Path(self.download_dir).rglob('*'))
                  # Run GAMDL
                result = self._run_gamdl(url, cookies_file)
                
                if result.returncode != 0:
                    error_msg = f"GAMDL failed: {result.stderr}"
                    self.logger.error(error_msg)
                    
                    # Check for specific error types
                    stderr_text = result.stderr.lower()
                    if "status\":-1002" in stderr_text:
                        error_msg = "Track not available - likely due to region restrictions or subscription requirements"
                    elif "widevine" in stderr_text or "drm" in stderr_text:
                        error_msg = "DRM/licensing error - track may not be available for download"
                    elif "authentication" in stderr_text or "login" in stderr_text:
                        error_msg = "Authentication failed - please re-run: python treta.py auth add --service apple"
                    
                    self.db_manager.add_download_history(url, success=False, error_message=error_msg)
                    print(f"ERROR: {error_msg}")
                    return None                # Find new files
                files_after = set(Path(self.download_dir).rglob('*'))
                new_files = files_after - files_before
                
                # Find the downloaded audio file
                audio_file = None
                for file_path in new_files:
                    if file_path.is_file() and file_path.suffix.lower() in ['.m4a', '.aac', '.mp3']:
                        audio_file = file_path
                        break
                
                if not audio_file:
                    self.logger.error("No audio file found after download")
                    return None
                
                # Calculate file hash
                file_hash = self._get_file_hash(str(audio_file))
                
                # Extract metadata from filename/path
                # GAMDL typically saves as: Artist/Album/Track.m4a
                relative_path = audio_file.relative_to(self.download_dir)
                path_parts = relative_path.parts
                
                if len(path_parts) >= 3:
                    artist = path_parts[0]
                    album = path_parts[1]
                    title = Path(path_parts[2]).stem
                else:
                    # Fallback parsing
                    title = audio_file.stem
                    artist = "Unknown Artist"
                    album = "Unknown Album"
                
                # Create track object
                track = Track(
                    title=title,
                    artist=artist,
                    album=album,
                    source='apple',
                    url=url,
                    file_path=str(audio_file),
                    file_hash=file_hash,
                    track_id=url_info['id']
                )
                
                # Save to database
                track_id = self.db_manager.add_track(track)
                track.id = track_id
                
                # Add to download history
                self.db_manager.add_download_history(url, file_hash, success=True)
                
                self.logger.info(f"Successfully downloaded: {artist} - {title}")
                return track
                
            finally:
                # Cleanup cookies file
                if os.path.exists(cookies_file):
                    os.unlink(cookies_file)
            
        except Exception as e:
            error_msg = f"Failed to download track {url}: {e}"
            self.logger.error(error_msg)
            self.db_manager.add_download_history(url, success=False, error_message=str(e))
            return None
    
    def download_album(self, url: str) -> List[Track]:
        """Download an entire album from Apple Music.
        
        Args:
            url: Apple Music album URL
            
        Returns:
            List of downloaded Track objects
        """
        try:
            # Parse URL
            url_info = self._parse_apple_url(url)
            if url_info['type'] != 'album':
                raise ValueError(f"Expected album URL, got {url_info['type']}")
            
            # Setup cookies
            cookies_file = self._setup_cookies_file()
            
            try:
                # Get files before download
                files_before = set(Path(self.download_dir).rglob('*'))
                
                # Run GAMDL
                result = self._run_gamdl(url, cookies_file)
                
                if result.returncode != 0:
                    error_msg = f"GAMDL failed: {result.stderr}"
                    self.logger.error(error_msg)
                    self.db_manager.add_download_history(url, success=False, error_message=error_msg)
                    return []
                
                # Find new files
                files_after = set(Path(self.download_dir).rglob('*'))
                new_files = files_after - files_before
                
                # Process downloaded files
                tracks = []
                for file_path in new_files:
                    if file_path.is_file() and file_path.suffix.lower() in ['.m4a', '.aac', '.mp3']:
                        try:
                            # Calculate file hash
                            file_hash = self._get_file_hash(str(file_path))
                            
                            # Check if already in database
                            existing_track = self.db_manager.get_track_by_hash(file_hash)
                            if existing_track:
                                continue
                            
                            # Extract metadata
                            relative_path = file_path.relative_to(self.download_dir)
                            path_parts = relative_path.parts
                            
                            if len(path_parts) >= 3:
                                artist = path_parts[0]
                                album = path_parts[1]
                                title = Path(path_parts[2]).stem
                            else:
                                title = file_path.stem
                                artist = "Unknown Artist"
                                album = "Unknown Album"
                            
                            # Create track object
                            track = Track(
                                title=title,
                                artist=artist,
                                album=album,
                                source='apple',
                                url=url,  # Album URL for reference
                                file_path=str(file_path),
                                file_hash=file_hash,
                                album_id=url_info['id']
                            )
                            
                            # Save to database
                            track_id = self.db_manager.add_track(track)
                            track.id = track_id
                            tracks.append(track)
                            
                        except Exception as e:
                            self.logger.error(f"Failed to process file {file_path}: {e}")
                
                # Add to download history
                self.db_manager.add_download_history(url, success=True)
                
                self.logger.info(f"Successfully downloaded album with {len(tracks)} tracks")
                return tracks
                
            finally:
                # Cleanup cookies file
                if os.path.exists(cookies_file):
                    os.unlink(cookies_file)
            
        except Exception as e:
            error_msg = f"Failed to download album {url}: {e}"
            self.logger.error(error_msg)
            self.db_manager.add_download_history(url, success=False, error_message=str(e))
            return []
    
    def download_playlist(self, url: str) -> List[Track]:
        """Download a playlist from Apple Music.
        
        Args:
            url: Apple Music playlist URL
            
        Returns:
            List of downloaded Track objects
        """
        # Similar implementation to download_album but for playlists
        return self.download_album(url)  # GAMDL handles playlists similarly
    
    def download_artist(self, url: str) -> List[Track]:
        """Download all albums from an artist.
        
        Args:
            url: Apple Music artist URL
            
        Returns:
            List of downloaded Track objects
        """
        # Similar implementation to download_album but for artists
        return self.download_album(url)  # GAMDL handles artists by downloading all albums
    
    def is_authenticated(self) -> bool:
        """Check if Apple Music authentication is available and valid."""
        return self.auth_store.test_apple_auth()
