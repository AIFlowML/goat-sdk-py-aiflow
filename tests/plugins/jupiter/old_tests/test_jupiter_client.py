"""Tests for Jupiter client."""

import base64
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
def mock_wallet_client():
    """Create mock wallet client."""
    client = AsyncMock()
    client.public_key = "0x" + "11" * 32  # Valid hex string
    return client


@pytest.fixture
def mock_quote_response():
    """Create mock quote response."""
    return QuoteResponse(
        input_mint="0x" + "22" * 32,
        in_amount="1000000",
        output_mint="0x" + "33" * 32,
        out_amount="2000000",
        other_amount_threshold="1900000",
        swap_mode=SwapMode.EXACT_IN.value,
        slippage_bps=50,
        price_impact_pct="1.5",
        route_plan=[{
            "swapInfo": {
                "ammKey": "amm_key",
                "label": "Orca",
                "inputMint": "0x" + "22" * 32,
                "outputMint": "0x" + "33" * 32,
                "inAmount": "1000000",
                "outAmount": "2000000",
                "feeAmount": "1000",
                "feeMint": "0x" + "44" * 32,
            },
            "percent": 100.0,
        }],
        context_slot=123456789,
        time_taken=0.123,
    )


@pytest.fixture
def mock_swap_response():
    """Create mock swap response."""
    return SwapResponse(
        swap_transaction=base64.b64encode(b"mock_transaction_data").decode(),
        address_lookup_tables=["0x" + "44" * 32],
    )


@pytest.mark.asyncio
async def test_get_quote():
    """Test get_quote method."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "inputMint": "0x" + "22" * 32,
        "inAmount": "1000000",
        "outputMint": "0x" + "33" * 32,
        "outAmount": "2000000",
        "otherAmountThreshold": "1900000",
        "swapMode": SwapMode.EXACT_IN.value,
        "slippageBps": 50,
        "priceImpactPct": "1.5",
        "routePlan": [{
            "swapInfo": {
                "ammKey": "amm_key",
                "label": "Orca",
                "inputMint": "0x" + "22" * 32,
                "outputMint": "0x" + "33" * 32,
                "inAmount": "1000000",
                "outAmount": "2000000",
                "feeAmount": "1000",
                "feeMint": "0x" + "44" * 32,
            },
            "percent": 100.0,
        }],
        "contextSlot": 123456789,
        "timeTaken": 0.123,
    })
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    quote = await client.get_quote(
        input_mint="0x" + "22" * 32,
        output_mint="0x" + "33" * 32,
        amount=1000000,
    )

    assert quote.input_mint == "0x" + "22" * 32
    assert quote.in_amount == "1000000"
    assert quote.output_mint == "0x" + "33" * 32
    assert quote.out_amount == "2000000"
    assert quote.other_amount_threshold == "1900000"
    assert quote.swap_mode == SwapMode.EXACT_IN
    assert quote.slippage_bps == 50
    assert quote.price_impact_pct == "1.5"
    assert len(quote.route_plan) == 1
    assert quote.route_plan[0].swap_info.amm_key == "amm_key"
    assert quote.route_plan[0].swap_info.label == "Orca"
    assert quote.route_plan[0].swap_info.input_mint == "0x" + "22" * 32
    assert quote.route_plan[0].swap_info.output_mint == "0x" + "33" * 32
    assert quote.route_plan[0].swap_info.in_amount == "1000000"
    assert quote.route_plan[0].swap_info.out_amount == "2000000"
    assert quote.route_plan[0].swap_info.fee_amount == "1000"
    assert quote.route_plan[0].swap_info.fee_mint == "0x" + "44" * 32
    assert quote.route_plan[0].percent == 100.0
    assert quote.context_slot == 123456789
    assert quote.time_taken == 0.123


@pytest.mark.asyncio
async def test_get_quote_failure():
    """Test get_quote method failure case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={"error": "Invalid input"})
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    with pytest.raises(QuoteError, match="Failed to get quote: Invalid input"):
        await client.get_quote(
            input_mint="0x" + "22" * 32,
            output_mint="0x" + "33" * 32,
            amount=1000000,
        )


@pytest.mark.asyncio
async def test_get_swap_transaction(mock_wallet_client, mock_quote_response):
    """Test get_swap_transaction method."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "swapTransaction": base64.b64encode(b"mock_transaction_data").decode(),
        "addressLookupTables": ["0x" + "44" * 32],
    })
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    swap_response = await client.get_swap_transaction(
        wallet_client=mock_wallet_client,
        quote=mock_quote_response,
    )

    assert swap_response.swap_transaction == base64.b64encode(b"mock_transaction_data").decode()
    assert swap_response.address_lookup_tables == ["0x" + "44" * 32]


@pytest.mark.asyncio
async def test_get_swap_transaction_failure(mock_wallet_client, mock_quote_response):
    """Test get_swap_transaction method failure case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={"error": "Invalid quote"})
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    with pytest.raises(SwapError, match="Failed to get swap transaction: Invalid quote"):
        await client.get_swap_transaction(
            wallet_client=mock_wallet_client,
            quote=mock_quote_response,
        )


@pytest.mark.asyncio
async def test_execute_swap(mock_wallet_client, mock_quote_response, mock_swap_response):
    """Test execute_swap method."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "swapTransaction": base64.b64encode(b"mock_transaction_data").decode(),
        "addressLookupTables": ["0x" + "44" * 32],
    })
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    mock_wallet_client.deserialize_transaction = AsyncMock(return_value="mock_transaction")
    mock_wallet_client.send_transaction = AsyncMock(return_value="0x" + "55" * 32)

    result = await client.execute_swap(
        wallet_client=mock_wallet_client,
        quote=mock_quote_response,
    )

    assert result.transaction_hash == "0x" + "55" * 32
    assert result.input_amount == mock_quote_response.in_amount
    assert result.output_amount == mock_quote_response.out_amount
    assert result.price_impact == mock_quote_response.price_impact_pct
    assert result.fee_amount == mock_quote_response.route_plan[0].swap_info.fee_amount
    assert result.route_plan == [step.model_dump(by_alias=True) for step in mock_quote_response.route_plan]

    mock_wallet_client.deserialize_transaction.assert_called_once_with(mock_swap_response.swap_transaction)
    mock_wallet_client.send_transaction.assert_called_once_with("mock_transaction")

    # Mock swap execution error
    with patch.object(client, "get_swap_transaction", side_effect=SwapError("Failed to get swap transaction")):
        async with client:
            with pytest.raises(SwapError, match="Failed to get swap transaction"):
                await client.execute_swap(
                    wallet_client=mock_wallet_client,
                    quote=mock_quote_response,
                ) 


@pytest.mark.asyncio
async def test_execute_swap_failure(mock_wallet_client, mock_quote_response):
    """Test execute_swap method failure case."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "swapTransaction": "invalid_transaction_data",
        "addressLookupTables": ["0x" + "44" * 32],
    })
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    # Set up the mock to raise the error when deserializing
    mock_wallet_client.deserialize_transaction = AsyncMock(side_effect=SwapError("Failed to deserialize transaction: Invalid transaction data"))

    async with client:
        with pytest.raises(SwapError, match="Failed to deserialize transaction: Invalid transaction data"):
            await client.execute_swap(
                wallet_client=mock_wallet_client,
                quote=mock_quote_response,
            )


@pytest.mark.asyncio
async def test_retry_on_network_error():
    """Test retry mechanism on network error."""
    client = JupiterClient(config=JupiterConfig(max_retries=2, retry_delay=0.1))
    mock_session = AsyncMock()
    
    # First call raises network error
    mock_session.post = AsyncMock(side_effect=[
        aiohttp.ClientError("Network error"),
        AsyncMock(
            status=200,
            json=AsyncMock(return_value={
                "inputMint": "0x" + "22" * 32,
                "inAmount": "1000000",
                "outputMint": "0x" + "33" * 32,
                "outAmount": "2000000",
                "otherAmountThreshold": "1900000",
                "swapMode": SwapMode.EXACT_IN.value,
                "slippageBps": 50,
                "priceImpactPct": "1.5",
                "routePlan": [{
                    "swapInfo": {
                        "ammKey": "amm_key",
                        "label": "Orca",
                        "inputMint": "0x" + "22" * 32,
                        "outputMint": "0x" + "33" * 32,
                        "inAmount": "1000000",
                        "outAmount": "2000000",
                        "feeAmount": "1000",
                        "feeMint": "0x" + "44" * 32,
                    },
                    "percent": 100.0,
                }],
                "contextSlot": 123456789,
                "timeTaken": 0.123,
            }),
            __aenter__=AsyncMock(return_value=AsyncMock(
                status=200,
                json=AsyncMock(return_value={
                    "inputMint": "0x" + "22" * 32,
                    "inAmount": "1000000",
                    "outputMint": "0x" + "33" * 32,
                    "outAmount": "2000000",
                    "otherAmountThreshold": "1900000",
                    "swapMode": SwapMode.EXACT_IN.value,
                    "slippageBps": 50,
                    "priceImpactPct": "1.5",
                    "routePlan": [{
                        "swapInfo": {
                            "ammKey": "amm_key",
                            "label": "Orca",
                            "inputMint": "0x" + "22" * 32,
                            "outputMint": "0x" + "33" * 32,
                            "inAmount": "1000000",
                            "outAmount": "2000000",
                            "feeAmount": "1000",
                            "feeMint": "0x" + "44" * 32,
                        },
                        "percent": 100.0,
                    }],
                    "contextSlot": 123456789,
                    "timeTaken": 0.123,
                })
            )),
            __aexit__=AsyncMock(return_value=None)
        )
    ])
    client._session = mock_session

    async with client:
        quote = await client.get_quote(
            input_mint="0x" + "22" * 32,
            output_mint="0x" + "33" * 32,
            amount=1000000,
        )

        assert quote.input_mint == "0x" + "22" * 32
        assert quote.in_amount == "1000000"
        assert mock_session.post.call_count == 2  # Verify retry happened


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization without session."""
    client = JupiterClient()
    assert client._session is None
    assert client.config is not None

    client = JupiterClient(session=AsyncMock())
    assert client._session is not None


@pytest.mark.asyncio
async def test_context_manager():
    """Test client context manager."""
    client = JupiterClient()
    assert client._session is None

    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.closed = False

    with patch("aiohttp.ClientSession", return_value=mock_session):
        async with client:
            assert client._session is not None

        assert client._session is None
        await mock_session.close.aclose()


@pytest.mark.asyncio
async def test_get_quote_not_initialized():
    """Test get_quote without initializing client."""
    client = JupiterClient()
    
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client._get_quote_internal(
            input_mint="0x" + "22" * 32,
            output_mint="0x" + "33" * 32,
            amount=1000000,
        )


@pytest.mark.asyncio
async def test_get_swap_transaction_not_initialized():
    """Test get_swap_transaction without initializing client."""
    client = JupiterClient()
    mock_wallet_client = AsyncMock()
    mock_quote_response = AsyncMock()
    
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client._get_swap_transaction_internal(
            wallet_client=mock_wallet_client,
            quote=mock_quote_response,
        )


@pytest.mark.asyncio
async def test_get_swap_transaction_with_error(mock_quote_response):
    """Test get_swap_transaction with error."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_session.post = AsyncMock(side_effect=Exception("Failed to get swap transaction"))
    client._session = mock_session

    mock_wallet_client = AsyncMock()
    mock_wallet_client.public_key = "0x" + "11" * 32

    with pytest.raises(SwapError, match="Failed to get swap transaction: Failed to get swap transaction"):
        await client.get_swap_transaction(
            wallet_client=mock_wallet_client,
            quote=mock_quote_response,
        )


@pytest.mark.asyncio
async def test_execute_swap_not_initialized(mock_wallet_client, mock_quote_response):
    """Test execute_swap without initializing client."""
    client = JupiterClient(config=JupiterConfig())
    
    with pytest.raises(RuntimeError, match="Client not initialized. Use async context manager."):
        await client.execute_swap(
            wallet_client=mock_wallet_client,
            quote=mock_quote_response,
        )


@pytest.mark.asyncio
async def test_execute_swap_send_error(mock_wallet_client, mock_quote_response):
    """Test execute_swap with transaction sending error."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "swapTransaction": base64.b64encode(b"mock_transaction_data").decode(),
        "addressLookupTables": ["0x" + "44" * 32],
    })
    mock_session.post = AsyncMock(return_value=mock_response)
    client._session = mock_session

    mock_wallet_client.deserialize_transaction = AsyncMock(return_value="mock_transaction")
    mock_wallet_client.send_transaction = AsyncMock(side_effect=Exception("Failed to send transaction"))

    async with client:
        with pytest.raises(SwapError, match="Failed to send transaction: Failed to send transaction"):
            await client.execute_swap(
                wallet_client=mock_wallet_client,
                quote=mock_quote_response,
            )


@pytest.mark.asyncio
async def test_execute_swap_error_handling(mock_wallet_client, mock_quote_response):
    """Test execute_swap error handling."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    
    # Test get_swap_transaction error
    mock_session.post = AsyncMock(side_effect=Exception("Failed to get swap transaction"))
    client._session = mock_session

    async with client:
        with pytest.raises(SwapError, match="Failed to get swap transaction: Failed to get swap transaction"):
            await client.execute_swap(
                wallet_client=mock_wallet_client,
                quote=mock_quote_response,
            )


@pytest.mark.asyncio
async def test_get_swap_transaction_network_error(mock_wallet_client, mock_quote_response):
    """Test get_swap_transaction with network error."""
    client = JupiterClient(config=JupiterConfig())
    mock_session = AsyncMock()
    mock_session.post = AsyncMock(side_effect=aiohttp.ClientError("Network error"))
    client._session = mock_session

    with pytest.raises(aiohttp.ClientError, match="Network error while getting swap transaction: Network error"):
        await client.get_swap_transaction(
            wallet_client=mock_wallet_client,
            quote=mock_quote_response,
        )