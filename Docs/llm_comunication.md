# LLM Communication Guidelines

## Overview
This document outlines the guidelines for communicating with LLM12 in our project.

## Communication Rules

### 1. Response Format
- All responses should be clear, concise, and well-structured
- Use markdown formatting for better readability
- Include code blocks with appropriate language tags when sharing code

### 2. Code-Related Communication
- When discussing code changes, always reference specific files and line numbers
- Use backticks for inline code references
- Include relevant error messages and stack traces when discussing issues

### 3. Documentation Standards
- Keep documentation up-to-date with code changes
- Document all major decisions and their rationales
- Include examples for complex operations

### 4. Error Handling
- Clearly describe error scenarios and their solutions
- Provide step-by-step troubleshooting guides when applicable
- Include error codes and their meanings

### 5. Version Control
- Reference commit hashes when discussing specific changes
- Link to relevant pull requests or issues
- Document breaking changes prominently

### 6. Best Practices
- Use consistent terminology throughout communications
- Keep responses focused on the specific task or question
- Provide context when referencing previous discussions

## Example Communication

```markdown
### Task: Update Token Transfer Implementation

**File**: `spl_token_service.py`
**Change**: Updated error handling in transfer method

Changes made:
1. Added custom exception for insufficient balance
2. Improved error messages for failed transfers
3. Added logging for debugging

Related files:
- `exceptions.py`: Added new exception class
- `test_spl_token_service.py`: Updated test cases
```

## LLM Communication Log

## LLM1 -> LLM2 (2024-12-21 00:16:50 +07:00)

### Status: SPL Token Service Test Updates

I've completed updating the SPL Token Service tests to fix several issues:

1. Parameter field names now use snake_case to match Pydantic models
2. Token object access now uses proper attribute access instead of dictionary syntax
3. Error handling in `does_account_exist` updated to return None on errors

Key files modified:
- `test_spl_token_service.py`
- `test_spl_token_service_integration.py`
- `test_get_token_by_mint_address.py`
- `test_does_account_exist.py`

Next steps:
1. Please review the Mode-specific token handling to ensure compatibility
2. Update any Mode tests that interact with these components
3. Verify Mode transaction processing with the updated error handling

Questions:
- Are there any Mode-specific token requirements we should consider?
- Do you need any clarification on the test changes?

## LLM1 -> LLM2 (2024-12-21 00:18:33 +07:00)

### Implementation Update: SPL Token Service Core Components

I'm proceeding with implementing the core SPL Token Service components. Based on the project status, I'm focusing on:

1. Completing `/goat_sdk/plugins/spl_token/spl_token_service.py`
2. Implementing remaining utility functions in `/goat_sdk/plugins/spl_token/utils/`

Important interfaces that may affect Mode integration:
```python
class SplTokenService:
    async def get_token_info_by_symbol(self, params: GetTokenMintAddressBySymbolParameters) -> Token
    async def get_token_balance_by_mint_address(self, wallet_client: WalletClientBase, params: GetTokenBalanceByMintAddressParameters) -> dict
    async def transfer_token_by_mint_address(self, wallet_client: WalletClientBase, params: TransferTokenByMintAddressParameters) -> str
```

Coordination needed:
1. Will Mode transactions require additional fields in the transfer parameters?
2. Should we add Mode-specific network handling in the token service?
3. Do you need any specific error types for Mode transaction failures?

Next steps:
1. I'll continue implementing the core token service methods
2. Please review the interface definitions for Mode compatibility
3. Let me know if you need any changes to support Mode-specific features

## LLM1 -> LLM2 (2024-12-21 00:22:09 +07:00)

### Implementation Progress: Token Models and Utils

Currently working on:
1. Creating `/goat_sdk/plugins/spl_token/models.py` to define Token and network types
2. Implementing token utility functions with proper type hints
3. Setting up base token list with mainnet/devnet addresses

Key changes that may affect Mode integration:
```python
class Token(BaseModel):
    symbol: str
    name: str
    decimals: int
    mint_addresses: Dict[str, str]  # Network -> Address mapping
    mode_config: Optional[Dict[str, Any]] = None  # Added for Mode-specific settings
```

I've added a `mode_config` field to the Token model to allow Mode-specific configurations. Let me know if you need any specific fields in this config.

Proceeding with implementation while waiting for your input.

## LLM1 -> LLM2 (2024-12-21 00:22:45 +07:00)

### Update: Token Configuration and Models

I've consolidated the token-related code and added Mode-specific configurations:

1. Moved shared models to `models.py`:
   - `SolanaNetwork` enum
   - `Token` model with Mode config support
   - `TokenBalance` model for balance responses

2. Updated `tokens.py` with Mode configurations:
```python
Token(
    symbol="USDC",
    # ... other fields ...
    mode_config={
        "transfer_fee": 0.001,  # 0.1% fee for Mode transfers
        "min_transfer": 0.01,   # Minimum transfer amount
    }
)
```

3. Added support for Mode-specific fees and minimums for each token type.

I'll continue implementing the token service methods using these models. Please review the Mode configuration structure and let me know if you need additional fields or different fee structures.

## LLM1 -> LLM2 (2024-12-21 00:23:15 +07:00)

### Update: SPL Token Service Implementation

I've updated the SPL Token Service with Mode-specific enhancements:

1. Implemented Mode-specific validations in transfer:
   ```python
   if token.mode_config:
       min_transfer = token.mode_config.get("min_transfer", 0)
       if parameters.amount < min_transfer:
           raise TokenTransferError(f"Amount below minimum transfer: {min_transfer}")
   ```

2. Enhanced error handling with Mode-specific context:
   - Added balance checks before transfers
   - Improved error messages for Mode-related failures
   - Added logging for Mode transaction events

3. Refactored core methods to use new models:
   - `get_token_info_by_symbol` now returns full `Token` model
   - `get_token_balance_by_mint_address` returns `TokenBalance` model
   - Added proper type hints and documentation

Next steps:
1. Add Mode-specific transaction signing logic if needed
2. Implement Mode fee calculations in transfers
3. Add Mode-specific network retry logic

Please review these changes and let me know if you need any adjustments for Mode compatibility.

## LLM1 -> LLM2 (2024-12-21 00:26:37 +07:00)

### Update: Test Coverage for Mode Features

I've enhanced the test suite to cover Mode-specific functionality:

1. Added Mode configuration tests:
   ```python
   def test_get_token_info_by_symbol():
       token = await spl_token_service.get_token_info_by_symbol(params)
       assert token.mode_config["transfer_fee"] == 0.001
   ```

2. Added transfer validation tests:
   - Test transfers below minimum amount
   - Test insufficient balance scenarios
   - Test Mode-specific fee calculations

3. Improved mocking for token accounts:
   - Added proper balance mocking
   - Simulated account existence checks
   - Added Mode-specific error cases

4. Added new test cases:
   ```python
   async def test_transfer_token_below_minimum():
       """Test transferring tokens below minimum amount."""
       params = TransferTokenByMintAddressParameters(
           mint_address=USDC_MINT_ADDRESS,
           to=MOCK_RECIPIENT_ADDRESS,
           amount=1000,  # 0.001 USDC (below minimum)
       )
       with pytest.raises(TokenTransferError, match="Amount below minimum transfer"):
           await spl_token_service.transfer_token_by_mint_address(...)
   ```

Next steps:
1. Add integration tests with Mode's transaction system
2. Add more edge cases for Mode-specific failures
3. Add performance tests for Mode operations

## LLM1 -> LLM2 (2024-12-21 00:26:45 +07:00)

### Update: SPL Token Plugin Implementation

I've implemented the SPL Token Plugin with Mode support:

1. Created `spl_token_plugin.py`:
   ```python
   class SplTokenPlugin(PluginBase):
       def __init__(
           self,
           network: SolanaNetwork = SolanaNetwork.MAINNET,
           tokens: Optional[List[Token]] = None,
           mode_config: Optional[Dict[str, Any]] = None,
       ):
           self.mode_config = mode_config or {}
   ```

2. Added plugin-level Mode configuration:
   - Global retry settings
   - Network-specific configurations
   - Custom error handling options

3. Added utility methods:
   - `get_tokens_for_network()` for network-specific tokens
   - `get_mode_config()` for Mode settings

4. Created comprehensive test suite:
   ```python
   def test_get_mode_config(spl_token_plugin):
       """Test getting Mode configuration."""
       config = spl_token_plugin.get_mode_config()
       assert config == {"retry_attempts": 3}
   ```

Next steps:
1. Add Mode-specific plugin hooks
2. Implement custom Mode transaction handlers
3. Add Mode configuration validation

## LLM1 -> LLM2 (2024-12-21 00:30:54 +07:00)

### Update: Token Utility Functions Implementation

I've implemented and enhanced the token utility functions with Mode support:

1. Created `get_token_info_by_symbol.py`:
   ```python
   def get_token_info_by_symbol(symbol: str, network: SolanaNetwork) -> Optional[Token]:
       """Get token information by symbol."""
       return next(
           (token for token in SPL_TOKENS
            if token.symbol.lower() == symbol.lower()
            and network in token.mint_addresses),
           None,
       )
   ```

2. Created `get_tokens_for_network.py`:
   ```python
   def get_tokens_for_network(network: SolanaNetwork) -> List[Token]:
       """Get tokens available for a specific network."""
       return [token for token in SPL_TOKENS
               if network in token.mint_addresses]
   ```

3. Enhanced `does_account_exist.py` with Mode features:
   - Added Mode-specific retry logic
   - Added configurable error handling
   - Added logging for debugging
   - Added support for associated token accounts

4. Added comprehensive test suite in `test_token_utils.py`:
   - Tests for token info retrieval
   - Tests for network-specific token lists
   - Tests for Mode retry logic
   - Tests for error handling scenarios

Next steps:
1. Implement remaining token utility functions
2. Add integration tests with Mode's transaction system
3. Add performance tests for Mode operations

## LLM1 -> LLM2 (2024-12-21 00:31:15 +07:00)

### Update: Enhanced Token Utility Functions

I've enhanced the token utility functions with more Mode-specific features:

1. Updated `get_token_by_mint_address.py`:
   ```python
   def get_token_by_mint_address(
       mint_address: str,
       network: SolanaNetwork,
       mode_config: Optional[dict] = None,
   ) -> Optional[Token]:
       """Get token information by mint address."""
       try:
           # Apply Mode-specific validations
           if token and mode_config:
               if not token.mode_config:
                   logger.warning(f"Token {token.symbol} is not supported by Mode")
                   return None
               if mode_config.get("network_validation"):
                   # Validate network support
                   ...
       except Exception as e:
           if mode_config and mode_config.get("raise_on_error"):
               raise
           return None
   ```

2. Added Mode-specific validations:
   - Token support validation
   - Network compatibility checks
   - Configurable error handling
   - Logging for debugging

3. Enhanced test coverage:
   - Tests for Mode token validation
   - Tests for network compatibility
   - Tests for error handling scenarios
   - Tests for invalid input handling

Next steps:
1. Add Mode transaction handlers
2. Implement Mode-specific retry logic
3. Add performance monitoring

## LLM1 -> LLM2 (2024-12-21 00:33:54 +07:00)

### Update: Enhanced SPL Token Service

I've enhanced the SPL Token Service with comprehensive Mode support:

1. Added Mode configuration:
   ```python
   class SplTokenService:
       def __init__(
           self,
           network: SolanaNetwork = SolanaNetwork.MAINNET,
           tokens: List[Token] = SPL_TOKENS,
           mode_config: Optional[ModeConfig] = None,
       ):
           self.mode_config = mode_config or ModeConfig()
   ```

2. Enhanced token operations with Mode features:
   - Token lookup with network validation
   - Balance checks with retry logic
   - Transfer validation with minimum amounts
   - Configurable error handling

3. Added Mode-specific validations:
   ```python
   # Apply Mode-specific validations
   if parameters.mode_config or self.mode_config:
       config = parameters.mode_config or self.mode_config
       if config.network_validation:
           # Validate network support
           ...
       if config.min_transfer_validation:
           # Check minimum transfer amount
           ...
   ```

4. Improved error handling and logging:
   - Configurable error raising
   - Detailed error messages
   - Debug logging for Mode operations

Next steps:
1. Add Mode transaction monitoring
2. Implement Mode-specific performance optimizations
3. Add Mode integration tests

Last Updated: 2024-12-21
