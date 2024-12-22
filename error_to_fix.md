# Errors to Fix in GOAT-sdk-py

## Import Errors

1. **PublicKey Import Error**
   - Files affected:
     - `tests/plugins/nft/test_nft_plugin.py`
     - `tests/plugins/spl_token/test_spl_token_service_integration.py`
   - Error: `ImportError: cannot import name 'PublicKey' from 'pubkey'`
   - Fix needed: Update imports to use correct Solders package path

2. **TransferParams Import Error**
   - File: `tests/plugins/spl_token/test_spl_token_plugin.py`
   - Error: `ImportError: cannot import name 'TransferParams' from 'goat_sdk.plugins.spl_token.models'`
   - Fix needed: Add TransferParams to models.py or update import path

## Collection Warnings

1. **Constructor Warnings**
   - Files affected:
     - `tests/core/decorators/test_tool.py`
     - `tests/core/utils/test_create_tool_parameters.py`
     - `tests/core/utils/test_get_tools.py`
   - Warning: `cannot collect test class because it has a __init__ constructor`
   - Fix needed: Review test class design and remove unnecessary constructors

## Action Items

1. Fix Solders Package Integration:
   - Verify solders package installation
   - Update import statements for PublicKey
   - Check package version compatibility

2. Update Models:
   - Add missing TransferParams model to models.py
   - Or correct the import path if it exists elsewhere

3. Test Class Refactoring:
   - Review and refactor test classes with constructors
   - Consider using pytest fixtures instead of constructors

## Dependencies to Check

1. solders
2. pytest
3. pydantic

## Next Steps

1. Fix import errors first as they're blocking test execution
2. Then address constructor warnings
3. Run tests again to identify any remaining issues 