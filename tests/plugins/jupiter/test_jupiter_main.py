"""Main tests for Jupiter plugin."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, create_autospec
import asyncio

from goat_sdk.plugins.jupiter.models import QuoteRequest, SwapRequest
from goat_sdk.plugins.jupiter.types import SwapMode, QuoteResponse, SwapResult
from goat_sdk.core.wallet_client import ModeWalletClient


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_response():
    """Create a mock response."""
    response = AsyncMock()
    response.status = 200
    return response


@pytest.fixture
def mock_wallet_client():
    """Create a mock wallet client."""
    client = create_autospec(ModeWalletClient, instance=True)
    client.deserialize_transaction = AsyncMock(return_value="0x" + "33" * 32)
    
    async def mock_send_transaction(*args, **kwargs):
        await asyncio.sleep(0)  # Ensure it's a coroutine
        return "0x" + "22" * 32
    
    client.send_transaction = mock_send_transaction
    client.public_key = "0x" + "44" * 32
    return client


async def test_get_quote(jupiter_client, mock_quote_response, mock_session, mock_response):
    """Test getting a quote."""
    mock_response.json.return_value = mock_quote_response
    mock_session.post.return_value = mock_response

    request = QuoteRequest(
        inputMint="0x" + "11" * 32,
        outputMint="0x" + "22" * 32,
        amount="1000000",
        slippageBps=50,
        swapMode=SwapMode.EXACT_IN
    )

    quote = await jupiter_client.get_quote(
        input_mint=request.input_mint,
        output_mint=request.output_mint,
        amount=request.amount,
        slippage_bps=request.slippage_bps,
        mode=request.swap_mode
    )

    assert quote.input_mint == request.input_mint
    assert quote.output_mint == request.output_mint
    assert quote.in_amount == request.amount
    assert quote.slippage_bps == request.slippage_bps
    assert quote.swap_mode == request.swap_mode


async def test_swap_tokens(jupiter_client, mock_quote_response, mock_swap_response, mock_session, mock_wallet_client, mock_response):
    """Test swapping tokens."""
    # Mock quote response
    mock_response.json.return_value = mock_quote_response
    mock_session.post.return_value = mock_response

    # Create quote response model
    quote = QuoteResponse(**mock_quote_response)

    # Mock swap response
    mock_response.json.return_value = mock_swap_response.model_dump()
    mock_session.post.return_value = mock_response

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

    result = await jupiter_client.execute_swap(
        wallet_client=request.wallet_client,
        quote=quote,
    )

    assert isinstance(result, SwapResult)
    assert result.transaction_hash == "0x" + "22" * 32
    assert result.input_amount == quote.in_amount
    assert result.output_amount == quote.out_amount
    assert result.price_impact == quote.price_impact_pct
    assert result.fee_amount == quote.route_plan[0].swap_info.fee_amount
    assert result.route_plan == [step.model_dump(by_alias=True) for step in quote.route_plan]


async def test_get_quote_validation(jupiter_client):
    """Test quote request validation."""
    with pytest.raises(ValueError, match="Amount must be a valid integer string"):
        QuoteRequest(
            inputMint="0x" + "11" * 32,
            outputMint="0x" + "22" * 32,
            amount="invalid",
            slippageBps=50,
            swapMode=SwapMode.EXACT_IN
        )

    with pytest.raises(ValueError, match="slippage_bps must be between 0 and 10000"):
        QuoteRequest(
            inputMint="0x" + "11" * 32,
            outputMint="0x" + "22" * 32,
            amount="1000000",
            slippageBps=20000,
            swapMode=SwapMode.EXACT_IN
        ) 