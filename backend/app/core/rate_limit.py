"""Rate limiting configuration using slowapi.

This module sets up rate limiting to protect the API from
brute-force attacks and excessive requests.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

# Create limiter instance
# Uses client IP address as the key for rate limiting
# Disabled during testing to avoid rate limit errors in test suite
limiter = Limiter(
    key_func=get_remote_address,
    enabled=not settings.TESTING
)
