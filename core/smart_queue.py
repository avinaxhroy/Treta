"""
Smart queue generation for Treta.
Creates intelligent playlists based on mood, behavior, and preferences.
"""

import random
import logging
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from db.manager import DatabaseManager
from db.models import Track, MOOD_CATEGORIES


class SmartQueue:
    """Generates intelligent music queues based on user behavior and mood."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize smart queue generator.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager or DatabaseManager()
        self.logger = logging.getLogger(__name__)
    
    def generate_mood_queue(self, mood: str, limit: int = 50) -> List[Track]:
        """Generate queue based on mood.
        
        Args:
            mood: Target mood category
            limit: Maximum number of tracks
            
        Returns:
            List of tracks matching the mood
        """
        try:
            # Get tracks with matching mood
            tracks = []
            all_tracks = self.db_manager.get_all_tracks()
            
            # Filter by exact mood match
            mood_tracks = [t for t in all_tracks if t.mood == mood]
            
            # If not enough tracks, include similar moods
            if len(mood_tracks) < limit:
                similar_moods = self._get_similar_moods(mood)
                for similar_mood in similar_moods:
                    similar_tracks = [t for t in all_tracks if t.mood == similar_mood]
                    mood_tracks.extend(similar_tracks)
                    if len(mood_tracks) >= limit:
                        break
            
            # Sort by play count and randomize
            mood_tracks.sort(key=lambda x: x.play_count, reverse=True)
            
            # Take top tracks and add some randomization
            if len(mood_tracks) > limit:
                top_tracks = mood_tracks[:limit//2]
                random_tracks = random.sample(mood_tracks[limit//2:], min(limit//2, len(mood_tracks[limit//2:])))
                tracks = top_tracks + random_tracks
            else:
                tracks = mood_tracks
            
            # Shuffle final selection
            random.shuffle(tracks)
            
            # Create queue
            track_ids = [t.id for t in tracks[:limit]]
            self.db_manager.create_smart_queue(track_ids, f'mood_{mood}')
            
            self.logger.info(f"Generated mood queue '{mood}' with {len(tracks)} tracks")
            return tracks[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to generate mood queue: {e}")
            return []
    
    def generate_artist_queue(self, artist_name: str, limit: int = 30) -> List[Track]:
        """Generate queue based on artist and similar artists.
        
        Args:
            artist_name: Target artist name
            limit: Maximum number of tracks
            
        Returns:
            List of tracks from artist and similar artists
        """
        try:
            all_tracks = self.db_manager.get_all_tracks()
            
            # Get tracks from exact artist
            artist_tracks = [t for t in all_tracks if t.artist.lower() == artist_name.lower()]
            
            # If not enough, find similar artists based on user behavior
            if len(artist_tracks) < limit:
                # Find users who like this artist and see what other artists they like
                similar_artists = self._find_similar_artists(artist_name, all_tracks)
                
                for similar_artist in similar_artists:
                    similar_tracks = [t for t in all_tracks if t.artist.lower() == similar_artist.lower()]
                    artist_tracks.extend(similar_tracks)
                    if len(artist_tracks) >= limit:
                        break
            
            # Sort by play count and add variety
            artist_tracks.sort(key=lambda x: x.play_count, reverse=True)
            
            # Mix popular and less played tracks
            if len(artist_tracks) > limit:
                popular = artist_tracks[:limit//3]
                medium = artist_tracks[limit//3:2*limit//3]
                random_selection = random.sample(medium, min(limit//3, len(medium)))
                tracks = popular + random_selection
                
                # Add some completely random tracks from the artist
                remaining = [t for t in artist_tracks if t not in tracks]
                if remaining:
                    random_tracks = random.sample(remaining, min(limit//3, len(remaining)))
                    tracks.extend(random_tracks)
            else:
                tracks = artist_tracks
            
            # Shuffle and limit
            random.shuffle(tracks)
            tracks = tracks[:limit]
            
            # Create queue
            track_ids = [t.id for t in tracks]
            self.db_manager.create_smart_queue(track_ids, f'artist_{artist_name.replace(" ", "_").lower()}')
            
            self.logger.info(f"Generated artist queue for '{artist_name}' with {len(tracks)} tracks")
            return tracks
            
        except Exception as e:
            self.logger.error(f"Failed to generate artist queue: {e}")
            return []
    
    def generate_discovery_queue(self, limit: int = 25) -> List[Track]:
        """Generate discovery queue with less-played tracks.
        
        Args:
            limit: Maximum number of tracks
            
        Returns:
            List of tracks for discovery
        """
        try:
            all_tracks = self.db_manager.get_all_tracks()
            
            # Filter tracks with low play count
            discovery_tracks = [t for t in all_tracks if t.play_count < 3]
            
            # If not enough, include tracks with moderate play count
            if len(discovery_tracks) < limit:
                moderate_tracks = [t for t in all_tracks if 3 <= t.play_count < 10]
                discovery_tracks.extend(moderate_tracks)
            
            # Sort by recency (newer downloads first) and add randomization
            discovery_tracks.sort(key=lambda x: x.downloaded_at or datetime.min, reverse=True)
            
            # Select tracks with variety
            selected_tracks = []
            used_artists = set()
            
            # First pass: one track per artist
            for track in discovery_tracks:
                if track.artist not in used_artists:
                    selected_tracks.append(track)
                    used_artists.add(track.artist)
                    if len(selected_tracks) >= limit:
                        break
            
            # Second pass: fill remaining slots
            if len(selected_tracks) < limit:
                remaining = [t for t in discovery_tracks if t not in selected_tracks]
                random.shuffle(remaining)
                selected_tracks.extend(remaining[:limit - len(selected_tracks)])
            
            # Create queue
            track_ids = [t.id for t in selected_tracks]
            self.db_manager.create_smart_queue(track_ids, 'discovery')
            
            self.logger.info(f"Generated discovery queue with {len(selected_tracks)} tracks")
            return selected_tracks
            
        except Exception as e:
            self.logger.error(f"Failed to generate discovery queue: {e}")
            return []
    
    def generate_favorites_queue(self, limit: int = 40) -> List[Track]:
        """Generate queue based on most played and recently played tracks.
        
        Args:
            limit: Maximum number of tracks
            
        Returns:
            List of favorite tracks
        """
        try:
            all_tracks = self.db_manager.get_all_tracks()
            
            # Get most played tracks
            most_played = sorted(all_tracks, key=lambda x: x.play_count, reverse=True)[:limit//2]
            
            # Get recently played tracks
            recent_cutoff = datetime.now() - timedelta(days=30)
            recently_played = [
                t for t in all_tracks 
                if t.last_played and t.last_played > recent_cutoff
            ]
            recently_played.sort(key=lambda x: x.last_played or datetime.min, reverse=True)
            recently_played = recently_played[:limit//2]
            
            # Combine and deduplicate
            favorites = list({t.id: t for t in (most_played + recently_played)}.values())
            
            # Sort by a combination of play count and recency
            def favorite_score(track):
                play_score = track.play_count * 10
                recency_score = 0
                if track.last_played:
                    days_ago = (datetime.now() - track.last_played).days
                    recency_score = max(0, 30 - days_ago)
                return play_score + recency_score
            
            favorites.sort(key=favorite_score, reverse=True)
            favorites = favorites[:limit]
            
            # Add some shuffle
            random.shuffle(favorites)
            
            # Create queue
            track_ids = [t.id for t in favorites]
            self.db_manager.create_smart_queue(track_ids, 'favorites')
            
            self.logger.info(f"Generated favorites queue with {len(favorites)} tracks")
            return favorites
            
        except Exception as e:
            self.logger.error(f"Failed to generate favorites queue: {e}")
            return []
    
    def generate_mixed_queue(self, limit: int = 50) -> List[Track]:
        """Generate mixed queue with variety from different categories.
        
        Args:
            limit: Maximum number of tracks
            
        Returns:
            List of mixed tracks
        """
        try:
            tracks = []
            
            # Get a mix from different sources
            favorites = self.generate_favorites_queue(limit=limit//4)
            discovery = self.generate_discovery_queue(limit=limit//4)
            
            # Get random mood queue
            available_moods = list(self.db_manager.get_stats().get('mood_breakdown', {}).keys())
            if available_moods:
                random_mood = random.choice(available_moods)
                mood_tracks = self.generate_mood_queue(random_mood, limit=limit//4)
            else:
                mood_tracks = []
            
            # Fill remainder with random tracks
            all_tracks = self.db_manager.get_all_tracks()
            used_ids = {t.id for t in (favorites + discovery + mood_tracks)}
            remaining_tracks = [t for t in all_tracks if t.id not in used_ids]
            random.shuffle(remaining_tracks)
            
            # Combine all
            mixed_tracks = favorites + discovery + mood_tracks + remaining_tracks
            mixed_tracks = mixed_tracks[:limit]
            
            # Final shuffle
            random.shuffle(mixed_tracks)
            
            # Create queue
            track_ids = [t.id for t in mixed_tracks]
            self.db_manager.create_smart_queue(track_ids, 'mixed')
            
            self.logger.info(f"Generated mixed queue with {len(mixed_tracks)} tracks")
            return mixed_tracks
            
        except Exception as e:
            self.logger.error(f"Failed to generate mixed queue: {e}")
            return []
    
    def get_next_track(self, queue_type: str = 'default') -> Optional[Track]:
        """Get next track from queue.
        
        Args:
            queue_type: Type of queue to get from
            
        Returns:
            Next track or None
        """
        return self.db_manager.get_next_in_queue(queue_type)
    
    def remove_from_queue(self, track_id: int, queue_type: str = 'default'):
        """Remove track from queue.
        
        Args:
            track_id: Track ID to remove
            queue_type: Queue type to remove from
        """
        self.db_manager.remove_from_queue(track_id, queue_type)
    
    def _get_similar_moods(self, mood: str) -> List[str]:
        """Get similar moods for the given mood.
        
        Args:
            mood: Base mood
            
        Returns:
            List of similar moods
        """
        mood_similarity = {
            'happy': ['upbeat', 'energetic', 'romantic'],
            'sad': ['melancholic', 'calm'],
            'energetic': ['upbeat', 'intense', 'happy'],
            'calm': ['chill', 'romantic', 'melancholic'],
            'angry': ['intense', 'energetic'],
            'romantic': ['calm', 'happy', 'chill'],
            'melancholic': ['sad', 'calm'],
            'upbeat': ['happy', 'energetic'],
            'chill': ['calm', 'romantic'],
            'intense': ['angry', 'energetic']
        }
        
        return mood_similarity.get(mood, [])
    
    def _find_similar_artists(self, artist_name: str, all_tracks: List[Track]) -> List[str]:
        """Find similar artists based on user listening patterns.
        
        Args:
            artist_name: Target artist
            all_tracks: All available tracks
            
        Returns:
            List of similar artist names
        """
        # Simple approach: find artists that appear in the same albums/playlists
        # or have similar play patterns
        
        target_tracks = [t for t in all_tracks if t.artist.lower() == artist_name.lower()]
        if not target_tracks:
            return []
        
        # Find artists with similar play counts
        avg_play_count = sum(t.play_count for t in target_tracks) / len(target_tracks)
        
        artist_stats = defaultdict(list)
        for track in all_tracks:
            if track.artist.lower() != artist_name.lower():
                artist_stats[track.artist].append(track.play_count)
        
        similar_artists = []
        for artist, play_counts in artist_stats.items():
            if len(play_counts) >= 2:  # At least 2 tracks
                avg_artist_plays = sum(play_counts) / len(play_counts)
                # Similar play pattern (within 50% range)
                if abs(avg_artist_plays - avg_play_count) / max(avg_play_count, 1) < 0.5:
                    similar_artists.append(artist)
        
        return similar_artists[:5]  # Return top 5 similar artists
