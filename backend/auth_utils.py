"""
Authentication Utilities for CloudEngineered Platform

This module provides secure authentication helpers:
- Secure secret key management
- Password validation
- Token generation and verification
- Rate limiting support
"""

import os
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
import jwt
import bcrypt
from functools import lru_cache

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

def get_secret_key() -> str:
    """
    Get the JWT secret key from environment or generate a secure fallback.
    
    In production, ALWAYS set SECRET_KEY environment variable!
    
    Returns:
        Secret key string
    """
    secret = os.getenv("SECRET_KEY")
    if not secret:
        # Log warning in production
        import logging
        logging.warning(
            "SECRET_KEY not set in environment! Using generated key. "
            "This is insecure for production - tokens will invalidate on restart."
        )
        # Generate a secure random key (will change on restart)
        if not hasattr(get_secret_key, '_fallback_key'):
            get_secret_key._fallback_key = secrets.token_urlsafe(64)
        return get_secret_key._fallback_key
    return secret


# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

class PasswordStrengthError(Exception):
    """Exception raised when password doesn't meet strength requirements."""
    pass


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements.
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    
    return True, ""


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with secure salt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as a string (decoded from bytes)
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')  # Return string for proper DB storage


def verify_password(password: str, hashed) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password (can be string or bytes)
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Handle both string and bytes hashes
        if isinstance(hashed, str):
            # Check if it's a Python bytes repr (b'...')
            if hashed.startswith("b'") and hashed.endswith("'"):
                # It was incorrectly stored as str(bytes), extract the actual hash
                hashed = hashed[2:-1]
            hashed_bytes = hashed.encode('utf-8')
        else:
            hashed_bytes = hashed
        
        return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


# ============================================================================
# TOKEN MANAGEMENT
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    return jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        user_id: User ID to encode
        
    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "jti": secrets.token_urlsafe(16)  # Unique token ID for revocation
    }
    
    return jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != token_type:
            return None
        
        # Check if token is expired (jwt.decode already does this, but double-check)
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            return None
        
        return payload
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


def generate_password_reset_token() -> str:
    """
    Generate a secure password reset token.
    
    Returns:
        URL-safe random token string
    """
    return secrets.token_urlsafe(32)


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def sanitize_username(username: str) -> Tuple[bool, str, str]:
    """
    Validate and sanitize username.
    
    Requirements:
    - 3-30 characters
    - Alphanumeric and underscores only
    - Must start with a letter
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, sanitized_username, error_message)
    """
    # Strip whitespace
    username = username.strip()
    
    if len(username) < 3:
        return False, username, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, username, "Username must be at most 30 characters"
    
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username):
        return False, username, "Username must start with a letter and contain only letters, numbers, and underscores"
    
    return True, username.lower(), ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    email = email.strip().lower()
    
    # Basic email regex (not exhaustive but covers most cases)
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 254:
        return False, "Email address too long"
    
    return True, ""


# ============================================================================
# RATE LIMITING (Simple in-memory implementation)
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self):
        self._attempts = {}  # {key: [(timestamp, count)]}
    
    def is_rate_limited(
        self, 
        key: str, 
        max_attempts: int = 5, 
        window_seconds: int = 300
    ) -> Tuple[bool, int]:
        """
        Check if a key is rate limited.
        
        Args:
            key: Identifier (e.g., IP address or email)
            max_attempts: Maximum attempts allowed in window
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_limited, seconds_until_reset)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        if key not in self._attempts:
            self._attempts[key] = []
        
        # Clean old attempts
        self._attempts[key] = [
            (ts, count) for ts, count in self._attempts[key]
            if ts > window_start
        ]
        
        # Count recent attempts
        total_attempts = sum(count for _, count in self._attempts[key])
        
        if total_attempts >= max_attempts:
            # Find when rate limit resets
            oldest = min(ts for ts, _ in self._attempts[key]) if self._attempts[key] else now
            reset_in = int((oldest + timedelta(seconds=window_seconds) - now).total_seconds())
            return True, max(0, reset_in)
        
        return False, 0
    
    def record_attempt(self, key: str):
        """
        Record an attempt for rate limiting.
        
        Args:
            key: Identifier (e.g., IP address or email)
        """
        now = datetime.utcnow()
        
        if key not in self._attempts:
            self._attempts[key] = []
        
        self._attempts[key].append((now, 1))
    
    def reset(self, key: str):
        """
        Reset attempts for a key (e.g., after successful login).
        
        Args:
            key: Identifier to reset
        """
        if key in self._attempts:
            del self._attempts[key]


# Global rate limiter instance
login_rate_limiter = RateLimiter()
password_reset_rate_limiter = RateLimiter()
