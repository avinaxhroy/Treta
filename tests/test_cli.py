"""Tests for CLI functionality."""

import pytest
from typer.testing import CliRunner
from pathlib import Path
import tempfile

from treta import app


class TestCLI:
    """Test CLI commands and functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
    
    def test_main_help(self):
        """Test main help command."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Treta" in result.stdout
    
    def test_download_help(self):
        """Test download command help."""
        result = self.runner.invoke(app, ["download", "--help"])
        assert result.exit_code == 0
        assert "download" in result.stdout.lower()
    
    def test_auth_help(self):
        """Test auth command help."""
        result = self.runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "authentication" in result.stdout.lower()
    
    def test_mood_help(self):
        """Test mood command help."""
        result = self.runner.invoke(app, ["mood", "--help"])
        assert result.exit_code == 0
        assert "mood" in result.stdout.lower()
    
    def test_stats_help(self):
        """Test stats command help."""
        result = self.runner.invoke(app, ["stats", "--help"])
        assert result.exit_code == 0
        assert "statistics" in result.stdout.lower()
    
    def test_queue_help(self):
        """Test queue command help."""
        result = self.runner.invoke(app, ["queue", "--help"])
        assert result.exit_code == 0
        assert "queue" in result.stdout.lower()
    
    def test_artist_help(self):
        """Test artist command help."""
        result = self.runner.invoke(app, ["artist", "--help"])
        assert result.exit_code == 0
        assert "artist" in result.stdout.lower()
