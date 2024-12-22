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
     
     Path: examples/hyperliquid/ai_trading_agent.py
"""

"""Token definitions and utilities."""
from dataclasses import dataclass
from typing import Dict, List, Optional
from eth_typing import ChecksumAddress


@dataclass
class ChainSpecificToken:
    """Token information for a specific chain."""
    chain_id: int
    decimals: int
    symbol: str
    name: str
    contract_address: ChecksumAddress


@dataclass
class Token:
    """Token information across multiple chains."""
    decimals: int
    symbol: str
    name: str
    chains: Dict[int, Dict[str, ChecksumAddress]]


# Pre-defined tokens
USDC = Token(
    decimals=6,
    symbol="USDC",
    name="USDC",
    chains={
        1: {"contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
        10: {"contract_address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85"},
        137: {"contract_address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"},
        8453: {"contract_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"},
        84532: {"contract_address": "0x036CbD53842c5426634e7929541eC2318f3dCF7e"},
        11155111: {"contract_address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238"},
        34443: {"contract_address": "0xd988097fb8612cc24eeC14542bC03424c656005f"},
    }
)

MODE = Token(
    decimals=18,
    symbol="MODE",
    name="Mode",
    chains={
        34443: {"contract_address": "0xDfc7C877a950e49D2610114102175A06C2e3167a"},
    }
)

# Default tokens list
DEFAULT_TOKENS = [USDC, MODE]


def get_tokens_for_network(chain_id: int, tokens: Optional[List[Token]] = None) -> List[ChainSpecificToken]:
    """Get all tokens available for a specific network.
    
    Args:
        chain_id: Chain ID to get tokens for
        tokens: Optional list of tokens to filter from. If not provided, uses DEFAULT_TOKENS
        
    Returns:
        List of tokens available on the specified chain
    """
    tokens = tokens or DEFAULT_TOKENS
    result = []

    for token in tokens:
        chain_data = token.chains.get(chain_id)
        if chain_data:
            result.append(ChainSpecificToken(
                chain_id=chain_id,
                decimals=token.decimals,
                symbol=token.symbol,
                name=token.name,
                contract_address=chain_data["contract_address"]
            ))

    return result


def get_token_by_symbol(symbol: str, chain_id: int, tokens: Optional[List[Token]] = None) -> Optional[ChainSpecificToken]:
    """Get token information by its symbol for a specific chain.
    
    Args:
        symbol: Token symbol to look for
        chain_id: Chain ID to get token for
        tokens: Optional list of tokens to search in. If not provided, uses DEFAULT_TOKENS
        
    Returns:
        Token information if found, None otherwise
    """
    tokens = tokens or DEFAULT_TOKENS
    symbol = symbol.upper()

    for token in tokens:
        if token.symbol.upper() == symbol and chain_id in token.chains:
            return ChainSpecificToken(
                chain_id=chain_id,
                decimals=token.decimals,
                symbol=token.symbol,
                name=token.name,
                contract_address=token.chains[chain_id]["contract_address"]
            )

    return None
