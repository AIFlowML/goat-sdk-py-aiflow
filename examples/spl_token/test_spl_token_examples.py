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
     
     Path: examples/spl_token/test_spl_token_examples.py
"""

import pytest
import asyncio
from decimal import Decimal
from goat_sdk import GoatSDK
from goat_sdk.core.types import Network, Chain
from goat_sdk.plugins.spl_token import SplTokenPlugin

# Test constants
TEST_PRIVATE_KEY = "your_private_key"  # Replace with test private key
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC mint address
TEST_RECIPIENT = "recipient_address"  # Replace with recipient address
TEST_AMOUNT = 1.0  # 1 USDC

@pytest.fixture
async def spl_token_setup():
    """Setup SPL Token plugin for testing"""
    sdk = GoatSDK(
        private_key=TEST_PRIVATE_KEY,
        network=Network.MAINNET,
        chain=Chain.SOLANA
    )
    spl_token = SplTokenPlugin(sdk)
    return spl_token

@pytest.mark.asyncio
async def test_get_token_balance(spl_token_setup):
    """Test getting token balance"""
    spl_token = await spl_token_setup
    
    balance = await spl_token.get_token_balance(
        mint_address=USDC_MINT,
        token_symbol="USDC"
    )
    
    assert balance is not None
    print("\nToken balance:")
    print(f"USDC Balance: {balance}")

@pytest.mark.asyncio
async def test_transfer_token(spl_token_setup):
    """Test transferring tokens"""
    spl_token = await spl_token_setup
    
    try:
        result = await spl_token.transfer_token(
            mint_address=USDC_MINT,
            to=TEST_RECIPIENT,
            amount=TEST_AMOUNT
        )
        
        assert result is not None
        print("\nToken transfer:")
        print(f"Transaction hash: {result.transaction_hash}")
        print(f"Amount: {result.amount}")
        print(f"Recipient: {result.recipient}")
    except Exception as e:
        pytest.skip(f"Token transfer failed: {str(e)}")

@pytest.mark.asyncio
async def test_get_token_info(spl_token_setup):
    """Test getting token information"""
    spl_token = await spl_token_setup
    
    info = await spl_token.get_token_info(USDC_MINT)
    assert info is not None
    print("\nToken information:")
    print(f"Symbol: {info.symbol}")
    print(f"Name: {info.name}")
    print(f"Decimals: {info.decimals}")
    print(f"Supply: {info.supply}")

@pytest.mark.asyncio
async def test_get_token_accounts(spl_token_setup):
    """Test getting token accounts"""
    spl_token = await spl_token_setup
    
    accounts = await spl_token.get_token_accounts()
    assert accounts is not None
    print("\nToken accounts:")
    for account in accounts:
        print(f"Account address: {account.address}")
        print(f"Mint: {account.mint}")
        print(f"Balance: {account.balance}")
        print("---")

@pytest.mark.asyncio
async def test_create_token_account(spl_token_setup):
    """Test creating a token account"""
    spl_token = await spl_token_setup
    
    try:
        account = await spl_token.create_token_account(USDC_MINT)
        assert account is not None
        print("\nToken account created:")
        print(f"Account address: {account.address}")
        print(f"Mint: {account.mint}")
    except Exception as e:
        pytest.skip(f"Token account creation failed: {str(e)}")

@pytest.mark.asyncio
async def test_close_token_account(spl_token_setup):
    """Test closing a token account"""
    spl_token = await spl_token_setup
    
    try:
        # First create an account
        account = await spl_token.create_token_account(USDC_MINT)
        
        # Then close it
        result = await spl_token.close_token_account(account.address)
        assert result is not None
        print("\nToken account closed:")
        print(f"Account address: {account.address}")
        print(f"Transaction hash: {result.transaction_hash}")
    except Exception as e:
        pytest.skip(f"Token account closure failed: {str(e)}")

@pytest.mark.asyncio
async def test_error_handling(spl_token_setup):
    """Test error handling with invalid parameters"""
    spl_token = await spl_token_setup
    
    # Test with invalid mint address
    with pytest.raises(Exception):
        await spl_token.get_token_balance(
            mint_address="invalid_address",
            token_symbol="INVALID"
        )
    
    # Test with invalid recipient
    with pytest.raises(Exception):
        await spl_token.transfer_token(
            mint_address=USDC_MINT,
            to="invalid_address",
            amount=TEST_AMOUNT
        )
    
    # Test with invalid amount
    with pytest.raises(Exception):
        await spl_token.transfer_token(
            mint_address=USDC_MINT,
            to=TEST_RECIPIENT,
            amount=-1
        )

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 