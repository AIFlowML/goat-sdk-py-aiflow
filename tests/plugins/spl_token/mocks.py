"""Mock responses for SPL Token tests."""

def get_mock_token_account_response():
    """Get a mock token account response."""
    return {
        "context": {"slot": 1},
        "value": {
            "data": {
                "parsed": {
                    "info": {
                        "isNative": False,
                        "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                        "owner": "5ZWj7a1f8tWkjBESHKgrLmXshuXxqeGWh9r9TE6aafPF",
                        "state": "initialized",
                        "tokenAmount": {
                            "amount": "100000000",
                            "decimals": 6,
                            "uiAmount": 100.0,
                            "uiAmountString": "100"
                        }
                    },
                    "type": "account"
                },
                "program": "spl-token",
                "space": 165
            },
            "executable": False,
            "lamports": 2039280,
            "owner": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
            "rentEpoch": 361
        }
    }

def get_mock_token_account_balance_response():
    """Get a mock token account balance response."""
    return {
        "context": {"slot": 1},
        "value": {
            "amount": "100000000",
            "decimals": 6,
            "uiAmount": 100.0,
            "uiAmountString": "100"
        }
    } 