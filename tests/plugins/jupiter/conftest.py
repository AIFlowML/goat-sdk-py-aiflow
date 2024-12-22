"""
          _____                    _____                    _____                    _____           _______                   _____          
         /\    \                  /\    \                  /\    \                  /\    \         /::\    \                 /\    \         
        /::\    \                /::\    \                /::\    \                /::\____\       /::::\    \               /::\____\        
       /::::\    \               \:::\    \              /::::\    \              /:::/    /      /::::::\    \             /:::/    /        
      /::::::\    \               \:::\    \            /::::::\    \            /:::/    /      /::::::::\    \           /:::/   _/___      
     /:::/\:::\    \               \:::\    \          /:::/\:::\    \          /:::/    /      /:::/~~\:::\    \         /:::/   /\    \     
    /:::/__\:::\    \               \:::\    \        /:::/__\:::\    \        /:::/    /      /:::/    \:::\    \       /:::/   /::\____\    
   /::::\   \:::\    \              /::::\    \      /::::\   \:::\    \      /:::/    /      /:::/    / \:::\    \     /:::/   /:::/    /    
  /::::::\   \:::\    \    ____    /::::::\    \    /::::::\   \:::\    \    /:::/    /      /:::/____/   \:::\____\   /:::/   /:::/   _/___  
 /:::/\:::\   \:::\    \  /\   \  /:::/\:::\    \  /:::/\:::\   \:::\    \  /:::/    /      |:::|    |     |:::|    | /:::/___/:::/   /\    \ 
/:::/  \:::\   \:::\____\/::\   \/:::/  \:::\____\/:::/  \:::\   \:::\____\/:::/____/       |:::|____|     |:::|    ||:::|   /:::/   /::\____\
\::/    \:::\  /:::/    /\:::\  /:::/    \::/    /\::/    \:::\   \::/    /\:::\    \        \:::\    \   /:::/    / |:::|__/:::/   /:::/    /
 \/____/ \:::\/:::/    /  \:::\/:::/    / \/____/  \/____/ \:::\   \/____/  \:::\    \        \:::\    \ /:::/    /   \:::\/:::/   /:::/    / 
          \::::::/    /    \::::::/    /                    \:::\    \       \:::\    \        \:::\    /:::/    /     \::::::/   /:::/    /  
           \::::/    /      \::::/____/                      \:::\____\       \:::\    \        \:::\__/:::/    /       \::::/___/:::/    /   
           /:::/    /        \:::\    \                       \::/    /        \:::\    \        \::::::::/    /         \:::\__/:::/    /    
          /:::/    /          \:::\    \                       \/____/          \:::\    \        \::::::/    /           \::::::::/    /     
         /:::/    /            \:::\    \                                        \:::\    \        \::::/    /             \::::::/    /      
        /:::/    /              \:::\____\                                        \:::\____\        \::/____/               \::::/    /       
        \::/    /                \::/    /                                         \::/    /         ~~                      \::/____/        
         \/____/                  \/____/                                           \/____/                                   ~~              
                                                                                                                                              

         
 
     GOAT-SDK Python - Unofficial SDK for GOAT - Igor Lessio - AIFlow.ml
     
     Path: tests/plugins/jupiter/conftest.py
"""

"""Test fixtures for Jupiter plugin."""

import pytest
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
import ssl

from goat_sdk.core.wallet_client import ModeWalletClient
from goat_sdk.plugins.jupiter.client import JupiterClient
from goat_sdk.plugins.jupiter.config import JupiterConfig
from goat_sdk.plugins.jupiter.types import (
    SwapMode,
    SwapInfo,
    PlatformFee,
    RoutePlanStep,
    QuoteResponse,
    SwapResponse,
)


@pytest.fixture
def mock_session():
    """Create mock aiohttp session."""
    session = AsyncMock()
    mock_response = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None
    session.post.return_value = mock_context
    session.get.return_value = mock_context
    return session


@pytest.fixture
def ssl_context():
    """Create SSL context that doesn't verify certificates."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock(spec=ModeWalletClient)
    client.public_key = "0x" + "11" * 32  # Valid hex string
    client.deserialize_transaction = MagicMock()
    client.send_transaction = AsyncMock(return_value="0x" + "22" * 32)
    return client


@pytest.fixture
def jupiter_config():
    """Create Jupiter configuration."""
    return JupiterConfig(
        api_url="https://test-api.jup.ag/v6",
        max_retries=1,
        retry_delay=0.1,
        timeout=5.0,
    )


@pytest.fixture
def jupiter_client(mock_session, jupiter_config):
    """Create Jupiter client."""
    return JupiterClient(
        config=jupiter_config,
        session=mock_session,
    )


@pytest.fixture
def mock_quote_response():
    """Create mock quote response."""
    return {
        "inputMint": "0x" + "11" * 32,
        "inAmount": "1000000",
        "outputMint": "0x" + "22" * 32,
        "outAmount": "2000000",
        "otherAmountThreshold": "1900000",
        "swapMode": "ExactIn",
        "slippageBps": 50,
        "priceImpactPct": "1.5",
        "routePlan": [{
            "swapInfo": {
                "ammKey": "amm_key",
                "label": "Orca",
                "inputMint": "0x" + "11" * 32,
                "outputMint": "0x" + "22" * 32,
                "inAmount": "1000000",
                "outAmount": "2000000",
                "feeAmount": "1000",
                "feeMint": "0x" + "33" * 32,
            },
            "percent": 100.0,
        }],
    }


@pytest.fixture
def mock_swap_response():
    """Create mock swap response."""
    return SwapResponse(
        swap_transaction="bW9ja190cmFuc2FjdGlvbl9kYXRh",
        address_lookup_tables=["0x" + "44" * 32],
    )


@pytest.fixture(autouse=True)
def mock_aiohttp_client_session():
    """Mock aiohttp ClientSession to use test SSL context."""
    mock = AsyncMock()
    mock.return_value = AsyncMock()
    mock.return_value.connector = AsyncMock()
    mock.return_value.connector.ssl = False
    with patch("aiohttp.ClientSession", mock):
        yield mock