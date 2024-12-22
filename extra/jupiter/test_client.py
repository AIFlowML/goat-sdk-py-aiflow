"""Tests for Jupiter client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from goat_sdk.plugins.jupiter.client import JupiterClient
from goat_sdk.plugins.jupiter.config import JupiterConfig
from goat_sdk.plugins.jupiter.types import (
    QuoteResponse,
    SwapMode,
    SwapRequest,
    SwapResponse,
    SwapResult,
)
from goat_sdk.plugins.jupiter.errors import QuoteError, SwapError


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    return JupiterConfig(
        api_url="https://test-api.jup.ag/v6",
        max_retries=3,
        retry_delay=0.5,
        timeout=30.0,
        default_slippage_bps=50,
        auto_retry_on_timeout=True,
        auto_retry_on_rate_limit=True,
        api_key=None,
    )


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


@pytest.fixture
def mock_session():
    """Create mock aiohttp session."""
    session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
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
    })
    session.post.return_value = mock_response
    return session


@pytest.fixture
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = "0x" + "11" * 32  # Valid hex string
    client.deserialize_transaction = AsyncMock(return_value="0x" + "33" * 32)
    client.send_transaction = AsyncMock(return_value="0x" + "22" * 32)
    return client


@pytest.mark.asyncio
async def test_context_manager():
    """Test client context manager."""
    mock_session = MagicMock()
    mock_session.post = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.closed = False

    with patch("aiohttp.ClientSession", return_value=mock_session):
        client = JupiterClient()
        async with client:
            assert not mock_session.closed
            assert isinstance(client._session, MagicMock)
        assert mock_session.close.called
        assert client._session is None


@pytest.mark.asyncio
async def test_get_quote_success(mock_session):
    """Test get_quote method success case."""
    client = JupiterClient(config=JupiterConfig())
    client._session = mock_session

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
    """Test get_quote method failure case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session.post.return_value.status = 400
    mock_session.post.return_value.json.return_value = {"error": "Invalid request"}
    client._session = mock_session

    with pytest.raises(QuoteError, match="Failed to get quote: Invalid request"):
        await client.get_quote(
            input_mint="0x" + "11" * 32,
            output_mint="0x" + "22" * 32,
            amount=1000000,
        )


@pytest.mark.asyncio
async def test_get_swap_transaction_success(mock_session, mock_wallet_client):
    """Test get_swap_transaction method success case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session.post.return_value.json.return_value = {
        "swapTransaction": "base64_encoded_transaction",
        "addressLookupTables": ["0x" + "44" * 32],
    }
    client._session = mock_session

    quote = QuoteResponse(
        inputMint="0x" + "11" * 32,
        inAmount="1000000",
        outputMint="0x" + "22" * 32,
        outAmount="2000000",
        otherAmountThreshold="1900000",
        swapMode=SwapMode.EXACT_IN.value,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[{
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
    )

    swap_tx = await client.get_swap_transaction(
        wallet_client=mock_wallet_client,
        quote=quote,
    )

    assert swap_tx.swap_transaction == "base64_encoded_transaction"
    assert swap_tx.address_lookup_tables == ["0x" + "44" * 32]


@pytest.mark.asyncio
async def test_get_swap_transaction_failure(mock_session, mock_wallet_client):
    """Test get_swap_transaction method failure case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session.post.return_value.status = 400
    mock_session.post.return_value.json.return_value = {"error": "Invalid request"}
    client._session = mock_session

    quote = QuoteResponse(
        inputMint="0x" + "11" * 32,
        inAmount="1000000",
        outputMint="0x" + "22" * 32,
        outAmount="2000000",
        otherAmountThreshold="1900000",
        swapMode=SwapMode.EXACT_IN.value,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[{
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
    )

    with pytest.raises(SwapError, match="Failed to get swap transaction: Invalid request"):
        await client.get_swap_transaction(
            wallet_client=mock_wallet_client,
            quote=quote,
        )


@pytest.mark.asyncio
async def test_execute_swap_success(mock_session, mock_wallet_client):
    """Test execute_swap method success case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session.post.return_value.json.return_value = {
        "swapTransaction": "base64_encoded_transaction",
        "addressLookupTables": ["0x" + "44" * 32],
    }
    client._session = mock_session

    quote = QuoteResponse(
        inputMint="0x" + "11" * 32,
        inAmount="1000000",
        outputMint="0x" + "22" * 32,
        outAmount="2000000",
        otherAmountThreshold="1900000",
        swapMode=SwapMode.EXACT_IN.value,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[{
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
    )

    result = await client.execute_swap(
        wallet_client=mock_wallet_client,
        quote=quote,
    )

    assert isinstance(result, SwapResult)
    assert result.transaction_hash == "0x" + "22" * 32
    assert result.input_amount == "1000000"
    assert result.output_amount == "2000000"
    assert result.price_impact == "1.5"
    assert result.fee_amount == "1000"
    assert len(result.route_plan) == 1


@pytest.mark.asyncio
async def test_execute_swap_failure(mock_session, mock_wallet_client):
    """Test execute_swap method failure case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session.post.return_value.status = 400
    mock_session.post.return_value.json.return_value = {"error": "Invalid request"}
    client._session = mock_session

    quote = QuoteResponse(
        inputMint="0x" + "11" * 32,
        inAmount="1000000",
        outputMint="0x" + "22" * 32,
        outAmount="2000000",
        otherAmountThreshold="1900000",
        swapMode=SwapMode.EXACT_IN.value,
        slippageBps=50,
        priceImpactPct="1.5",
        routePlan=[{
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
    )

    with pytest.raises(SwapError, match="Failed to get swap transaction: Invalid request"):
        await client.execute_swap(
            wallet_client=mock_wallet_client,
            quote=quote,
        )


@pytest.mark.asyncio
async def test_retry_on_network_error(mock_session):
    """Test retry on network error."""
    client = JupiterClient(config=JupiterConfig())
    mock_session.post.side_effect = [
        aiohttp.ClientError("Network error"),
        aiohttp.ClientError("Network error"),
        mock_session.post.return_value,
    ]
    client._session = mock_session

    quote = await client.get_quote(
        input_mint="0x" + "11" * 32,
        output_mint="0x" + "22" * 32,
        amount=1000000,
    )

    assert quote.input_mint == "0x" + "11" * 32
    assert quote.output_mint == "0x" + "22" * 32
    assert quote.in_amount == "1000000"
    assert quote.out_amount == "2000000"