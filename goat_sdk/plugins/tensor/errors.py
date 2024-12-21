"""Error types for Tensor plugin."""

from goat_sdk.core.errors import ModeError


class TensorError(ModeError):
    """Base error for Tensor plugin."""
    pass


class NFTInfoError(TensorError):
    """Error when getting NFT information."""
    pass


class BuyListingError(TensorError):
    """Error when getting buy listing transaction."""
    pass


class TransactionError(TensorError):
    """Error when handling transactions."""
    pass 