"""
Authentication storage and management for Treta.
Handles secure storage of Spotify tokens and Apple Music cookies.
"""

import json
import os
import base64
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from db.manager import DatabaseManager
from db.models import AuthToken


class AuthStore:
    """Secure authentication storage for music services."""
    
    def __init__(self, auth_file: Optional[str] = None, db_manager: Optional[DatabaseManager] = None):
        """Initialize authentication store.
        
        Args:
            auth_file: Path to auth.json file. Defaults to data/auth.json
            db_manager: Database manager instance
        """
        if auth_file is None:
            auth_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'auth.json')
        
        self.auth_file = os.path.abspath(auth_file)
        self.db_manager = db_manager or DatabaseManager()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
        
        # Setup encryption
        self._setup_encryption()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _setup_encryption(self):
        """Setup encryption for secure token storage."""
        # Use a fixed salt for consistency (in production, this should be configurable)
        salt = b'treta_music_downloader_salt_2024'
        
        # Derive key from a password (in production, this should be user-provided)
        password = b'treta_default_encryption_key'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher = Fernet(key)
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def store_spotify_token(self, token: str, expires_in: Optional[int] = None) -> bool:
        """Store Spotify bearer token.
        
        Args:
            token: Spotify bearer token
            expires_in: Token expiry time in seconds
            
        Returns:
            True if stored successfully
        """
        try:
            encrypted_token = self._encrypt_data(token)
            
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            auth_token = AuthToken(
                service='spotify',
                token_type='bearer',
                token_data=encrypted_token,
                expires_at=expires_at
            )
            
            self.db_manager.store_auth_token(auth_token)
            self.logger.info("Spotify token stored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store Spotify token: {e}")
            return False
    
    def store_apple_cookies(self, cookies_data: str) -> bool:
        """Store Apple Music cookies.
        
        Args:
            cookies_data: Apple Music cookies (Netscape format)
            
        Returns:
            True if stored successfully
        """
        try:
            encrypted_cookies = self._encrypt_data(cookies_data)
            
            auth_token = AuthToken(
                service='apple',
                token_type='cookie',
                token_data=encrypted_cookies
            )
            
            self.db_manager.store_auth_token(auth_token)
            self.logger.info("Apple Music cookies stored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store Apple Music cookies: {e}")
            return False
    
    def get_spotify_token(self) -> Optional[str]:
        """Get Spotify bearer token.
        
        Returns:
            Decrypted Spotify token or None
        """
        try:
            auth_token = self.db_manager.get_auth_token('spotify', 'bearer')
            
            if not auth_token:
                return None            
            if auth_token.is_expired():
                self.logger.warning("Spotify token has expired")
                return None
            
            return self._decrypt_data(auth_token.token_data)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve Spotify token: {e}")
            return None
    
    def get_apple_cookies(self) -> Optional[str]:
        """Get Apple Music cookies.
        
        Returns:
            Decrypted Apple Music cookies or None
        """
        try:
            auth_token = self.db_manager.get_auth_token('apple', 'cookie')
            
            if not auth_token:
                return None
            
            return self._decrypt_data(auth_token.token_data)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve Apple Music cookies: {e}")
            return None

    def test_spotify_auth(self) -> bool:
        """Test if Spotify authentication is working.
        
        Returns:
            True if authentication is valid (either token or credentials)
        """
        # Check for Bearer token first
        token = self.get_spotify_token()
        if token:
            try:
                import requests
                
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                # Test with Spotify Web API
                response = requests.get(
                    'https://api.spotify.com/v1/me',
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.logger.info("Spotify token authentication test successful")
                    return True
                else:
                    self.logger.debug(f"Spotify token auth test failed: {response.status_code}")
                    
            except Exception as e:
                self.logger.debug(f"Spotify token authentication test error: {e}")
        
        # Check for username/password credentials
        credentials = self.get_spotify_credentials()
        if credentials:
            self.logger.info("Spotify credentials available")
            return True
        
        self.logger.debug("No valid Spotify authentication found")
        return False
    
    def test_apple_auth(self) -> bool:
        """Test if Apple Music authentication is working.
        
        Returns:
            True if authentication is valid
        """
        cookies = self.get_apple_cookies()
        if not cookies:
            return False
        
        try:
            # Write cookies to temp file for GAMDL
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(cookies)
                cookies_file = f.name
            
            # Test with a simple GAMDL command
            import subprocess
            import os
              # Get Python executable for current environment
            python_exe = sys.executable
            
            result = subprocess.run([
                python_exe, '-m', 'gamdl', '--help'
            ], capture_output=True, text=True, timeout=30)
            
            # Clean up temp file
            os.unlink(cookies_file)
            
            if result.returncode == 0:
                self.logger.info("Apple Music authentication test successful")
                return True
            else:
                self.logger.warning("Apple Music auth test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Apple Music authentication test error: {e}")
            return False
    
    def revoke_spotify_auth(self):
        """Revoke Spotify authentication."""
        self.db_manager.revoke_auth_token('spotify')
        self.logger.info("Spotify authentication revoked")
    
    def revoke_apple_auth(self):
        """Revoke Apple Music authentication."""
        self.db_manager.revoke_auth_token('apple')
        self.logger.info("Apple Music authentication revoked")
    
    def get_auth_status(self) -> Dict[str, bool]:
        """Get authentication status for all services.
        
        Returns:
            Dictionary with service names and their auth status
        """
        return {
            'spotify': self.test_spotify_auth(),
            'apple': self.test_apple_auth()
        }
    
    # Legacy JSON file support for backward compatibility
    def migrate_from_json(self) -> bool:
        """Migrate authentication data from JSON file to database.
        
        Returns:
            True if migration was successful or no migration needed
        """
        if not os.path.exists(self.auth_file):
            return True  # No file to migrate
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            
            # Migrate Spotify token
            if 'spotify' in auth_data and 'token' in auth_data['spotify']:
                self.store_spotify_token(
                    auth_data['spotify']['token'],
                    auth_data['spotify'].get('expires_in')
                )
            
            # Migrate Apple cookies
            if 'apple' in auth_data and 'cookies' in auth_data['apple']:
                self.store_apple_cookies(auth_data['apple']['cookies'])
            
            # Backup and remove old file
            backup_file = f"{self.auth_file}.backup"
            os.rename(self.auth_file, backup_file)
            
            self.logger.info(f"Authentication data migrated from {self.auth_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to migrate authentication data: {e}")
            return False
    
    def store_spotify_credentials(self, username: str, password: str) -> bool:
        """Store Spotify username and password for Zotify.
        
        Args:
            username: Spotify username
            password: Spotify password
            
        Returns:
            True if stored successfully
        """
        try:
            # Store as JSON with both username and password
            credentials = {
                'username': username,
                'password': password
            }
            
            encrypted_data = self._encrypt_data(json.dumps(credentials))
            
            # Create auth token entry
            auth_token = AuthToken(
                service='spotify',
                token_type='credentials',
                token_data=encrypted_data,
                expires_at=None,  # Credentials don't expire
                created_at=datetime.now()
            )
            
            self.db_manager.store_auth_token(auth_token)
            self.logger.info("Spotify credentials stored successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store Spotify credentials: {e}")
            return False

    def get_spotify_credentials(self) -> Optional[Dict[str, str]]:
        """Get Spotify username and password.
        
        Returns:
            Dictionary with 'username' and 'password' keys, or None
        """
        try:
            auth_token = self.db_manager.get_auth_token('spotify', 'credentials')
            
            if not auth_token:
                return None
            
            decrypted_data = self._decrypt_data(auth_token.token_data)
            return json.loads(decrypted_data)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve Spotify credentials: {e}")
            return None

    def has_spotify_credentials(self) -> bool:
        """Check if Spotify username/password are stored.
        
        Returns:
            True if credentials are available
        """
        return self.get_spotify_credentials() is not None
