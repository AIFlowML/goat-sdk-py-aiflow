import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from web3 import Web3
from goat_sdk.plugins.uniswap.advanced_security import TokenSecurityChecker

@pytest.fixture
async def mock_web3():
    with patch('web3.Web3') as MockWeb3:
        mock_instance = MockWeb3.return_value
        mock_instance.eth.get_code = AsyncMock(return_value=b'')
        mock_instance.eth.get_storage_at = AsyncMock(return_value=b'')
        yield mock_instance

@pytest.fixture
async def token_security_checker(mock_web3):
    return TokenSecurityChecker(web3=mock_web3)

@pytest.mark.asyncio
async def test_verify_token_no_code(token_security_checker):
    result, reason = await token_security_checker.verify_token('0x0000000000000000000000000000000000000000')
    assert not result
    assert reason == "No contract code found"

@pytest.mark.asyncio
async def test_verify_token_malicious_pattern(token_security_checker, mock_web3):
    mock_web3.eth.get_code = AsyncMock(return_value=b'\xde\xad\xbe\xef' + b'selfdestruct')
    mock_web3.eth.contract.return_value.functions.name.return_value.call.return_value = 'TestToken'
    mock_web3.eth.contract.return_value.functions.symbol.return_value.call.return_value = 'TT'
    mock_web3.eth.contract.return_value.functions.decimals.return_value.call.return_value = 18
    mock_web3.eth.contract.return_value.functions.totalSupply.return_value.call.return_value = 1000000
    with patch.object(TokenSecurityChecker, '_analyze_pattern_context', return_value=True):
        result, reason = await token_security_checker.verify_token('0x0000000000000000000000000000000000000000')
        assert not result
        assert "Malicious pattern detected" in reason

@pytest.mark.asyncio
async def test_is_proxy_contract(token_security_checker):
    code = bytes.fromhex('363d3d373d3d3d363d73')
    assert token_security_checker._is_proxy_contract(code)

@pytest.mark.asyncio
async def test_get_implementation_address(token_security_checker, mock_web3):
    mock_web3.eth.get_storage_at = AsyncMock(return_value=b'\x00' * 12 + bytes.fromhex('0000000000000000000000000000000000000001'))
    address = await token_security_checker._get_implementation_address('0x0000000000000000000000000000000000000000')
    assert address == Web3.to_checksum_address('0x0000000000000000000000000000000000000001')

@pytest.mark.asyncio
async def test_call_async(token_security_checker):
    async def sample_func():
        return 'test'
    result = await token_security_checker._call_async(sample_func)
    assert result == 'test'
