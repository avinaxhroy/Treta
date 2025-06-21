"""
Metadata extraction and management for Treta.
Handles audio file metadata using various libraries.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON
    from mutagen.mp4 import MP4
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
except ImportError:
    raise ImportError("mutagen is required for metadata operations. Install with: pip install mutagen")

from db.models import Track


class MetadataManager:
    """Manages audio file metadata extraction and modification."""
    
    def __init__(self):
        """Initialize metadata manager."""
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary of metadata
        """
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                self.logger.warning(f"Could not read metadata from {file_path}")
                return {}
            
            metadata = {
                'title': self._extract_field(audio_file, ['TIT2', 'TITLE', '\xa9nam']),
                'artist': self._extract_field(audio_file, ['TPE1', 'ARTIST', '\xa9ART']),
                'album': self._extract_field(audio_file, ['TALB', 'ALBUM', '\xa9alb']),
                'date': self._extract_field(audio_file, ['TDRC', 'DATE', '\xa9day']),
                'genre': self._extract_field(audio_file, ['TCON', 'GENRE', '\xa9gen']),
                'track_number': self._extract_field(audio_file, ['TRCK', 'TRACKNUMBER', 'trkn']),
                'album_artist': self._extract_field(audio_file, ['TPE2', 'ALBUMARTIST', 'aART']),
                'duration': getattr(audio_file, 'info', None) and getattr(audio_file.info, 'length', None),
                'bitrate': getattr(audio_file, 'info', None) and getattr(audio_file.info, 'bitrate', None),
                'format': audio_file.mime[0] if hasattr(audio_file, 'mime') and audio_file.mime else None
            }
            
            # Clean up None values and convert to strings
            metadata = {k: str(v) if v is not None else None for k, v in metadata.items()}
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {}
    
    def _extract_field(self, audio_file, field_names: list) -> Optional[str]:
        """Extract a field from audio file using multiple possible field names.
        
        Args:
            audio_file: Mutagen audio file object
            field_names: List of possible field names to try
            
        Returns:
            Field value as string or None
        """
        for field_name in field_names:
            try:
                if field_name in audio_file:
                    value = audio_file[field_name]
                    if isinstance(value, list) and value:
                        value = value[0]
                    if hasattr(value, 'text'):
                        value = value.text[0] if value.text else None
                    return str(value) if value else None
            except (KeyError, IndexError, AttributeError):
                continue
        return None
    
    def update_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata in audio file.
        
        Args:
            file_path: Path to audio file
            metadata: Dictionary of metadata to update
            
        Returns:
            True if update successful
        """
        try:
            audio_file = MutagenFile(file_path)
            if audio_file is None:
                self.logger.error(f"Could not open {file_path} for metadata update")
                return False
            
            # Update based on file type
            if isinstance(audio_file, MP4):
                self._update_mp4_metadata(audio_file, metadata)
            elif hasattr(audio_file, 'tags') and audio_file.tags is not None:
                self._update_id3_metadata(audio_file, metadata)
            else:
                self.logger.warning(f"Unsupported file type for metadata update: {file_path}")
                return False
            
            audio_file.save()
            self.logger.info(f"Updated metadata for {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update metadata for {file_path}: {e}")
            return False
    
    def _update_mp4_metadata(self, audio_file: MP4, metadata: Dict[str, Any]):
        """Update MP4/M4A metadata."""
        mapping = {
            'title': '\xa9nam',
            'artist': '\xa9ART',
            'album': '\xa9alb',
            'date': '\xa9day',
            'genre': '\xa9gen',
            'album_artist': 'aART'
        }
        
        for key, value in metadata.items():
            if key in mapping and value:
                audio_file.tags[mapping[key]] = [str(value)]
    
    def _update_id3_metadata(self, audio_file, metadata: Dict[str, Any]):
        """Update ID3 metadata for MP3 files."""
        if not hasattr(audio_file, 'tags') or audio_file.tags is None:
            audio_file.add_tags()
        
        mapping = {
            'title': TIT2,
            'artist': TPE1,
            'album': TALB,
            'date': TDRC,
            'genre': TCON
        }
        
        for key, value in metadata.items():
            if key in mapping and value:
                audio_file.tags[mapping[key].__name__] = mapping[key](encoding=3, text=[str(value)])
    
    def enrich_track_metadata(self, track: Track) -> Track:
        """Enrich track object with metadata from file.
        
        Args:
            track: Track object to enrich
            
        Returns:
            Updated track object
        """
        if not track.file_path or not os.path.exists(track.file_path):
            return track
        
        try:
            metadata = self.extract_metadata(track.file_path)
            
            # Update track fields if metadata is better
            if metadata.get('title') and not track.title:
                track.title = metadata['title']
            
            if metadata.get('artist') and not track.artist:
                track.artist = metadata['artist']
            
            if metadata.get('album') and not track.album:
                track.album = metadata['album']
            
            if metadata.get('duration'):
                try:
                    track.duration = int(float(metadata['duration']))
                except (ValueError, TypeError):
                    pass
            
            return track
            
        except Exception as e:
            self.logger.error(f"Failed to enrich track metadata: {e}")
            return track
    
    def add_treta_metadata(self, file_path: str, track: Track) -> bool:
        """Add Treta-specific metadata to audio file.
        
        Args:
            file_path: Path to audio file
            track: Track object with Treta metadata
            
        Returns:
            True if successful
        """
        try:
            metadata = {
                'comment': f"Downloaded by Treta from {track.source}",
                'source': track.source,
                'download_date': datetime.now().isoformat()
            }
            
            if track.mood:
                metadata['mood'] = track.mood
            
            return self.update_metadata(file_path, metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to add Treta metadata: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with file information
        """
        try:
            file_stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            # Basic file info
            info = {
                'file_name': path_obj.name,
                'file_size': file_stat.st_size,
                'file_extension': path_obj.suffix.lower(),
                'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                'modified_at': datetime.fromtimestamp(file_stat.st_mtime),
                'file_size_mb': round(file_stat.st_size / (1024 * 1024), 2)
            }
            
            # Audio info
            try:
                audio_file = MutagenFile(file_path)
                if audio_file and hasattr(audio_file, 'info'):
                    info.update({
                        'duration': getattr(audio_file.info, 'length', None),
                        'bitrate': getattr(audio_file.info, 'bitrate', None),
                        'sample_rate': getattr(audio_file.info, 'sample_rate', None),
                        'channels': getattr(audio_file.info, 'channels', None),
                        'format': audio_file.mime[0] if hasattr(audio_file, 'mime') and audio_file.mime else None
                    })
            except Exception:
                pass
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {e}")
            return {}
    
    def validate_audio_file(self, file_path: str) -> bool:
        """Validate if file is a supported audio file.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if valid audio file
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            audio_file = MutagenFile(file_path)
            return audio_file is not None
            
        except Exception:
            return False
