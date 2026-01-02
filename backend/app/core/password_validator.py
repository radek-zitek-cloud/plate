"""Password validation utilities.

This module provides password strength validation to ensure
users create secure passwords that meet security requirements.
"""

import re
from typing import List


class PasswordValidationError(Exception):
    """Raised when password doesn't meet security requirements."""
    pass


def validate_password(password: str) -> List[str]:
    """
    Validate password meets security requirements.

    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number

    Args:
        password: The password to validate

    Returns:
        List of error messages. Empty list if password is valid.
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")

    return errors


def validate_password_or_raise(password: str) -> None:
    """
    Validate password and raise exception if invalid.

    Args:
        password: The password to validate

    Raises:
        PasswordValidationError: If password doesn't meet requirements
    """
    errors = validate_password(password)
    if errors:
        raise PasswordValidationError("; ".join(errors))
