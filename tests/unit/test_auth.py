#!/usr/bin/env python3
"""
Unit tests for authentication functionality.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime, timedelta
import jwt
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    oauth2_scheme
)

class TestAuth(unittest.TestCase):
    """Tests for authentication functionality."""
    
    def setUp(self):
        """Set up test environment."""
        os.environ["SECRET_KEY"] = "testsecretkey"
    
    def tearDown(self):
        """Clean up test environment."""
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword"
        hashed = get_password_hash(password)
        
        # Verify the hash is different from the password
        self.assertNotEqual(password, hashed)
        
        # Verify the password against the hash
        self.assertTrue(verify_password(password, hashed))
        
        # Test with wrong password
        self.assertFalse(verify_password("wrongpassword", hashed))
    
    @patch('src.api.auth.get_user_by_username')
    def test_authenticate_user(self, mock_get_user):
        """Test user authentication."""
        # Setup mock
        mock_user = {
            "username": "testuser",
            "hashed_password": get_password_hash("testpassword"),
            "disabled": False
        }
        mock_get_user.return_value = mock_user
        
        # Test valid authentication
        user = authenticate_user("testuser", "testpassword")
        self.assertEqual(user, mock_user)
        
        # Test invalid password
        user = authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(user)
        
        # Test non-existent user
        mock_get_user.return_value = None
        user = authenticate_user("nonexistent", "testpassword")
        self.assertIsNone(user)
        
        # Test disabled user
        mock_user["disabled"] = True
        mock_get_user.return_value = mock_user
        user = authenticate_user("testuser", "testpassword")
        self.assertIsNone(user)
    
    def test_create_access_token(self):
        """Test token creation."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(data, expires_delta)
        
        # Decode the token to verify contents
        decoded = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
        
        self.assertEqual(decoded["sub"], "testuser")
        self.assertTrue("exp" in decoded)
        
        # Test token without explicit expiry
        token = create_access_token(data)
        decoded = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
        self.assertEqual(decoded["sub"], "testuser")
        self.assertTrue("exp" in decoded)
    
    @patch('src.api.auth.jwt.decode')
    @patch('src.api.auth.get_user_by_username')
    async def test_get_current_user(self, mock_get_user, mock_decode):
        """Test getting current user from token."""
        # Setup mocks
        mock_decode.return_value = {"sub": "testuser"}
        mock_user = {"username": "testuser", "disabled": False}
        mock_get_user.return_value = mock_user
        
        # Test valid token
        user = await get_current_user("valid_token")
        self.assertEqual(user, mock_user)
        
        # Test expired token
        mock_decode.side_effect = jwt.ExpiredSignatureError
        with self.assertRaises(Exception) as context:
            await get_current_user("expired_token")
        self.assertIn("expired", str(context.exception))
        
        # Test invalid token
        mock_decode.side_effect = jwt.InvalidTokenError
        with self.assertRaises(Exception) as context:
            await get_current_user("invalid_token")
        self.assertIn("invalid", str(context.exception))
        
        # Test non-existent user
        mock_decode.side_effect = None
        mock_get_user.return_value = None
        with self.assertRaises(Exception) as context:
            await get_current_user("valid_token")
        self.assertIn("not found", str(context.exception))
        
        # Test disabled user
        mock_user["disabled"] = True
        mock_get_user.return_value = mock_user
        with self.assertRaises(Exception) as context:
            await get_current_user("valid_token")
        self.assertIn("disabled", str(context.exception))

if __name__ == '__main__':
    unittest.main()
