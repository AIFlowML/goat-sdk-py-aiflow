# SPL Token Service Fix Plan - Revised

## Current State Analysis

### Fixed Components
1. ✅ `does_account_exist.py`
   - Already fixed to handle string to PublicKey conversion
   - Already handles proper error propagation
   - No further changes needed

### Failing Tests Overview

1. `test_get_token_balance_by_mint_address`
   - Error: TokenAccountNotFoundError
   - Root cause: Connection mocking issue
   - File to fix: test_spl_token_service.py

2. `test_transfer_token_by_mint_address`
   - Error: AsyncMock can't be used in await
   - Root cause: Mock setup issue in test
   - File to fix: test_spl_token_service.py

3. `test_transfer_error_handling`
   - Error: Assertion error on error message
   - Root cause: Error message mismatch
   - File to fix: test_spl_token_service_integration.py

## Fix Plan (In Order)

### Phase 1: Test Infrastructure (Day 1 Morning)
1. Create proper mock fixtures in `conftest.py`
   ```python
   @pytest.fixture
   def mock_connection():
       connection = MagicMock()
       connection.get_account_info = AsyncMock()
       connection.get_token_account_balance = AsyncMock()
       return connection

   @pytest.fixture
   def mock_wallet_client(mock_connection):
       client = MagicMock()
       client.get_connection = AsyncMock(return_value=mock_connection)
       return client
   ```

### Phase 2: Fix Token Balance Tests (Day 1 Afternoon)
1. Update `test_spl_token_service.py`
   - Fix mock setup for get_token_balance_by_mint_address test
   - Ensure proper mock responses for account info
   - DO NOT touch the actual service code

### Phase 3: Fix Transfer Tests (Day 1 Evening)
1. Update test mock setup in `test_spl_token_service.py`
   - Fix AsyncMock usage in transfer tests
   - Update error assertions
   - DO NOT modify service implementation yet

### Phase 4: Error Handling (Day 2 Morning)
1. Update error handling in `spl_token_service.py`
   - Focus on transfer_token_by_mint_address error wrapping
   - Standardize error messages
   - Add proper error context

### Phase 5: Integration Tests (Day 2 Afternoon)
1. Fix `test_spl_token_service_integration.py`
   - Update error message assertions
   - Fix mock setup for full flow test
   - Ensure proper error propagation tests

## Testing Strategy

1. Test each phase independently:
```bash
# Phase 1
pytest tests/plugins/spl_token/conftest.py -v

# Phase 2
pytest tests/plugins/spl_token/test_spl_token_service.py::test_get_token_balance_by_mint_address -v

# Phase 3
pytest tests/plugins/spl_token/test_spl_token_service.py::test_transfer_token_by_mint_address -v

# Phase 4
pytest tests/plugins/spl_token/test_spl_token_service.py::test_transfer_error_handling -v

# Phase 5
pytest tests/plugins/spl_token/test_spl_token_service_integration.py -v
```

## Rules for Implementation

1. **No Overlapping Changes**
   - Complete each phase before moving to next
   - Get sign-off on each phase
   - Document any dependencies between phases

2. **Test First Approach**
   - Write/fix tests first
   - Then update implementation
   - Verify no regression

3. **Error Handling Standards**
   - TokenTransferError wraps all transfer errors
   - TokenAccountNotFoundError for missing accounts
   - InsufficientBalanceError for balance issues
   - InvalidTokenAddressError for address validation

4. **Mock Standards**
   - Use MagicMock for synchronous operations
   - Use AsyncMock for coroutines
   - Always mock at fixture level when possible

## Success Criteria

Each phase must meet these criteria before moving on:
1. All tests in the phase pass
2. No regression in previously fixed tests
3. Clear error messages
4. Proper error context
5. Consistent mock usage

## Current Test Status

✅ Fixed:
- does_account_exist.py and related tests

❌ Needs Fix:
1. Token Balance Tests
   - Mock setup issues
   - Connection handling

2. Transfer Tests
   - AsyncMock usage
   - Error propagation

3. Integration Tests
   - Error message assertions
   - Full flow stability

## Next Steps

1. Create `conftest.py` with proper fixtures
2. Update token balance test mocks
3. Fix transfer test async handling
4. Standardize error messages
5. Fix integration test assertions