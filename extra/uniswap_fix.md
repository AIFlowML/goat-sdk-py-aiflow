# Uniswap Test and Implementation Discrepancies

## Discrepancies Found

1. **Method Availability**: Ensure all methods called in the test file exist in the `UniswapService` class.
   - Methods like `get_token_info`, `get_pool_info_v3`, etc., should be verified for existence and correct implementation.

2. **Parameter Matching**: Verify that parameters used in test methods match those expected by the implementation.

3. **Mocking Consistency**: Ensure that mocking aligns with actual dependencies and interactions in the implementation.
