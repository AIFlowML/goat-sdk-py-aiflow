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
     
     Path: examples/adapters/langchain_example.py
"""

"""
Helper functions and classes for testing GOAT SDK.
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
import asyncio
from unittest.mock import AsyncMock
from web3.types import Wei

class TransactionBuilder:
    """Helper class to build test transactions."""
    @staticmethod
    def build_swap_tx(
        token_in: str,
        token_out: str,
        amount_in: Decimal,
        min_amount_out: Decimal,
        path: List[str],
        recipient: str,
        deadline: int
    ) -> Dict[str, Any]:
        """Build a swap transaction."""
        return {
            "to": "0x" + "1" * 40,  # Router address
            "data": "0x",  # Encoded function data
            "value": Wei(0),
            "gas": 200000,
            "maxFeePerGas": Wei(20000000000),  # 20 gwei
            "maxPriorityFeePerGas": Wei(2000000000),  # 2 gwei
            "nonce": 0,
            "chainId": 1
        }

    @staticmethod
    def build_approve_tx(
        token: str,
        spender: str,
        amount: int
    ) -> Dict[str, Any]:
        """Build an approve transaction."""
        return {
            "to": token,
            "data": "0x",  # Encoded approve function data
            "value": Wei(0),
            "gas": 50000,
            "maxFeePerGas": Wei(20000000000),
            "maxPriorityFeePerGas": Wei(2000000000),
            "nonce": 0,
            "chainId": 1
        }

class EventSimulator:
    """Helper class to simulate blockchain events."""
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.blocks: List[Dict[str, Any]] = []
        self.current_block = 1000

    def add_swap_event(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        amount_out: int,
        sender: str,
        recipient: str,
        block_number: Optional[int] = None
    ):
        """Add a swap event."""
        if block_number is None:
            block_number = self.current_block
        
        self.events.append({
            "event": "Swap",
            "address": "0x" + "1" * 40,
            "blockNumber": block_number,
            "transactionHash": "0x" + "2" * 64,
            "args": {
                "tokenIn": token_in,
                "tokenOut": token_out,
                "amountIn": amount_in,
                "amountOut": amount_out,
                "sender": sender,
                "recipient": recipient
            }
        })

    def add_block(
        self,
        transactions: Optional[List[Dict[str, Any]]] = None,
        timestamp: Optional[int] = None
    ):
        """Add a new block."""
        self.current_block += 1
        self.blocks.append({
            "number": self.current_block,
            "timestamp": timestamp or (1600000000 + self.current_block),
            "transactions": transactions or []
        })

    async def get_events(
        self,
        from_block: int,
        to_block: int,
        event_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get events matching the filter."""
        return [
            event for event in self.events
            if from_block <= event["blockNumber"] <= to_block
        ]

class PriceSimulator:
    """Helper class to simulate price updates."""
    def __init__(self):
        self.prices: Dict[str, Decimal] = {}
        self.updates: List[Dict[str, Any]] = []

    def set_token_price(self, token: str, price: Decimal):
        """Set price for a token."""
        self.prices[token] = price
        self.updates.append({
            "token": token,
            "price": price,
            "timestamp": 1600000000
        })

    def get_token_price(self, token: str) -> Optional[Decimal]:
        """Get current price for a token."""
        return self.prices.get(token)

    def simulate_price_impact(
        self,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Decimal:
        """Simulate price impact of a swap."""
        if token_in not in self.prices or token_out not in self.prices:
            return Decimal("0")

        # Simple price impact simulation
        price_in = self.prices[token_in]
        price_out = self.prices[token_out]
        value = amount_in * price_in
        impact = Decimal("0.997") if value < 10000 else Decimal("0.995")
        return (Decimal("1") - impact) * Decimal("100")

class GasSimulator:
    """Helper class to simulate gas prices and estimates."""
    def __init__(self):
        self.base_fee = Wei(10000000000)  # 10 gwei
        self.priority_fee = Wei(2000000000)  # 2 gwei
        self.estimates: Dict[str, int] = {}

    def set_gas_price(self, base_fee: Wei, priority_fee: Wei):
        """Set current gas prices."""
        self.base_fee = base_fee
        self.priority_fee = priority_fee

    def set_estimate(self, operation: str, gas: int):
        """Set gas estimate for operation."""
        self.estimates[operation] = gas

    async def get_gas_price(self) -> Dict[str, Wei]:
        """Get current gas prices."""
        return {
            "baseFee": self.base_fee,
            "priorityFee": self.priority_fee,
            "maxFee": self.base_fee * 2
        }

    async def estimate_gas(self, operation: str) -> int:
        """Estimate gas for operation."""
        return self.estimates.get(operation, 200000)

class NetworkSimulator:
    """Helper class to simulate network conditions."""
    def __init__(self):
        self.latency = 0.1  # seconds
        self.failure_rate = 0.0
        self.rpc_calls = 0
        self.failed_calls = 0

    def set_conditions(self, latency: float, failure_rate: float):
        """Set network conditions."""
        self.latency = latency
        self.failure_rate = failure_rate

    async def simulate_call(self):
        """Simulate an RPC call."""
        self.rpc_calls += 1
        await asyncio.sleep(self.latency)
        
        if self.failure_rate > 0:
            import random
            if random.random() < self.failure_rate:
                self.failed_calls += 1
                raise Exception("Network error")
