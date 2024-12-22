# API Reference

## Core Components

### WalletClient

Base client for interacting with a Solana wallet.

```python
class WalletClient:
    def __init__(self, private_key: str, provider_url: str = "https://api.mainnet-beta.solana.com"):
        """Initialize wallet client.
        
        Args:
            private_key (str): Base58 encoded private key
            provider_url (str): RPC endpoint URL
        """
        pass

    async def send_transaction(self, transaction: Transaction) -> str:
        """Send a transaction.
        
        Args:
            transaction (Transaction): Transaction to send
            
        Returns:
            str: Transaction signature
        """
        pass
```

## Jupiter Plugin

### JupiterPlugin

Plugin for token swaps using Jupiter aggregator.

```python
class JupiterPlugin:
    def __init__(self, wallet_client: WalletClient):
        """Initialize Jupiter plugin.
        
        Args:
            wallet_client (WalletClient): Wallet client instance
        """
        pass

    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
    ) -> Quote:
        """Get a quote for swapping tokens.
        
        Args:
            input_mint (str): Input token mint address
            output_mint (str): Output token mint address
            amount (int): Amount of input tokens (in smallest units)
            slippage_bps (int): Slippage tolerance in basis points (1 bp = 0.01%)
            
        Returns:
            Quote: Quote information including output amount and price impact
            
        Raises:
            QuoteError: If quote cannot be obtained
            NetworkError: If network request fails
        """
        pass

    async def swap(self, quote: Quote) -> str:
        """Execute a token swap.
        
        Args:
            quote (Quote): Quote from get_quote()
            
        Returns:
            str: Transaction signature
            
        Raises:
            TransactionError: If transaction fails
            NetworkError: If network request fails
        """
        pass
```

## NFT Plugin

### NFTPlugin

Plugin for NFT operations on Solana.

```python
class NFTPlugin:
    def __init__(self, wallet_client: WalletClient):
        """Initialize NFT plugin.
        
        Args:
            wallet_client (WalletClient): Wallet client instance
        """
        pass

    async def mint(self, metadata: NFTMetadata) -> MintResult:
        """Mint a regular NFT.
        
        Args:
            metadata (NFTMetadata): NFT metadata
            
        Returns:
            MintResult: Mint result containing addresses
            
        Raises:
            TransactionError: If minting fails
        """
        pass

    async def mint_compressed_nft(self, params: CompressedNFTParams) -> CompressedMintResult:
        """Mint a compressed NFT.
        
        Args:
            params (CompressedNFTParams): Minting parameters
            
        Returns:
            CompressedMintResult: Mint result containing asset ID and tree info
            
        Raises:
            TransactionError: If minting fails
        """
        pass

    async def transfer(self, mint: str, to_address: str) -> str:
        """Transfer a regular NFT.
        
        Args:
            mint (str): NFT mint address
            to_address (str): Recipient address
            
        Returns:
            str: Transaction signature
            
        Raises:
            TransactionError: If transfer fails
        """
        pass

    async def transfer_compressed_nft(
        self,
        asset_id: str,
        to_address: str,
    ) -> str:
        """Transfer a compressed NFT.
        
        Args:
            asset_id (str): Asset ID of the compressed NFT
            to_address (str): Recipient address
            
        Returns:
            str: Transaction signature
            
        Raises:
            TransactionError: If transfer fails
        """
        pass
```

### Types

```python
class NFTMetadata(BaseModel):
    """NFT metadata."""
    name: str
    symbol: str
    description: str
    seller_fee_basis_points: int
    image: str
    external_url: Optional[str] = None
    attributes: Optional[List[Dict[str, Any]]] = None
    collection: Optional[Dict[str, str]] = None
    properties: Optional[Dict[str, Any]] = None
    creators: List[Creator]

class Creator(BaseModel):
    """NFT creator."""
    address: str
    share: int
    verified: bool

class CompressedNFTParams(BaseModel):
    """Parameters for minting compressed NFTs."""
    metadata: NFTMetadata
    tree_address: Optional[str] = None
    max_depth: int = 14
    max_buffer_size: int = 64
```

## SPL Token Plugin

### SPLTokenPlugin

Plugin for SPL token operations.

```python
class SPLTokenPlugin:
    def __init__(self, wallet_client: WalletClient):
        """Initialize SPL Token plugin.
        
        Args:
            wallet_client (WalletClient): Wallet client instance
        """
        pass

    async def create_account(self, mint: str) -> str:
        """Create a token account.
        
        Args:
            mint (str): Token mint address
            
        Returns:
            str: Token account address
            
        Raises:
            TransactionError: If account creation fails
        """
        pass

    async def transfer(
        self,
        mint: str,
        to_address: str,
        amount: int,
    ) -> str:
        """Transfer tokens.
        
        Args:
            mint (str): Token mint address
            to_address (str): Recipient address
            amount (int): Amount to transfer (in smallest units)
            
        Returns:
            str: Transaction signature
            
        Raises:
            TransactionError: If transfer fails
            InsufficientBalanceError: If balance is insufficient
        """
        pass

    async def get_balance(self, mint: str) -> int:
        """Get token balance.
        
        Args:
            mint (str): Token mint address
            
        Returns:
            int: Token balance in smallest units
        """
        pass
```

## Tensor Plugin

### TensorPlugin

Plugin for NFT trading on Tensor.

```python
class TensorPlugin:
    def __init__(self, wallet_client: WalletClient, config: TensorConfig):
        """Initialize Tensor plugin.
        
        Args:
            wallet_client (WalletClient): Wallet client instance
            config (TensorConfig): Tensor configuration
        """
        pass

    async def get_nft_info(self, mint: str) -> NFTInfo:
        """Get NFT information.
        
        Args:
            mint (str): NFT mint address
            
        Returns:
            NFTInfo: NFT information including owner and sales history
            
        Raises:
            NetworkError: If API request fails
        """
        pass

    async def get_buy_listing_transaction(self, mint: str) -> Transaction:
        """Get transaction for buying an NFT.
        
        Args:
            mint (str): NFT mint address
            
        Returns:
            Transaction: Transaction to execute the purchase
            
        Raises:
            NetworkError: If API request fails
            NoListingError: If no listing is found
        """
        pass
```

### Types

```python
class TensorConfig(BaseModel):
    """Tensor configuration."""
    api_key: str
    api_url: str = "https://api.tensor.so"

class NFTInfo(BaseModel):
    """NFT information from Tensor."""
    onchain_id: str
    owner: str
    last_sale: Optional[LastSale] = None
    listings: List[Listing] = []

class LastSale(BaseModel):
    """Last sale information."""
    price: float
    timestamp: int
    buyer: str
    seller: str

class Listing(BaseModel):
    """NFT listing information."""
    price: float
    seller: str
    signature: str
```

## Error Types

```python
class QuoteError(Exception):
    """Error getting a quote."""
    pass

class TransactionError(Exception):
    """Error executing a transaction."""
    pass

class NetworkError(Exception):
    """Network request error."""
    pass

class InsufficientBalanceError(Exception):
    """Insufficient balance for operation."""
    pass

class NoListingError(Exception):
    """No listing found for NFT."""
    pass
```

## Constants

```python
# Common token mints
WSOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Program IDs
METADATA_PROGRAM_ID = "metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s"
BUBBLEGUM_PROGRAM_ID = "BGUMAp9Gq7iTEuizy4pqaxsTyUCBK68MDfK752saRPUY"

# Default values
DEFAULT_SLIPPAGE_BPS = 50  # 0.5%
DEFAULT_COMMITMENT = "confirmed"
``` 