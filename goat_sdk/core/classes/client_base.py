"""Base client class for Mode SDK."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ModeClientBase:
    """Base client class for Mode SDK."""

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize the client."""
        self._error: Optional[Exception] = None

    @property
    def error(self) -> Optional[Exception]:
        """Get the last error."""
        return self._error

    def __str__(self) -> str:
        """Return a string representation of the client."""
        return f"{self.__class__.__name__}(error={self._error})" 