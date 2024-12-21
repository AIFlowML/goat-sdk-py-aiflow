"""
Tests for advanced security features.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from decimal import Decimal
from web3 import Web3

from goat_sdk.plugins.uniswap.advanced_security import TokenSecurityChecker

@pytest.fixture
def web3_mock():
    mock = Mock(spec=Web3)
    mock.eth = MagicMock()
    mock.eth.chain_id = 1
    mock.eth.get_code = AsyncMock()
    mock.eth.get_storage_at = AsyncMock()
    mock.eth.get_transaction_receipt = AsyncMock()
    return mock

@pytest.fixture
def security_checker(web3_mock):
    return TokenSecurityChecker(web3_mock)

@pytest.mark.asyncio
async def test_verify_token_no_code(security_checker, web3_mock):
    """Test verification of non-existent contract."""
    web3_mock.eth.get_code.return_value = b""
    
    result, message = await security_checker.verify_token("0x1234")
    assert result is False
    assert "No contract code found" in message

@pytest.mark.asyncio
async def test_verify_token_proxy_contract(security_checker, web3_mock):
    """Test verification of proxy contract."""
    # Mock proxy contract code
    proxy_code = "0x363d3d373d3d3d363d73"
    web3_mock.eth.get_code.return_value = bytes.fromhex(proxy_code[2:])
    
    # Mock implementation address
    impl_address = "0x" + "1" * 40
    web3_mock.eth.get_storage_at.return_value = bytes.fromhex("00" * 12 + impl_address[2:])
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock Etherscan response
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"status": "1", "result": "Contract source code"}
        )
        
        result, message = await security_checker.verify_token("0x1234")
        assert result is True
        assert message is None

@pytest.mark.asyncio
async def test_verify_token_malicious_pattern(security_checker, web3_mock):
    """Test detection of malicious patterns."""
    # Mock contract code with selfdestruct
    code = "0x60806040selfdestruct"
    web3_mock.eth.get_code.return_value = bytes.fromhex(code[2:])
    
    result, message = await security_checker.verify_token("0x1234")
    assert result is False
    assert "Malicious pattern detected" in message

@pytest.mark.asyncio
async def test_verify_token_metadata(security_checker, web3_mock):
    """Test token metadata verification."""
    web3_mock.eth.get_code.return_value = bytes.fromhex("60806040")
    
    contract_mock = Mock()
    contract_mock.functions.name.return_value.call = AsyncMock(return_value="Test Token")
    contract_mock.functions.symbol.return_value.call = AsyncMock(return_value="TEST")
    contract_mock.functions.decimals.return_value.call = AsyncMock(return_value=18)
    contract_mock.functions.totalSupply.return_value.call = AsyncMock(return_value=1000000)
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={"status": "1", "result": "Contract source code"}
            )
            
            result, message = await security_checker.verify_token("0x1234")
            assert result is True
            assert message is None

@pytest.mark.asyncio
async def test_verify_token_transfer_functionality(security_checker, web3_mock):
    """Test transfer functionality verification."""
    web3_mock.eth.get_code.return_value = bytes.fromhex("60806040")
    
    contract_mock = Mock()
    contract_mock.functions.transfer.return_value.call = AsyncMock(return_value=True)
    contract_mock.functions.name.return_value.call = AsyncMock(return_value="Test Token")
    contract_mock.functions.symbol.return_value.call = AsyncMock(return_value="TEST")
    contract_mock.functions.decimals.return_value.call = AsyncMock(return_value=18)
    contract_mock.functions.totalSupply.return_value.call = AsyncMock(return_value=1000000)
    
    with patch("web3.eth.Contract", return_value=contract_mock):
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(
                return_value={"status": "1", "result": "Contract source code"}
            )
            
            result, message = await security_checker.verify_token("0x1234")
            assert result is True
            assert message is None

@pytest.mark.asyncio
async def test_verify_token_blacklisted(security_checker, web3_mock):
    """Test blacklisted token detection."""
    web3_mock.eth.get_code.return_value = bytes.fromhex("60806040")
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        # Mock GoPlus Security API response
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"result": {"is_blacklisted": True}}
        )
        
        result, message = await security_checker.verify_token("0x1234")
        assert result is False
        assert "blacklisted" in message.lower()

@pytest.mark.asyncio
async def test_analyze_pattern_context(security_checker, web3_mock):
    """Test pattern context analysis."""
    web3_mock.eth.get_code.return_value = bytes.fromhex("60806040")
    web3_mock.eth.get_transaction_receipt.return_value = {
        "blockNumber": 1000000,
        "status": 1
    }
    
    result = await security_checker._analyze_pattern_context("0x1234", "selfdestruct")
    assert isinstance(result, bool)
