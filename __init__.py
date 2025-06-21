"""
Treta - Modern Music Downloader and Library Manager

A modular, production-ready music downloader that supports Spotify and Apple Music,
with advanced features like mood detection, smart queues, and comprehensive metadata management.
"""

__version__ = "1.0.0"
__author__ = "Treta Team"
__description__ = "Modern Music Downloader and Library Manager"

# Make the app available at the top level
from treta import app

# Import and expose the main app
try:
    from treta import app
except ImportError:
    # If treta module is not importable yet,
    # try to import locally from the file
    try:
        from .treta import app
    except ImportError:
        # Fallback option for direct execution
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from treta import app
        except ImportError:
            print("ERROR: Could not import Treta app")
            print("Try running directly with: python treta.py")
            app = None
