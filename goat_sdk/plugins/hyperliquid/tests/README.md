# Hyperliquid Plugin Tests

This directory contains tests for the Hyperliquid plugin. The tests cover market data, order management, and account management functionality.

## Test Structure

- `conftest.py`: Test configuration and fixtures
- `test_market_data.py`: Tests for market data methods
- `test_order_management.py`: Tests for order management methods
- `test_account.py`: Tests for account management methods
- `pytest.ini`: Pytest configuration

## Running Tests

### Environment Setup

Before running the tests, set up your environment variables:

```bash
export HYPERLIQUID_API_KEY="your_api_key"
export HYPERLIQUID_API_SECRET="your_api_secret"
```

### Running All Tests

To run all tests:

```bash
pytest
```

### Running Specific Test Categories

To run only market data tests (no authentication required):
```bash
pytest test_market_data.py
```

To run tests that require authentication:
```bash
pytest --run-auth
```

To run tests for a specific module with authentication:
```bash
pytest --run-auth test_order_management.py
```

### Test Options

- `--run-auth`: Enable tests that require authentication
- `-v`: Verbose output
- `-s`: Show print statements
- `-k "test_name"`: Run specific test by name

## Test Coverage

The tests cover:

1. Market Data
   - Getting market information
   - Getting market summaries
   - Getting orderbook data
   - Getting recent trades
   - WebSocket subscriptions

2. Order Management
   - Creating orders
   - Canceling orders
   - Getting order status
   - Managing open orders

3. Account Management
   - Getting account information
   - Managing positions
   - Getting margin information
   - Setting leverage
   - Viewing funding payments and transaction history

## Test Environment

Tests are configured to run against the Hyperliquid testnet by default. The test address used is:
```
0xEfDaFA4Cc07BbF8421477db4E3Ce79C96Baf5465
```

## Notes

- All authenticated tests are marked with `@pytest.mark.skipif(not pytest.config.getoption("--run-auth"))`
- Tests use small order sizes and far-from-market prices to avoid accidental executions
- WebSocket tests have timeouts to prevent hanging
- All tests clean up after themselves (canceling orders, resetting leverage, etc.) 