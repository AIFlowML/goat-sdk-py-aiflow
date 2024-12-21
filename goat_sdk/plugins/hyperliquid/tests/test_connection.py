"""Test connection to Hyperliquid API."""

import pytest
import aiohttp
import ssl
import json

pytestmark = pytest.mark.asyncio

async def test_api_connection():
    """Test basic connection to Hyperliquid API endpoints."""
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Test mainnet endpoint
    mainnet_url = "https://api.hyperliquid.xyz/info"
    testnet_url = "https://api.hyperliquid-testnet.xyz/info"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "goat-sdk/1.0.0"
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        # Test mainnet
        print("\nTesting mainnet connection...")
        try:
            async with session.post(mainnet_url, json={"type": "meta"}, ssl=ssl_context) as response:
                print(f"Mainnet Status: {response.status}")
                print(f"Mainnet Headers: {json.dumps(dict(response.headers), indent=2)}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Mainnet Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
        except Exception as e:
            print(f"Mainnet Error: {str(e)}")
            raise
            
        # Test testnet
        print("\nTesting testnet connection...")
        try:
            async with session.post(testnet_url, json={"type": "meta"}, ssl=ssl_context) as response:
                print(f"Testnet Status: {response.status}")
                print(f"Testnet Headers: {json.dumps(dict(response.headers), indent=2)}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Testnet Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
        except Exception as e:
            print(f"Testnet Error: {str(e)}")
            raise
            
        # Test getting all markets
        print("\nTesting get all markets...")
        try:
            async with session.post(testnet_url, json={"type": "metaAndAssetCtxs"}, ssl=ssl_context) as response:
                print(f"Markets Status: {response.status}")
                print(f"Markets Headers: {json.dumps(dict(response.headers), indent=2)}")
                if response.status == 200:
                    data = await response.json()
                    print(f"Markets Response: {json.dumps(data, indent=2)}")
                assert response.status == 200
        except Exception as e:
            print(f"Markets Error: {str(e)}")
            raise 