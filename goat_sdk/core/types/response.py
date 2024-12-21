from typing import Any, Dict, Optional

class Response:
    """Base class for responses."""
    def __init__(self, error: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        self.error = error
        self.data = data

class ErrorResponse(Response):
    """Error response."""
    def __init__(self, error: str):
        super().__init__(error=error)

class SuccessResponse(Response):
    """Success response."""
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data=data) 