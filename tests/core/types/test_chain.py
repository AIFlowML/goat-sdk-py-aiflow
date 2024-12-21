"""Tests for chain type definitions."""

import pytest
from typing import cast

from goat_sdk.core.types.chain import Chain, SolanaChain


def test_solana_chain():
    """Test Solana chain type creation and type checking."""
    chain: SolanaChain = {"type": "solana"}
    assert chain["type"] == "solana"

    # Test type checking
    chain_union: Chain = chain
    assert isinstance(chain_union, dict)
    assert chain_union["type"] == "solana"


def test_invalid_chain_type():
    """Test that invalid chain types raise type errors."""
    with pytest.raises(TypeError):
        chain: Chain = {"type": "invalid"}  # type: ignore
        assert chain["type"] != "solana"  # This line should not be reached
