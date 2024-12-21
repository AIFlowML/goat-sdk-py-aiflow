"""Core error types for Mode SDK."""

from typing import Optional


class ModeError(Exception):
    """Base error class for Mode SDK."""

    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize ModeError.
        
        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of error."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message 