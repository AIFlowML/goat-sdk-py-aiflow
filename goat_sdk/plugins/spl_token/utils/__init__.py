"""Utility functions for SPL Token Service."""

import logging
from typing import Optional, Dict, Any
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

from .does_account_exist import does_account_exist
from .token_account import create_associated_token_account

logger = logging.getLogger(__name__)


def log_error_details(operation: str, error: Exception, action: str) -> None:
    """
    Log detailed error information.

    Args:
        operation: The operation being performed (e.g., "get_token_balance_by_mint_address")
        error: The exception that was raised
        action: The action being performed (e.g., "getting token balance")
    """
    error_type = type(error).__name__
    error_message = str(error)
    error_attributes = {
        attr: getattr(error, attr)
        for attr in dir(error)
        if not attr.startswith('_') and not callable(getattr(error, attr))
    }

    logger.error(f"[{operation}] Error {action}: {error_type} - {error_message}")
    if error_attributes:
        logger.error(f"[{operation}] Error attributes: {error_attributes}")


__all__ = [
    'does_account_exist',
    'create_associated_token_account',
    'log_error_details',
]
