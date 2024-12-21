"""Custom exceptions for SPL Token Service."""

class SplTokenError(Exception):
    """Base exception for SPL Token Service errors."""
    pass


class TokenNotFoundError(SplTokenError):
    """Raised when a token is not found by symbol."""
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Token not found with symbol: {symbol}")


class TokenAccountNotFoundError(SplTokenError):
    """Raised when a token account is not found."""
    def __init__(self, account_type: str, address: str):
        self.account_type = account_type
        self.address = address
        super().__init__(f"{account_type} token account not found for address: {address}")


class InvalidTokenAddressError(SplTokenError):
    """Raised when a token address is invalid."""
    def __init__(self, address: str):
        self.address = address
        super().__init__(f"Invalid token address: {address}")


class InsufficientBalanceError(SplTokenError):
    """Raised when there are insufficient tokens for a transfer."""
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient balance for transfer. Required: {required}, Available: {available}"
        )


class TokenTransferError(SplTokenError):
    """Raised when a token transfer fails."""
    def __init__(self, message: str, details: dict = None):
        self.details = details or {}
        super().__init__(f"Token transfer failed: {message}")
