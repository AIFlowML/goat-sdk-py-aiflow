"""
Advanced security features for Uniswap operations.
"""

import asyncio
from typing import Dict, List, Optional, Set, Tuple
from decimal import Decimal
import json
import aiohttp
from web3 import Web3
from eth_abi.codec import ABICodec
from eth_utils import to_checksum_address
from datetime import datetime, timedelta

class TokenSecurityChecker:
    """Advanced token security verification."""
    
    def __init__(self, web3: Web3):
        self.web3 = web3
        self._verified_cache: Dict[str, bool] = {}
        self._token_metadata: Dict[str, Dict] = {}
        self._suspicious_patterns: Set[str] = set()
        
    async def verify_token(self, token_address: str) -> Tuple[bool, Optional[str]]:
        """Comprehensive token verification."""
        try:
            # Check contract code
            code = await self._get_contract_code(token_address)
            if not code:
                return False, "No contract code found"

            # Check for proxy patterns
            if await self._is_proxy_contract(token_address, code):
                implementation = await self._get_implementation_address(token_address)
                if not implementation:
                    return False, "Unable to verify proxy implementation"
                token_address = implementation

            # Verify source code
            if not await self._verify_source_code(token_address):
                return False, "Contract not verified"

            # Check for malicious patterns
            malicious = await self._check_malicious_patterns(token_address, code)
            if malicious:
                return False, f"Malicious pattern detected: {malicious}"

            # Check token metadata
            if not await self._verify_token_metadata(token_address):
                return False, "Invalid token metadata"

            # Check transfer functionality
            if not await self._test_transfer_functionality(token_address):
                return False, "Transfer functionality check failed"

            # Check for blacklists
            if await self._is_blacklisted(token_address):
                return False, "Token is blacklisted"

            return True, None

        except Exception as e:
            return False, f"Verification error: {str(e)}"

    async def _get_contract_code(self, address: str) -> Optional[str]:
        """Get contract bytecode."""
        code = await self._call_async(self.web3.eth.get_code, address)
        return code.hex() if code else None

    async def _is_proxy_contract(self, address: str, code: str) -> bool:
        """Check if contract is a proxy."""
        proxy_patterns = [
            "363d3d373d3d3d363d73",  # EIP-1167 minimal proxy
            "5c60806040",  # OpenZeppelin TransparentUpgradeableProxy
        ]
        return any(pattern in code for pattern in proxy_patterns)

    async def _get_implementation_address(self, proxy_address: str) -> Optional[str]:
        """Get implementation address for proxy contract."""
        try:
            # Try EIP-1967 storage slot
            slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
            implementation = await self._call_async(
                self.web3.eth.get_storage_at,
                proxy_address,
                slot
            )
            return to_checksum_address(implementation[-20:])
        except:
            return None

    async def _verify_source_code(self, address: str) -> bool:
        """Verify contract source code using multiple sources."""
        # Check Etherscan
        async with aiohttp.ClientSession() as session:
            try:
                etherscan_api_key = "YOUR_API_KEY"  # Should be configured
                url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={etherscan_api_key}"
                async with session.get(url) as response:
                    data = await response.json()
                    if data["status"] == "1" and data["result"] != "Contract source code not verified":
                        return True
            except:
                pass

        # Check Sourcify
        try:
            url = f"https://sourcify.dev/server/check-by-addresses?addresses={address}&chainIds={self.web3.eth.chain_id}"
            async with session.get(url) as response:
                data = await response.json()
                if data and data[0]["status"] == "perfect":
                    return True
        except:
            pass

        return False

    async def _check_malicious_patterns(self, address: str, code: str) -> Optional[str]:
        """Check for malicious code patterns."""
        patterns = {
            "selfdestruct": "Potential self-destruct functionality",
            "delegatecall": "Dangerous delegatecall usage",
            "transfer.{0,20}\\(address": "Potential fee manipulation",
            "owner.{0,20}transfer": "Suspicious owner transfer",
            "_balances\\[address\\]": "Direct balance manipulation",
            "assembly": "Contains assembly code",
        }

        for pattern, message in patterns.items():
            if pattern in code.lower():
                # Further analyze context
                if await self._analyze_pattern_context(address, pattern):
                    return message

        return None

    async def _verify_token_metadata(self, address: str) -> bool:
        """Verify token metadata integrity."""
        try:
            erc20_abi = [
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
            ]
            
            contract = self.web3.eth.contract(address=address, abi=erc20_abi)
            
            # Check basic metadata
            name = await self._call_async(contract.functions.name().call)
            symbol = await self._call_async(contract.functions.symbol().call)
            decimals = await self._call_async(contract.functions.decimals().call)
            total_supply = await self._call_async(contract.functions.totalSupply().call)
            
            # Validate metadata
            if not name or not symbol or decimals > 18 or total_supply == 0:
                return False
                
            # Cache metadata
            self._token_metadata[address] = {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "totalSupply": total_supply,
            }
            
            return True
            
        except Exception:
            return False

    async def _test_transfer_functionality(self, address: str) -> bool:
        """Test token transfer functionality."""
        try:
            erc20_abi = [
                {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
                {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
            ]
            
            contract = self.web3.eth.contract(address=address, abi=erc20_abi)
            
            # Simulate transfer
            test_address = "0x0000000000000000000000000000000000000001"
            try:
                success = await self._call_async(
                    contract.functions.transfer(test_address, 0).call
                )
                return bool(success)
            except Exception as e:
                # Check if revert reason is acceptable
                revert_msg = str(e).lower()
                acceptable_reasons = ["insufficient", "balance", "allowance"]
                return any(reason in revert_msg for reason in acceptable_reasons)
                
        except Exception:
            return False

    async def _is_blacklisted(self, address: str) -> bool:
        """Check if token is blacklisted."""
        # Check local blacklist
        if address in self._suspicious_patterns:
            return True
            
        # Check external blacklists
        async with aiohttp.ClientSession() as session:
            try:
                # Example: Check GoPlus Security API
                url = f"https://api.gopluslabs.io/api/v1/token_security/{self.web3.eth.chain_id}/{address}"
                async with session.get(url) as response:
                    data = await response.json()
                    if data.get("result", {}).get("is_blacklisted"):
                        return True
            except:
                pass
        
        return False

    async def _analyze_pattern_context(self, address: str, pattern: str) -> bool:
        """Analyze context of suspicious pattern."""
        try:
            # Get contract creation transaction
            creation_tx = await self._get_contract_creation_tx(address)
            if not creation_tx:
                return True  # Suspicious if we can't verify

            # Analyze transaction history
            suspicious_activity = await self._analyze_transaction_history(address)
            if suspicious_activity:
                return True

            # Pattern-specific checks
            if pattern == "selfdestruct":
                return await self._check_selfdestruct_risk(address)
            elif pattern == "delegatecall":
                return await self._check_delegatecall_risk(address)

            return False

        except Exception:
            return True  # Suspicious if analysis fails

    async def _call_async(self, func, *args, **kwargs):
        """Execute Web3 calls asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(
            None, func, *args, **kwargs
        )
