"""Chain type definitions."""

from typing import Literal
from typing_extensions import TypedDict


class Chain(TypedDict):
    """Base chain type."""
    type: str


class SolanaChain(TypedDict):
    """Solana chain type."""
    type: Literal["solana"]


class EthereumChain(TypedDict):
    """Ethereum chain type."""
    type: Literal["ethereum"]


class ModeChain(TypedDict):
    """Mode chain type."""
    type: Literal["mode"]
