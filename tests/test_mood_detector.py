"""Tests for mood detection functionality."""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from core.mood_detector import MoodDetector


class TestMoodDetector:
    """Test mood detection functionality."""
    
    def test_mood_detector_init(self):
        """Test mood detector initialization."""
        detector = MoodDetector()
        assert detector is not None
    
    @patch('librosa.load')
    @patch('librosa.feature')
    def test_extract_features(self, mock_feature, mock_load):
        """Test audio feature extraction."""
        # Mock librosa functions
        mock_load.return_value = (np.random.random(22050), 22050)
        mock_feature.mfcc.return_value = np.random.random((13, 100))
        mock_feature.chroma.return_value = np.random.random((12, 100))
        mock_feature.spectral_centroid.return_value = np.random.random((1, 100))
        mock_feature.spectral_rolloff.return_value = np.random.random((1, 100))
        mock_feature.zero_crossing_rate.return_value = np.random.random((1, 100))
        mock_feature.tempo.return_value = (120.0, np.random.random((1, 100)))
        
        detector = MoodDetector()
        features = detector.extract_features("dummy_path.mp3")
        
        assert features is not None
        assert len(features) > 0
    
    def test_predict_mood_without_model(self):
        """Test mood prediction without trained model."""
        detector = MoodDetector()
        
        # Should return default mood when no model is trained
        mood = detector.predict_mood("dummy_path.mp3")
        assert mood in ["energetic", "calm", "happy", "sad", "unknown"]
