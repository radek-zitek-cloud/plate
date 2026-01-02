"""
Unit tests for security utilities (password hashing and JWT tokens).
"""

import pytest
from datetime import timedelta
from jose import jwt
from jose.exceptions import JWTError

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test that password hashing works."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_correct_password(self):
        """Test verifying a correct password."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Test verifying an incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that hashing the same password twice produces different hashes (due to salt)."""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_empty_password(self):
        """Test handling of empty password."""
        password = ""
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True
        assert verify_password("not_empty", hashed) is False

    def test_special_characters_in_password(self):
        """Test password with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_unicode_password(self):
        """Test password with unicode characters (within bcrypt 72 byte limit)."""
        password = "пароль123"  # Shorter unicode password
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test creating a JWT token."""
        subject = "test_user_123"
        token = create_access_token(subject=subject)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_with_custom_expiration(self):
        """Test creating a token with custom expiration."""
        subject = "test_user_123"
        expires_delta = timedelta(minutes=15)
        token = create_access_token(subject=subject, expires_delta=expires_delta)

        # Decode token to verify
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == subject
        assert "exp" in payload

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        subject = "test_user_456"
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == subject
        assert "exp" in payload

    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises error."""
        invalid_token = "invalid.token.here"

        with pytest.raises(JWTError):
            jwt.decode(
                invalid_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

    def test_token_with_integer_subject(self):
        """Test creating a token with integer subject (user ID)."""
        subject = 12345
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Subject is converted to string in the token
        assert payload["sub"] == "12345"

    def test_token_with_default_expiration(self):
        """Test that token uses default expiration when none provided."""
        subject = "test_user"
        token = create_access_token(subject=subject)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert "exp" in payload
        assert payload["exp"] > 0

    def test_decode_with_wrong_secret(self):
        """Test decoding with wrong secret key fails."""
        subject = "test_user"
        token = create_access_token(subject=subject)

        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret_key", algorithms=[settings.ALGORITHM])

    def test_decode_with_wrong_algorithm(self):
        """Test decoding with wrong algorithm fails."""
        subject = "test_user"
        token = create_access_token(subject=subject)

        with pytest.raises(JWTError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS512"])
