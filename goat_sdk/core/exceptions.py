"""
Core exceptions for GOAT SDK.
Provides a hierarchy of exceptions that can be used across all plugins.
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ErrorContext:
    """Container for error context information."""
    timestamp: datetime
    operation: str
    parameters: Dict[str, Any]
    chain_id: Optional[int] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None

class GoatError(Exception):
    """Base exception for all GOAT SDK errors."""
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        parent: Optional[Exception] = None
    ):
        self.context = context or {}
        self.parent = parent
        self.timestamp = datetime.utcnow()
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            'error_type': self.__class__.__name__,
            'message': str(self),
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'parent': str(self.parent) if self.parent else None
        }

class ConfigurationError(GoatError):
    """Raised when there's an issue with configuration."""
    pass

class NetworkError(GoatError):
    """Raised when there's an issue with network communication."""
    pass

class ValidationError(GoatError):
    """Raised when validation fails."""
    pass

class SecurityError(GoatError):
    """Raised when a security check fails."""
    pass

class TransactionError(GoatError):
    """Base class for transaction-related errors."""
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        tx_hash: Optional[str] = None,
        parent: Optional[Exception] = None
    ):
        self.tx_hash = tx_hash
        super().__init__(message, context, parent)

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result['transaction_hash'] = self.tx_hash
        return result

class InsufficientFundsError(TransactionError):
    """Raised when account has insufficient funds."""
    pass

class GasEstimationError(TransactionError):
    """Raised when gas estimation fails."""
    pass

class TransactionRevertedError(TransactionError):
    """Raised when a transaction is reverted."""
    pass

class MEVError(SecurityError):
    """Raised when MEV protection detects an issue."""
    pass

class SlippageError(SecurityError):
    """Raised when slippage exceeds allowed threshold."""
    pass

class RateLimitError(NetworkError):
    """Raised when rate limit is exceeded."""
    pass

class TimeoutError(NetworkError):
    """Raised when operation times out."""
    pass

def create_error_context(
    operation: str,
    parameters: Dict[str, Any],
    chain_id: Optional[int] = None,
    transaction_hash: Optional[str] = None,
    block_number: Optional[int] = None
) -> ErrorContext:
    """Create a standardized error context."""
    return ErrorContext(
        timestamp=datetime.utcnow(),
        operation=operation,
        parameters=parameters,
        chain_id=chain_id,
        transaction_hash=transaction_hash,
        block_number=block_number
    )
