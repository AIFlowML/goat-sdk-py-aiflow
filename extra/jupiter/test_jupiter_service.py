"""Tests for Jupiter service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from goat_sdk.core.wallet_client import ModeWalletClient

from goat_sdk.plugins.jupiter.service import JupiterService
from goat_sdk.plugins.jupiter.types import QuoteResponse, SwapMode, SwapResult
from goat_sdk.plugins.jupiter.models import QuoteRequest, SwapRequest
from goat_sdk.plugins.jupiter.errors import QuoteError, SwapError


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = MagicMock(spec=ModeWalletClient)
    client.public_key = "0x" + "11" * 32  # Valid hex string
    client.sign_and_send_transaction = AsyncMock(return_value="0x" + "33" * 32)
    return client


@pytest.fixture
def mock_quote_response():
    """Create mock quote response."""
    return QuoteResponse(
        inputMint="input_mint",
        inAmount="1000000",
        outputMint="output_mint",
        outAmount="2000000",
        otherAmountThreshold="1900000",
        swapMode=SwapMode.EXACT_IN.value,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[{
            "swapInfo": {
                "ammKey": "amm_key",
                "label": "label",
                "inputMint": "input_mint",
                "outputMint": "output_mint",
                "inAmount": "1000000",
                "outAmount": "2000000",
                "feeAmount": "1000",
                "feeMint": "fee_mint",
            },
            "percent": 100.0,
        }],
    )


@pytest.mark.asyncio
async def test_get_quote(mock_quote_response):
    """Test get_quote method."""
    service = JupiterService()
    
    request = QuoteRequest(
        inputMint="0x" + "11" * 32,
        outputMint="0x" + "22" * 32,
        amount="1000000",
        slippageBps=50,
        swapMode=SwapMode.EXACT_IN
    )

    mock_client = AsyncMock()
    mock_client.get_quote = AsyncMock(return_value=mock_quote_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()

    with patch("goat_sdk.plugins.jupiter.service.JupiterClient", return_value=mock_client):
        quote = await service.get_quote(request=request)

        assert quote.input_mint == "input_mint"
        assert quote.in_amount == "1000000"
        assert quote.output_mint == "output_mint"
        assert quote.out_amount == "2000000"
        assert quote.slippage_bps == 50
        assert quote.swap_mode == SwapMode.EXACT_IN.value


@pytest.mark.asyncio
async def test_swap_tokens(mock_wallet_client, mock_quote_response):
    """Test swap_tokens method."""
    service = JupiterService()

    request = SwapRequest(
        wallet_client=mock_wallet_client,
        quoteRequest=QuoteRequest(
            inputMint="0x" + "11" * 32,
            outputMint="0x" + "22" * 32,
            amount="1000000",
            slippageBps=50,
            swapMode=SwapMode.EXACT_IN
        )
    )

    mock_client = AsyncMock()
    mock_client.get_quote = AsyncMock(return_value=mock_quote_response)
    mock_client.execute_swap = AsyncMock(return_value=SwapResult(
        transaction_hash="0x" + "33" * 32,
        input_amount="1000000",
        output_amount="2000000",
        price_impact="1.5",
        fee_amount="1000",
        route_plan=[{
            "swapInfo": {
                "ammKey": "amm_key",
                "label": "label",
                "inputMint": "input_mint",
                "outputMint": "output_mint",
                "inAmount": "1000000",
                "outAmount": "2000000",
                "feeAmount": "1000",
                "feeMint": "fee_mint",
            },
            "percent": 100.0,
        }],
    ))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()

    with patch("goat_sdk.plugins.jupiter.service.JupiterClient", return_value=mock_client):
        result = await service.swap_tokens(request=request)

        assert result.transaction_hash == "0x" + "33" * 32
        assert result.input_amount == "1000000"
        assert result.output_amount == "2000000"
        assert result.price_impact == "1.5"
        assert result.fee_amount == "1000"
        assert len(result.route_plan) == 1