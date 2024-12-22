"""Tests for Jupiter service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from goat_sdk.plugins.jupiter.service import JupiterService
from goat_sdk.plugins.jupiter.types import QuoteResponse, SwapMode, SwapResult
from goat_sdk.plugins.jupiter.errors import QuoteError, SwapError


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = "0x" + "11" * 32  # Valid hex string
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

    # Mock successful quote
    with patch("goat_sdk.plugins.jupiter.client.JupiterClient.get_quote") as mock_get_quote:
        mock_get_quote.return_value = mock_quote_response

        quote = await service.get_quote(
            input_mint="input_mint",
            output_mint="output_mint",
            amount=1000000,
        )

        assert quote.input_mint == "input_mint"
        assert quote.output_mint == "output_mint"
        assert quote.in_amount == "1000000"
        assert quote.out_amount == "2000000"

    # Mock quote error
    with patch("goat_sdk.plugins.jupiter.client.JupiterClient.get_quote") as mock_get_quote:
        mock_get_quote.side_effect = QuoteError("Failed to get quote")

        with pytest.raises(QuoteError):
            await service.get_quote(
                input_mint="input_mint",
                output_mint="output_mint",
                amount=1000000,
            )


@pytest.mark.asyncio
async def test_swap_tokens(mock_wallet_client, mock_quote_response):
    """Test swap_tokens method."""
    service = JupiterService()

    # Mock successful swap
    with patch("goat_sdk.plugins.jupiter.client.JupiterClient.get_quote") as mock_get_quote, \
         patch("goat_sdk.plugins.jupiter.client.JupiterClient.execute_swap") as mock_execute_swap:
        mock_get_quote.return_value = mock_quote_response
        mock_execute_swap.return_value = SwapResult(
            transaction_hash="0x" + "44" * 32,
            input_amount="1000000",
            output_amount="2000000",
            price_impact="1.5",
            fee_amount="1000",
            platform_fee=None,
            route_plan=[],
        )

        result = await service.swap_tokens(
            wallet_client=mock_wallet_client,
            input_mint="input_mint",
            output_mint="output_mint",
            amount=1000000,
        )

        assert result.transaction_hash == "0x" + "44" * 32
        assert result.input_amount == "1000000"
        assert result.output_amount == "2000000"

    # Mock swap error
    with patch("goat_sdk.plugins.jupiter.client.JupiterClient.get_quote") as mock_get_quote, \
         patch("goat_sdk.plugins.jupiter.client.JupiterClient.execute_swap") as mock_execute_swap:
        mock_get_quote.return_value = mock_quote_response
        mock_execute_swap.side_effect = SwapError("Failed to execute swap")

        with pytest.raises(SwapError):
            await service.swap_tokens(
                wallet_client=mock_wallet_client,
                input_mint="input_mint",
                output_mint="output_mint",
                amount=1000000,
            ) 