"""
Spotify downloader wrapper using Zotify.
Handles downloading from Spotify URLs with proper authentication.
"""

import os
import subprocess
import tempfile
import logging
import hashlib
import json
import sys
import shutil
import importlib.util
import time
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs

from db.manager import DatabaseManager
from db.models import Track
from core.auth_store import AuthStore

# Metadata extraction for file renaming
try:
    from mutagen import File as MutagenFile
    from mutagen.flac import FLAC
    from mutagen.mp3 import MP3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False


class SpotifyDownloader:
    """Wrapper for Zotify to download Spotify music."""
    
    def __init__(self, download_dir: Optional[str] = None, auth_store: Optional[AuthStore] = None, 
                 db_manager: Optional[DatabaseManager] = None):
        """Initialize Spotify downloader.
        
        Args:
            download_dir: Directory to save downloads. Defaults to downloads/spotify
            auth_store: Authentication store instance
            db_manager: Database manager instance
        """        # Check if zotify is installed
        self.zotify_available = self._check_zotify_available()
        if not self.zotify_available:
            logging.warning("Zotify not found. Spotify downloads will not work.")
            print("\n❌ Zotify module is required for Spotify downloads but was not found.")
            print("\nRecommended installation methods:")
            print("Option 1 - Install Git first, then Zotify:")
            print("1. Run: install_git.bat (CMD) or .\\install_git.ps1 (PowerShell)")
            print("2. After Git is installed: pip install git+https://github.com/zotify-dev/zotify.git")
            print("\nOption 2 - Try direct installation without Git:")
            print("1. Run: python install_zotify_no_git.py")
            print("\nThe script will guide you through the installation process.")
        
        if download_dir is None:
            download_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'downloads', 'spotify')
        
        self.download_dir = os.path.abspath(download_dir)
        self.auth_store = auth_store or AuthStore()
        self.db_manager = db_manager or DatabaseManager()
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
          # Zotify configuration
        self.config = {
            'ROOT_PATH': self.download_dir,
            'DOWNLOAD_FORMAT': 'flac',  # Use FLAC for highest quality
            'DOWNLOAD_QUALITY': 'very_high',
            'SKIP_EXISTING_FILES': True,
            'DOWNLOAD_LYRICS': False,  # Set to False to reduce errors as per Reddit guide
            'DOWNLOAD_REAL_TIME': True,  # Set to True to prevent audio key errors
            'PRINT_SPLASH': False,
            'PRINT_DOWNLOAD_PROGRESS': True,
            'PRINT_ERRORS': True,
            'PRINT_DOWNLOADS': True
        }
    
    def _check_zotify_available(self) -> bool:
        """Check if zotify module is available."""
        return importlib.util.find_spec("zotify") is not None
    
    def _get_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _parse_spotify_url(self, url: str) -> Dict[str, Any]:
        """Parse Spotify URL to extract type and ID.
        
        Args:
            url: Spotify URL
            
        Returns:
            Dictionary with 'type' and 'id' keys
        """
        try:
            # Handle both open.spotify.com and spotify: URLs
            if url.startswith('spotify:'):
                # Format: spotify:track:4iV5W9uYEdYUVa79Axb7Rh
                parts = url.split(':')
                return {'type': parts[1], 'id': parts[2]}
            else:
                # Format: https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
                path_parts = urlparse(url).path.strip('/').split('/')
                if len(path_parts) >= 2:
                    return {'type': path_parts[0], 'id': path_parts[1]}
            
            raise ValueError("Invalid Spotify URL format")            
        except Exception as e:
            self.logger.error(f"Failed to parse Spotify URL {url}: {e}")
            raise ValueError(f"Invalid Spotify URL: {url}")
    
    def _get_zotify_config_dir(self) -> str:
        """Get the Zotify configuration directory."""
        # Try local config first (avoids permission issues)
        local_config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'zotify_config')
        local_config_dir = os.path.abspath(local_config_dir)
        
        if os.path.exists(local_config_dir) and os.path.exists(os.path.join(local_config_dir, 'credentials.json')):
            return local_config_dir
        
        # Fallback to user profile directory
        return os.path.join(os.path.expanduser('~'), '.zotify')
    
    def _check_zotify_credentials(self) -> bool:
        """Check if Zotify credentials exist and are valid."""
        zotify_config_dir = self._get_zotify_config_dir()
        credentials_file = os.path.join(zotify_config_dir, 'credentials.json')
        
        if not os.path.exists(credentials_file):
            return False
        
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
              # Check if the credentials file has the required format
            required_fields = ['username', 'type', 'credentials']
            if all(field in creds for field in required_fields):
                return True
        except (json.JSONDecodeError, IOError):
            pass
        
        return False
    
    def _setup_zotify_config(self) -> str:
        """Setup Zotify configuration file.
        
        Returns:
            Path to configuration directory
        """
        zotify_config_dir = self._get_zotify_config_dir()
        
        try:
            # Ensure the config directory exists
            os.makedirs(zotify_config_dir, mode=0o755, exist_ok=True)
            
            config_file = os.path.join(zotify_config_dir, 'config.json')
            
            # Only update config if it doesn't exist or we're using local config
            if not os.path.exists(config_file) or 'zotify_config' in zotify_config_dir:
                # Write configuration
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2)
                
                # Ensure file is readable (Windows compatible)
                try:
                    os.chmod(config_file, 0o644)
                except:                    pass  # Windows may not support chmod
            
            return zotify_config_dir
            
        except Exception as e:
            self.logger.error(f"Failed to setup zotify config: {e}")
            raise
    
    def _run_zotify(self, url: str) -> subprocess.CompletedProcess:
        """Run Zotify command with proper authentication.
        
        Args:
            url: Spotify URL to download
            
        Returns:
            Subprocess result
        """
        # Check if Zotify credentials exist
        if not self._check_zotify_credentials():
            raise ValueError(self._format_credential_setup_error())
        
        # Setup Zotify configuration
        zotify_config_dir = self._setup_zotify_config()        # Run Zotify using correct command-line arguments
        # Use FLAC for highest quality, fallback to MP3 very_high
        cmd = [
            sys.executable, '-m', 'zotify',
            '--config', os.path.join(zotify_config_dir, 'zconfig.json'),
            '--credentials', os.path.join(zotify_config_dir, 'credentials.json'),
            '--output', self.download_dir,
            '--audio-format', 'flac',  # Use FLAC for highest quality
            '--download-quality', 'very_high',
            '--print-progress',  # Show progress bars
            '--print-downloads',  # Show download info
            url
        ]
        
        self.logger.info(f"Running Zotify with saved credentials from {self._get_zotify_config_dir()}")        # Ensure FFmpeg is available by adding local installation to PATH
        env = os.environ.copy()
        local_ffmpeg = os.path.join(os.path.dirname(__file__), '..', '..', 'ffmpeg', 'bin')
        local_ffmpeg = os.path.abspath(local_ffmpeg)
        if os.path.exists(local_ffmpeg):
            env['PATH'] = f"{local_ffmpeg};{env.get('PATH', '')}"
            self.logger.info(f"Added local FFmpeg to PATH: {local_ffmpeg}")
        else:
            self.logger.warning(f"Local FFmpeg not found at: {local_ffmpeg}")
            # Try to use system FFmpeg
            if not any('ffmpeg' in path.lower() for path in env.get('PATH', '').split(';')):
                self.logger.warning("FFmpeg not found in PATH. Downloads may fail at post-processing stage.")        
        try:
            # Show progress to user by not capturing stdout during download
            self.logger.info("Starting Zotify download with progress display...")
            print(f"\n🎵 Downloading: {url}")
            print("Progress will be shown below:")
            
            result = subprocess.run(
                cmd,
                cwd=self.download_dir,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=300,
                # Don't capture stdout so user can see progress
                capture_output=False,
                stderr=subprocess.PIPE  # Only capture stderr for error handling
            )
            
            # Check for specific authentication errors
            if result.returncode != 0 and result.stderr:
                if any(error in result.stderr.lower() for error in [
                    "badcredentials", "authentication", "login", "credentials", "permission denied"
                ]):
                    # For permission errors, provide specific guidance
                    if "permission denied" in result.stderr.lower():
                        error_msg = self._format_permission_error()
                    else:
                        error_msg = self._format_auth_error()
                    raise ValueError(error_msg)
            
            return result
            
        except subprocess.TimeoutExpired:
            raise ValueError("Zotify download timed out after 5 minutes. Please try again.")
        except Exception as e:
            if any(error in str(e).lower() for error in [
                "badcredentials", "authentication", "login", "credentials", "permission"
            ]):
                if "permission" in str(e).lower():
                    error_msg = self._format_permission_error()
                else:
                    error_msg = self._format_auth_error()
                raise ValueError(error_msg)
            else:
                raise
    
    def _format_permission_error(self) -> str:
        """Format error message for permission issues."""
        return """Permission denied accessing Zotify configuration directory.

This is likely due to Windows file permissions. Try these solutions:

1. Run as Administrator:
   • Right-click Command Prompt and select "Run as Administrator"
   • Run the command again

2. Check folder permissions:
   • Go to C:\\Users\\[YourUsername]\\.zotify
   • Right-click the folder → Properties → Security
   • Ensure your user has "Full Control"

3. Reset Zotify configuration:
   • Delete the .zotify folder: rmdir /s "C:\\Users\\%USERNAME%\\.zotify"
   • Run: treta auth setup-librespot (recommended)
   • Or run: python setup_zotify_credentials.py (quick fix)

4. Alternative: Use a different configuration location:
   • Set environment variable: set ZOTIFY_CONFIG_DIR=E:\\Treta\\zotify_config
   • Re-run the setup

The librespot-auth method (treta auth setup-librespot) is most reliable."""
    
    def _format_credential_setup_error(self) -> str:
        """Format error message for missing credentials setup."""
        return """Zotify credentials not found or invalid. 

To set up Spotify credentials for downloads:

1. Install Rust (required for librespot-auth):
   • Download and install from: https://rustup.rs/
   • Follow the installation instructions for Windows

2. Download librespot-auth:
   • Go to: https://github.com/dspearson/librespot-auth
   • Download the ZIP file and extract it

3. Build librespot-auth:
   • Open Command Prompt in the extracted folder
   • Run: cargo build --release

4. Generate credentials:
   • Run: .\\target\\release\\librespot-auth.exe
   • Open Spotify and change playback device to "speaker"
   • This will create a credentials.json file

5. Format the credentials file:
   • Open credentials.json in notepad
   • Format it like this:
     {
       "username": "your_generated_username_here",
       "type": "AUTHENTICATION_STORED_SPOTIFY_CREDENTIALS",
       "credentials": "your_generated_credentials_here"
     }

6. Move credentials file:
   • Copy the formatted credentials.json
   • Press Win+R, type %userprofile%\\.zotify
   • Paste the credentials.json file there
   • Create the .zotify folder if it doesn't exist

Alternative: Use 'treta auth setup-librespot' for guided setup."""
    
    def _format_auth_error(self) -> str:
        """Format a helpful error message for authentication failures."""
        return """Spotify authentication failed. This could be due to:

• Invalid or expired credentials
• Your account needs Spotify Premium for downloads
• Two-factor authentication is enabled (try using an app password)
• Too many login attempts (wait a few minutes and try again)
• Your account is restricted or suspended

Troubleshooting steps:
1. Verify your credentials are correct
2. Make sure you have a Spotify Premium subscription
3. Re-generate credentials using librespot-auth
4. Wait a few minutes if you've tried multiple times recently

Helpful commands:
• Check requirements: treta auth spotify-requirements
• Test credentials: treta auth test-zotify
• Setup credentials: treta auth setup-librespot
• Update credentials: treta auth add --service spotify"""

    def _setup_zotify_credentials(self) -> bool:
        """Setup Zotify credentials if not already configured.
        
        Returns:
            True if credentials are set up successfully
        """
        # Check if librespot-auth generated credentials exist (preferred)
        if self._check_zotify_credentials():
            self.logger.info("Zotify credentials already exist (librespot-auth)")
            return True
        
        # Fallback: try to use stored username/password credentials
        credentials = self.auth_store.get_spotify_credentials()
        if not credentials:
            return False
            
        username = credentials['username']
        password = credentials['password']
        
        zotify_config_dir = self._get_zotify_config_dir()
        credentials_file = os.path.join(zotify_config_dir, 'credentials.json')
        
        # Set up Zotify credentials by running a simple command
        self.logger.info("Setting up Zotify credentials from stored username/password...")
        
        try:
            # Create the config directory
            os.makedirs(zotify_config_dir, exist_ok=True)
            
            # Try to generate credentials using the librespot-auth format
            # This is a fallback method that may not work as reliably
            cmd = [
                sys.executable, '-m', 'zotify',
                '--username', username,
                '--password', password,
                '--save-credentials',
                '--credentials-location', zotify_config_dir,
                '--print-splash', 'false',
                '--print-errors', 'true'
            ]
            
            # Use a very short timeout since we just want to save credentials
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check if credentials were saved
            if os.path.exists(credentials_file):
                self.logger.info("Zotify credentials saved successfully")
                return True
            else:
                self.logger.error("Failed to save Zotify credentials")
                if result.stderr:
                    self.logger.error(f"Zotify error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            # Timeout might be OK if credentials were saved
            if os.path.exists(credentials_file):
                self.logger.info("Zotify credentials saved (timeout after auth)")
                return True
            else:
                self.logger.error("Zotify credential setup timed out")
                return False
        except Exception as e:
            self.logger.error(f"Failed to setup Zotify credentials: {e}")
            return False

    def download_track(self, url: str) -> Optional[Track]:
        """Download a single track from Spotify.
        
        Args:
            url: Spotify track URL
            
        Returns:
            Track object if download successful, None otherwise
        """
        try:
            # Check if already downloaded
            if self.db_manager.is_already_downloaded(url):
                self.logger.info(f"Track already downloaded: {url}")
                return None

            # Parse URL
            url_info = self._parse_spotify_url(url)
            if url_info['type'] != 'track':
                raise ValueError(f"Expected track URL, got {url_info['type']}")

            # Setup Zotify
            config_dir = self._setup_zotify_config()
            
            # Get files before download
            files_before = set(Path(self.download_dir).rglob('*'))
              # Run Zotify
            result = self._run_zotify(url)
              # Check if download succeeded even if return code is non-zero
            # The DraftKinner fork may return non-zero due to minor issues but still download the file
            download_succeeded = False
            if result.returncode == 0:
                download_succeeded = True
                print("✅ Download completed successfully!")
            else:
                # Check if there's a file that was downloaded despite non-zero return code
                recent_files = []
                for file_path in Path(self.download_dir).rglob('*'):
                    if (file_path.is_file() and 
                        file_path.suffix.lower() in ['.mp3', '.m4a', '.ogg', '.flac', '.wav'] and
                        file_path.stat().st_mtime > time.time() - 600):
                        recent_files.append(file_path)
                
                if recent_files:
                    download_succeeded = True
                    print("✅ Download completed (with minor warnings)")
                    self.logger.warning("Download completed but Zotify returned non-zero exit code (possibly FFmpeg warnings)")
                elif result.stderr and ("99%" in result.stderr or "100%" in result.stderr or "Converting audio" in result.stderr):
                    download_succeeded = True
                    print("✅ Download completed (processing finished)")
                    self.logger.warning("Download appears to have completed based on progress indicators")
            
            if not download_succeeded:
                error_msg = f"Zotify failed: {result.stderr if result.stderr else 'Unknown error'}"
                if result.stderr and "ffmpeg" in result.stderr.lower():
                    error_msg += "\n\n🔧 Note: FFmpeg is required. Run: python setup_ffmpeg_session.py"
                elif result.stderr and "login" in result.stderr.lower():
                    error_msg += "\n\n🔑 Note: Authentication may have expired. Check credentials."
                
                print(f"❌ Download failed!")
                self.logger.error(error_msg)
                self.db_manager.add_download_history(url, success=False, error_message=error_msg)
                return None
            
            # Find new files
            files_after = set(Path(self.download_dir).rglob('*'))
            new_files = files_after - files_before            # Find the downloaded audio file
            # Look for the most recently created audio file in the download directory and its parent
            audio_file = None
            download_path = Path(self.download_dir)
            
            # Search directories: specified directory and its parent (Zotify sometimes ignores --output)
            search_paths = [download_path, download_path.parent]
            
            # Get all audio files (including various formats) and sort by modification time
            audio_files = []
            for search_path in search_paths:
                if search_path.exists():
                    for file_path in search_path.rglob('*'):
                        if (file_path.is_file() and 
                            (file_path.suffix.lower() in ['.mp3', '.m4a', '.ogg', '.flac', '.wav'] or
                             '_tmp.' in file_path.name) and
                            file_path.stat().st_mtime > time.time() - 600):  # Last 10 minutes
                            audio_files.append(file_path)
            
            if audio_files:
                # Sort by modification time and get the most recent
                audio_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                most_recent = audio_files[0]
                
                # Check if it was created in the last 10 minutes (more lenient)
                if most_recent.stat().st_mtime > time.time() - 600:
                    # If it's a temporary file, try to rename it
                    if '_tmp.' in most_recent.name:
                        final_name = most_recent.name.replace('_tmp.', '.')
                        final_path = most_recent.parent / final_name
                        try:
                            most_recent.rename(final_path)
                            audio_file = final_path
                            self.logger.info(f"Renamed temporary file to: {final_path}")
                        except Exception as e:
                            self.logger.warning(f"Could not rename temporary file: {e}")
                            audio_file = most_recent
                    else:
                        audio_file = most_recent
                        
                    # Log what we found
                    self.logger.info(f"Found downloaded file: {audio_file.name} ({audio_file.stat().st_size} bytes)")
              # If still no file found, be more aggressive in searching
            if not audio_file:
                # Look for any files that might have been created, even with generic names
                all_recent_files = []
                for search_path in search_paths:
                    if search_path.exists():
                        for file_path in search_path.rglob('*'):
                            if (file_path.is_file() and 
                                file_path.stat().st_mtime > time.time() - 600 and
                                file_path.suffix.lower() in ['.mp3', '.m4a', '.ogg', '.flac', '.wav']):
                                all_recent_files.append(file_path)
                
                if all_recent_files:
                    # Use the largest recent file (likely the download)
                    audio_file = max(all_recent_files, key=lambda f: f.stat().st_size)
                    self.logger.info(f"Using largest recent file: {audio_file.name}")
            if not audio_file:
                self.logger.error("No audio file found after download")
                # Log details for debugging
                self.logger.debug(f"Files before download: {len(files_before)}")
                self.logger.debug(f"Files after download: {len(files_after)}")
                self.logger.debug(f"New files: {[str(f) for f in new_files]}")
                self.logger.debug(f"Download directory: {self.download_dir}")
                self.logger.debug(f"Recent audio files found: {len(audio_files)}")
                return None
            
            # Extract metadata and rename file before creating Track object
            audio_file = self._extract_metadata_and_rename(audio_file)
            
            # Calculate file hash
            file_hash = self._get_file_hash(str(audio_file))            # Extract metadata from the audio file
            title = "Unknown Title"
            artist = "Unknown Artist"
            album = "Unknown Album"
            
            if MUTAGEN_AVAILABLE:
                try:
                    audio_metadata = MutagenFile(str(audio_file))
                    if audio_metadata and hasattr(audio_metadata, 'tags') and audio_metadata.tags:
                        tags = audio_metadata.tags
                        
                        # FLAC/Vorbis style tags
                        if 'ARTIST' in tags:
                            artist = tags['ARTIST'][0] if isinstance(tags['ARTIST'], list) else str(tags['ARTIST'])
                        if 'TITLE' in tags:
                            title = tags['TITLE'][0] if isinstance(tags['TITLE'], list) else str(tags['TITLE'])
                        if 'ALBUM' in tags:
                            album = tags['ALBUM'][0] if isinstance(tags['ALBUM'], list) else str(tags['ALBUM'])
                        
                        # ID3 style tags (MP3)
                        if 'TPE1' in tags:  # Artist
                            artist = str(tags['TPE1'])
                        if 'TIT2' in tags:  # Title
                            title = str(tags['TIT2'])
                        if 'TALB' in tags:  # Album
                            album = str(tags['TALB'])
                except Exception as e:
                    self.logger.warning(f"Could not extract metadata from {audio_file.name}: {e}")
            
            # Fallback to filename if metadata extraction failed
            if title == "Unknown Title":
                # If the file was renamed, try to extract from filename
                if " - " in audio_file.stem:
                    parts = audio_file.stem.split(" - ", 1)
                    if len(parts) == 2:
                        artist, title = parts
                else:
                    title = audio_file.stem
            
            # Create track object
            track = Track(
                title=title,
                artist=artist,
                album=album,
                source='spotify',
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
            
        except Exception as e:
            error_msg = f"Failed to download track {url}: {e}"
            self.logger.error(error_msg)
            self.db_manager.add_download_history(url, success=False, error_message=str(e))
            return None
    
    def download_album(self, url: str) -> List[Track]:
        """Download an entire album from Spotify.
        
        Args:
            url: Spotify album URL
            
        Returns:
            List of downloaded Track objects
        """
        try:
            # Parse URL
            url_info = self._parse_spotify_url(url)
            if url_info['type'] != 'album':
                raise ValueError(f"Expected album URL, got {url_info['type']}")
            
            # Setup Zotify
            config_dir = self._setup_zotify_config()
            
            # Get files before download
            files_before = set(Path(self.download_dir).rglob('*'))
              # Run Zotify
            result = self._run_zotify(url)
            
            if result.returncode != 0:
                error_msg = f"Zotify failed: {result.stderr}"
                self.logger.error(error_msg)
                self.db_manager.add_download_history(url, success=False, error_message=error_msg)
                return []
            
            # Find new files
            files_after = set(Path(self.download_dir).rglob('*'))
            new_files = files_after - files_before
            
            # Process downloaded files
            tracks = []
            for file_path in new_files:
                if file_path.is_file() and file_path.suffix.lower() in ['.mp3', '.m4a', '.ogg']:
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
                            source='spotify',
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
            
        except Exception as e:
            error_msg = f"Failed to download album {url}: {e}"
            self.logger.error(error_msg)
            self.db_manager.add_download_history(url, success=False, error_message=str(e))
            return []
    
    def download_playlist(self, url: str) -> List[Track]:
        """Download a playlist from Spotify.
        
        Args:
            url: Spotify playlist URL
            
        Returns:
            List of downloaded Track objects
        """
        # Similar implementation to download_album but for playlists
        return self.download_album(url)  # Zotify handles playlists similarly
    
    def download_artist(self, url: str) -> List[Track]:
        """Download all albums from an artist.
        
        Args:
            url: Spotify artist URL
              Returns:
            List of downloaded Track objects
        """
        # Similar implementation to download_album but for artists
        return self.download_album(url)  # Zotify handles artists by downloading all albums
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated with Spotify for downloads."""
        if not self.zotify_available:
            return False
        
        # Check for librespot-auth generated credentials (preferred)
        if self._check_zotify_credentials():
            return True
        
        # Fallback: check for username/password credentials
        credentials = self.auth_store.get_spotify_credentials()
        return credentials is not None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove or replace invalid filename characters."""
        # Remove invalid Windows filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(c for c in filename if ord(c) >= 32)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length to avoid filesystem issues
        if len(filename) > 200:
            filename = filename[:200]
        
        return filename

    def _extract_metadata_and_rename(self, file_path: Path) -> Path:
        """Extract metadata from audio file and rename it properly."""
        if not MUTAGEN_AVAILABLE:
            self.logger.warning("Mutagen not available - keeping original filename")
            return file_path
        
        try:
            # Load metadata
            audio_file = MutagenFile(str(file_path))
            if audio_file is None:
                self.logger.warning(f"Could not read metadata from {file_path.name}")
                return file_path
            
            # Extract artist and title
            artist = None
            title = None
            
            # Try different tag formats
            if hasattr(audio_file, 'tags') and audio_file.tags:
                tags = audio_file.tags
                
                # FLAC/Vorbis style tags
                if 'ARTIST' in tags:
                    artist = tags['ARTIST'][0] if isinstance(tags['ARTIST'], list) else str(tags['ARTIST'])
                if 'TITLE' in tags:
                    title = tags['TITLE'][0] if isinstance(tags['TITLE'], list) else str(tags['TITLE'])
                
                # ID3 style tags (MP3)
                if 'TPE1' in tags:  # Artist
                    artist = str(tags['TPE1'])
                if 'TIT2' in tags:  # Title
                    title = str(tags['TIT2'])
            
            # If we couldn't get metadata, keep original name
            if not artist or not title:
                self.logger.warning(f"Incomplete metadata for {file_path.name} (artist: {artist}, title: {title})")
                return file_path
            
            # Create new filename
            new_name = f"{self._sanitize_filename(artist)} - {self._sanitize_filename(title)}{file_path.suffix}"
            new_path = file_path.parent / new_name
            
            # Rename if different
            if new_path != file_path:
                # Handle file conflicts
                counter = 1
                original_new_path = new_path
                while new_path.exists():
                    stem = original_new_path.stem
                    suffix = original_new_path.suffix
                    new_path = original_new_path.parent / f"{stem} ({counter}){suffix}"
                    counter += 1
                
                try:
                    file_path.rename(new_path)
                    self.logger.info(f"Renamed: {file_path.name} → {new_path.name}")
                    return new_path
                except Exception as e:
                    self.logger.warning(f"Could not rename {file_path.name}: {e}")
                    return file_path
            
            return file_path
            
        except Exception as e:
            self.logger.warning(f"Error processing metadata for {file_path.name}: {e}")
            return file_path
