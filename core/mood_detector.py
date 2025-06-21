"""
Mood detection for Treta using librosa and scikit-learn.
Analyzes audio features to classify tracks by mood.
"""

import os
import logging
import numpy as np
import joblib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

try:
    import librosa
    import librosa.display
except ImportError:
    raise ImportError("librosa is required for mood detection. Install with: pip install librosa")

from db.manager import DatabaseManager
from db.models import Track, MOOD_CATEGORIES


class MoodDetector:
    """Audio mood detection using machine learning."""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Initialize mood detector.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager or DatabaseManager()
        self.logger = logging.getLogger(__name__)
        
        # ML components
        self.classifier = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'tempo', 'spectral_centroid_mean', 'spectral_centroid_std',
            'spectral_rolloff_mean', 'spectral_rolloff_std',
            'zero_crossing_rate_mean', 'zero_crossing_rate_std',
            'mfcc_1_mean', 'mfcc_1_std', 'mfcc_2_mean', 'mfcc_2_std',
            'mfcc_3_mean', 'mfcc_3_std', 'mfcc_4_mean', 'mfcc_4_std',
            'mfcc_5_mean', 'mfcc_5_std', 'chroma_mean', 'chroma_std',
            'rmse_mean', 'rmse_std'
        ]
        
        # Model path
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, 'mood_model.joblib')
        self.scaler_path = os.path.join(self.model_dir, 'mood_scaler.joblib')
        
        # Load existing model if available
        self._load_model()
    
    def extract_features(self, audio_file: str, duration: Optional[float] = 30.0) -> Dict[str, float]:
        """Extract audio features from a file.
        
        Args:
            audio_file: Path to audio file
            duration: Duration to analyze (None for full file)
            
        Returns:
            Dictionary of extracted features
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_file, duration=duration)
            
            # Tempo
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCCs (first 5 coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=5)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # RMS energy
            rmse = librosa.feature.rms(y=y)[0]
            
            # Compile features
            features = {
                'tempo': float(tempo),
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'spectral_centroid_std': float(np.std(spectral_centroids)),
                'spectral_rolloff_mean': float(np.mean(spectral_rolloff)),
                'spectral_rolloff_std': float(np.std(spectral_rolloff)),
                'zero_crossing_rate_mean': float(np.mean(zcr)),
                'zero_crossing_rate_std': float(np.std(zcr)),
                'rmse_mean': float(np.mean(rmse)),
                'rmse_std': float(np.std(rmse)),
                'chroma_mean': float(np.mean(chroma)),
                'chroma_std': float(np.std(chroma))
            }
            
            # Add MFCC features
            for i in range(5):
                features[f'mfcc_{i+1}_mean'] = float(np.mean(mfccs[i]))
                features[f'mfcc_{i+1}_std'] = float(np.std(mfccs[i]))
            
            return features
            
        except Exception as e:
            self.logger.error(f"Failed to extract features from {audio_file}: {e}")
            return {}
    
    def predict_mood(self, audio_file: str) -> Tuple[Optional[str], float]:
        """Predict mood of an audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Tuple of (predicted_mood, confidence)
        """
        if not self.classifier:
            self.logger.warning("No trained model available for mood prediction")
            return None, 0.0
        
        try:
            # Extract features
            features = self.extract_features(audio_file)
            if not features:
                return None, 0.0
            
            # Prepare feature vector
            feature_vector = np.array([features[name] for name in self.feature_names]).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict
            prediction = self.classifier.predict(feature_vector_scaled)[0]
            probabilities = self.classifier.predict_proba(feature_vector_scaled)[0]
            confidence = float(np.max(probabilities))
            
            return prediction, confidence
            
        except Exception as e:
            self.logger.error(f"Failed to predict mood for {audio_file}: {e}")
            return None, 0.0
    
    def analyze_track(self, track: Track) -> bool:
        """Analyze mood for a track and update database.
        
        Args:
            track: Track object to analyze
            
        Returns:
            True if analysis successful
        """
        if not track.file_path or not os.path.exists(track.file_path):
            self.logger.error(f"Audio file not found: {track.file_path}")
            return False
        
        try:
            # Extract features and store them
            features = self.extract_features(track.file_path)
            if features:
                # Update track with audio features
                track.audio_features = features
                
                # Predict mood if model is available
                mood, confidence = self.predict_mood(track.file_path)
                if mood and confidence > 0.6:  # Only update if confident
                    track.mood = mood
                    self.db_manager.update_track_mood(track.id, mood)
                    self.logger.info(f"Predicted mood '{mood}' for {track.title} (confidence: {confidence:.2f})")
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to analyze track {track.title}: {e}")
            return False
    
    def train_model(self, use_existing_data: bool = True) -> bool:
        """Train mood classification model.
        
        Args:
            use_existing_data: Whether to use existing mood labels from database
            
        Returns:
            True if training successful
        """
        try:
            # Collect training data
            training_data = []
            training_labels = []
            
            if use_existing_data:
                # Get tracks with mood labels
                tracks = self.db_manager.get_all_tracks()
                for track in tracks:
                    if track.mood and track.audio_features:
                        # Extract feature vector
                        try:
                            feature_vector = [track.audio_features[name] for name in self.feature_names]
                            training_data.append(feature_vector)
                            training_labels.append(track.mood)
                        except KeyError:
                            # Re-extract features if not complete
                            if track.file_path and os.path.exists(track.file_path):
                                features = self.extract_features(track.file_path)
                                if features:
                                    feature_vector = [features[name] for name in self.feature_names]
                                    training_data.append(feature_vector)
                                    training_labels.append(track.mood)
            
            if len(training_data) < 10:
                self.logger.warning("Not enough training data for mood classification")
                return False
            
            # Convert to numpy arrays
            X = np.array(training_data)
            y = np.array(training_labels)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train classifier
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                class_weight='balanced'
            )
            self.classifier.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = self.classifier.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.logger.info(f"Mood classification model trained with accuracy: {accuracy:.3f}")
            self.logger.info(f"Training data: {len(training_data)} samples")
            
            # Save model
            self._save_model()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to train mood model: {e}")
            return False
    
    def _save_model(self):
        """Save trained model to disk."""
        try:
            if self.classifier:
                joblib.dump(self.classifier, self.model_path)
                joblib.dump(self.scaler, self.scaler_path)
                self.logger.info("Mood model saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save mood model: {e}")
    
    def _load_model(self):
        """Load trained model from disk."""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.classifier = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.logger.info("Mood model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load mood model: {e}")
    
    def get_mood_distribution(self) -> Dict[str, int]:
        """Get mood distribution from database.
        
        Returns:
            Dictionary with mood counts
        """
        stats = self.db_manager.get_stats()
        return stats.get('mood_breakdown', {})
    
    def suggest_mood_for_features(self, features: Dict[str, float]) -> str:
        """Suggest mood based on audio features using heuristics.
        
        Args:
            features: Audio features dictionary
            
        Returns:
            Suggested mood category
        """
        try:
            tempo = features.get('tempo', 120)
            energy = features.get('rmse_mean', 0.1)
            brightness = features.get('spectral_centroid_mean', 2000)
            
            # Simple heuristic rules
            if tempo > 140 and energy > 0.15:
                return 'energetic'
            elif tempo > 120 and energy > 0.12:
                return 'upbeat'
            elif tempo < 80 and energy < 0.08:
                return 'sad'
            elif tempo < 100 and brightness < 1500:
                return 'melancholic'
            elif energy > 0.2:
                return 'intense'
            elif tempo > 100 and brightness > 2500:
                return 'happy'
            elif energy < 0.1:
                return 'calm'
            else:
                return 'chill'
                
        except Exception:
            return 'unknown'
