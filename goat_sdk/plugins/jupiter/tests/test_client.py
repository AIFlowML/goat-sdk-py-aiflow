"""Tests for Jupiter client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from goat_sdk.plugins.jupiter.client import JupiterClient
from goat_sdk.plugins.jupiter.types import QuoteResponse, SwapMode, SwapResult
from goat_sdk.plugins.jupiter.errors import QuoteError, SwapError


@pytest.fixture
def mock_session():
    """Create mock aiohttp session."""
    session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={})
    session.post = AsyncMock(return_value=mock_response)
    session.get = AsyncMock(return_value=mock_response)
    return session


@pytest.fixture
def mock_quote_response():
    """Create mock quote response."""
    return {
        "inputMint": "0x" + "11" * 32,
        "inAmount": "1000000",
        "outputMint": "0x" + "22" * 32,
        "outAmount": "2000000",
        "otherAmountThreshold": "1900000",
        "swapMode": SwapMode.EXACT_IN.value,
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


@pytest.mark.asyncio
async def test_context_manager(mock_session):
    """Test client as context manager."""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            assert isinstance(client._session, AsyncMock)


@pytest.mark.asyncio
async def test_get_quote_success(mock_session, mock_quote_response):
    """Test successful quote retrieval."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_quote_response)
    mock_session.post = AsyncMock(return_value=mock_response)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            quote = await client.get_quote(
                input_mint="0x" + "11" * 32,
                output_mint="0x" + "22" * 32,
                amount=1000000,
            )

            assert quote.input_mint == "0x" + "11" * 32
            assert quote.output_mint == "0x" + "22" * 32
            assert quote.in_amount == "1000000"
            assert quote.out_amount == "2000000"


@pytest.mark.asyncio
async def test_get_quote_failure(mock_session):
    """Test quote retrieval failure."""
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={"error": "Invalid request"})
    mock_session.post = AsyncMock(return_value=mock_response)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            with pytest.raises(QuoteError, match="Failed to get quote: Invalid request"):
                await client.get_quote(
                    input_mint="0x" + "11" * 32,
                    output_mint="0x" + "22" * 32,
                    amount=1000000,
                )


@pytest.mark.asyncio
async def test_get_swap_transaction_success(mock_session, mock_quote_response):
    """Test successful swap transaction retrieval."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "swapTransaction": "bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ=",
            "addressLookupTables": ["0x" + "44" * 32],
        },
    )
    mock_session.post = AsyncMock(return_value=mock_response)

    mock_wallet_client = AsyncMock()
    mock_wallet_client.public_key = "0x" + "11" * 32

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            swap_tx = await client.get_swap_transaction(
                wallet_client=mock_wallet_client,
                quote=QuoteResponse(**mock_quote_response),
            )

            assert swap_tx.swap_transaction == "bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ="
            assert swap_tx.address_lookup_tables == ["0x" + "44" * 32]


@pytest.mark.asyncio
async def test_get_swap_transaction_failure(mock_session, mock_quote_response):
    """Test swap transaction retrieval failure."""
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={"error": "Invalid request"})
    mock_session.post = AsyncMock(return_value=mock_response)

    mock_wallet_client = AsyncMock()
    mock_wallet_client.public_key = "0x" + "11" * 32

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            with pytest.raises(SwapError, match="Failed to get swap transaction: Invalid request"):
                await client.get_swap_transaction(
                    wallet_client=mock_wallet_client,
                    quote=QuoteResponse(**mock_quote_response),
                )


@pytest.mark.asyncio
async def test_execute_swap_success(mock_session, mock_quote_response):
    """Test successful swap execution."""
    # Mock swap transaction response
    mock_swap_response = AsyncMock()
    mock_swap_response.status = 200
    mock_swap_response.json = AsyncMock(
        return_value={
            "swapTransaction": "bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ=",
            "addressLookupTables": ["0x" + "44" * 32],
        }
    )
    mock_session.post = AsyncMock(return_value=mock_swap_response)

    # Mock wallet client
    mock_wallet_client = AsyncMock()
    mock_wallet_client.public_key = "0x" + "11" * 32
    mock_wallet_client.deserialize_transaction = AsyncMock(return_value="mock_transaction")
    mock_wallet_client.send_transaction = AsyncMock(return_value="0x" + "44" * 32)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            result = await client.execute_swap(
                wallet_client=mock_wallet_client,
                quote=QuoteResponse(**mock_quote_response),
            )

            assert isinstance(result, SwapResult)
            assert result.transaction_hash == "0x" + "44" * 32
            assert result.input_amount == "1000000"
            assert result.output_amount == "2000000"
            assert result.price_impact == "1.5"
            assert result.fee_amount == "1000"
            assert result.route_plan == mock_quote_response["routePlan"]
            mock_wallet_client.deserialize_transaction.assert_called_once_with("bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ=")
            mock_wallet_client.send_transaction.assert_called_once_with("mock_transaction")


@pytest.mark.asyncio
async def test_execute_swap_failure(mock_session, mock_quote_response):
    """Test swap execution failure."""
    # Mock swap transaction response
    mock_swap_response = AsyncMock()
    mock_swap_response.status = 200
    mock_swap_response.json = AsyncMock(
        return_value={
            "swapTransaction": "bW9ja190cmFuc2FjdGlvbl9iYXNlNjQ=",
            "addressLookupTables": ["0x" + "44" * 32],
        }
    )
    mock_session.post = AsyncMock(return_value=mock_swap_response)

    # Mock wallet client with failing transaction
    mock_wallet_client = AsyncMock()
    mock_wallet_client.public_key = "0x" + "11" * 32
    mock_wallet_client.deserialize_transaction = AsyncMock(return_value="mock_transaction")
    mock_wallet_client.send_transaction = AsyncMock(side_effect=Exception("Transaction failed"))

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            with pytest.raises(SwapError, match="Failed to send transaction: Transaction failed"):
                await client.execute_swap(
                    wallet_client=mock_wallet_client,
                    quote=QuoteResponse(**mock_quote_response),
                )


@pytest.mark.asyncio
async def test_retry_on_network_error(mock_session, mock_quote_response):
    """Test retry on network error."""
    # First call fails with network error
    mock_fail_response = AsyncMock()
    mock_fail_response.status = 500
    mock_fail_response.json = AsyncMock(return_value={"error": "Internal server error"})

    # Second call succeeds
    mock_success_response = AsyncMock()
    mock_success_response.status = 200
    mock_success_response.json = AsyncMock(return_value=mock_quote_response)

    # Set up mock session to fail first, then succeed
    mock_session.post = AsyncMock(side_effect=[
        aiohttp.ClientError("Network error"),
        mock_success_response,
    ])

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with JupiterClient() as client:
            quote = await client.get_quote(
                input_mint="0x" + "11" * 32,
                output_mint="0x" + "22" * 32,
                amount=1000000,
            )

            assert quote.input_mint == "0x" + "11" * 32
            assert quote.output_mint == "0x" + "22" * 32
            assert quote.in_amount == "1000000"
            assert quote.out_amount == "2000000"
  